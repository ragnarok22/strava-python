from __future__ import annotations

from strava.models.streams import StreamSet
from strava.resources._base import AsyncAPIResource, SyncAPIResource


class Streams(SyncAPIResource):
    def _get_streams(
        self,
        path: str,
        *,
        keys: list[str] | None = None,
        key_by_type: bool = True,
    ) -> StreamSet:
        params: dict = {"key_by_type": str(key_by_type).lower()}
        if keys:
            params["keys"] = ",".join(keys)
        raw = self._client._request_json("GET", path, params=params)
        return StreamSet.from_stream_list(raw)

    def get_activity_streams(
        self,
        activity_id: int,
        *,
        keys: list[str],
        key_by_type: bool = True,
    ) -> StreamSet:
        return self._get_streams(
            f"/activities/{activity_id}/streams",
            keys=keys,
            key_by_type=key_by_type,
        )

    def get_route_streams(self, route_id: int) -> StreamSet:
        return self._get_streams(f"/routes/{route_id}/streams")

    def get_segment_effort_streams(
        self,
        effort_id: int,
        *,
        keys: list[str],
        key_by_type: bool = True,
    ) -> StreamSet:
        return self._get_streams(
            f"/segment_efforts/{effort_id}/streams",
            keys=keys,
            key_by_type=key_by_type,
        )

    def get_segment_streams(
        self,
        segment_id: int,
        *,
        keys: list[str],
        key_by_type: bool = True,
    ) -> StreamSet:
        return self._get_streams(
            f"/segments/{segment_id}/streams",
            keys=keys,
            key_by_type=key_by_type,
        )


class AsyncStreams(AsyncAPIResource):
    async def _get_streams(
        self,
        path: str,
        *,
        keys: list[str] | None = None,
        key_by_type: bool = True,
    ) -> StreamSet:
        params: dict = {"key_by_type": str(key_by_type).lower()}
        if keys:
            params["keys"] = ",".join(keys)
        raw = await self._client._request_json("GET", path, params=params)
        return StreamSet.from_stream_list(raw)

    async def get_activity_streams(
        self,
        activity_id: int,
        *,
        keys: list[str],
        key_by_type: bool = True,
    ) -> StreamSet:
        return await self._get_streams(
            f"/activities/{activity_id}/streams",
            keys=keys,
            key_by_type=key_by_type,
        )

    async def get_route_streams(self, route_id: int) -> StreamSet:
        return await self._get_streams(f"/routes/{route_id}/streams")

    async def get_segment_effort_streams(
        self,
        effort_id: int,
        *,
        keys: list[str],
        key_by_type: bool = True,
    ) -> StreamSet:
        return await self._get_streams(
            f"/segment_efforts/{effort_id}/streams",
            keys=keys,
            key_by_type=key_by_type,
        )

    async def get_segment_streams(
        self,
        segment_id: int,
        *,
        keys: list[str],
        key_by_type: bool = True,
    ) -> StreamSet:
        return await self._get_streams(
            f"/segments/{segment_id}/streams",
            keys=keys,
            key_by_type=key_by_type,
        )
