from __future__ import annotations

from dataclasses import dataclass, field

from strava.models._base import StravaModel
from strava.models._enums import ActivityType


@dataclass(slots=True, kw_only=True)
class MetaClub(StravaModel):
    id: int | None = None
    resource_state: int | None = None
    name: str | None = None


@dataclass(slots=True, kw_only=True)
class SummaryClub(StravaModel):
    id: int | None = None
    resource_state: int | None = None
    name: str | None = None
    profile_medium: str | None = None
    cover_photo: str | None = None
    cover_photo_small: str | None = None
    sport_type: str | None = None
    activity_types: list[ActivityType] = field(default_factory=list)
    city: str | None = None
    state: str | None = None
    country: str | None = None
    private: bool | None = None
    member_count: int | None = None
    featured: bool | None = None
    verified: bool | None = None
    url: str | None = None


@dataclass(slots=True, kw_only=True)
class DetailedClub(StravaModel):
    id: int | None = None
    resource_state: int | None = None
    name: str | None = None
    profile_medium: str | None = None
    cover_photo: str | None = None
    cover_photo_small: str | None = None
    sport_type: str | None = None
    activity_types: list[ActivityType] = field(default_factory=list)
    city: str | None = None
    state: str | None = None
    country: str | None = None
    private: bool | None = None
    member_count: int | None = None
    featured: bool | None = None
    verified: bool | None = None
    url: str | None = None
    membership: str | None = None
    admin: bool | None = None
    owner: bool | None = None
    following_count: int | None = None
