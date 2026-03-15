from __future__ import annotations

from dataclasses import dataclass

from strava.models._base import StravaModel


@dataclass(slots=True, kw_only=True)
class Upload(StravaModel):
    id: int | None = None
    id_str: str | None = None
    external_id: str | None = None
    error: str | None = None
    status: str | None = None
    activity_id: int | None = None
