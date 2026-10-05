from __future__ import annotations

from collections.abc import Callable
from typing import Any, Self, TypeVar

import httpx

from strava._auth import OAuth2Auth
from strava._base_client import BASE_URL, build_query_params, build_resource_url
from strava._exceptions import RateLimitInfo, extract_rate_limits, raise_for_status
from strava._types import NOT_GIVEN, NotGiven
from strava.models._base import StravaModel
from strava.resources.activities import Activities
from strava.resources.athletes import Athletes
from strava.resources.clubs import Clubs
from strava.resources.gear import Gear
from strava.resources.routes import Routes
from strava.resources.segment_efforts import SegmentEfforts
from strava.resources.segments import Segments
from strava.resources.streams import Streams
from strava.resources.uploads import Uploads
from strava.resources.webhooks import Webhooks

T = TypeVar("T", bound=StravaModel)


class Strava:
    """Synchronous Strava API v3 client."""

    activities: Activities
    athletes: Athletes
    clubs: Clubs
    gear: Gear
    routes: Routes
    segments: Segments
    segment_efforts: SegmentEfforts
    streams: Streams
    uploads: Uploads
    webhooks: Webhooks

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
        http_client: httpx.Client | None = None,
    ) -> None:
        self._auth = OAuth2Auth(
            access_token,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            expires_at=expires_at,
            on_token_refresh=on_token_refresh,
        )
        self._base_url = base_url
        self._timeout = timeout
        self._owns_http_client = http_client is None

        if http_client is not None:
            self._http = http_client
        else:
            self._http = httpx.Client(
                base_url=base_url,
                auth=self._auth,
                timeout=timeout,
            )

        self._rate_limits = RateLimitInfo()

        self.activities = Activities(self)
        self.athletes = Athletes(self)
        self.clubs = Clubs(self)
        self.gear = Gear(self)
        self.routes = Routes(self)
        self.segments = Segments(self)
        self.segment_efforts = SegmentEfforts(self)
        self.streams = Streams(self)
        self.uploads = Uploads(self)
        self.webhooks = Webhooks(self)

    @property
    def rate_limits(self) -> RateLimitInfo:
        """Most recent rate limit state from the last API response."""
        return self._rate_limits

    def _handle_response(self, response: httpx.Response) -> None:
        self._rate_limits = extract_rate_limits(response)
        raise_for_status(response)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        auth: httpx.Auth | None | NotGiven = NOT_GIVEN,
    ) -> httpx.Response:
        request_auth = self._auth if isinstance(auth, NotGiven) else auth
        request = self._http.build_request(
            method,
            build_resource_url(self._base_url, path),
            params=build_query_params(params),
            json=json,
            data=data,
            files=files,
            timeout=self._timeout,
        )
        if request_auth is None:
            request.headers.pop("Authorization", None)
        response = self._http.send(request, auth=request_auth)
        self._handle_response(response)
        return response

    def _request_model(
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
        response = self._request(
            method,
            path,
            params=params,
            json=json,
            data=data,
            files=files,
        )
        return model_cls.from_dict(response.json())

    def _request_model_list(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        model_cls: type[T],
    ) -> list[T]:
        response = self._request(method, path, params=params)
        return [model_cls.from_dict(item) for item in response.json()]

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        response = self._request(method, path, params=params)
        return response.json()

    def _request_bytes(
        self,
        method: str,
        path: str,
    ) -> bytes:
        response = self._request(method, path)
        return response.content

    def close(self) -> None:
        if self._owns_http_client:
            self._http.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
