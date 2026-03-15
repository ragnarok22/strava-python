from __future__ import annotations

from typing import TypeAlias


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


def resolve_per_page(per_page: int | _NotGiven, default: int = 30) -> int:
    """Extract per_page value, falling back to default if NOT_GIVEN."""
    return per_page if not isinstance(per_page, _NotGiven) else default
