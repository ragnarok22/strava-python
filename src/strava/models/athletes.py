from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from strava.models._base import StravaModel
from strava.models.clubs import SummaryClub
from strava.models.gear import SummaryGear


@dataclass(slots=True, kw_only=True)
class MetaAthlete(StravaModel):
    id: int | None = None


@dataclass(slots=True, kw_only=True)
class SummaryAthlete(StravaModel):
    id: int | None = None
    resource_state: int | None = None
    firstname: str | None = None
    lastname: str | None = None
    profile_medium: str | None = None
    profile: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    sex: str | None = None
    premium: bool | None = None
    summit: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class DetailedAthlete(StravaModel):
    id: int | None = None
    resource_state: int | None = None
    firstname: str | None = None
    lastname: str | None = None
    profile_medium: str | None = None
    profile: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    sex: str | None = None
    premium: bool | None = None
    summit: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    follower_count: int | None = None
    friend_count: int | None = None
    measurement_preference: str | None = None
    ftp: int | None = None
    weight: float | None = None
    clubs: list[SummaryClub] = field(default_factory=list)
    bikes: list[SummaryGear] = field(default_factory=list)
    shoes: list[SummaryGear] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class ClubAthlete(StravaModel):
    resource_state: int | None = None
    firstname: str | None = None
    lastname: str | None = None
    member: str | None = None
    admin: bool | None = None
    owner: bool | None = None
