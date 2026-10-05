from __future__ import annotations

import inspect

import httpx
import pytest
import pytest_asyncio
import respx

from strava import AsyncPaginator, AsyncStrava, Strava, SyncPaginator
from strava.models.activities import SummaryActivity

BASE = "https://www.strava.com/api/v3"


@pytest.mark.asyncio
@pytest.mark.parametrize("paginator_cls", [SyncPaginator, AsyncPaginator])
@pytest.mark.parametrize("max_items", [None, 3])
async def test_short_intermediate_pages_do_not_terminate_pagination(
    paginator_cls, max_items
):
    calls = []
    pages = {
        1: [{"id": 1}],
        2: [{"id": 2}, {"id": 3}],
        3: [{"id": 4}],
        4: [],
    }

    def request_fn(*, params):
        calls.append(dict(params))
        return pages[params["page"]]

    async def async_request_fn(*, params):
        return request_fn(params=params)

    paginator = paginator_cls(
        request_fn=(
            async_request_fn if paginator_cls is AsyncPaginator else request_fn
        ),
        model_cls=SummaryActivity,
        params={"after": 123},
        per_page=2,
    )
    result = paginator.collect(max_items=max_items)
    activities = await result if inspect.isawaitable(result) else result

    expected_ids = [1, 2, 3, 4] if max_items is None else [1, 2, 3]
    assert [activity.id for activity in activities] == expected_ids
    expected_pages = [1, 2, 3, 4] if max_items is None else [1, 2]
    assert calls == [
        {"after": 123, "page": page, "per_page": 2} for page in expected_pages
    ]


@pytest_asyncio.fixture(params=[Strava, AsyncStrava], ids=["sync", "async"])
async def client(request):
    client = request.param(access_token="test_token")
    yield client
    result = client.close()
    if inspect.isawaitable(result):
        await result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "options",
    [
        {"page_size": 2},
        {"per_page": 2},
        {"page_size": 2, "after_cursor": "resume%2F+"},
    ],
    ids=["cursor-default", "legacy-size-alias", "resume-cursor"],
)
@pytest.mark.parametrize("max_items", [None, 2])
@respx.mock
async def test_comments_advance_opaque_cursor_without_page_number_params(
    client, options, max_items
):
    requests = []
    initial_cursor = options.get("after_cursor")
    next_cursor = "next+/%20="
    last_cursor = "last%2F+="

    def response(request):
        requests.append(dict(request.url.params))
        assert len(requests) <= 3, "Comment pagination did not advance the cursor"
        cursor = request.url.params.get("after_cursor")
        if cursor == initial_cursor:
            payload = [
                {"id": 1, "text": "First", "cursor": "first"},
                {"id": 2, "text": "Second", "cursor": next_cursor},
            ]
        elif cursor == next_cursor:
            payload = [{"id": 3, "text": "Third", "cursor": last_cursor}]
        else:
            assert cursor == last_cursor
            payload = []
        return httpx.Response(200, json=payload)

    respx.get(f"{BASE}/activities/123/comments").mock(side_effect=response)
    paginator = client.activities.list_comments(123, **options)
    result = paginator.collect(max_items=max_items)
    comments = await result if inspect.isawaitable(result) else result

    assert [comment.id for comment in comments] == (
        [1, 2, 3] if max_items is None else [1, 2]
    )
    assert comments[1].cursor == next_cursor
    assert comments[1].to_dict()["cursor"] == next_cursor
    first_params = {"page_size": "2"}
    if initial_cursor is not None:
        first_params["after_cursor"] = initial_cursor
    expected_requests = [first_params]
    if max_items is None:
        expected_requests.extend(
            [
                {"page_size": "2", "after_cursor": next_cursor},
                {"page_size": "2", "after_cursor": last_cursor},
            ]
        )
    assert requests == expected_requests
