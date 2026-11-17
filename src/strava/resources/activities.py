from __future__ import annotations

import builtins
from collections.abc import Mapping
from typing import Any

from strava._paginator import (
    AsyncCursorPaginator,
    AsyncPaginator,
    SyncCursorPaginator,
    SyncPaginator,
)
from strava._serialization import strip_not_given, to_form_data
from strava._types import NOT_GIVEN, NotGiven, resolve_per_page
from strava.models._enums import (
    ActivityTag,
    ActivityType,
    ActivityVisibility,
    SportType,
)
from strava.models.activities import (
    ActivityZone,
    Comment,
    DetailedActivity,
    Lap,
    SummaryActivity,
)
from strava.models.athletes import SummaryAthlete
from strava.resources._activity_options import activity_tag_data
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
    visibility: ActivityVisibility | str | NotGiven = NOT_GIVEN,
    tags: Mapping[str, bool] | Mapping[ActivityTag, bool] | NotGiven = NOT_GIVEN,
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
            "visibility": visibility,
        }
    ) | activity_tag_data(tags, commute=commute, form=True)


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
    visibility: ActivityVisibility | str | NotGiven = NOT_GIVEN,
    tags: Mapping[str, bool] | Mapping[ActivityTag, bool] | NotGiven = NOT_GIVEN,
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
            "visibility": visibility,
        }
    ) | activity_tag_data(tags, commute=commute, form=False)


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
        visibility: ActivityVisibility | str | NotGiven = NOT_GIVEN,
        tags: Mapping[str, bool] | Mapping[ActivityTag, bool] | NotGiven = NOT_GIVEN,
    ) -> DetailedActivity:
        """Create a manual activity; requires ``activity:write``.

        ``distance`` is meters, ``elapsed_time`` seconds, and ``start_date_local``
        an ISO 8601 local date-time. Visibility accepts ``followers_only`` or
        ``only_me`` (more restrictive only).
        ``tags`` maps supported tag names to booleans (add/remove); omitted tags
        are unchanged. Do not combine it with ``commute``, even ``commute=False``.
        """
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
            visibility=visibility,
            tags=tags,
        )
        return self._client._request_model(
            "POST", "/activities", data=data, model_cls=DetailedActivity
        )

    def retrieve(
        self,
        activity_id: int | str,
        *,
        include_all_efforts: bool | NotGiven = NOT_GIVEN,
    ) -> DetailedActivity:
        """Get an owned activity with ``activity:read`` (``activity:read_all`` for Only Me)."""
        params = strip_not_given({"include_all_efforts": include_all_efforts})
        return self._client._request_model(
            "GET",
            f"/activities/{activity_id}",
            params=params,
            model_cls=DetailedActivity,
        )

    def update(
        self,
        activity_id: int | str,
        *,
        name: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        type: ActivityType | str | NotGiven = NOT_GIVEN,
        sport_type: SportType | str | NotGiven = NOT_GIVEN,
        gear_id: str | NotGiven = NOT_GIVEN,
        trainer: bool | NotGiven = NOT_GIVEN,
        commute: bool | NotGiven = NOT_GIVEN,
        hide_from_home: bool | NotGiven = NOT_GIVEN,
        visibility: ActivityVisibility | str | NotGiven = NOT_GIVEN,
        tags: Mapping[str, bool] | Mapping[ActivityTag, bool] | NotGiven = NOT_GIVEN,
    ) -> DetailedActivity:
        """Update supplied fields; requires ``activity:write``.

        Only Me activities also require ``activity:read_all``.
        ``visibility`` can only become more restrictive: ``followers_only`` or
        ``only_me``. ``tags`` cannot be combined with legacy ``commute``.
        """
        body = _activity_update_body(
            name=name,
            description=description,
            type=type,
            sport_type=sport_type,
            gear_id=gear_id,
            trainer=trainer,
            commute=commute,
            hide_from_home=hide_from_home,
            visibility=visibility,
            tags=tags,
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
        """Iterate activities with ``activity:read``; Only Me needs ``activity:read_all``.

        ``per_page`` sets the page size, not the total number of results.
        """
        params = strip_not_given({"before": before, "after": after})
        return self._paginated_get(
            "/athlete/activities",
            model_cls=SummaryActivity,
            params=params,
            per_page=per_page,
        )

    def list_comments(
        self,
        activity_id: int | str,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        after_cursor: str | NotGiven = NOT_GIVEN,
    ) -> SyncPaginator[Comment]:
        """Iterate comments with ``activity:read`` (``activity:read_all`` for Only Me).

        Uses cursor pagination; ``page_size`` overrides the legacy ``per_page``
        alias. Neither limits the total number of results.
        """
        size = per_page if isinstance(page_size, NotGiven) else page_size
        return SyncCursorPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET", f"/activities/{activity_id}/comments", params=kw["params"]
            ),
            model_cls=Comment,
            params=strip_not_given({"after_cursor": after_cursor}),
            per_page=resolve_per_page(size),
        )

    def list_kudoers(
        self,
        activity_id: int | str,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> SyncPaginator[SummaryAthlete]:
        """Iterate kudoers with ``activity:read`` (``activity:read_all`` for Only Me).

        ``per_page`` sets the page size, not the total number of results.
        """
        return self._paginated_get(
            f"/activities/{activity_id}/kudos",
            model_cls=SummaryAthlete,
            per_page=per_page,
        )

    def list_laps(self, activity_id: int | str) -> builtins.list[Lap]:
        """Get laps with ``activity:read`` (``activity:read_all`` for Only Me)."""
        return self._client._request_model_list(
            "GET", f"/activities/{activity_id}/laps", model_cls=Lap
        )

    def list_zones(self, activity_id: int | str) -> builtins.list[ActivityZone]:
        """Get Summit zones with ``activity:read`` (``activity:read_all`` for Only Me)."""
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
        visibility: ActivityVisibility | str | NotGiven = NOT_GIVEN,
        tags: Mapping[str, bool] | Mapping[ActivityTag, bool] | NotGiven = NOT_GIVEN,
    ) -> DetailedActivity:
        """Create a manual activity; requires ``activity:write``.

        ``distance`` is meters, ``elapsed_time`` seconds, and ``start_date_local``
        an ISO 8601 local date-time. Visibility accepts ``followers_only`` or
        ``only_me`` (more restrictive only).
        ``tags`` maps supported tag names to booleans (add/remove); omitted tags
        are unchanged. Do not combine it with ``commute``, even ``commute=False``.
        """
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
            visibility=visibility,
            tags=tags,
        )
        return await self._client._request_model(
            "POST", "/activities", data=data, model_cls=DetailedActivity
        )

    async def retrieve(
        self,
        activity_id: int | str,
        *,
        include_all_efforts: bool | NotGiven = NOT_GIVEN,
    ) -> DetailedActivity:
        """Get an owned activity with ``activity:read`` (``activity:read_all`` for Only Me)."""
        params = strip_not_given({"include_all_efforts": include_all_efforts})
        return await self._client._request_model(
            "GET",
            f"/activities/{activity_id}",
            params=params,
            model_cls=DetailedActivity,
        )

    async def update(
        self,
        activity_id: int | str,
        *,
        name: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        type: ActivityType | str | NotGiven = NOT_GIVEN,
        sport_type: SportType | str | NotGiven = NOT_GIVEN,
        gear_id: str | NotGiven = NOT_GIVEN,
        trainer: bool | NotGiven = NOT_GIVEN,
        commute: bool | NotGiven = NOT_GIVEN,
        hide_from_home: bool | NotGiven = NOT_GIVEN,
        visibility: ActivityVisibility | str | NotGiven = NOT_GIVEN,
        tags: Mapping[str, bool] | Mapping[ActivityTag, bool] | NotGiven = NOT_GIVEN,
    ) -> DetailedActivity:
        """Update supplied fields; requires ``activity:write``.

        Only Me activities also require ``activity:read_all``.
        ``visibility`` can only become more restrictive: ``followers_only`` or
        ``only_me``. ``tags`` cannot be combined with legacy ``commute``.
        """
        body = _activity_update_body(
            name=name,
            description=description,
            type=type,
            sport_type=sport_type,
            gear_id=gear_id,
            trainer=trainer,
            commute=commute,
            hide_from_home=hide_from_home,
            visibility=visibility,
            tags=tags,
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
        """Iterate activities with ``activity:read``; Only Me needs ``activity:read_all``.

        ``per_page`` sets the page size, not the total number of results.
        """
        params = strip_not_given({"before": before, "after": after})
        return self._paginated_get(
            "/athlete/activities",
            model_cls=SummaryActivity,
            params=params,
            per_page=per_page,
        )

    def list_comments(
        self,
        activity_id: int | str,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        after_cursor: str | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[Comment]:
        """Iterate comments with ``activity:read`` (``activity:read_all`` for Only Me).

        Uses cursor pagination; ``page_size`` overrides the legacy ``per_page``
        alias. Neither limits the total number of results.
        """
        size = per_page if isinstance(page_size, NotGiven) else page_size
        return AsyncCursorPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET", f"/activities/{activity_id}/comments", params=kw["params"]
            ),
            model_cls=Comment,
            params=strip_not_given({"after_cursor": after_cursor}),
            per_page=resolve_per_page(size),
        )

    def list_kudoers(
        self,
        activity_id: int | str,
        *,
        per_page: int | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[SummaryAthlete]:
        """Iterate kudoers with ``activity:read`` (``activity:read_all`` for Only Me).

        ``per_page`` sets the page size, not the total number of results.
        """
        return self._paginated_get(
            f"/activities/{activity_id}/kudos",
            model_cls=SummaryAthlete,
            per_page=per_page,
        )

    async def list_laps(self, activity_id: int | str) -> builtins.list[Lap]:
        """Get laps with ``activity:read`` (``activity:read_all`` for Only Me)."""
        return await self._client._request_model_list(
            "GET", f"/activities/{activity_id}/laps", model_cls=Lap
        )

    async def list_zones(self, activity_id: int | str) -> builtins.list[ActivityZone]:
        """Get Summit zones with ``activity:read`` (``activity:read_all`` for Only Me)."""
        return await self._client._request_model_list(
            "GET", f"/activities/{activity_id}/zones", model_cls=ActivityZone
        )
