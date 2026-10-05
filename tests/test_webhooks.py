from __future__ import annotations

import inspect
from urllib.parse import parse_qs

import httpx
import pytest
import pytest_asyncio
import respx

from strava import AsyncStrava, AuthenticationError, Strava, WebhookSubscription

BASE = "https://www.strava.com/api/v3"


@pytest_asyncio.fixture(params=[Strava, AsyncStrava], ids=["sync", "async"])
async def client(request):
    client = request.param(
        access_token="expired_athlete_token",
        client_id="12345",
        client_secret="test_secret",
        refresh_token="test_refresh",
        expires_at=0,
        base_url=BASE,
    )
    yield client
    result = client.close()
    if inspect.isawaitable(result):
        await result


async def invoke(method, *args, **kwargs):
    result = method(*args, **kwargs)
    return await result if inspect.isawaitable(result) else result


@pytest.mark.asyncio
@respx.mock
async def test_create_uses_application_form_credentials(client):
    route = respx.post(f"{BASE}/push_subscriptions").mock(
        return_value=httpx.Response(201, json={"id": 42})
    )
    subscription = await invoke(
        client.webhooks.create,
        client_id="12345",
        client_secret="test_secret",
        callback_url="https://example.com/webhooks?source=strava",
        verify_token="verify & confirm",
    )

    assert isinstance(subscription, WebhookSubscription)
    assert subscription.id == 42
    request = route.calls.last.request
    assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"
    assert parse_qs(request.content.decode()) == {
        "client_id": ["12345"],
        "client_secret": ["test_secret"],
        "callback_url": ["https://example.com/webhooks?source=strava"],
        "verify_token": ["verify & confirm"],
    }
    assert "Authorization" not in request.headers
    assert not request.url.params
    assert len(respx.calls) == 1  # No attempt to refresh the expired athlete token.


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload", [[], [{"id": 42, "callback_url": "https://example.com/webhooks"}]]
)
@respx.mock
async def test_list_uses_query_credentials_without_pagination(client, payload):
    route = respx.get(f"{BASE}/push_subscriptions").mock(
        return_value=httpx.Response(200, json=payload)
    )
    subscriptions = await invoke(
        client.webhooks.list, client_id="12345", client_secret="test_secret"
    )

    assert [s.to_dict() for s in subscriptions] == payload
    assert dict(route.calls.last.request.url.params) == {
        "client_id": "12345",
        "client_secret": "test_secret",
    }
    assert "Authorization" not in route.calls.last.request.headers
    assert len(respx.calls) == 1


@pytest.mark.asyncio
@respx.mock
async def test_delete_uses_query_credentials_and_accepts_empty_response(client):
    route = respx.delete(f"{BASE}/push_subscriptions/42").mock(
        return_value=httpx.Response(204)
    )
    result = await invoke(
        client.webhooks.delete,
        42,
        client_id="12345",
        client_secret="test_secret",
    )

    assert result is None
    request = route.calls.last.request
    assert dict(request.url.params) == {
        "client_id": "12345",
        "client_secret": "test_secret",
    }
    assert not request.content
    assert "Authorization" not in request.headers
    assert len(respx.calls) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["create", "list", "delete"])
@respx.mock
async def test_errors_use_sdk_exception_mapping(client, operation):
    respx.route().mock(
        return_value=httpx.Response(401, json={"message": "Invalid application"})
    )
    kwargs = {"client_id": "12345", "client_secret": "invalid_secret"}
    args = ()
    if operation == "create":
        kwargs.update(callback_url="https://example.com", verify_token="verify")
    elif operation == "delete":
        args = (42,)

    with pytest.raises(AuthenticationError, match="Invalid application"):
        await invoke(getattr(client.webhooks, operation), *args, **kwargs)

    assert len(respx.calls) == 1
