from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx
import pytest

from strava._auth import TOKEN_URL, OAuth2Auth


class AsyncTokenBody(httpx.AsyncByteStream):
    def __init__(self, payload: dict) -> None:
        self.payload = json.dumps(payload).encode()
        self.read_count = 0
        self.closed = False

    async def __aiter__(self) -> AsyncIterator[bytes]:
        self.read_count += 1
        yield self.payload[:20]
        yield self.payload[20:]

    async def aclose(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_async_refresh_reads_stream_then_rotates_tokens_before_request():
    body = AsyncTokenBody(
        {
            "access_token": "rotated_access",
            "refresh_token": "rotated_refresh",
            "expires_at": 9999999999,
            "expires_in": 21600,
            "token_type": "Bearer",
        }
    )
    requests = []
    callbacks = []

    async def handler(request):
        requests.append(request)
        if str(request.url) == TOKEN_URL:
            return httpx.Response(200, stream=body)
        assert body.closed
        return httpx.Response(200, json={"id": 123})

    auth = OAuth2Auth(
        "expired_access",
        client_id="12345",
        client_secret="test_secret",
        refresh_token="old_refresh",
        expires_at=0,
        on_token_refresh=lambda *args: callbacks.append(args),
    )
    async with httpx.AsyncClient(
        auth=auth, transport=httpx.MockTransport(handler)
    ) as client:
        first = await client.get("https://www.strava.com/api/v3/athlete")
        second = await client.get("https://www.strava.com/api/v3/athlete")

    assert first.json() == second.json() == {"id": 123}
    assert body.read_count == 1
    assert body.closed
    assert auth.refresh_token == "rotated_refresh"
    assert auth.access_token == "rotated_access"
    assert callbacks == [("rotated_access", "rotated_refresh", 9999999999)]
    assert [str(request.url) for request in requests] == [
        TOKEN_URL,
        "https://www.strava.com/api/v3/athlete",
        "https://www.strava.com/api/v3/athlete",
    ]
    assert [request.headers["Authorization"] for request in requests[1:]] == [
        "Bearer rotated_access",
        "Bearer rotated_access",
    ]


@pytest.mark.asyncio
async def test_async_auth_does_not_refresh_unexpired_access_token():
    requests = []

    async def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"id": 123})

    auth = OAuth2Auth(
        "current_access",
        client_id="12345",
        client_secret="test_secret",
        refresh_token="current_refresh",
        expires_at=9999999999,
    )
    async with httpx.AsyncClient(
        auth=auth, transport=httpx.MockTransport(handler)
    ) as client:
        response = await client.get("https://www.strava.com/api/v3/athlete")

    assert response.json() == {"id": 123}
    assert len(requests) == 1
    assert requests[0].headers["Authorization"] == "Bearer current_access"
