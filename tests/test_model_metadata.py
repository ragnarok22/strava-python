from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import ClassVar
from unittest.mock import patch

from strava import SummaryActivity
from strava.models import _base


def test_repeated_parsing_reuses_resolved_type_metadata():
    @dataclass(slots=True, kw_only=True)
    class Activity(SummaryActivity):
        recorded_at: datetime | None = None

    payload = {"id": 123, "recorded_at": "2026-11-17T08:00:00Z"}
    with patch.object(_base, "get_type_hints", wraps=_base.get_type_hints) as resolve:
        first = Activity.from_dict(payload)
        second = Activity.from_dict(payload)

    assert resolve.call_count == 1
    assert first == second
    assert first is not second
    assert first.recorded_at == datetime(2026, 11, 17, 8, tzinfo=UTC)


def test_subclasses_resolve_their_own_fields_types_and_aliases():
    SummaryActivity.from_dict({"id": 1})

    @dataclass(slots=True, kw_only=True)
    class Activity(SummaryActivity):
        recorded_at: datetime | None = None
        _field_aliases: ClassVar[dict[str, str]] = {"recorded_at": "recordedAt"}

    activity = Activity.from_dict(
        {"id": 2, "recordedAt": "2026-11-17T09:00:00+01:00", "unknown": True}
    )
    assert isinstance(activity, Activity)
    assert activity.id == 2
    assert activity.recorded_at == datetime(2026, 11, 17, 8, tzinfo=UTC)
    assert activity.to_dict()["recordedAt"] == "2026-11-17T08:00:00+00:00"

    # Cached annotations must not freeze a consumer's mutable alias configuration.
    Activity._field_aliases["recorded_at"] = "timestamp"
    reparsed = Activity.from_dict({"timestamp": "2026-11-18T08:00:00Z"})
    assert reparsed.recorded_at == datetime(2026, 11, 18, 8, tzinfo=UTC)
