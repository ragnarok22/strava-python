from __future__ import annotations

import httpx
import pytest
import respx

from strava import AsyncStrava, Strava
from strava._auth import TOKEN_URL
from strava._types import NOT_GIVEN
from tests._helpers import invoke


async def close_http(client):
    if isinstance(client, httpx.AsyncClient):
        await client.aclose()
    else:
        client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("sdk_cls", "http_cls"), [(Strava, httpx.Client), (AsyncStrava, httpx.AsyncClient)]
)
@pytest.mark.parametrize("override", [False, True])
async def test_sdk_controls_request_auth_base_url_and_timeout_without_mutating_client(
    sdk_cls, http_cls, override
):
    requests = []
    caller_auth = httpx.BasicAuth("caller", "test_secret")

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"id": 123})

    http = http_cls(
        base_url="https://transport.example/prefix",
        auth=caller_auth,
        timeout=1.5,
        headers={"X-Caller": "retained"},
        transport=httpx.MockTransport(handler),
    )
    kwargs = (
        {"base_url": "https://api.example/custom/v3", "timeout": 7.0}
        if override
        else {}
    )
    sdk = sdk_cls(access_token="sdk_token", http_client=http, **kwargs)
    try:
        athlete = await invoke(sdk.athletes.retrieve_authenticated)
        assert athlete.id == 123
        assert str(requests[0].url) == (
            "https://api.example/custom/v3/athlete"
            if override
            else "https://www.strava.com/api/v3/athlete"
        )
        assert requests[0].headers["Authorization"] == "Bearer sdk_token"
        assert requests[0].headers["X-Caller"] == "retained"
        expected_timeout = 7.0 if override else 30.0
        assert requests[0].extensions["timeout"] == {
            name: expected_timeout for name in ("connect", "read", "write", "pool")
        }
        assert str(http.base_url) == "https://transport.example/prefix/"
        assert http.timeout == httpx.Timeout(1.5)
        assert http.auth is caller_auth
        await invoke(sdk.close)
        assert not http.is_closed
        await invoke(http.get, "https://transport.example/health")
        assert requests[1].headers["Authorization"].startswith("Basic ")
    finally:
        await close_http(http)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("sdk_cls", "http_cls"), [(Strava, httpx.Client), (AsyncStrava, httpx.AsyncClient)]
)
async def test_supplied_client_supports_sdk_token_refresh(sdk_cls, http_cls):
    requests = []
    callbacks = []

    def handler(request):
        requests.append(request)
        if str(request.url) == TOKEN_URL:
            return httpx.Response(
                200,
                json={
                    "access_token": "new_access",
                    "refresh_token": "new_refresh",
                    "expires_at": 9999999999,
                },
            )
        return httpx.Response(200, json={"id": 123})

    http = http_cls(
        base_url="https://www.strava.com/api/v3",
        transport=httpx.MockTransport(handler),
    )
    sdk = sdk_cls(
        access_token="expired_access",
        client_id="12345",
        client_secret="test_secret",
        refresh_token="old_refresh",
        expires_at=0,
        on_token_refresh=lambda *args: callbacks.append(args),
        http_client=http,
    )
    try:
        await invoke(sdk.athletes.retrieve_authenticated)
        await invoke(sdk.athletes.retrieve_authenticated)
        assert [str(request.url) for request in requests] == [
            TOKEN_URL,
            "https://www.strava.com/api/v3/athlete",
            "https://www.strava.com/api/v3/athlete",
        ]
        assert [request.headers["Authorization"] for request in requests[1:]] == [
            "Bearer new_access",
            "Bearer new_access",
        ]
        assert callbacks == [("new_access", "new_refresh", 9999999999)]
    finally:
        await invoke(sdk.close)
        await close_http(http)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("sdk_cls", "http_cls"), [(Strava, httpx.Client), (AsyncStrava, httpx.AsyncClient)]
)
async def test_webhooks_suppress_supplied_auth_and_authorization_headers(
    sdk_cls, http_cls
):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=[])

    http = http_cls(
        base_url="https://www.strava.com/api/v3",
        auth=httpx.BasicAuth("caller", "test_secret"),
        headers={"Authorization": "Bearer caller_header"},
        transport=httpx.MockTransport(handler),
    )
    sdk = sdk_cls(
        access_token="expired_access",
        client_id="12345",
        client_secret="test_secret",
        refresh_token="old_refresh",
        expires_at=0,
        http_client=http,
    )
    try:
        subscriptions = await invoke(
            sdk.webhooks.list, client_id="12345", client_secret="test_secret"
        )
        assert subscriptions == []
        assert len(requests) == 1
        assert "Authorization" not in requests[0].headers
        assert http.headers["Authorization"] == "Bearer caller_header"
    finally:
        await invoke(sdk.close)
        await close_http(http)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("sdk_cls", "http_cls"), [(Strava, httpx.Client), (AsyncStrava, httpx.AsyncClient)]
)
async def test_sdk_context_exit_leaves_supplied_client_open(sdk_cls, http_cls):
    http = http_cls()
    try:
        sdk = sdk_cls(access_token="sdk_token", http_client=http)
        if isinstance(sdk, AsyncStrava):
            async with sdk:
                assert not http.is_closed
        else:
            with sdk:
                assert not http.is_closed
        assert not http.is_closed
    finally:
        await close_http(http)


