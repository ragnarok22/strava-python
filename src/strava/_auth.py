from __future__ import annotations

import time
import warnings
from collections.abc import AsyncGenerator, Callable, Generator
from contextlib import nullcontext
from dataclasses import dataclass, field
from threading import Lock
from typing import Literal
from urllib.parse import urlencode

import anyio
import httpx

from strava._exceptions import raise_for_status
from strava.models.athletes import SummaryAthlete

TOKEN_URL = "https://www.strava.com/oauth/token"
AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
DEAUTHORIZE_URL = "https://www.strava.com/oauth/deauthorize"
REVOKE_URL = "https://www.strava.com/oauth/revoke"

TokenTypeHint = Literal["access_token", "refresh_token"]


@dataclass(slots=True)
class TokenResponse:
    """OAuth tokens with optional granted scopes and athlete summary metadata."""

    access_token: str = field(repr=False)
    refresh_token: str = field(repr=False)
    expires_at: int
    expires_in: int
    token_type: str
    scope: str | None = None
    athlete: SummaryAthlete | None = None


class OAuth2Auth(httpx.Auth):
    """httpx Auth handler with automatic token refresh for Strava OAuth2."""

    def __init__(
        self,
        access_token: str,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        refresh_token: str | None = None,
        expires_at: int | None = None,
        on_token_refresh: Callable[[str, str, int], None] | None = None,
    ) -> None:
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.expires_at = expires_at
        self.on_token_refresh = on_token_refresh
        self._sync_refresh_lock = Lock()
        self._async_refresh_lock = anyio.Lock()

    def _is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() >= self.expires_at

    def _can_refresh(self) -> bool:
        return bool(self.client_id and self.client_secret and self.refresh_token)

    def _build_refresh_request(self, request: httpx.Request) -> httpx.Request:
        return httpx.Request(
            "POST",
            TOKEN_URL,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            },
            extensions=(
                {"timeout": request.extensions["timeout"]}
                if "timeout" in request.extensions
                else {}
            ),
        )

    def _handle_refresh_response(self, response: httpx.Response) -> None:
        raise_for_status(response)
        if response.status_code == 200:
            body = response.json()
            self.access_token = body["access_token"]
            self.refresh_token = body["refresh_token"]
            self.expires_at = body["expires_at"]
            if self.on_token_refresh:
                self.on_token_refresh(
                    self.access_token,
                    self.refresh_token,
                    self.expires_at,
                )

    def sync_auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        if self._is_expired() and self._can_refresh():
            with self._sync_refresh_lock:
                if self._is_expired() and self._can_refresh():
                    refresh_response = yield self._build_refresh_request(request)
                    refresh_response.read()
                    self._handle_refresh_response(refresh_response)

        request.headers["Authorization"] = f"Bearer {self.access_token}"
        yield request

    async def async_auth_flow(
        self, request: httpx.Request
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        if self._is_expired() and self._can_refresh():
            async with self._async_refresh_lock:
                if self._is_expired() and self._can_refresh():
                    refresh_response = yield self._build_refresh_request(request)
                    await refresh_response.aread()
                    self._handle_refresh_response(refresh_response)

        request.headers["Authorization"] = f"Bearer {self.access_token}"
        yield request


def build_authorization_url(
    client_id: str,
    redirect_uri: str,
    *,
    scopes: list[str] | None = None,
    state: str | None = None,
    approval_prompt: str = "auto",
) -> str:
    """Build an OAuth URL; persist and validate a random state in your callback."""
    params: dict[str, str] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "approval_prompt": approval_prompt,
    }
    if scopes:
        params["scope"] = ",".join(scopes)
    if state:
        params["state"] = state
    return f"{AUTHORIZE_URL}?{urlencode(params)}"


def _build_oauth_request(
    http_client: httpx.Client | httpx.AsyncClient,
    url: str,
    data: dict[str, str],
    timeout: httpx.Timeout | float | None,
) -> httpx.Request:
    request = http_client.build_request("POST", url, data=data, timeout=timeout)
    # Disabling client.auth alone does not remove default Authorization headers.
    request.headers.pop("Authorization", None)
    return request


def _post_oauth(
    url: str,
    data: dict[str, str],
    *,
    timeout: httpx.Timeout | float | None,
    http_client: httpx.Client | None,
    auth: httpx.BasicAuth | None = None,
) -> httpx.Response:
    with httpx.Client() if http_client is None else nullcontext(http_client) as client:
        request = _build_oauth_request(client, url, data, timeout)
        response = client.send(request, auth=auth, follow_redirects=False)
        raise_for_status(response)
        return response


