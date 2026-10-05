from __future__ import annotations

import httpx
import pytest
import respx

from strava import AsyncStrava, Strava
from tests._helpers import invoke


@pytest.mark.asyncio
@pytest.mark.parametrize("client_cls", [Strava, AsyncStrava], ids=["sync", "async"])
@pytest.mark.parametrize(
    ("base_url", "expected_url"),
    [
        (None, "https://www.strava.com/api/v3/athlete"),
        ("https://api-v3.strava.com", "https://api-v3.strava.com/athlete"),
    ],
    ids=["current-default", "explicit-future-host"],
)
@respx.mock
async def test_requests_use_documented_default_or_explicit_host(
    client_cls, base_url, expected_url
):
    route = respx.get(expected_url).mock(
        return_value=httpx.Response(200, json={"id": 123})
    )
    kwargs = {"base_url": base_url} if base_url is not None else {}
    client = client_cls(access_token="test_token", **kwargs)
    try:
        athlete = await invoke(client.athletes.retrieve_authenticated)
    finally:
        await invoke(client.close)

    assert athlete.id == 123
    assert route.call_count == 1
    assert route.calls.last.request.headers["Authorization"] == "Bearer test_token"
