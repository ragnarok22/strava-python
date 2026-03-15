from __future__ import annotations

from typing import TypeAlias

LatLng: TypeAlias = list[float]
HeadersLike: TypeAlias = dict[str, str]


class _NotGiven:
    """Sentinel for distinguishing 'not provided' from None."""

    _instance: _NotGiven | None = None

    def __new__(cls) -> _NotGiven:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "NOT_GIVEN"


NOT_GIVEN = _NotGiven()
NotGiven: TypeAlias = _NotGiven
