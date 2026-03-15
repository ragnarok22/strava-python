from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from strava._async_client import AsyncStrava
    from strava._client import Strava


class SyncAPIResource:
    _client: Strava

    def __init__(self, client: Strava) -> None:
        self._client = client


class AsyncAPIResource:
    _client: AsyncStrava

    def __init__(self, client: AsyncStrava) -> None:
        self._client = client
