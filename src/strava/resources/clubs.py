from __future__ import annotations

from strava._paginator import AsyncPaginator, SyncPaginator
from strava._types import NOT_GIVEN, NotGiven, resolve_per_page
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
        return SyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET",
                f"/clubs/{club_id}/activities",
                params=kw.get("params", {}),
            ),
            model_cls=ClubActivity,
            params={},
            per_page=resolve_per_page(per_page),
        )

    def list_admins(
        self,
        club_id: int,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> SyncPaginator[SummaryAthlete]:
        return SyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET",
                f"/clubs/{club_id}/admins",
                params=kw.get("params", {}),
            ),
            model_cls=SummaryAthlete,
            params={},
            per_page=resolve_per_page(per_page),
        )

    def list_members(
        self,
        club_id: int,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> SyncPaginator[ClubAthlete]:
        return SyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET",
                f"/clubs/{club_id}/members",
                params=kw.get("params", {}),
            ),
            model_cls=ClubAthlete,
            params={},
            per_page=resolve_per_page(per_page),
        )

    def list_authenticated(
        self,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> SyncPaginator[SummaryClub]:
        return SyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET", "/athlete/clubs", params=kw.get("params", {})
            ),
            model_cls=SummaryClub,
            params={},
            per_page=resolve_per_page(per_page),
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
        return AsyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET",
                f"/clubs/{club_id}/activities",
                params=kw.get("params", {}),
            ),
            model_cls=ClubActivity,
            params={},
            per_page=resolve_per_page(per_page),
        )

    def list_admins(
        self,
        club_id: int,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[SummaryAthlete]:
        return AsyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET",
                f"/clubs/{club_id}/admins",
                params=kw.get("params", {}),
            ),
            model_cls=SummaryAthlete,
            params={},
            per_page=resolve_per_page(per_page),
        )

    def list_members(
        self,
        club_id: int,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[ClubAthlete]:
        return AsyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET",
                f"/clubs/{club_id}/members",
                params=kw.get("params", {}),
            ),
            model_cls=ClubAthlete,
            params={},
            per_page=resolve_per_page(per_page),
        )

    def list_authenticated(
        self,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[SummaryClub]:
        return AsyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET", "/athlete/clubs", params=kw.get("params", {})
            ),
            model_cls=SummaryClub,
            params={},
            per_page=resolve_per_page(per_page),
        )