async def _async_post_oauth(
    url: str,
    data: dict[str, str],
    *,
    timeout: httpx.Timeout | float | None,
    http_client: httpx.AsyncClient | None,
    auth: httpx.BasicAuth | None = None,
) -> httpx.Response:
    async with (
        httpx.AsyncClient() if http_client is None else nullcontext(http_client)
    ) as client:
        request = _build_oauth_request(client, url, data, timeout)
        response = await client.send(request, auth=auth, follow_redirects=False)
        raise_for_status(response)
        return response


def _parse_token_response(response: httpx.Response) -> TokenResponse:
    body = response.json()
    return TokenResponse(
        access_token=body["access_token"],
        refresh_token=body["refresh_token"],
        expires_at=body["expires_at"],
        expires_in=body["expires_in"],
        token_type=body["token_type"],
        scope=body.get("scope"),
        athlete=(
            SummaryAthlete.from_dict(body["athlete"])
            if body.get("athlete") is not None
            else None
        ),
    )


def exchange_token(
    client_id: str,
    client_secret: str,
    code: str,
    *,
    timeout: httpx.Timeout | float | None = 30.0,
    http_client: httpx.Client | None = None,
) -> TokenResponse:
    """Exchange an authorization code; a supplied HTTP client stays open."""
    response = _post_oauth(
        TOKEN_URL,
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
        },
        timeout=timeout,
        http_client=http_client,
    )
    return _parse_token_response(response)


def refresh_access_token(
    client_id: str,
    client_secret: str,
    refresh_token: str,
    *,
    timeout: httpx.Timeout | float | None = 30.0,
    http_client: httpx.Client | None = None,
) -> TokenResponse:
    """Refresh OAuth tokens; a supplied HTTP client stays open."""
    response = _post_oauth(
        TOKEN_URL,
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        timeout=timeout,
        http_client=http_client,
    )
    return _parse_token_response(response)


async def async_exchange_token(
    client_id: str,
    client_secret: str,
    code: str,
    *,
    timeout: httpx.Timeout | float | None = 30.0,
    http_client: httpx.AsyncClient | None = None,
) -> TokenResponse:
    """Asynchronously exchange a code; a supplied HTTP client stays open."""
    response = await _async_post_oauth(
        TOKEN_URL,
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
        },
        timeout=timeout,
        http_client=http_client,
    )
    return _parse_token_response(response)


async def async_refresh_access_token(
    client_id: str,
    client_secret: str,
    refresh_token: str,
    *,
    timeout: httpx.Timeout | float | None = 30.0,
    http_client: httpx.AsyncClient | None = None,
) -> TokenResponse:
    """Asynchronously refresh tokens; a supplied HTTP client stays open."""
    response = await _async_post_oauth(
        TOKEN_URL,
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        timeout=timeout,
        http_client=http_client,
    )
    return _parse_token_response(response)


def revoke_token(
    client_id: str,
    client_secret: str,
    token: str,
    *,
    token_type_hint: TokenTypeHint | None = None,
    timeout: httpx.Timeout | float | None = 30.0,
    http_client: httpx.Client | None = None,
) -> None:
    """Revoke an access or refresh token using Strava's oauth/revoke endpoint."""

    data = {"token": token}
    if token_type_hint is not None:
        data["token_type_hint"] = token_type_hint

    _post_oauth(
        REVOKE_URL,
        data,
        timeout=timeout,
        http_client=http_client,
        auth=httpx.BasicAuth(str(client_id), client_secret),
    )


async def async_revoke_token(
    client_id: str,
    client_secret: str,
    token: str,
    *,
    token_type_hint: TokenTypeHint | None = None,
    timeout: httpx.Timeout | float | None = 30.0,
    http_client: httpx.AsyncClient | None = None,
) -> None:
    """Asynchronously revoke a token; a supplied HTTP client stays open."""
    data = {"token": token}
    if token_type_hint is not None:
        data["token_type_hint"] = token_type_hint

    await _async_post_oauth(
        REVOKE_URL,
        data,
        timeout=timeout,
        http_client=http_client,
        auth=httpx.BasicAuth(str(client_id), client_secret),
    )


def deauthorize(
    access_token: str,
    *,
    client_id: str | None = None,
    client_secret: str | None = None,
    timeout: httpx.Timeout | float | None = 30.0,
    http_client: httpx.Client | None = None,
) -> None:
    """Deprecated compatibility helper for Strava's retiring deauthorize endpoint."""

    warnings.warn(
        "deauthorize() is deprecated; use revoke_token() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if client_id is not None or client_secret is not None:
        if client_id is None or client_secret is None:
            raise ValueError("client_id and client_secret must be provided together")
        revoke_token(
            client_id,
            client_secret,
            access_token,
            token_type_hint="access_token",
            timeout=timeout,
            http_client=http_client,
        )
        return

    _post_oauth(
        DEAUTHORIZE_URL,
        {"access_token": access_token},
        timeout=timeout,
        http_client=http_client,
    )
