from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from strava._types import NOT_GIVEN, NotGiven
from strava.models._enums import ActivityTag

_ACTIVITY_TAG_NAMES = frozenset(ActivityTag)


def activity_tag_data(
    tags: Mapping[str, bool] | Mapping[ActivityTag, bool] | NotGiven,
    *,
    commute: bool | NotGiven,
    form: bool,
) -> dict[str, Any]:
    """Validate partial tag changes and copy them into the endpoint's wire format."""
    if isinstance(tags, NotGiven):
        return {}
    if commute is not NOT_GIVEN:
        raise ValueError("tags cannot be combined with the legacy commute parameter")
    if not isinstance(tags, Mapping):
        raise TypeError("tags must be a mapping of tag names to booleans")

    changes: dict[str, bool] = {}
    for tag, value in tags.items():
        if tag not in _ACTIVITY_TAG_NAMES:
            raise ValueError(f"Unsupported activity tag: {tag!r}")
        if not isinstance(value, bool):
            raise TypeError(f"Activity tag {tag!r} must have a boolean value")
        changes[str(tag)] = value

    if form:
        return {
            f"tags[{tag}]": "true" if value else "false"
            for tag, value in changes.items()
        }
    return {"tags": changes}
