from __future__ import annotations

import httpx
import pytest
import respx

from tests._helpers import invoke

BASE = "https://www.strava.com/api/v3"


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["list_activities", "list_members", "list_admins"])
@respx.mock
async def test_retired_club_endpoints_are_not_exposed(client, method):
    with pytest.raises(AttributeError):
        getattr(client.clubs, method)
    assert len(respx.calls) == 0


@pytest.mark.asyncio
@respx.mock
async def test_supported_club_retrieval_preserves_typed_response(client):
    route = respx.get(f"{BASE}/clubs/123").mock(
        return_value=httpx.Response(
            200, json={"id": 123, "name": "Runners", "member_count": 20}
        )
    )
    club = await invoke(client.clubs.retrieve, 123)

    assert club.id == 123
    assert club.name == "Runners"
    assert club.member_count == 20
    assert route.call_count == 1


@pytest.mark.asyncio
@respx.mock
async def test_supported_athlete_clubs_list_paginates_until_empty(client):
    route = respx.get(f"{BASE}/athlete/clubs").mock(
        side_effect=[
            httpx.Response(200, json=[{"id": 1, "name": "Club One"}]),
            httpx.Response(200, json=[{"id": 2, "name": "Club Two"}]),
            httpx.Response(200, json=[]),
        ]
    )
    clubs = await invoke(client.clubs.list_authenticated(per_page=50).collect)

    assert [(club.id, club.name) for club in clubs] == [
        (1, "Club One"),
        (2, "Club Two"),
    ]
    assert [dict(call.request.url.params) for call in route.calls] == [
        {"page": "1", "per_page": "50"},
        {"page": "2", "per_page": "50"},
        {"page": "3", "per_page": "50"},
    ]
