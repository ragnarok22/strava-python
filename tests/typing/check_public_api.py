"""Static consumer contracts; these functions are checked, never network-executed."""

from __future__ import annotations

from typing import assert_type

from strava import (
    ActivityStats,
    ActivityZone,
    AsyncPaginator,
    AsyncStrava,
    Comment,
    DetailedActivity,
    DetailedAthlete,
    Lap,
    MetaActivity,
    MetaAthlete,
    Route,
    SportType,
    Strava,
    StreamSet,
    SummaryActivity,
    SummaryAthlete,
    SyncPaginator,
    TokenResponse,
    WebhookSubscription,
)


class CustomActivity(SummaryActivity):
    pass


def check_model_parsing() -> None:
    assert_type(SummaryActivity.from_dict({"id": 1}), SummaryActivity)
    assert_type(DetailedActivity.from_dict({"id": 1}), DetailedActivity)
    assert_type(CustomActivity.from_dict({"id": 1}), CustomActivity)
    activity = SummaryActivity.from_dict({"sport_type": "FutureSport"})
    assert_type(activity.sport_type, SportType | str | None)


def check_identifier_fields(
    model: MetaActivity
    | SummaryActivity
    | DetailedActivity
    | MetaAthlete
    | SummaryAthlete
    | DetailedAthlete,
) -> None:
    assert_type(model.id, int | None)
    assert_type(model.id_str, str | None)


def check_sync_identifier_endpoints(client: Strava, identifier: int | str) -> None:
    assert_type(client.activities.retrieve(identifier), DetailedActivity)
    assert_type(client.activities.update(identifier, name="Updated"), DetailedActivity)
    assert_type(client.activities.list_comments(identifier), SyncPaginator[Comment])
    assert_type(
        client.activities.list_kudoers(identifier), SyncPaginator[SummaryAthlete]
    )
    assert_type(client.activities.list_laps(identifier), list[Lap])
    assert_type(client.activities.list_zones(identifier), list[ActivityZone])
    assert_type(client.athletes.retrieve_stats(identifier), ActivityStats)
    assert_type(client.routes.list_by_athlete(identifier), SyncPaginator[Route])
    assert_type(
        client.streams.get_activity_streams(identifier, keys=["time"]), StreamSet
    )


async def check_async_identifier_endpoints(
    client: AsyncStrava, identifier: int | str
) -> None:
    assert_type(await client.activities.retrieve(identifier), DetailedActivity)
    assert_type(
        await client.activities.update(identifier, name="Updated"), DetailedActivity
    )
    assert_type(client.activities.list_comments(identifier), AsyncPaginator[Comment])
    assert_type(
        client.activities.list_kudoers(identifier), AsyncPaginator[SummaryAthlete]
    )
    assert_type(await client.activities.list_laps(identifier), list[Lap])
    assert_type(await client.activities.list_zones(identifier), list[ActivityZone])
    assert_type(await client.athletes.retrieve_stats(identifier), ActivityStats)
    assert_type(client.routes.list_by_athlete(identifier), AsyncPaginator[Route])
    assert_type(
        await client.streams.get_activity_streams(identifier, keys=["time"]), StreamSet
    )


def check_sync_endpoints(client: Strava) -> None:
    assert_type(client.athletes.retrieve_authenticated(), DetailedAthlete)
    assert_type(client.activities.retrieve(123), DetailedActivity)
    paginator = client.activities.list()
    assert_type(paginator, SyncPaginator[SummaryActivity])
    assert_type(paginator.collect(max_items=2), list[SummaryActivity])
    for activity in paginator:
        assert_type(activity, SummaryActivity)
    assert_type(
        client.webhooks.list(client_id="example_id", client_secret="example_secret"),
        list[WebhookSubscription],
    )


async def check_async_endpoints(client: AsyncStrava) -> None:
    assert_type(await client.athletes.retrieve_authenticated(), DetailedAthlete)
    assert_type(await client.activities.retrieve(123), DetailedActivity)
    paginator = client.activities.list()
    assert_type(paginator, AsyncPaginator[SummaryActivity])
    assert_type(await paginator.collect(max_items=2), list[SummaryActivity])
    async for activity in paginator:
        assert_type(activity, SummaryActivity)
    assert_type(
        await client.webhooks.list(
            client_id="example_id", client_secret="example_secret"
        ),
        list[WebhookSubscription],
    )


def check_oauth_metadata(tokens: TokenResponse) -> None:
    assert_type(tokens.scope, str | None)
    assert_type(tokens.athlete, SummaryAthlete | None)
