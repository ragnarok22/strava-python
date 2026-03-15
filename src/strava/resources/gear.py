from __future__ import annotations

from strava.models.gear import DetailedGear
from strava.resources._base import AsyncAPIResource, SyncAPIResource


class Gear(SyncAPIResource):
    def retrieve(self, gear_id: str) -> DetailedGear:
        return self._client._request_model(
            "GET", f"/gear/{gear_id}", model_cls=DetailedGear
        )


class AsyncGear(AsyncAPIResource):
    async def retrieve(self, gear_id: str) -> DetailedGear:
        return await self._client._request_model(
            "GET", f"/gear/{gear_id}", model_cls=DetailedGear
        )
