from __future__ import annotations

from urllib.parse import parse_qs

import httpx
import pytest

from strava import (
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    ServerError,
    TokenResponse,
    ValidationError,
    async_exchange_token,
    async_refresh_access_token,
    async_revoke_token,
    deauthorize,
    exchange_token,
    refresh_access_token,
    revoke_token,
)
from strava._auth import DEAUTHORIZE_URL, REVOKE_URL, TOKEN_URL
from tests._helpers import assert_basic_auth

TOKEN_BODY = {
    "access_token": "new_access",
    "refresh_token": "new_refresh",
    "expires_at": 21600,
    "expires_in": 21600,
    "token_type": "Bearer",
    "scope": "read activity:read_all",
    "athlete": {"id": 123, "firstname": "Jane"},
}
OPERATIONS = [
    (False, "exchange"),
    (False, "refresh"),
    (False, "revoke"),
    (False, "deauthorize"),
    (False, "deauthorize_revoke"),
    (True, "exchange"),
    (True, "refresh"),
    (True, "revoke"),
]
ERRORS = [
    (400, ValidationError),
    (401, AuthenticationError),
    (403, AuthorizationError),
    (429, RateLimitError),
    (503, ServerError),
]


async def call_helper(asynchronous, operation, **kwargs):
    if operation == "exchange":
        if asynchronous:
            return await async_exchange_token("12345", "secret", "code", **kwargs)
        return exchange_token("12345", "secret", "code", **kwargs)
    if operation == "refresh":
        if asynchronous:
            return await async_refresh_access_token(
                "12345", "secret", "old_refresh", **kwargs
            )
        return refresh_access_token("12345", "secret", "old_refresh", **kwargs)
    if operation == "revoke":
        if asynchronous:
            return await async_revoke_token("12345", "secret", "token", **kwargs)
        return revoke_token("12345", "secret", "token", **kwargs)
    if operation == "deauthorize_revoke":
        kwargs.update(client_id="12345", client_secret="secret")
    with pytest.warns(DeprecationWarning):
        return deauthorize("token", **kwargs)


async def close_client(client):
    if isinstance(client, httpx.AsyncClient):
        await client.aclose()
    else:
        client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(("asynchronous", "operation"), OPERATIONS)
@pytest.mark.parametrize(
    ("options", "expected_timeout"),
    [
        pytest.param({}, httpx.Timeout(30.0), id="default"),
        pytest.param({"timeout": None}, httpx.Timeout(None), id="disabled"),
        pytest.param({"timeout": 2.5}, httpx.Timeout(2.5), id="float"),
        pytest.param(
            {"timeout": httpx.Timeout(7.0, connect=1.0)},
            httpx.Timeout(7.0, connect=1.0),
            id="timeout-object",
        ),
    ],
)
async def test_helpers_use_official_url_and_request_timeout_without_mutating_client(
    asynchronous, operation, options, expected_timeout
):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=TOKEN_BODY)

    def unexpected_auth(request):
        pytest.fail("OAuth helpers must not run the supplied client's default auth")

    client_cls = httpx.AsyncClient if asynchronous else httpx.Client
    client = client_cls(
        base_url="https://unrelated.example/api/",
        headers={"Authorization": "Bearer caller_secret", "X-Caller": "retained"},
        auth=unexpected_auth,
        timeout=99.0,
        transport=httpx.MockTransport(handler),
    )
    headers = client.headers.copy()
    timeout = client.timeout
    auth = client.auth
    try:
        result = await call_helper(
            asynchronous, operation, http_client=client, **options
        )

        assert not client.is_closed
        assert client.headers == headers
        assert client.timeout is timeout
        assert client.auth is auth
        assert client.base_url == "https://unrelated.example/api/"

        request = requests[0]
        assert request.method == "POST"
        assert request.extensions["timeout"] == expected_timeout.as_dict()
        assert request.headers["X-Caller"] == "retained"
        data = parse_qs(request.content.decode())
        if operation in {"exchange", "refresh"}:
            assert str(request.url) == TOKEN_URL
            assert "Authorization" not in request.headers
            assert data["client_id"] == ["12345"]
            assert data["client_secret"] == ["secret"]
            assert isinstance(result, TokenResponse)
            assert result.access_token == "new_access"
            assert result.refresh_token == "new_refresh"
            assert result.scope == "read activity:read_all"
            assert result.athlete.id == 123
            if operation == "exchange":
                assert data["grant_type"] == ["authorization_code"]
                assert data["code"] == ["code"]
            else:
                assert data["grant_type"] == ["refresh_token"]
                assert data["refresh_token"] == ["old_refresh"]
        elif operation in {"revoke", "deauthorize_revoke"}:
            assert str(request.url) == REVOKE_URL
            assert_basic_auth(request, "12345", "secret")
            assert data["token"] == ["token"]
            assert result is None
            if operation == "deauthorize_revoke":
                assert data["token_type_hint"] == ["access_token"]
            else:
                assert "token_type_hint" not in data
        else:
            assert str(request.url) == DEAUTHORIZE_URL
            assert "Authorization" not in request.headers
            assert data == {"access_token": ["token"]}
            assert result is None
    finally:
        await close_client(client)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("hint", ["access_token", "refresh_token"])
