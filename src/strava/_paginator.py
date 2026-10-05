from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Iterator
from typing import Any, Generic, TypeVar

from strava.models._base import StravaModel

T = TypeVar("T")
CursorT = TypeVar("CursorT", bound=StravaModel)


class SyncPaginator(Generic[T]):
    """Lazy synchronous paginator that yields individual items across pages."""

    def __init__(
        self,
        *,
        request_fn: Callable[..., list[dict[str, Any]]],
        model_cls: type[T],
        params: dict[str, Any],
        per_page: int = 30,
    ) -> None:
        self._request_fn = request_fn
        self._model_cls = model_cls
        self._params = params
        self._per_page = per_page

    def __iter__(self) -> Iterator[T]:
        for page in self.pages():
            yield from page

    def pages(self) -> Iterator[list[T]]:
        page_num = 1
        while True:
            params = {**self._params, "page": page_num, "per_page": self._per_page}
            raw_items = self._request_fn(params=params)
            items = [self._model_cls.from_dict(item) for item in raw_items]  # type: ignore[attr-defined]
            if not items:
                break
            yield items
            page_num += 1

    def collect(self, *, max_items: int | None = None) -> list[T]:
        if max_items is not None:
            if max_items < 0:
                raise ValueError("max_items must be non-negative")
            if max_items == 0:
                return []

        result: list[T] = []
        for item in self:
            result.append(item)
            if max_items is not None and len(result) >= max_items:
                break
        return result


class AsyncPaginator(Generic[T]):
    """Lazy asynchronous paginator that yields individual items across pages."""

    def __init__(
        self,
        *,
        request_fn: Callable[..., Any],
        model_cls: type[T],
        params: dict[str, Any],
        per_page: int = 30,
    ) -> None:
        self._request_fn = request_fn
        self._model_cls = model_cls
        self._params = params
        self._per_page = per_page

    async def __aiter__(self) -> AsyncIterator[T]:
        async for page in self.pages():
            for item in page:
                yield item

    async def pages(self) -> AsyncIterator[list[T]]:
        page_num = 1
        while True:
            params = {**self._params, "page": page_num, "per_page": self._per_page}
            raw_items = await self._request_fn(params=params)
            items = [self._model_cls.from_dict(item) for item in raw_items]  # type: ignore[attr-defined]
            if not items:
                break
            yield items
            page_num += 1

    async def collect(self, *, max_items: int | None = None) -> list[T]:
        if max_items is not None:
            if max_items < 0:
                raise ValueError("max_items must be non-negative")
            if max_items == 0:
                return []

        result: list[T] = []
        async for item in self:
            result.append(item)
            if max_items is not None and len(result) >= max_items:
                break
        return result


def _next_cursor(last_item: dict[str, Any], seen_cursors: set[str]) -> str:
    cursor = last_item.get("cursor")
    if not isinstance(cursor, str) or not cursor:
        raise RuntimeError(
            "Cannot continue cursor pagination: last item has a missing or invalid cursor"
        )
    if cursor in seen_cursors:
        raise RuntimeError(
            "Cannot continue cursor pagination: cursor did not advance (repeated or cycling)"
        )
    seen_cursors.add(cursor)
    return cursor


class SyncCursorPaginator(SyncPaginator[CursorT]):
    """Lazy cursor pagination; the inherited per_page sets the API's page_size."""

    def pages(self) -> Iterator[list[CursorT]]:
        params = {**self._params, "page_size": self._per_page}
        seen_cursors: set[str] = set()
        if "after_cursor" in params:
            seen_cursors.add(params["after_cursor"])
        while True:
            raw_items = self._request_fn(params=params)
            if not raw_items:
                break
            yield [self._model_cls.from_dict(item) for item in raw_items]
            # Validate only when resumed: bounded collection can stop at this page.
            params = {
                **params,
                "after_cursor": _next_cursor(raw_items[-1], seen_cursors),
            }


class AsyncCursorPaginator(AsyncPaginator[CursorT]):
    """Lazy async cursor pagination with the same API as AsyncPaginator."""

    async def pages(self) -> AsyncIterator[list[CursorT]]:
        params = {**self._params, "page_size": self._per_page}
        seen_cursors: set[str] = set()
        if "after_cursor" in params:
            seen_cursors.add(params["after_cursor"])
        while True:
            raw_items = await self._request_fn(params=params)
            if not raw_items:
                break
            yield [self._model_cls.from_dict(item) for item in raw_items]
            # Validate only when resumed: bounded collection can stop at this page.
            params = {
                **params,
                "after_cursor": _next_cursor(raw_items[-1], seen_cursors),
            }
