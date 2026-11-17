"""Static OAuth consumer contracts; never network-executed."""

from __future__ import annotations

from typing import assert_type

import httpx

from strava import (
    TokenResponse,
    async_exchange_token,
    async_refresh_access_token,
    async_revoke_token,
    deauthorize,
    exchange_token,
    refresh_access_token,
    revoke_token,
)


def check_sync_oauth(client: httpx.Client) -> None:
    assert_type(exchange_token("id", "secret", "code"), TokenResponse)
    assert_type(
        exchange_token(
            "id", "secret", "code", timeout=httpx.Timeout(5), http_client=client
        ),
        TokenResponse,
    )
    assert_type(
        refresh_access_token(
            "id", "secret", "refresh", timeout=None, http_client=client
        ),
        TokenResponse,
    )
    revoke_token(
        "id",
        "secret",
        "token",
        token_type_hint="refresh_token",
        timeout=5.0,
        http_client=client,
    )
    deauthorize("access", timeout=5.0, http_client=client)
    deauthorize(
        "access",
        client_id="id",
        client_secret="secret",
        timeout=None,
        http_client=client,
    )


async def check_async_oauth(client: httpx.AsyncClient) -> None:
    assert_type(await async_exchange_token("id", "secret", "code"), TokenResponse)
    assert_type(
        await async_exchange_token(
            "id", "secret", "code", timeout=httpx.Timeout(5), http_client=client
        ),
        TokenResponse,
    )
    assert_type(
        await async_refresh_access_token(
            "id", "secret", "refresh", timeout=None, http_client=client
        ),
        TokenResponse,
    )
    await async_revoke_token(
        "id",
        "secret",
        "token",
        token_type_hint="access_token",
        timeout=5.0,
        http_client=client,
    )
