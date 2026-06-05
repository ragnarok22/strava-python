from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from strava._types import _NotGiven


def parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    if value.endswith("Z"):
        value = f"{value[:-1]}+00:00"

    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


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
