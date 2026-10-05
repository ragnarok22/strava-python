"""Regression fixtures drawn from Strava's reference examples and model schemas.

Activity metrics combine selected fields from the list/get activity examples.
PR stats match the starSegment sample; effort stats match SummarySegmentEffort.
Source: https://developers.strava.com/docs/reference/
"""

from __future__ import annotations

import inspect
import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest
import pytest_asyncio
import respx

from strava import (
    AsyncStrava,
    DetailedActivity,
    DetailedSegment,
    Strava,
    SummaryActivity,
    SummarySegment,
    SummarySegmentEffort,
)

BASE = "https://www.strava.com/api/v3"
FIXTURES = Path(__file__).parent / "fixtures"
ACTIVITY_FIELDS = (
    "resource_state",
    "has_heartrate",
    "average_heartrate",
    "max_heartrate",
    "average_cadence",
    "average_temp",
    "pr_count",
    "suffer_score",
    "utc_offset",
)


def fixture(name):
    return json.loads((FIXTURES / name).read_text())


@pytest.mark.parametrize("model_cls", [SummaryActivity, DetailedActivity])
def test_activity_metrics_survive_parsing_and_serialization(model_cls):
    payload = fixture("activity-metrics.json")
    activity = model_cls.from_dict(payload)

    for name in ACTIVITY_FIELDS:
        assert getattr(activity, name) == payload[name]
        assert activity.to_dict()[name] == payload[name]


@pytest.mark.parametrize("model_cls", [SummaryActivity, DetailedActivity])
@pytest.mark.parametrize("values", ["omitted", "null", "zero"])
def test_activity_metrics_handle_optional_and_zero_values(model_cls, values):
    if values == "omitted":
        payload = {"id": 1}
    elif values == "null":
        payload = {name: None for name in ACTIVITY_FIELDS}
    else:
        payload = {name: 0 for name in ACTIVITY_FIELDS}
        payload["resource_state"] = 2
        payload["has_heartrate"] = False
    activity = model_cls.from_dict(payload)

    for name in ACTIVITY_FIELDS:
        assert getattr(activity, name) == payload.get(name)
        if values == "zero":
            assert activity.to_dict()[name] == payload[name]
        else:
            assert name not in activity.to_dict()


@pytest.mark.parametrize("model_cls", [SummarySegment, DetailedSegment])
def test_segment_flags_and_sample_pr_stats_survive_parsing(model_cls):
    segment = model_cls.from_dict(fixture("segment-pr-stats.json"))

    assert segment.resource_state == 3
    assert segment.starred is False
    assert segment.hazardous is False
    assert isinstance(segment.athlete_segment_stats, SummarySegmentEffort)
    stats = segment.athlete_segment_stats
    assert stats.pr_elapsed_time == 553
    assert stats.pr_date == datetime(1993, 4, 3, tzinfo=UTC)
    assert stats.effort_count == 2
    serialized = segment.to_dict()
    assert serialized["starred"] is False
    assert serialized["hazardous"] is False
    assert serialized["athlete_segment_stats"] == {
        "pr_elapsed_time": 553,
        "pr_date": "1993-04-03T00:00:00+00:00",
        "effort_count": 2,
    }


@pytest.mark.parametrize("model_cls", [SummarySegment, DetailedSegment])
def test_segment_stats_still_accept_documented_effort_shape(model_cls):
    segment = model_cls.from_dict(fixture("segment-effort-stats.json"))
    stats = segment.athlete_segment_stats

    assert isinstance(stats, SummarySegmentEffort)
    assert stats.id == 987654
    assert stats.activity_id == 123456
    assert stats.elapsed_time == 553
    assert stats.start_date == datetime(2026, 10, 5, 8, 30, tzinfo=UTC)
    assert stats.distance == 2684.82
    assert stats.is_kom is False
    assert stats.to_dict() == {
        **fixture("segment-effort-stats.json")["athlete_segment_stats"],
        "start_date": "2026-10-05T08:30:00+00:00",
        "start_date_local": "2026-10-05T08:30:00+00:00",
    }


@pytest.mark.parametrize("model_cls", [SummarySegment, DetailedSegment])
def test_segment_stats_accept_pr_and_effort_fields_together(model_cls):
    payload = fixture("segment-pr-stats.json")
    payload["athlete_segment_stats"].update(
        fixture("segment-effort-stats.json")["athlete_segment_stats"]
    )
    segment = model_cls.from_dict(payload)
    stats = segment.athlete_segment_stats

    assert stats.activity_id == 123456
    assert stats.pr_elapsed_time == 553
    assert stats.effort_count == 2
    assert isinstance(stats, SummarySegmentEffort)
    assert stats.to_dict() == {
        **payload["athlete_segment_stats"],
        "start_date": "2026-10-05T08:30:00+00:00",
        "start_date_local": "2026-10-05T08:30:00+00:00",
        "pr_date": "1993-04-03T00:00:00+00:00",
    }
    assert model_cls.from_dict(segment.to_dict()) == segment


