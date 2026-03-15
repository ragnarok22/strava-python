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
        page: int | NotGiven = NOT_GIVEN,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> SyncPaginator[ClubActivity]:
        p = per_page if not isinstance(per_page, NotGiven) else 30
        return SyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET",
                f"/clubs/{club_id}/activities",
                params=kw.get("params", {}),
            ),
            model_cls=ClubActivity,
            params={},
            per_page=p,
        )

    def list_admins(
        self,
        club_id: int,
        *,
        page: int | NotGiven = NOT_GIVEN,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> SyncPaginator[SummaryAthlete]:
        p = per_page if not isinstance(per_page, NotGiven) else 30
        return SyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET",
                f"/clubs/{club_id}/admins",
                params=kw.get("params", {}),
            ),
            model_cls=SummaryAthlete,
            params={},
            per_page=p,
        )

    def list_members(
        self,
        club_id: int,
        *,
        page: int | NotGiven = NOT_GIVEN,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> SyncPaginator[ClubAthlete]:
        p = per_page if not isinstance(per_page, NotGiven) else 30
        return SyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET",
                f"/clubs/{club_id}/members",
                params=kw.get("params", {}),
            ),
            model_cls=ClubAthlete,
            params={},
            per_page=p,
        )

    def list_authenticated(
        self,
        *,
        page: int | NotGiven = NOT_GIVEN,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> SyncPaginator[SummaryClub]:
        p = per_page if not isinstance(per_page, NotGiven) else 30
        return SyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET", "/athlete/clubs", params=kw.get("params", {})
            ),
            model_cls=SummaryClub,
            params={},
            per_page=p,
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
        page: int | NotGiven = NOT_GIVEN,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[ClubActivity]:
        p = per_page if not isinstance(per_page, NotGiven) else 30
        return AsyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET",
                f"/clubs/{club_id}/activities",
                params=kw.get("params", {}),
            ),
            model_cls=ClubActivity,
            params={},
            per_page=p,
        )

    def list_admins(
        self,
        club_id: int,
        *,
        page: int | NotGiven = NOT_GIVEN,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[SummaryAthlete]:
        p = per_page if not isinstance(per_page, NotGiven) else 30
        return AsyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET",
                f"/clubs/{club_id}/admins",
                params=kw.get("params", {}),
            ),
            model_cls=SummaryAthlete,
            params={},
            per_page=p,
        )

    def list_members(
        self,
        club_id: int,
        *,
        page: int | NotGiven = NOT_GIVEN,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[ClubAthlete]:
        p = per_page if not isinstance(per_page, NotGiven) else 30
        return AsyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET",
                f"/clubs/{club_id}/members",
                params=kw.get("params", {}),
            ),
            model_cls=ClubAthlete,
            params={},
            per_page=p,
        )

    def list_authenticated(
        self,
        *,
        page: int | NotGiven = NOT_GIVEN,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[SummaryClub]:
        p = per_page if not isinstance(per_page, NotGiven) else 30
        return AsyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET", "/athlete/clubs", params=kw.get("params", {})
            ),
            model_cls=SummaryClub,
            params={},
            per_page=p,
        )
