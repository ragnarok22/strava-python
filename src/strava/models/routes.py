from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from strava.models._base import StravaModel
from strava.models.athletes import SummaryAthlete
from strava.models.common import PolylineMap, Waypoint
from strava.models.segments import SummarySegment


@dataclass(slots=True, kw_only=True)
class Route(StravaModel):
    id: int | None = None
    id_str: str | None = None
    athlete: SummaryAthlete | None = None
    description: str | None = None
    distance: float | None = None
    elevation_gain: float | None = None
    map: PolylineMap | None = None
    name: str | None = None
    private: bool | None = None
    starred: bool | None = None
    timestamp: int | None = None
    type: int | None = None
    sub_type: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    estimated_moving_time: int | None = None
    segments: list[SummarySegment] = field(default_factory=list)
    waypoints: list[Waypoint] = field(default_factory=list)
