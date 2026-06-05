from __future__ import annotations

from strava._paginator import AsyncPaginator, SyncPaginator
from strava._types import NOT_GIVEN, NotGiven
from strava.models.routes import Route
from strava.resources._base import AsyncAPIResource, SyncAPIResource


class Routes(SyncAPIResource):
    def retrieve(self, route_id: int) -> Route:
        return self._client._request_model(
            "GET", f"/routes/{route_id}", model_cls=Route
        )

    def export_gpx(self, route_id: int) -> bytes:
        return self._client._request_bytes("GET", f"/routes/{route_id}/export_gpx")

    def export_tcx(self, route_id: int) -> bytes:
        return self._client._request_bytes("GET", f"/routes/{route_id}/export_tcx")

    def list_by_athlete(
        self,
        athlete_id: int,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> SyncPaginator[Route]:
        return self._paginated_get(
            f"/athletes/{athlete_id}/routes",
            model_cls=Route,
            per_page=per_page,
        )


class AsyncRoutes(AsyncAPIResource):
    async def retrieve(self, route_id: int) -> Route:
        return await self._client._request_model(
            "GET", f"/routes/{route_id}", model_cls=Route
        )

    async def export_gpx(self, route_id: int) -> bytes:
        return await self._client._request_bytes(
            "GET", f"/routes/{route_id}/export_gpx"
        )

    async def export_tcx(self, route_id: int) -> bytes:
        return await self._client._request_bytes(
            "GET", f"/routes/{route_id}/export_tcx"
        )

    def list_by_athlete(
        self,
        athlete_id: int,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[Route]:
        return self._paginated_get(
            f"/athletes/{athlete_id}/routes",
            model_cls=Route,
            per_page=per_page,
        )