@pytest.mark.asyncio
@pytest.mark.parametrize("sdk_cls", [Strava, AsyncStrava])
async def test_sdk_closes_clients_it_creates(sdk_cls):
    sdk = sdk_cls(access_token="sdk_token")
    await invoke(sdk.close)
    assert sdk._http.is_closed


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("sdk_cls", "http_cls"), [(Strava, httpx.Client), (AsyncStrava, httpx.AsyncClient)]
)
@pytest.mark.parametrize("supplied", [False, True])
@pytest.mark.parametrize("timeout", [None, 7.0])
@respx.mock
async def test_automatic_refresh_preserves_sdk_timeout(
    sdk_cls, http_cls, supplied, timeout
):
    refresh = respx.post(TOKEN_URL).respond(
        200,
        json={
            "access_token": "new_access",
            "refresh_token": "new_refresh",
            "expires_at": 9999999999,
        },
    )
    athlete = respx.get("https://www.strava.com/api/v3/athlete").respond(
        200, json={"id": 123}
    )
    http = http_cls(timeout=1.5) if supplied else None
    kwargs = {} if timeout is None else {"timeout": timeout}
    sdk = sdk_cls(
        access_token="expired_access",
        client_id="12345",
        client_secret="test_secret",
        refresh_token="old_refresh",
        expires_at=0,
        http_client=http,
        **kwargs,
    )
    try:
        await invoke(sdk.athletes.retrieve_authenticated)
        expected = httpx.Timeout(30.0 if timeout is None else timeout).as_dict()
        assert refresh.calls.last.request.extensions["timeout"] == expected
        assert athlete.calls.last.request.extensions["timeout"] == expected
    finally:
        await invoke(sdk.close)
        if http is not None:
            await close_http(http)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("sdk_cls", "http_cls"), [(Strava, httpx.Client), (AsyncStrava, httpx.AsyncClient)]
)
@pytest.mark.parametrize(
    "auth", [NOT_GIVEN, None, httpx.BasicAuth("override", "secret")]
)
async def test_request_auth_overrides_preserve_client_headers_and_hooks(
    sdk_cls, http_cls, auth
):
    requests = []
    hooked = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"id": 123})

    def hook(request):
        hooked.append(request)

    async def async_hook(request):
        hook(request)

    http = http_cls(
        headers={"Authorization": "Bearer caller_header", "X-Caller": "retained"},
        auth=httpx.BasicAuth("caller", "secret"),
        event_hooks={"request": [async_hook if sdk_cls is AsyncStrava else hook]},
        transport=httpx.MockTransport(handler),
    )
    sdk = sdk_cls(
        access_token="sdk_token",
        base_url="https://api.example/custom/v3/",
        http_client=http,
    )
    original_headers = http.headers.copy()
    try:
        await invoke(sdk._request, "GET", "/athlete", auth=auth)
        request = requests[0]
        assert str(request.url) == "https://api.example/custom/v3/athlete"
        assert request.headers["X-Caller"] == "retained"
        if auth is None:
            assert "Authorization" not in request.headers
        elif auth is NOT_GIVEN:
            assert request.headers["Authorization"] == "Bearer sdk_token"
        else:
            assert request.headers["Authorization"] == "Basic b3ZlcnJpZGU6c2VjcmV0"
        assert hooked == requests
        assert http.headers == original_headers
    finally:
        await invoke(sdk.close)
        await close_http(http)
