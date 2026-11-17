from __future__ import annotations

import httpx
import pytest
import respx

from strava import (
    AsyncPaginator,
    ClubActivity,
    Comment,
    DetailedActivity,
    DetailedAthlete,
    DetailedSegmentEffort,
    Lap,
    MetaActivity,
    MetaAthlete,
    Route,
    SummaryActivity,
    SummaryAthlete,
    SyncPaginator,
)
from tests._helpers import invoke

BASE = "https://www.strava.com/api/v3"
LARGE_ID = 2**63 - 1
ID_PAYLOAD = {"id": LARGE_ID, "id_str": str(LARGE_ID)}
MODELS = (
    MetaActivity,
    SummaryActivity,
    DetailedActivity,
    MetaAthlete,
    SummaryAthlete,
    DetailedAthlete,
)


@pytest.mark.parametrize("model_cls", MODELS)
@pytest.mark.parametrize("identifier", [2**31 + 1, 2**53 + 1, LARGE_ID])
def test_identifiers_survive_json_parsing_and_serialization(model_cls, identifier):
    payload = {"id": identifier, "id_str": str(identifier)}
    response = httpx.Response(200, json=payload)
    model = model_cls.from_dict(response.json())

    assert isinstance(model.id, int)
    assert model.id == identifier
    assert model.id_str == str(identifier)
    serialized = model.to_dict()
    assert serialized["id"] == identifier
    assert serialized["id_str"] == str(identifier)
    assert model_cls.from_dict(serialized) == model


@pytest.mark.parametrize("model_cls", MODELS)
@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"id": LARGE_ID},
        {"id": LARGE_ID, "id_str": None},
        {"id": None, "id_str": None},
        {"id": None, "id_str": str(LARGE_ID)},
        {"id_str": str(LARGE_ID)},
    ],
)
def test_identifier_fields_are_independent_and_optional(model_cls, payload):
    model = model_cls.from_dict(payload)
    serialized = model.to_dict()

    for name in ("id", "id_str"):
        assert getattr(model, name) == payload.get(name)
        if payload.get(name) is None:
            assert name not in serialized
        else:
            assert serialized[name] == payload[name]


@pytest.mark.parametrize(
    ("model_cls", "field", "nested_cls"),
    [
        (SummaryActivity, "athlete", MetaAthlete),
        (DetailedActivity, "athlete", MetaAthlete),
        (Lap, "activity", MetaActivity),
        (Lap, "athlete", MetaAthlete),
        (Comment, "athlete", SummaryAthlete),
        (Route, "athlete", SummaryAthlete),
        (DetailedSegmentEffort, "athlete", MetaAthlete),
        (ClubActivity, "athlete", MetaAthlete),
    ],
)
def test_nested_identifiers_survive_parsing_and_serialization(
    model_cls, field, nested_cls
):
    model = model_cls.from_dict({field: ID_PAYLOAD})
    nested = getattr(model, field)

    assert isinstance(nested, nested_cls)
    assert nested.id == LARGE_ID
    assert nested.id_str == str(LARGE_ID)
    assert model.to_dict()[field] == ID_PAYLOAD


@pytest.mark.asyncio
@pytest.mark.parametrize("identifier", [LARGE_ID, str(LARGE_ID)], ids=["int", "str"])
@pytest.mark.parametrize(
    ("resource", "method", "path", "options", "payload"),
    [
        ("activities", "retrieve", f"/activities/{LARGE_ID}", {}, ID_PAYLOAD),
        (
            "activities",
            "update",
            f"/activities/{LARGE_ID}",
            {"name": "Updated"},
            ID_PAYLOAD,
        ),
        ("activities", "list_comments", f"/activities/{LARGE_ID}/comments", {}, []),
        ("activities", "list_kudoers", f"/activities/{LARGE_ID}/kudos", {}, []),
        ("activities", "list_laps", f"/activities/{LARGE_ID}/laps", {}, []),
        ("activities", "list_zones", f"/activities/{LARGE_ID}/zones", {}, []),
        ("athletes", "retrieve_stats", f"/athletes/{LARGE_ID}/stats", {}, {}),
        ("routes", "list_by_athlete", f"/athletes/{LARGE_ID}/routes", {}, []),
        (
            "streams",
            "get_activity_streams",
            f"/activities/{LARGE_ID}/streams",
            {"keys": ["time"]},
            {},
        ),
    ],
)
@respx.mock
async def test_endpoints_preserve_integer_and_string_identifier_paths(
    client, identifier, resource, method, path, options, payload
):
    route = respx.request("PUT" if method == "update" else "GET", f"{BASE}{path}").mock(
        return_value=httpx.Response(200, json=payload)
    )

    endpoint = getattr(getattr(client, resource), method)
    result = await invoke(endpoint, identifier, **options)
    if isinstance(result, (SyncPaginator, AsyncPaginator)):
        await invoke(result.collect)
    elif isinstance(result, DetailedActivity):
        assert result.id == LARGE_ID
        assert result.id_str == str(LARGE_ID)

    assert route.call_count == 1
    assert route.calls.last.request.url.path == f"/api/v3{path}"
