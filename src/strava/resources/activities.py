from __future__ import annotations

from typing import Any

from strava._paginator import AsyncPaginator, SyncPaginator
from strava._serialization import strip_not_given, to_form_data
from strava._types import NOT_GIVEN, NotGiven
from strava.models._enums import ActivityType, SportType
from strava.models.activities import (
    ActivityZone,
    Comment,
    DetailedActivity,
    Lap,
    SummaryActivity,
)
from strava.models.athletes import SummaryAthlete
from strava.resources._base import AsyncAPIResource, SyncAPIResource


def _activity_create_data(
    *,
    name: str,
    sport_type: SportType | str,
    start_date_local: str,
    elapsed_time: int,
    type: ActivityType | str | NotGiven = NOT_GIVEN,
    description: str | NotGiven = NOT_GIVEN,
    distance: float | NotGiven = NOT_GIVEN,
    trainer: bool | NotGiven = NOT_GIVEN,
    commute: bool | NotGiven = NOT_GIVEN,
) -> dict[str, Any]:
    return to_form_data(
        {
            "name": name,
            "sport_type": sport_type,
            "start_date_local": start_date_local,
            "elapsed_time": elapsed_time,
            "type": type,
            "description": description,
            "distance": distance,
            "trainer": trainer,
            "commute": commute,
        }
    )


def _activity_update_body(
    *,
    name: str | NotGiven = NOT_GIVEN,
    description: str | NotGiven = NOT_GIVEN,
    type: ActivityType | str | NotGiven = NOT_GIVEN,
    sport_type: SportType | str | NotGiven = NOT_GIVEN,
    gear_id: str | NotGiven = NOT_GIVEN,
    trainer: bool | NotGiven = NOT_GIVEN,
    commute: bool | NotGiven = NOT_GIVEN,
    hide_from_home: bool | NotGiven = NOT_GIVEN,
) -> dict[str, Any]:
    return strip_not_given(
        {
            "name": name,
            "description": description,
            "type": type,
            "sport_type": sport_type,
            "gear_id": gear_id,
            "trainer": trainer,
            "commute": commute,
            "hide_from_home": hide_from_home,
        }
    )


