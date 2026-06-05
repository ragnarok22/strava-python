from __future__ import annotations

from typing import Any, AsyncIterator, Callable, Generic, Iterator, TypeVar

T = TypeVar("T")


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
            if len(raw_items) < self._per_page:
                break
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
            if len(raw_items) < self._per_page:
                break
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
