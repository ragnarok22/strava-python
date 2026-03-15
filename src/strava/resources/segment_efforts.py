from __future__ import annotations

from strava._serialization import strip_not_given
from strava._types import NOT_GIVEN, NotGiven
from strava.models.segments import DetailedSegmentEffort
from strava.resources._base import AsyncAPIResource, SyncAPIResource


class SegmentEfforts(SyncAPIResource):
    def retrieve(self, effort_id: int) -> DetailedSegmentEffort:
        return self._client._request_model(
            "GET",
            f"/segment_efforts/{effort_id}",
            model_cls=DetailedSegmentEffort,
        )

    def list(
        self,
        *,
        segment_id: int,
        start_date_local: str | NotGiven = NOT_GIVEN,
        end_date_local: str | NotGiven = NOT_GIVEN,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> list[DetailedSegmentEffort]:
        params = strip_not_given(
            {
                "segment_id": segment_id,
                "start_date_local": start_date_local,
                "end_date_local": end_date_local,
                "per_page": per_page,
            }
        )
        return self._client._request_model_list(
            "GET",
            "/segment_efforts",
            params=params,
            model_cls=DetailedSegmentEffort,
        )


class AsyncSegmentEfforts(AsyncAPIResource):
    async def retrieve(self, effort_id: int) -> DetailedSegmentEffort:
        return await self._client._request_model(
            "GET",
            f"/segment_efforts/{effort_id}",
            model_cls=DetailedSegmentEffort,
        )

    async def list(
        self,
        *,
        segment_id: int,
        start_date_local: str | NotGiven = NOT_GIVEN,
        end_date_local: str | NotGiven = NOT_GIVEN,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> list[DetailedSegmentEffort]:
        params = strip_not_given(
            {
                "segment_id": segment_id,
                "start_date_local": start_date_local,
                "end_date_local": end_date_local,
                "per_page": per_page,
            }
        )
        return await self._client._request_model_list(
            "GET",
            "/segment_efforts",
            params=params,
            model_cls=DetailedSegmentEffort,
        )
