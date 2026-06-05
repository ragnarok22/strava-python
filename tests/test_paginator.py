from __future__ import annotations

import pytest

from strava._paginator import AsyncPaginator, SyncPaginator
from strava.models.activities import SummaryActivity


def make_page(page_num: int, count: int) -> list[dict]:
    return [
        {"id": (page_num - 1) * 30 + i, "name": f"Activity {i}"} for i in range(count)
    ]


class TestSyncPaginator:
    def test_single_page(self):
        def request_fn(params=None):
            page = params.get("page", 1) if params else 1
            if page == 1:
                return make_page(1, 5)
            return []

        paginator = SyncPaginator(
            request_fn=request_fn,
            model_cls=SummaryActivity,
            params={},
            per_page=30,
        )
        items = list(paginator)
        assert len(items) == 5
        assert all(isinstance(a, SummaryActivity) for a in items)

    def test_multiple_pages(self):
        def request_fn(params=None):
            page = params.get("page", 1) if params else 1
            if page <= 3:
                return make_page(page, 30)
            return []

        paginator = SyncPaginator(
            request_fn=request_fn,
            model_cls=SummaryActivity,
            params={},
            per_page=30,
        )
        items = paginator.collect()
        assert len(items) == 90

    def test_collect_with_max(self):
        def request_fn(params=None):
            page = params.get("page", 1) if params else 1
            return make_page(page, 30)

        paginator = SyncPaginator(
            request_fn=request_fn,
            model_cls=SummaryActivity,
            params={},
            per_page=30,
        )
        items = paginator.collect(max_items=50)
        assert len(items) == 50

    def test_collect_with_zero_max_returns_empty_without_request(self):
        def request_fn(params=None):
            raise AssertionError("collect(max_items=0) should not request a page")

        paginator = SyncPaginator(
            request_fn=request_fn,
            model_cls=SummaryActivity,
            params={},
            per_page=30,
        )
        assert paginator.collect(max_items=0) == []

    def test_collect_with_negative_max_raises(self):
        def request_fn(params=None):
            raise AssertionError("collect(max_items=-1) should not request a page")

        paginator = SyncPaginator(
            request_fn=request_fn,
            model_cls=SummaryActivity,
            params={},
            per_page=30,
        )
        with pytest.raises(ValueError):
            paginator.collect(max_items=-1)

    def test_pages_iterator(self):
        def request_fn(params=None):
            page = params.get("page", 1) if params else 1
            if page <= 2:
                return make_page(page, 30)
            return []

        paginator = SyncPaginator(
            request_fn=request_fn,
            model_cls=SummaryActivity,
            params={},
            per_page=30,
        )
        pages = list(paginator.pages())
        assert len(pages) == 2
        assert len(pages[0]) == 30
        assert len(pages[1]) == 30

    def test_empty_first_page(self):
        def request_fn(params=None):
            return []

        paginator = SyncPaginator(
            request_fn=request_fn,
            model_cls=SummaryActivity,
            params={},
            per_page=30,
        )
        items = list(paginator)
        assert len(items) == 0


class TestAsyncPaginator:
    @pytest.mark.asyncio
    async def test_single_page(self):
        async def request_fn(params=None):
            page = params.get("page", 1) if params else 1
            if page == 1:
                return make_page(1, 5)
            return []

        paginator = AsyncPaginator(
            request_fn=request_fn,
            model_cls=SummaryActivity,
            params={},
            per_page=30,
        )
        items = await paginator.collect()
        assert len(items) == 5

    @pytest.mark.asyncio
    async def test_collect_with_max(self):
        async def request_fn(params=None):
            page = params.get("page", 1) if params else 1
            return make_page(page, 30)

        paginator = AsyncPaginator(
            request_fn=request_fn,
            model_cls=SummaryActivity,
            params={},
            per_page=30,
        )
        items = await paginator.collect(max_items=50)
        assert len(items) == 50

    @pytest.mark.asyncio
    async def test_collect_with_zero_max_returns_empty_without_request(self):
        async def request_fn(params=None):
            raise AssertionError("collect(max_items=0) should not request a page")

        paginator = AsyncPaginator(
            request_fn=request_fn,
            model_cls=SummaryActivity,
            params={},
            per_page=30,
        )
        assert await paginator.collect(max_items=0) == []

    @pytest.mark.asyncio
    async def test_collect_with_negative_max_raises(self):
        async def request_fn(params=None):
            raise AssertionError("collect(max_items=-1) should not request a page")

        paginator = AsyncPaginator(
            request_fn=request_fn,
            model_cls=SummaryActivity,
            params={},
            per_page=30,
        )
        with pytest.raises(ValueError):
            await paginator.collect(max_items=-1)
