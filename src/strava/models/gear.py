from __future__ import annotations

from dataclasses import dataclass

from strava.models._base import StravaModel


@dataclass(slots=True, kw_only=True)
class SummaryGear(StravaModel):
    id: str | None = None
    resource_state: int | None = None
    primary: bool | None = None
    name: str | None = None
    distance: float | None = None


@dataclass(slots=True, kw_only=True)
class DetailedGear(StravaModel):
    id: str | None = None
    resource_state: int | None = None
    primary: bool | None = None
    name: str | None = None
    distance: float | None = None
    brand_name: str | None = None
    model_name: str | None = None
    frame_type: int | None = None
    description: str | None = None
