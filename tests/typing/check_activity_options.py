"""Static consumer contracts for activity options; never network-executed."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import assert_type

from strava import (
    NOT_GIVEN,
    ActivityTag,
    ActivityVisibility,
    AsyncStrava,
    DetailedActivity,
    Strava,
    SummaryActivity,
    UpdatableActivity,
    Upload,
)


def check_response_and_update_shapes(
    activity: SummaryActivity | DetailedActivity,
    update: UpdatableActivity,
) -> None:
    assert_type(activity.visibility, ActivityVisibility | str | None)
    assert_type(activity.tags, list[ActivityTag | str] | None)
    assert_type(update.visibility, ActivityVisibility | str | None)
    assert_type(update.tags, dict[str, bool] | None)
    assert_type(
        UpdatableActivity(
            visibility=ActivityVisibility.ONLY_ME,
            tags={ActivityTag.COMMUTE: False, "WithPet": True},
        ),
        UpdatableActivity,
    )


def check_sync_options(
    client: Strava,
    identifier: int | str,
    tags: Mapping[str, bool],
) -> None:
    enum_tags = {ActivityTag.WITH_PET: True, ActivityTag.COMMUTE: False}
    assert_type(client.activities.update(identifier, tags=enum_tags), DetailedActivity)
    assert_type(
        client.activities.create(
            name="Run",
            sport_type="Run",
            start_date_local="2026-11-17T09:00:00",
            elapsed_time=1800,
            visibility=ActivityVisibility.FOLLOWERS_ONLY,
            tags=tags,
        ),
        DetailedActivity,
    )
    assert_type(
        client.activities.update(
            identifier, visibility="only_me", tags=MappingProxyType({"Recovery": False})
        ),
        DetailedActivity,
    )
    assert_type(
        client.uploads.create(
            file=b"<gpx/>",
            data_type="gpx",
            visibility=ActivityVisibility.ONLY_ME,
            tags={ActivityTag.WITH_PET: True},
        ),
        Upload,
    )
    assert_type(
        client.activities.update(
            identifier, commute=False, visibility=NOT_GIVEN, tags=NOT_GIVEN
        ),
        DetailedActivity,
    )


async def check_async_options(
    client: AsyncStrava,
    identifier: int | str,
    tags: Mapping[str, bool],
) -> None:
    enum_tags = {ActivityTag.WITH_PET: True, ActivityTag.COMMUTE: False}
    assert_type(
        await client.activities.update(identifier, tags=enum_tags), DetailedActivity
    )
    assert_type(
        await client.activities.create(
            name="Run",
            sport_type="Run",
            start_date_local="2026-11-17T09:00:00",
            elapsed_time=1800,
            visibility=ActivityVisibility.FOLLOWERS_ONLY,
            tags=tags,
        ),
        DetailedActivity,
    )
    assert_type(
        await client.activities.update(
            identifier, visibility="only_me", tags=MappingProxyType({"Recovery": False})
        ),
        DetailedActivity,
    )
    assert_type(
        await client.uploads.create(
            file=b"<gpx/>",
            data_type="gpx",
            visibility=ActivityVisibility.ONLY_ME,
            tags={ActivityTag.WITH_PET: True},
        ),
        Upload,
    )
    assert_type(
        await client.activities.update(
            identifier, commute=False, visibility=NOT_GIVEN, tags=NOT_GIVEN
        ),
        DetailedActivity,
    )
