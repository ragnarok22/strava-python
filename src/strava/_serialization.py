from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from strava._types import _NotGiven


def parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    value = value.rstrip("Z")
    if "+" not in value and value.count("-") <= 2:
        value += "+00:00"
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


def strip_not_given(data: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in data.items() if not isinstance(v, _NotGiven)}


def to_form_data(data: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for k, v in data.items():
        if isinstance(v, _NotGiven):
            continue
        if isinstance(v, bool):
            result[k] = str(int(v))
        elif isinstance(v, (int, float)):
            result[k] = str(v)
        elif v is None:
            continue
        else:
            result[k] = str(v)
    return result
