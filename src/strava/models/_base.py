from __future__ import annotations

import dataclasses
import types
import typing
from datetime import datetime
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Protocol,
    Self,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from strava._serialization import parse_datetime


class _Dataclass(Protocol):
    __dataclass_fields__: ClassVar[dict[str, dataclasses.Field[Any]]]


class _FromDict(Protocol):
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self: ...


def _is_dataclass_type(tp: object) -> bool:
    return isinstance(tp, type) and dataclasses.is_dataclass(tp)


def _unwrap_optional(tp: Any) -> tuple[Any, bool]:
    """Unwrap Optional[X] / X | None to (X, True). Returns (tp, False) if not optional."""
    if get_origin(tp) in (types.UnionType, typing.Union):
        args = get_args(tp)
        if type(None) in args:
            non_none = [a for a in args if a is not type(None)]
            if len(non_none) == 1:
                return non_none[0], True
    return tp, False


def _unwrap_list(tp: Any) -> Any | None:
    """If tp is list[X], return X. Otherwise None."""
    origin = get_origin(tp)
    if origin is list:
        args = get_args(tp)
        return args[0] if args else None
    return None


def _coerce_value(value: Any, target_type: Any) -> Any:
    if value is None:
        return None

    inner, is_optional = _unwrap_optional(target_type)
    if is_optional:
        target_type = inner

    # Enum | str (optionally | None) keeps forward-compatible API strings,
    # but known values must still become enum members before the str fallback.
    if get_origin(target_type) in (types.UnionType, typing.Union):
        members = [tp for tp in get_args(target_type) if tp is not type(None)]
        enum_types = [
            tp for tp in members if isinstance(tp, type) and issubclass(tp, Enum)
        ]
        if len(members) == 2 and str in members and len(enum_types) == 1:
            return _coerce_value(value, enum_types[0])

    # list[X]
    item_type = _unwrap_list(target_type)
    if item_type is not None:
        if isinstance(value, list):
            return [_coerce_value(item, item_type) for item in value]
        return value

    # datetime
    if target_type is datetime:
        if isinstance(value, str):
            return parse_datetime(value)
        return value

    # Enum subclass
    if isinstance(target_type, type) and issubclass(target_type, Enum):
        if isinstance(value, str):
            try:
                return target_type(value)
            except ValueError:
                return value
        return value

    # Nested dataclass
    if _is_dataclass_type(target_type):
        if isinstance(value, dict):
            # Nested dataclasses in model annotations expose the parsing protocol.
            return cast(type[_FromDict], target_type).from_dict(value)
        return value

    return value


class StravaModel:
    _field_aliases: ClassVar[dict[str, str]] = {}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        if not data:
            return cls()

        # Build reverse alias map: api_name -> field_name
        reverse_aliases = {v: k for k, v in cls._field_aliases.items()}

        hints = get_type_hints(cls)
        # Concrete SDK models are dataclasses; keep the base class layout intact.
        field_names = {f.name for f in dataclasses.fields(cast(type[_Dataclass], cls))}
        kwargs: dict[str, Any] = {}

        for key, value in data.items():
            field_name = reverse_aliases.get(key, key)
            if field_name not in field_names:
                continue
            target_type = hints.get(field_name)
            if target_type is not None:
                value = _coerce_value(value, target_type)
            kwargs[field_name] = value

        return cls(**kwargs)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        aliases = self._field_aliases
        for f in dataclasses.fields(cast(_Dataclass, self)):
            value = getattr(self, f.name)
            if value is None:
                continue
            key = aliases.get(f.name, f.name)
            if isinstance(value, StravaModel):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [
                    item.to_dict() if isinstance(item, StravaModel) else item
                    for item in value
                ]
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, Enum):
                result[key] = value.value
            else:
                result[key] = value
        return result