async def test_revoke_forwards_token_type_hint(asynchronous, hint):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(204)

    client_cls = httpx.AsyncClient if asynchronous else httpx.Client
    client = client_cls(transport=httpx.MockTransport(handler))
    try:
        assert (
            await call_helper(
                asynchronous, "revoke", token_type_hint=hint, http_client=client
            )
            is None
        )
        assert parse_qs(requests[0].content.decode()) == {
            "token": ["token"],
            "token_type_hint": [hint],
        }
    finally:
        await close_client(client)


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["exchange", "refresh", "revoke"])
@pytest.mark.parametrize(("status", "error_cls"), ERRORS)
async def test_async_helpers_preserve_sdk_error_metadata(operation, status, error_cls):
    responses = []
    fault = {"message": "OAuth rejected", "errors": [{"code": "invalid"}]}

    async def handler(request):
        response = httpx.Response(
            status,
            json=fault,
            headers={"X-RateLimit-Limit": "200,2000", "X-RateLimit-Usage": "201,20"},
        )
        responses.append(response)
        return response

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(error_cls, match="OAuth rejected") as raised:
            await call_helper(True, operation, http_client=client)
        assert not client.is_closed

    assert raised.value.status_code == status
    assert raised.value.fault == fault
    assert raised.value.response is responses[0]
    assert raised.value.response.is_closed
    if status == 429:
        assert raised.value.limit_15min == 200
        assert raised.value.usage_15min == 201


@pytest.mark.asyncio
async def test_async_helpers_preserve_non_json_error_text():
    async def handler(request):
        return httpx.Response(503, text="OAuth temporarily unavailable")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(
            ServerError, match="OAuth temporarily unavailable"
        ) as raised:
            await async_exchange_token("12345", "secret", "code", http_client=client)

    assert raised.value.fault is None
    assert raised.value.status_code == 503


@pytest.mark.asyncio
@pytest.mark.parametrize(("asynchronous", "operation"), OPERATIONS)
@pytest.mark.parametrize("outcome", ["success", "http_error", "timeout"])
async def test_helpers_close_only_owned_clients(
    monkeypatch, asynchronous, operation, outcome
):
    clients = []
    client_cls = httpx.AsyncClient if asynchronous else httpx.Client
    timeout_error = httpx.ReadTimeout("OAuth read timed out")

    def handler(request):
        assert request.extensions["timeout"] == httpx.Timeout(30.0).as_dict()
        if outcome == "timeout":
            raise timeout_error
        if outcome == "http_error":
            return httpx.Response(401, json={"message": "OAuth rejected"})
        return httpx.Response(200, json=TOKEN_BODY)

    def create_client():
        client = client_cls(transport=httpx.MockTransport(handler))
        clients.append(client)
        return client

    monkeypatch.setattr(
        "strava._auth.httpx.AsyncClient"
        if asynchronous
        else "strava._auth.httpx.Client",
        create_client,
    )

    if outcome == "success":
        await call_helper(asynchronous, operation)
    else:
        error_cls = httpx.ReadTimeout if outcome == "timeout" else AuthenticationError
        with pytest.raises(error_cls) as raised:
            await call_helper(asynchronous, operation)
        if outcome == "timeout":
            assert raised.value is timeout_error
    assert len(clients) == 1
    assert clients[0].is_closed


@pytest.mark.asyncio
@pytest.mark.parametrize(("asynchronous", "operation"), OPERATIONS)
async def test_transport_timeout_keeps_supplied_client_open(asynchronous, operation):
    timeout_error = httpx.ReadTimeout("OAuth read timed out")

    def handler(request):
        raise timeout_error

    client_cls = httpx.AsyncClient if asynchronous else httpx.Client
    client = client_cls(transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(httpx.ReadTimeout) as raised:
            await call_helper(asynchronous, operation, http_client=client)
        assert raised.value is timeout_error
        assert not client.is_closed
    finally:
        await close_client(client)
