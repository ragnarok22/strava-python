from __future__ import annotations

from dataclasses import dataclass, field

from strava.models._base import StravaModel


@dataclass(slots=True, kw_only=True)
class PolylineMap(StravaModel):
    id: str | None = None
    polyline: str | None = None
    summary_polyline: str | None = None


@dataclass(slots=True, kw_only=True)
class PhotosSummary(StravaModel):
    count: int | None = None
    primary: dict | None = None


@dataclass(slots=True, kw_only=True)
class Split(StravaModel):
    average_speed: float | None = None
    distance: float | None = None
    elapsed_time: int | None = None
    elevation_difference: float | None = None
    pace_zone: int | None = None
    moving_time: int | None = None
    split: int | None = None


@dataclass(slots=True, kw_only=True)
class Waypoint(StravaModel):
    latlng: list[float] | None = None
    target_latlng: list[float] | None = None
    categories: list[str] = field(default_factory=list)
    title: str | None = None
    description: str | None = None
    distance_into_route: float | None = None


@dataclass(slots=True, kw_only=True)
class ZoneRange(StravaModel):
    min: int | None = None
    max: int | None = None


@dataclass(slots=True, kw_only=True)
class TimedZoneRange(StravaModel):
    min: int | None = None
    max: int | None = None
    time: int | None = None


@dataclass(slots=True, kw_only=True)
class Error(StravaModel):
    code: str | None = None
    field: str | None = None
    resource: str | None = None


@dataclass(slots=True, kw_only=True)
class Fault(StravaModel):
    errors: list[Error] = field(default_factory=list)
    message: str | None = None
