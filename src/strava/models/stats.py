from __future__ import annotations

from dataclasses import dataclass, field

from strava.models._base import StravaModel
from strava.models.common import ZoneRange


@dataclass(slots=True, kw_only=True)
class ActivityTotal(StravaModel):
    count: int | None = None
    distance: float | None = None
    moving_time: int | None = None
    elapsed_time: int | None = None
    elevation_gain: float | None = None
    achievement_count: int | None = None


@dataclass(slots=True, kw_only=True)
class ActivityStats(StravaModel):
    biggest_ride_distance: float | None = None
    biggest_climb_elevation_gain: float | None = None
    recent_ride_totals: ActivityTotal | None = None
    recent_run_totals: ActivityTotal | None = None
    recent_swim_totals: ActivityTotal | None = None
    ytd_ride_totals: ActivityTotal | None = None
    ytd_run_totals: ActivityTotal | None = None
    ytd_swim_totals: ActivityTotal | None = None
    all_ride_totals: ActivityTotal | None = None
    all_run_totals: ActivityTotal | None = None
    all_swim_totals: ActivityTotal | None = None


@dataclass(slots=True, kw_only=True)
class HeartRateZoneRanges(StravaModel):
    custom_zones: bool | None = None
    zones: list[ZoneRange] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class PowerZoneRanges(StravaModel):
    zones: list[ZoneRange] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class Zones(StravaModel):
    heart_rate: HeartRateZoneRanges | None = None
    power: PowerZoneRanges | None = None
