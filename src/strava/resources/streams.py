from __future__ import annotations

from typing import Literal

from strava.models.streams import StreamSet
from strava.resources._base import AsyncAPIResource, SyncAPIResource


def _stream_params(
    keys: list[str] | None, key_by_type: Literal[True]
) -> dict[str, str]:
    if key_by_type is not True:
        raise ValueError("key_by_type must be true for stream requests")
    if keys is None:
        return {}
    return {"keys": ",".join(keys), "key_by_type": "true"}


class Streams(SyncAPIResource):
    def _get_streams(
        self,
        path: str,
        *,
        keys: list[str] | None = None,
        key_by_type: Literal[True] = True,
    ) -> StreamSet:
        params = _stream_params(keys, key_by_type)
        response = self._client._request("GET", path, params=params)
        return StreamSet.from_response(response.json())

    def get_activity_streams(
        self,
        activity_id: int,
        *,
        keys: list[str],
        key_by_type: Literal[True] = True,
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
        key_by_type: Literal[True] = True,
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
        key_by_type: Literal[True] = True,
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
        key_by_type: Literal[True] = True,
    ) -> StreamSet:
        params = _stream_params(keys, key_by_type)
        response = await self._client._request("GET", path, params=params)
        return StreamSet.from_response(response.json())

    async def get_activity_streams(
        self,
        activity_id: int,
        *,
        keys: list[str],
        key_by_type: Literal[True] = True,
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
        key_by_type: Literal[True] = True,
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
        key_by_type: Literal[True] = True,
    ) -> StreamSet:
        return await self._get_streams(
            f"/segments/{segment_id}/streams",
            keys=keys,
            key_by_type=key_by_type,
        )
