from __future__ import annotations

from strava._paginator import AsyncPaginator, SyncPaginator
from strava._types import NOT_GIVEN, NotGiven
from strava.models.activities import ClubActivity
from strava.models.athletes import ClubAthlete, SummaryAthlete
from strava.models.clubs import DetailedClub, SummaryClub
from strava.resources._base import AsyncAPIResource, SyncAPIResource


class Clubs(SyncAPIResource):
    def retrieve(self, club_id: int) -> DetailedClub:
        return self._client._request_model(
            "GET", f"/clubs/{club_id}", model_cls=DetailedClub
        )

    def list_activities(
        self,
        club_id: int,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> SyncPaginator[ClubActivity]:
        """Deprecated by Strava effective September 1, 2026."""

        return self._paginated_get(
            f"/clubs/{club_id}/activities",
            model_cls=ClubActivity,
            per_page=per_page,
        )

    def list_admins(
        self,
        club_id: int,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> SyncPaginator[SummaryAthlete]:
        """Deprecated by Strava effective September 1, 2026."""

        return self._paginated_get(
            f"/clubs/{club_id}/admins",
            model_cls=SummaryAthlete,
            per_page=per_page,
        )

    def list_members(
        self,
        club_id: int,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> SyncPaginator[ClubAthlete]:
        """Deprecated by Strava effective September 1, 2026."""

        return self._paginated_get(
            f"/clubs/{club_id}/members",
            model_cls=ClubAthlete,
            per_page=per_page,
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

    def list_activities(
        self,
        club_id: int,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[ClubActivity]:
        """Deprecated by Strava effective September 1, 2026."""

        return self._paginated_get(
            f"/clubs/{club_id}/activities",
            model_cls=ClubActivity,
            per_page=per_page,
        )

    def list_admins(
        self,
        club_id: int,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[SummaryAthlete]:
        """Deprecated by Strava effective September 1, 2026."""

        return self._paginated_get(
            f"/clubs/{club_id}/admins",
            model_cls=SummaryAthlete,
            per_page=per_page,
        )

    def list_members(
        self,
        club_id: int,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[ClubAthlete]:
        """Deprecated by Strava effective September 1, 2026."""

        return self._paginated_get(
            f"/clubs/{club_id}/members",
            model_cls=ClubAthlete,
            per_page=per_page,
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
