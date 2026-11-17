from __future__ import annotations

from strava._paginator import AsyncPaginator, SyncPaginator
from strava._serialization import strip_not_given
from strava._types import NOT_GIVEN, NotGiven
from strava.models.segments import (
    DetailedSegment,
    ExplorerResponse,
    SummarySegment,
)
from strava.resources._base import AsyncAPIResource, SyncAPIResource


class Segments(SyncAPIResource):
    def retrieve(self, segment_id: int) -> DetailedSegment:
        """Retrieve a segment; distance and elevation are measured in metres."""
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
        """Explore [south, west, north, east] bounds in decimal degrees.

        Restricted to approved Extended Access apps since September 1, 2026.
        """

        params = strip_not_given(
            {
                "bounds": bounds,
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
        """Lazily list starred segments; per_page is not a total limit."""
        return self._paginated_get(
            "/segments/starred",
            model_cls=SummarySegment,
            per_page=per_page,
        )

    def star(self, segment_id: int, *, starred: bool) -> DetailedSegment:
        """Star or unstar a segment; requires profile:write."""
        return self._client._request_model(
            "PUT",
            f"/segments/{segment_id}/starred",
            data={"starred": str(starred).lower()},
            model_cls=DetailedSegment,
        )


class AsyncSegments(AsyncAPIResource):
    async def retrieve(self, segment_id: int) -> DetailedSegment:
        """Retrieve a segment; distance and elevation are measured in metres."""
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
        """Explore [south, west, north, east] bounds in decimal degrees.

        Restricted to approved Extended Access apps since September 1, 2026.
        """

        params = strip_not_given(
            {
                "bounds": bounds,
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
        """Lazily list starred segments; per_page is not a total limit."""
        return self._paginated_get(
            "/segments/starred",
            model_cls=SummarySegment,
            per_page=per_page,
        )

    async def star(self, segment_id: int, *, starred: bool) -> DetailedSegment:
        """Star or unstar a segment; requires profile:write."""
        return await self._client._request_model(
            "PUT",
            f"/segments/{segment_id}/starred",
            data={"starred": str(starred).lower()},
            model_cls=DetailedSegment,
        )
