from __future__ import annotations

import httpx
import pytest
import respx

from strava import AsyncPaginator, SyncPaginator
from tests._helpers import invoke

BASE = "https://www.strava.com/api/v3"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payloads, initial_cursor, message",
    [
        ([[{"id": 1}]], None, "missing or invalid cursor"),
        ([[{"id": 1, "cursor": None}]], None, "missing or invalid cursor"),
        ([[{"id": 1, "cursor": ""}]], None, "missing or invalid cursor"),
        ([[{"id": 1, "cursor": 123}]], None, "missing or invalid cursor"),
        ([[{"id": 1, "cursor": "resume"}]], "resume", "did not advance"),
        (
            [[{"id": 1, "cursor": "a"}], [{"id": 2, "cursor": "a"}]],
            None,
            "did not advance",
        ),
        (
            [
                [{"id": 1, "cursor": "a"}],
                [{"id": 2, "cursor": "b"}],
                [{"id": 3, "cursor": "a"}],
            ],
            None,
            "did not advance",
        ),
        # The last raw comment must supply the cursor, not an earlier comment.
        ([[{"id": 1, "cursor": "a"}, {"id": 2}]], None, "missing or invalid cursor"),
    ],
    ids=["missing", "null", "empty", "invalid", "resume", "repeated", "cycle", "last"],
)
@respx.mock
async def test_cursor_guards_only_run_when_continuation_is_needed(
    client, payloads, initial_cursor, message
):
    route = respx.get(f"{BASE}/activities/123/comments")
    options = {} if initial_cursor is None else {"after_cursor": initial_cursor}

    def reset_responses():
        route.mock(
            side_effect=[httpx.Response(200, json=payload) for payload in payloads]
        )

    reset_responses()
    paginator = client.activities.list_comments(123, page_size=2, **options)
    count = sum(len(payload) for payload in payloads)
    comments = await invoke(paginator.collect, max_items=count)
    assert len(comments) == count
    assert route.call_count == len(payloads)

    reset_responses()
    with pytest.raises(RuntimeError, match=message):
        await invoke(paginator.collect)
    # Reject continuation before requesting a repeated page or exhausting the mock.
    assert route.call_count == 2 * len(payloads)


@pytest.mark.asyncio
@respx.mock
async def test_empty_comments_and_size_precedence(client):
    route = respx.get(f"{BASE}/activities/123/comments").mock(
        return_value=httpx.Response(200, json=[])
    )
    paginator = client.activities.list_comments(123, page_size=7, per_page=2)
    assert isinstance(paginator, (SyncPaginator, AsyncPaginator))
    assert await invoke(paginator.collect, max_items=0) == []
    with pytest.raises(ValueError, match="max_items must be non-negative"):
        await invoke(paginator.collect, max_items=-1)
    assert route.call_count == 0
    assert await invoke(paginator.collect) == []
    assert route.call_count == 1
    assert dict(route.calls.last.request.url.params) == {"page_size": "7"}


@pytest.mark.asyncio
@respx.mock
async def test_comment_pages_are_lazy_and_restartable(client):
    route = respx.get(f"{BASE}/activities/123/comments").mock(
        side_effect=[
            httpx.Response(200, json=[{"id": 1, "cursor": "first"}]),
            httpx.Response(200, json=[{"id": 2, "cursor": "second"}]),
            httpx.Response(200, json=[]),
            httpx.Response(200, json=[{"id": 1, "cursor": "first"}]),
        ]
    )
    paginator = client.activities.list_comments(123)
    pages = paginator.pages()
    assert route.call_count == 0
    if isinstance(paginator, AsyncPaginator):
        first = await anext(pages)
        assert route.call_count == 1
        rest = [page async for page in pages]
    else:
        first = next(pages)
        assert route.call_count == 1
        rest = list(pages)
    assert [[comment.id for comment in page] for page in [first, *rest]] == [[1], [2]]
    assert [dict(call.request.url.params) for call in route.calls] == [
        {"page_size": "30"},
        {"page_size": "30", "after_cursor": "first"},
        {"page_size": "30", "after_cursor": "second"},
    ]
    assert [comment.id for comment in await invoke(paginator.collect, max_items=1)] == [
        1
    ]
    assert dict(route.calls.last.request.url.params) == {"page_size": "30"}
