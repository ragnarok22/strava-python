from __future__ import annotations

from strava._paginator import AsyncPaginator, SyncPaginator
from strava._serialization import strip_not_given
from strava._types import NOT_GIVEN, NotGiven, resolve_per_page
from strava.models.segments import (
    DetailedSegment,
    ExplorerResponse,
    SummarySegment,
)
from strava.resources._base import AsyncAPIResource, SyncAPIResource


class Segments(SyncAPIResource):
    def retrieve(self, segment_id: int) -> DetailedSegment:
        return self._client._request_model(
            "GET", f"/segments/{segment_id}", model_cls=DetailedSegment
        )

    def explore(
        self,
        *,
        bounds: list[float],
        activity_type: str | NotGiven = NOT_GIVEN,
        min_cat: int | NotGiven = NOT_GIVEN,
        max_cat: int | NotGiven = NOT_GIVEN,
    ) -> ExplorerResponse:
        """Restricted to approved Extended Access apps effective September 1, 2026."""

        params = strip_not_given(
            {
                "bounds": ",".join(str(b) for b in bounds),
                "activity_type": activity_type,
                "min_cat": min_cat,
                "max_cat": max_cat,
            }
        )
        return self._client._request_model(
            "GET", "/segments/explore", params=params, model_cls=ExplorerResponse
        )

    def list_starred(
        self,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> SyncPaginator[SummarySegment]:
        return SyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET", "/segments/starred", params=kw.get("params", {})
            ),
            model_cls=SummarySegment,
            params={},
            per_page=resolve_per_page(per_page),
        )

    def star(self, segment_id: int, *, starred: bool) -> DetailedSegment:
        return self._client._request_model(
            "PUT",
            f"/segments/{segment_id}/starred",
            data={"starred": str(starred).lower()},
            model_cls=DetailedSegment,
        )


class AsyncSegments(AsyncAPIResource):
    async def retrieve(self, segment_id: int) -> DetailedSegment:
        return await self._client._request_model(
            "GET", f"/segments/{segment_id}", model_cls=DetailedSegment
        )

    async def explore(
        self,
        *,
        bounds: list[float],
        activity_type: str | NotGiven = NOT_GIVEN,
        min_cat: int | NotGiven = NOT_GIVEN,
        max_cat: int | NotGiven = NOT_GIVEN,
    ) -> ExplorerResponse:
        """Restricted to approved Extended Access apps effective September 1, 2026."""

        params = strip_not_given(
            {
                "bounds": ",".join(str(b) for b in bounds),
                "activity_type": activity_type,
                "min_cat": min_cat,
                "max_cat": max_cat,
            }
        )
        return await self._client._request_model(
            "GET", "/segments/explore", params=params, model_cls=ExplorerResponse
        )

    def list_starred(
        self,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[SummarySegment]:
        return AsyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET", "/segments/starred", params=kw.get("params", {})
            ),
            model_cls=SummarySegment,
            params={},
            per_page=resolve_per_page(per_page),
        )

    async def star(self, segment_id: int, *, starred: bool) -> DetailedSegment:
        return await self._client._request_model(
            "PUT",
            f"/segments/{segment_id}/starred",
            data={"starred": str(starred).lower()},
            model_cls=DetailedSegment,
        )
