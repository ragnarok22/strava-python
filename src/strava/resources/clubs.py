from __future__ import annotations

from strava._paginator import AsyncPaginator, SyncPaginator
from strava._types import NOT_GIVEN, NotGiven
from strava.models.clubs import DetailedClub, SummaryClub
from strava.resources._base import AsyncAPIResource, SyncAPIResource


class Clubs(SyncAPIResource):
    def retrieve(self, club_id: int) -> DetailedClub:
        return self._client._request_model(
            "GET", f"/clubs/{club_id}", model_cls=DetailedClub
        )

    def list_authenticated(
        self,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> SyncPaginator[SummaryClub]:
        return self._paginated_get(
            "/athlete/clubs",
            model_cls=SummaryClub,
            per_page=per_page,
        )


class AsyncClubs(AsyncAPIResource):
    async def retrieve(self, club_id: int) -> DetailedClub:
        return await self._client._request_model(
            "GET", f"/clubs/{club_id}", model_cls=DetailedClub
        )

    def list_authenticated(
        self,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[SummaryClub]:
        return self._paginated_get(
            "/athlete/clubs",
            model_cls=SummaryClub,
            per_page=per_page,
        )
