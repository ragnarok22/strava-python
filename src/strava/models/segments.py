from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from strava.models._base import StravaModel
from strava.models.athletes import MetaAthlete
from strava.models.common import PolylineMap


@dataclass(slots=True, kw_only=True)
class SummaryPRSegmentEffort(StravaModel):
    pr_activity_id: int | None = None
    pr_elapsed_time: int | None = None
    pr_date: datetime | None = None
    effort_count: int | None = None


@dataclass(slots=True, kw_only=True)
class SummarySegmentEffort(StravaModel):
    id: int | None = None
    activity_id: int | None = None
    elapsed_time: int | None = None
    start_date: datetime | None = None
    start_date_local: datetime | None = None
    distance: float | None = None
    is_kom: bool | None = None


@dataclass(slots=True, kw_only=True)
class SummarySegment(StravaModel):
    id: int | None = None
    name: str | None = None
    activity_type: str | None = None
    distance: float | None = None
    average_grade: float | None = None
    maximum_grade: float | None = None
    elevation_high: float | None = None
    elevation_low: float | None = None
    start_latlng: list[float] | None = None
    end_latlng: list[float] | None = None
    climb_category: int | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    private: bool | None = None
    athlete_pr_effort: SummaryPRSegmentEffort | None = None
    athlete_segment_stats: SummarySegmentEffort | None = None


@dataclass(slots=True, kw_only=True)
class DetailedSegment(StravaModel):
    id: int | None = None
    name: str | None = None
    activity_type: str | None = None
    distance: float | None = None
    average_grade: float | None = None
    maximum_grade: float | None = None
    elevation_high: float | None = None
    elevation_low: float | None = None
    start_latlng: list[float] | None = None
    end_latlng: list[float] | None = None
    climb_category: int | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    private: bool | None = None
    athlete_pr_effort: SummaryPRSegmentEffort | None = None
    athlete_segment_stats: SummarySegmentEffort | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    total_elevation_gain: float | None = None
    map: PolylineMap | None = None
    effort_count: int | None = None
    athlete_count: int | None = None
    hazardous: bool | None = None
    star_count: int | None = None


@dataclass(slots=True, kw_only=True)
class DetailedSegmentEffort(StravaModel):
    id: int | None = None
    activity_id: int | None = None
    elapsed_time: int | None = None
    start_date: datetime | None = None
    start_date_local: datetime | None = None
    distance: float | None = None
    is_kom: bool | None = None
    name: str | None = None
    activity: dict | None = None
    athlete: MetaAthlete | None = None
    moving_time: int | None = None
    start_index: int | None = None
    end_index: int | None = None
    average_cadence: float | None = None
    average_watts: float | None = None
    device_watts: bool | None = None
    average_heartrate: float | None = None
    max_heartrate: float | None = None
    segment: SummarySegment | None = None
    kom_rank: int | None = None
    pr_rank: int | None = None
    hidden: bool | None = None


@dataclass(slots=True, kw_only=True)
class ExplorerSegment(StravaModel):
    id: int | None = None
    name: str | None = None
    climb_category: int | None = None
    climb_category_desc: str | None = None
    avg_grade: float | None = None
    start_latlng: list[float] | None = None
    end_latlng: list[float] | None = None
    elev_difference: float | None = None
    distance: float | None = None
    points: str | None = None


@dataclass(slots=True, kw_only=True)
class ExplorerResponse(StravaModel):
    segments: list[ExplorerSegment] = field(default_factory=list)
