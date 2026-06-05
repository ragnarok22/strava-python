from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from strava._paginator import AsyncPaginator, SyncPaginator
from strava._types import NotGiven, resolve_per_page

if TYPE_CHECKING:
    from strava._async_client import AsyncStrava
    from strava._client import Strava


T = TypeVar("T")


class SyncAPIResource:
    _client: Strava

    def __init__(self, client: Strava) -> None:
        self._client = client

    def _paginated_get(
        self,
        path: str,
        *,
        model_cls: type[T],
        params: dict[str, Any] | None = None,
        per_page: int | NotGiven,
    ) -> SyncPaginator[T]:
        return SyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET", path, params=kw.get("params", {})
            ),
            model_cls=model_cls,
            params=params or {},
            per_page=resolve_per_page(per_page),
        )


class AsyncAPIResource:
    _client: AsyncStrava

    def __init__(self, client: AsyncStrava) -> None:
        self._client = client

    def _paginated_get(
        self,
        path: str,
        *,
        model_cls: type[T],
        params: dict[str, Any] | None = None,
        per_page: int | NotGiven,
    ) -> AsyncPaginator[T]:
        return AsyncPaginator(
            request_fn=lambda **kw: self._client._request_json(
                "GET", path, params=kw.get("params", {})
            ),
            model_cls=model_cls,
            params=params or {},
            per_page=resolve_per_page(per_page),
        )
