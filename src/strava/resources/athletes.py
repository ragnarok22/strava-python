from __future__ import annotations

from strava.models.athletes import DetailedAthlete
from strava.models.stats import ActivityStats, Zones
from strava.resources._base import AsyncAPIResource, SyncAPIResource


class Athletes(SyncAPIResource):
    def retrieve_authenticated(self) -> DetailedAthlete:
        return self._client._request_model("GET", "/athlete", model_cls=DetailedAthlete)

    def update_authenticated(self, *, weight: float) -> DetailedAthlete:
        return self._client._request_model(
            "PUT",
            "/athlete",
            data={"weight": str(weight)},
            model_cls=DetailedAthlete,
        )

    def retrieve_zones(self) -> Zones:
        return self._client._request_model("GET", "/athlete/zones", model_cls=Zones)

    def retrieve_stats(self, athlete_id: int) -> ActivityStats:
        return self._client._request_model(
            "GET", f"/athletes/{athlete_id}/stats", model_cls=ActivityStats
        )


class AsyncAthletes(AsyncAPIResource):
    async def retrieve_authenticated(self) -> DetailedAthlete:
        return await self._client._request_model(
            "GET", "/athlete", model_cls=DetailedAthlete
        )

    async def update_authenticated(self, *, weight: float) -> DetailedAthlete:
        return await self._client._request_model(
            "PUT",
            "/athlete",
            data={"weight": str(weight)},
            model_cls=DetailedAthlete,
        )

    async def retrieve_zones(self) -> Zones:
        return await self._client._request_model(
            "GET", "/athlete/zones", model_cls=Zones
        )

    async def retrieve_stats(self, athlete_id: int) -> ActivityStats:
        return await self._client._request_model(
            "GET", f"/athletes/{athlete_id}/stats", model_cls=ActivityStats
        )