class Activities(SyncAPIResource):
    def create(
        self,
        *,
        name: str,
        sport_type: SportType | str,
        start_date_local: str,
        elapsed_time: int,
        type: ActivityType | str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        distance: float | NotGiven = NOT_GIVEN,
        trainer: bool | NotGiven = NOT_GIVEN,
        commute: bool | NotGiven = NOT_GIVEN,
    ) -> DetailedActivity:
        data = _activity_create_data(
            name=name,
            sport_type=sport_type,
            start_date_local=start_date_local,
            elapsed_time=elapsed_time,
            type=type,
            description=description,
            distance=distance,
            trainer=trainer,
            commute=commute,
        )
        return self._client._request_model(
            "POST", "/activities", data=data, model_cls=DetailedActivity
        )

    def retrieve(
        self,
        activity_id: int,
        *,
        include_all_efforts: bool | NotGiven = NOT_GIVEN,
    ) -> DetailedActivity:
        params = strip_not_given({"include_all_efforts": include_all_efforts})
        return self._client._request_model(
            "GET",
            f"/activities/{activity_id}",
            params=params,
            model_cls=DetailedActivity,
        )

    def update(
        self,
        activity_id: int,
        *,
        name: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        type: ActivityType | str | NotGiven = NOT_GIVEN,
        sport_type: SportType | str | NotGiven = NOT_GIVEN,
        gear_id: str | NotGiven = NOT_GIVEN,
        trainer: bool | NotGiven = NOT_GIVEN,
        commute: bool | NotGiven = NOT_GIVEN,
        hide_from_home: bool | NotGiven = NOT_GIVEN,
    ) -> DetailedActivity:
        body = _activity_update_body(
            name=name,
            description=description,
            type=type,
            sport_type=sport_type,
            gear_id=gear_id,
            trainer=trainer,
            commute=commute,
            hide_from_home=hide_from_home,
        )
        return self._client._request_model(
            "PUT",
            f"/activities/{activity_id}",
            json=body,
            model_cls=DetailedActivity,
        )

    def list(
        self,
        *,
        before: int | NotGiven = NOT_GIVEN,
        after: int | NotGiven = NOT_GIVEN,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> SyncPaginator[SummaryActivity]:
        params = strip_not_given({"before": before, "after": after})
        return self._paginated_get(
            "/athlete/activities",
            model_cls=SummaryActivity,
            params=params,
            per_page=per_page,
        )

    def list_comments(
        self,
        activity_id: int,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        after_cursor: str | NotGiven = NOT_GIVEN,
    ) -> SyncPaginator[Comment]:
        params = strip_not_given({"page_size": page_size, "after_cursor": after_cursor})
        return self._paginated_get(
            f"/activities/{activity_id}/comments",
            model_cls=Comment,
            params=params,
            per_page=per_page,
        )

    def list_kudoers(
        self,
        activity_id: int,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> SyncPaginator[SummaryAthlete]:
        return self._paginated_get(
            f"/activities/{activity_id}/kudos",
            model_cls=SummaryAthlete,
            per_page=per_page,
        )

    def list_laps(self, activity_id: int) -> list[Lap]:
        return self._client._request_model_list(
            "GET", f"/activities/{activity_id}/laps", model_cls=Lap
        )

    def list_zones(self, activity_id: int) -> list[ActivityZone]:
        return self._client._request_model_list(
            "GET", f"/activities/{activity_id}/zones", model_cls=ActivityZone
        )


class AsyncActivities(AsyncAPIResource):
    async def create(
        self,
        *,
        name: str,
        sport_type: SportType | str,
        start_date_local: str,
        elapsed_time: int,
        type: ActivityType | str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        distance: float | NotGiven = NOT_GIVEN,
        trainer: bool | NotGiven = NOT_GIVEN,
        commute: bool | NotGiven = NOT_GIVEN,
    ) -> DetailedActivity:
        data = _activity_create_data(
            name=name,
            sport_type=sport_type,
            start_date_local=start_date_local,
            elapsed_time=elapsed_time,
            type=type,
            description=description,
            distance=distance,
            trainer=trainer,
            commute=commute,
        )
        return await self._client._request_model(
            "POST", "/activities", data=data, model_cls=DetailedActivity
        )

    async def retrieve(
        self,
        activity_id: int,
        *,
        include_all_efforts: bool | NotGiven = NOT_GIVEN,
    ) -> DetailedActivity:
        params = strip_not_given({"include_all_efforts": include_all_efforts})
        return await self._client._request_model(
            "GET",
            f"/activities/{activity_id}",
            params=params,
            model_cls=DetailedActivity,
        )

    async def update(
        self,
        activity_id: int,
        *,
        name: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        type: ActivityType | str | NotGiven = NOT_GIVEN,
        sport_type: SportType | str | NotGiven = NOT_GIVEN,
        gear_id: str | NotGiven = NOT_GIVEN,
        trainer: bool | NotGiven = NOT_GIVEN,
        commute: bool | NotGiven = NOT_GIVEN,
        hide_from_home: bool | NotGiven = NOT_GIVEN,
    ) -> DetailedActivity:
        body = _activity_update_body(
            name=name,
            description=description,
            type=type,
            sport_type=sport_type,
            gear_id=gear_id,
            trainer=trainer,
            commute=commute,
            hide_from_home=hide_from_home,
        )
        return await self._client._request_model(
            "PUT",
            f"/activities/{activity_id}",
            json=body,
            model_cls=DetailedActivity,
        )

    def list(
        self,
        *,
        before: int | NotGiven = NOT_GIVEN,
        after: int | NotGiven = NOT_GIVEN,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[SummaryActivity]:
        params = strip_not_given({"before": before, "after": after})
        return self._paginated_get(
            "/athlete/activities",
            model_cls=SummaryActivity,
            params=params,
            per_page=per_page,
        )

    def list_comments(
        self,
        activity_id: int,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        after_cursor: str | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[Comment]:
        params = strip_not_given({"page_size": page_size, "after_cursor": after_cursor})
        return self._paginated_get(
            f"/activities/{activity_id}/comments",
            model_cls=Comment,
            params=params,
            per_page=per_page,
        )

    def list_kudoers(
        self,
        activity_id: int,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[SummaryAthlete]:
        return self._paginated_get(
            f"/activities/{activity_id}/kudos",
            model_cls=SummaryAthlete,
            per_page=per_page,
        )

    async def list_laps(self, activity_id: int) -> list[Lap]:
        return await self._client._request_model_list(
            "GET", f"/activities/{activity_id}/laps", model_cls=Lap
        )

    async def list_zones(self, activity_id: int) -> list[ActivityZone]:
        return await self._client._request_model_list(
            "GET", f"/activities/{activity_id}/zones", model_cls=ActivityZone
        )
