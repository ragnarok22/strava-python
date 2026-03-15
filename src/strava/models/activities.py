from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from strava.models._base import StravaModel
from strava.models._enums import ActivityType, SportType
from strava.models.athletes import MetaAthlete, SummaryAthlete
from strava.models.common import PhotosSummary, PolylineMap, Split, TimedZoneRange
from strava.models.gear import SummaryGear
from strava.models.segments import DetailedSegmentEffort, SummarySegment


@dataclass(slots=True, kw_only=True)
class MetaActivity(StravaModel):
    id: int | None = None


@dataclass(slots=True, kw_only=True)
class SummaryActivity(StravaModel):
    id: int | None = None
    external_id: str | None = None
    upload_id: int | None = None
    athlete: MetaAthlete | None = None
    name: str | None = None
    distance: float | None = None
    moving_time: int | None = None
    elapsed_time: int | None = None
    total_elevation_gain: float | None = None
    elev_high: float | None = None
    elev_low: float | None = None
    type: ActivityType | None = None
    sport_type: SportType | None = None
    start_date: datetime | None = None
    start_date_local: datetime | None = None
    timezone: str | None = None
    start_latlng: list[float] | None = None
    end_latlng: list[float] | None = None
    achievement_count: int | None = None
    kudos_count: int | None = None
    comment_count: int | None = None
    athlete_count: int | None = None
    photo_count: int | None = None
    total_photo_count: int | None = None
    map: PolylineMap | None = None
    trainer: bool | None = None
    commute: bool | None = None
    manual: bool | None = None
    private: bool | None = None
    flagged: bool | None = None
    workout_type: int | None = None
    upload_id_str: str | None = None
    average_speed: float | None = None
    max_speed: float | None = None
    has_kudoed: bool | None = None
    hide_from_home: bool | None = None
    gear_id: str | None = None
    kilojoules: float | None = None
    average_watts: float | None = None
    device_watts: bool | None = None
    max_watts: int | None = None
    weighted_average_watts: int | None = None


@dataclass(slots=True, kw_only=True)
class DetailedActivity(StravaModel):
    id: int | None = None
    external_id: str | None = None
    upload_id: int | None = None
    athlete: MetaAthlete | None = None
    name: str | None = None
    distance: float | None = None
    moving_time: int | None = None
    elapsed_time: int | None = None
    total_elevation_gain: float | None = None
    elev_high: float | None = None
    elev_low: float | None = None
    type: ActivityType | None = None
    sport_type: SportType | None = None
    start_date: datetime | None = None
    start_date_local: datetime | None = None
    timezone: str | None = None
    start_latlng: list[float] | None = None
    end_latlng: list[float] | None = None
    achievement_count: int | None = None
    kudos_count: int | None = None
    comment_count: int | None = None
    athlete_count: int | None = None
    photo_count: int | None = None
    total_photo_count: int | None = None
    map: PolylineMap | None = None
    trainer: bool | None = None
    commute: bool | None = None
    manual: bool | None = None
    private: bool | None = None
    flagged: bool | None = None
    workout_type: int | None = None
    upload_id_str: str | None = None
    average_speed: float | None = None
    max_speed: float | None = None
    has_kudoed: bool | None = None
    hide_from_home: bool | None = None
    gear_id: str | None = None
    kilojoules: float | None = None
    average_watts: float | None = None
    device_watts: bool | None = None
    max_watts: int | None = None
    weighted_average_watts: int | None = None
    description: str | None = None
    photos: PhotosSummary | None = None
    gear: SummaryGear | None = None
    calories: float | None = None
    segment_efforts: list[DetailedSegmentEffort] = field(default_factory=list)
    device_name: str | None = None
    embed_token: str | None = None
    splits_metric: list[Split] = field(default_factory=list)
    splits_standard: list[Split] = field(default_factory=list)
    laps: list[Lap] = field(default_factory=list)
    best_efforts: list[DetailedSegmentEffort] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class UpdatableActivity(StravaModel):
    commute: bool | None = None
    trainer: bool | None = None
    hide_from_home: bool | None = None
    description: str | None = None
    name: str | None = None
    type: ActivityType | None = None
    sport_type: SportType | None = None
    gear_id: str | None = None


@dataclass(slots=True, kw_only=True)
class Lap(StravaModel):
    id: int | None = None
    activity: MetaActivity | None = None
    athlete: MetaAthlete | None = None
    average_cadence: float | None = None
    average_speed: float | None = None
    distance: float | None = None
    elapsed_time: int | None = None
    start_index: int | None = None
    end_index: int | None = None
    lap_index: int | None = None
    max_speed: float | None = None
    moving_time: int | None = None
    name: str | None = None
    pace_zone: int | None = None
    split: int | None = None
    start_date: datetime | None = None
    start_date_local: datetime | None = None
    total_elevation_gain: float | None = None


@dataclass(slots=True, kw_only=True)
class Comment(StravaModel):
    id: int | None = None
    activity_id: int | None = None
    text: str | None = None
    athlete: SummaryAthlete | None = None
    created_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class ActivityZone(StravaModel):
    score: int | None = None
    distribution_buckets: list[TimedZoneRange] = field(default_factory=list)
    type: str | None = None
    sensor_based: bool | None = None
    points: int | None = None
    custom_zones: bool | None = None
    max: int | None = None


@dataclass(slots=True, kw_only=True)
class ClubActivity(StravaModel):
    athlete: MetaAthlete | None = None
    name: str | None = None
    distance: float | None = None
    moving_time: int | None = None
    elapsed_time: int | None = None
    total_elevation_gain: float | None = None
    type: ActivityType | None = None
    sport_type: SportType | None = None
    workout_type: int | None = None