@pytest.mark.parametrize("model_cls", [SummarySegment, DetailedSegment])
@pytest.mark.parametrize("values", ["omitted", "null", "zero"])
def test_segment_flags_handle_optional_false_and_zero_values(model_cls, values):
    fields = ("resource_state", "starred", "hazardous")
    if values == "omitted":
        payload = {"id": 1}
    elif values == "null":
        payload = dict.fromkeys(fields)
    else:
        payload = {"resource_state": 0, "starred": False, "hazardous": False}
    segment = model_cls.from_dict(payload)

    for name in fields:
        assert getattr(segment, name) == payload.get(name)
        if values == "zero":
            assert segment.to_dict()[name] == payload[name]
        else:
            assert name not in segment.to_dict()


@pytest.mark.parametrize("model_cls", [SummarySegment, DetailedSegment])
@pytest.mark.parametrize("payload", [{"id": 1}, {"athlete_segment_stats": None}])
def test_segment_stats_are_optional(model_cls, payload):
    segment = model_cls.from_dict(payload)

    assert segment.athlete_segment_stats is None
    assert "athlete_segment_stats" not in segment.to_dict()


@pytest.mark.parametrize("model_cls", [SummarySegment, DetailedSegment])
@pytest.mark.parametrize("values", ["omitted", "null", "zero"])
def test_segment_pr_stats_handle_optional_and_zero_values(model_cls, values):
    fields = ("pr_activity_id", "pr_elapsed_time", "pr_date", "effort_count")
    if values == "omitted":
        payload = {}
    elif values == "null":
        payload = dict.fromkeys(fields)
    else:
        payload = {"pr_activity_id": 0, "pr_elapsed_time": 0, "effort_count": 0}
    segment = model_cls.from_dict({"athlete_segment_stats": payload})
    stats = segment.athlete_segment_stats

    assert isinstance(stats, SummarySegmentEffort)
    for name in fields:
        assert getattr(stats, name) == payload.get(name)
    assert stats.to_dict() == (payload if values == "zero" else {})


@pytest.mark.parametrize("model_cls", [SummarySegment, DetailedSegment])
@pytest.mark.parametrize(
    ("pr_date", "expected"),
    [
        ("1993-04-03", datetime(1993, 4, 3, tzinfo=UTC)),
        ("1993-04-03T08:30:00Z", datetime(1993, 4, 3, 8, 30, tzinfo=UTC)),
        ("1993-04-03T08:30:00", datetime(1993, 4, 3, 8, 30, tzinfo=UTC)),
        ("1993-04-03T08:30:00+02:00", datetime(1993, 4, 3, 6, 30, tzinfo=UTC)),
    ],
)
def test_segment_pr_stats_dates_normalize_to_utc(model_cls, pr_date, expected):
    segment = model_cls.from_dict(
        {"athlete_segment_stats": {"pr_activity_id": 123456, "pr_date": pr_date}}
    )
    stats = segment.athlete_segment_stats

    assert isinstance(stats, SummarySegmentEffort)
    assert stats.pr_activity_id == 123456
    assert stats.pr_date == expected
    assert stats.pr_date.tzinfo is UTC
    assert stats.to_dict() == {
        "pr_activity_id": 123456,
        "pr_date": expected.isoformat(),
    }
    assert model_cls.from_dict(segment.to_dict()) == segment


@pytest_asyncio.fixture(params=[Strava, AsyncStrava], ids=["sync", "async"])
async def client(request):
    client = request.param(access_token="test_token")
    yield client
    result = client.close()
    if inspect.isawaitable(result):
        await result


@pytest.mark.asyncio
@pytest.mark.parametrize("representation", ["summary", "detail"])
@respx.mock
async def test_activity_endpoints_preserve_metrics(client, representation):
    payload = fixture("activity-metrics.json")
    if representation == "summary":
        respx.get(f"{BASE}/athlete/activities").mock(
            side_effect=[
                httpx.Response(200, json=[payload]),
                httpx.Response(200, json=[]),
            ]
        )
        result = client.activities.list().collect()
        activities = await result if inspect.isawaitable(result) else result
        activity = activities[0]
    else:
        respx.get(f"{BASE}/activities/154504250376823").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = client.activities.retrieve(154504250376823)
        activity = await result if inspect.isawaitable(result) else result

    for name in ACTIVITY_FIELDS:
        assert getattr(activity, name) == payload[name]


@pytest.mark.asyncio
@pytest.mark.parametrize("representation", ["summary", "detail"])
@respx.mock
async def test_segment_endpoints_preserve_flags_and_pr_stats(client, representation):
    payload = fixture("segment-pr-stats.json")
    if representation == "summary":
        respx.get(f"{BASE}/segments/starred").mock(
            side_effect=[
                httpx.Response(200, json=[payload]),
                httpx.Response(200, json=[]),
            ]
        )
        result = client.segments.list_starred().collect()
        segments = await result if inspect.isawaitable(result) else result
        segment = segments[0]
    else:
        respx.get(f"{BASE}/segments/229781").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = client.segments.retrieve(229781)
        segment = await result if inspect.isawaitable(result) else result

    assert segment.starred is False
    assert segment.athlete_segment_stats.pr_elapsed_time == 553
    assert segment.athlete_segment_stats.effort_count == 2
