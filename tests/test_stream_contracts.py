from __future__ import annotations

import httpx
import pytest
import respx

from tests._helpers import invoke

BASE = "https://www.strava.com/api/v3"
ENDPOINTS = [
    ("get_activity_streams", "/activities/123/streams"),
    ("get_route_streams", "/routes/123/streams"),
    ("get_segment_effort_streams", "/segment_efforts/123/streams"),
    ("get_segment_streams", "/segments/123/streams"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(("method", "path"), ENDPOINTS)
@pytest.mark.parametrize("shape", ["keyed", "array", "empty-keyed", "empty-array"])
@respx.mock
async def test_stream_endpoints_normalize_responses_and_documented_query(
    client, method, path, shape
):
    keyed = {
        "time": {"data": [0, 1], "original_size": 2, "series_type": "time"},
        "heartrate": {"data": [120, 130], "original_size": 2},
        "future_stream": {"data": [1, 2]},
    }
    if shape == "keyed":
        payload = keyed
    elif shape == "array":
        payload = [{"type": key, **value} for key, value in keyed.items()]
    elif shape == "empty-keyed":
        payload = {}
    else:
        payload = []
    route = respx.get(f"{BASE}{path}").mock(
        return_value=httpx.Response(200, json=payload)
    )
    options = {} if method == "get_route_streams" else {"keys": ["time", "heartrate"]}
    streams = await invoke(getattr(client.streams, method), 123, **options)

    if shape.startswith("empty"):
        assert streams.time is None
        assert streams.heartrate is None
    else:
        assert streams.time.data == [0, 1]
        assert streams.heartrate.data == [120, 130]
        assert "future_stream" not in streams.to_dict()
    expected_query = (
        {}
        if method == "get_route_streams"
        else {"keys": "time,heartrate", "key_by_type": "true"}
    )
    assert dict(route.calls.last.request.url.params) == expected_query


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method", [name for name, _ in ENDPOINTS if name != "get_route_streams"]
)
@respx.mock
async def test_key_by_type_false_is_rejected_before_request(client, method):
    with pytest.raises(ValueError, match="key_by_type.*true"):
        await invoke(
            getattr(client.streams, method), 123, keys=["time"], key_by_type=False
        )

    assert len(respx.calls) == 0
