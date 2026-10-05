from __future__ import annotations

import httpx
import pytest
import respx

from strava import (
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    ServerError,
    ValidationError,
    deauthorize,
    exchange_token,
    refresh_access_token,
    revoke_token,
)
from strava._auth import DEAUTHORIZE_URL, REVOKE_URL, TOKEN_URL, OAuth2Auth
from tests._helpers import invoke

ERRORS = [
    (400, ValidationError),
    (401, AuthenticationError),
    (403, AuthorizationError),
    (429, RateLimitError),
    (503, ServerError),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("client_cls", [httpx.Client, httpx.AsyncClient])
@pytest.mark.parametrize(("status", "error_cls"), ERRORS)
async def test_failed_refresh_preserves_error_and_never_requests_resource(
    client_cls, status, error_cls
):
    requests = []
    callbacks = []
    fault = {
        "message": "Refresh rejected",
        "errors": [
            {"resource": "RefreshToken", "field": "refresh_token", "code": "invalid"}
        ],
    }

    def handler(request):
        requests.append(request)
        if str(request.url) == TOKEN_URL:
            return httpx.Response(status, json=fault)
        return httpx.Response(401, json={"message": "Generic authorization error"})

    auth = OAuth2Auth(
        "expired_access",
        client_id="12345",
        client_secret="test_secret",
        refresh_token="invalid_refresh",
        expires_at=0,
        on_token_refresh=lambda *args: callbacks.append(args),
    )
    client = client_cls(auth=auth, transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(error_cls, match="Refresh rejected") as raised:
            await invoke(client.get, "https://www.strava.com/api/v3/athlete")
    finally:
        if isinstance(client, httpx.AsyncClient):
            await client.aclose()
        else:
            client.close()

    assert raised.value.status_code == status
    assert raised.value.fault == fault
    assert str(raised.value.response.url) == TOKEN_URL
    assert raised.value.response.is_closed
    assert [str(request.url) for request in requests] == [TOKEN_URL]
    assert auth.access_token == "expired_access"
    assert auth.refresh_token == "invalid_refresh"
    assert auth.expires_at == 0
    assert callbacks == []


@pytest.mark.parametrize("operation", ["exchange", "refresh", "revoke", "deauthorize"])
@pytest.mark.parametrize(("status", "error_cls"), ERRORS)
@respx.mock(using="httpx")
def test_oauth_helpers_raise_sdk_errors_with_response_metadata(
    operation, status, error_cls, respx_mock
):
    url = {
        "exchange": TOKEN_URL,
        "refresh": TOKEN_URL,
        "revoke": REVOKE_URL,
        "deauthorize": DEAUTHORIZE_URL,
    }[operation]
    fault = {"message": "OAuth rejected", "errors": [{"code": "invalid"}]}
    # Mock at HTTPX level so the recorded response is the one returned to the SDK.
    route = respx_mock.post(url).mock(
        return_value=httpx.Response(
            status,
            json=fault,
            headers={"X-RateLimit-Limit": "200,2000", "X-RateLimit-Usage": "201,20"},
        )
    )

    with pytest.raises(error_cls, match="OAuth rejected") as raised:
        if operation == "exchange":
            exchange_token("12345", "test_secret", "test_code")
        elif operation == "refresh":
            refresh_access_token("12345", "test_secret", "test_refresh")
        elif operation == "revoke":
            revoke_token("12345", "test_secret", "test_token")
        else:
            with pytest.warns(DeprecationWarning):
                deauthorize("test_token")

    assert raised.value.status_code == status
    assert raised.value.fault == fault
    assert raised.value.response is route.calls.last.response
    if status == 429:
        assert raised.value.limit_15min == 200
        assert raised.value.usage_15min == 201


@respx.mock
def test_token_exchange_preserves_non_json_error_text():
    respx.post(TOKEN_URL).mock(
        return_value=httpx.Response(503, text="OAuth temporarily unavailable")
    )
    with pytest.raises(ServerError, match="OAuth temporarily unavailable") as raised:
        exchange_token("12345", "test_secret", "test_code")

    assert raised.value.fault is None
    assert raised.value.status_code == 503
