from __future__ import annotations

from typing import Any, Callable, TypeVar

import httpx

from strava._auth import OAuth2Auth
from strava._base_client import BASE_URL, build_query_params
from strava._exceptions import raise_for_status
from strava.models._base import StravaModel
from strava.resources.activities import AsyncActivities
from strava.resources.athletes import AsyncAthletes
from strava.resources.clubs import AsyncClubs
from strava.resources.gear import AsyncGear
from strava.resources.routes import AsyncRoutes
from strava.resources.segment_efforts import AsyncSegmentEfforts
from strava.resources.segments import AsyncSegments
from strava.resources.streams import AsyncStreams
from strava.resources.uploads import AsyncUploads

T = TypeVar("T", bound=StravaModel)


class AsyncStrava:
    """Asynchronous Strava API v3 client."""

    activities: AsyncActivities
    athletes: AsyncAthletes
    clubs: AsyncClubs
    gear: AsyncGear
    routes: AsyncRoutes
    segments: AsyncSegments
    segment_efforts: AsyncSegmentEfforts
    streams: AsyncStreams
    uploads: AsyncUploads

    def __init__(
        self,
        *,
        access_token: str,
        client_id: str | None = None,
        client_secret: str | None = None,
        refresh_token: str | None = None,
        expires_at: int | None = None,
        on_token_refresh: Callable[[str, str, int], None] | None = None,
        base_url: str = BASE_URL,
        timeout: float = 30.0,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        auth = OAuth2Auth(
            access_token,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            expires_at=expires_at,
            on_token_refresh=on_token_refresh,
        )

        if http_client is not None:
            self._http = http_client
        else:
            self._http = httpx.AsyncClient(
                base_url=base_url,
                auth=auth,
                timeout=timeout,
            )

        self.activities = AsyncActivities(self)
        self.athletes = AsyncAthletes(self)
        self.clubs = AsyncClubs(self)
        self.gear = AsyncGear(self)
        self.routes = AsyncRoutes(self)
        self.segments = AsyncSegments(self)
        self.segment_efforts = AsyncSegmentEfforts(self)
        self.streams = AsyncStreams(self)
        self.uploads = AsyncUploads(self)

    async def _request_model(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        model_cls: type[T],
    ) -> T:
        response = await self._http.request(
            method,
            path,
            params=build_query_params(params),
            json=json,
            data=data,
            files=files,
        )
        raise_for_status(response)
        return model_cls.from_dict(response.json())

    async def _request_model_list(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        model_cls: type[T],
    ) -> list[T]:
        response = await self._http.request(
            method,
            path,
            params=build_query_params(params),
        )
        raise_for_status(response)
        return [model_cls.from_dict(item) for item in response.json()]

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        response = await self._http.request(
            method,
            path,
            params=build_query_params(params),
        )
        raise_for_status(response)
        return response.json()

    async def _request_bytes(
        self,
        method: str,
        path: str,
    ) -> bytes:
        response = await self._http.request(method, path)
        raise_for_status(response)
        return response.content

    async def close(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> AsyncStrava:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
