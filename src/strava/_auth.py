from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, Generator
from urllib.parse import urlencode

import httpx

TOKEN_URL = "https://www.strava.com/oauth/token"
AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
DEAUTHORIZE_URL = "https://www.strava.com/oauth/deauthorize"


@dataclass(slots=True)
class TokenResponse:
    access_token: str
    refresh_token: str
    expires_at: int
    expires_in: int
    token_type: str


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

    def _is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() >= self.expires_at

    def _can_refresh(self) -> bool:
        return bool(self.client_id and self.client_secret and self.refresh_token)

    def _build_refresh_request(self) -> httpx.Request:
        return httpx.Request(
            "POST",
            TOKEN_URL,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            },
        )

    def _handle_refresh_response(self, response: httpx.Response) -> None:
        response.read()
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
            refresh_response = yield self._build_refresh_request()
            self._handle_refresh_response(refresh_response)

        request.headers["Authorization"] = f"Bearer {self.access_token}"
        yield request

    async def async_auth_flow(
        self, request: httpx.Request
    ) -> Any:
        if self._is_expired() and self._can_refresh():
            refresh_response = yield self._build_refresh_request()
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


def exchange_token(
    client_id: str,
    client_secret: str,
    code: str,
) -> TokenResponse:
    response = httpx.post(
        TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
        },
    )
    response.raise_for_status()
    body = response.json()
    return TokenResponse(
        access_token=body["access_token"],
        refresh_token=body["refresh_token"],
        expires_at=body["expires_at"],
        expires_in=body["expires_in"],
        token_type=body["token_type"],
    )


def refresh_access_token(
    client_id: str,
    client_secret: str,
    refresh_token: str,
) -> TokenResponse:
    response = httpx.post(
        TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
    )
    response.raise_for_status()
    body = response.json()
    return TokenResponse(
        access_token=body["access_token"],
        refresh_token=body["refresh_token"],
        expires_at=body["expires_at"],
        expires_in=body["expires_in"],
        token_type=body["token_type"],
    )


def deauthorize(access_token: str) -> None:
    response = httpx.post(
        DEAUTHORIZE_URL,
        data={"access_token": access_token},
    )
    response.raise_for_status()
