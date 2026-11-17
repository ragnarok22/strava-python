from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor

import anyio
import httpx
import pytest

from strava import AuthenticationError
from strava._auth import TOKEN_URL, OAuth2Auth, TokenResponse
from tests._helpers import invoke

RESOURCE_URL = "https://www.strava.com/api/v3/athlete"
TOKEN_BODY = {
    "access_token": "rotated_access",
    "refresh_token": "rotated_refresh",
    "expires_at": 9999999999,
    "expires_in": 21600,
    "token_type": "Bearer",
}


def expired_auth(**kwargs):
    return OAuth2Auth(
        "expired_access",
        client_id="12345",
        client_secret="test_secret",
        refresh_token="old_refresh",
        expires_at=0,
        **kwargs,
    )


def test_token_response_repr_excludes_both_secrets():
    tokens = TokenResponse(**TOKEN_BODY)

    assert tokens.access_token == "rotated_access"
    assert tokens.refresh_token == "rotated_refresh"
    assert "rotated_access" not in repr(tokens)
    assert "rotated_refresh" not in repr(tokens)
    assert "expires_at=9999999999" in repr(tokens)


def test_sync_concurrent_requests_share_one_refresh(monkeypatch):
    callbacks = []
    auth = expired_auth(on_token_refresh=lambda *args: callbacks.append(args))
    barrier = threading.Barrier(4, timeout=5)
    thread_state = threading.local()
    is_expired = auth._is_expired
    refreshes = []
    requests = []

    def check_expiry():
        expired = is_expired()
        if not getattr(thread_state, "checked", False):
            thread_state.checked = True
            barrier.wait()
        return expired

    monkeypatch.setattr(auth, "_is_expired", check_expiry)

    def handler(request):
        if str(request.url) == TOKEN_URL:
            refreshes.append(request)
            return httpx.Response(200, json=TOKEN_BODY)
        requests.append(request)
        return httpx.Response(200)

    with (
        httpx.Client(auth=auth, transport=httpx.MockTransport(handler)) as client,
        ThreadPoolExecutor(max_workers=4) as executor,
    ):
        futures = [executor.submit(client.get, RESOURCE_URL) for _ in range(4)]
        assert [future.result(timeout=5).status_code for future in futures] == [200] * 4

    assert len(refreshes) == 1
    assert len(requests) == 4
    assert all(
        request.headers["Authorization"] == "Bearer rotated_access"
        for request in requests
    )
    assert callbacks == [("rotated_access", "rotated_refresh", 9999999999)]


@pytest.mark.asyncio
async def test_async_concurrent_requests_share_one_refresh(monkeypatch):
    callbacks = []
    auth = expired_auth(on_token_refresh=lambda *args: callbacks.append(args))
    all_checked = anyio.Event()
    release_refresh = anyio.Event()
    checked_tasks = set()
    is_expired = auth._is_expired
    refreshes = []
    requests = []

    def check_expiry():
        expired = is_expired()
        checked_tasks.add(anyio.get_current_task().id)
        if len(checked_tasks) == 4:
            all_checked.set()
        return expired

    monkeypatch.setattr(auth, "_is_expired", check_expiry)

    async def handler(request):
        if str(request.url) == TOKEN_URL:
            refreshes.append(request)
            await release_refresh.wait()
            return httpx.Response(200, json=TOKEN_BODY)
        requests.append(request)
        return httpx.Response(200)

    async with httpx.AsyncClient(
        auth=auth, transport=httpx.MockTransport(handler)
    ) as client:
        with anyio.fail_after(5):
            async with anyio.create_task_group() as group:
                for _ in range(4):
                    group.start_soon(client.get, RESOURCE_URL)
                await all_checked.wait()
                release_refresh.set()

    assert len(refreshes) == 1
    assert len(requests) == 4
    assert all(
        request.headers["Authorization"] == "Bearer rotated_access"
        for request in requests
    )
    assert callbacks == [("rotated_access", "rotated_refresh", 9999999999)]


@pytest.mark.asyncio
async def test_cancelled_refresh_releases_lock_for_waiter():
    auth = expired_auth()
    refresh_started = anyio.Event()
    waiter_started = anyio.Event()
    leader_scope = anyio.CancelScope()
    refreshes = []
    responses = []

    async def handler(request):
        if str(request.url) == TOKEN_URL:
            refreshes.append(request)
            if len(refreshes) == 1:
                refresh_started.set()
                await anyio.Event().wait()
            return httpx.Response(200, json=TOKEN_BODY)
        return httpx.Response(200)

    async with httpx.AsyncClient(
        auth=auth, transport=httpx.MockTransport(handler)
    ) as client:

        async def leader():
            with leader_scope:
                await client.get(RESOURCE_URL)

        async def waiter():
            waiter_started.set()
            responses.append(await client.get(RESOURCE_URL))

        with anyio.fail_after(5):
            async with anyio.create_task_group() as group:
                group.start_soon(leader)
                await refresh_started.wait()
                group.start_soon(waiter)
                await waiter_started.wait()
                leader_scope.cancel()

    assert len(refreshes) == 2
    assert len(responses) == 1
    assert responses[0].status_code == 200
    assert auth.access_token == "rotated_access"


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("failure", ["http_error", "transport_error", "callback_error"])
async def test_failed_refresh_releases_lock_and_can_retry(asynchronous, failure):
    refreshes = []
    callbacks = []

    def on_refresh(*args):
        callbacks.append(args)
        if failure == "callback_error" and len(callbacks) == 1:
            raise RuntimeError("Token persistence failed")

    def handler(request):
        if str(request.url) == TOKEN_URL:
            refreshes.append(request)
            if len(refreshes) == 1:
                if failure == "http_error":
                    return httpx.Response(401, json={"message": "Refresh rejected"})
                if failure == "transport_error":
                    raise httpx.ReadTimeout("Refresh timed out")
            return httpx.Response(200, json=TOKEN_BODY)
        return httpx.Response(200)

    auth = expired_auth(on_token_refresh=on_refresh)
    client_cls = httpx.AsyncClient if asynchronous else httpx.Client
    client = client_cls(auth=auth, transport=httpx.MockTransport(handler))
    error_cls = {
        "http_error": AuthenticationError,
        "transport_error": httpx.ReadTimeout,
        "callback_error": RuntimeError,
    }[failure]
    try:
        with pytest.raises(error_cls):
            await invoke(client.get, RESOURCE_URL)

        lock = auth._async_refresh_lock if asynchronous else auth._sync_refresh_lock
        assert not lock.locked()
        if failure != "callback_error":
            assert auth.access_token == "expired_access"
            assert auth.refresh_token == "old_refresh"
            assert callbacks == []
        auth.expires_at = 0

        with anyio.fail_after(5):
            response = await invoke(client.get, RESOURCE_URL)
        assert response.status_code == 200
        assert len(refreshes) == 2
    finally:
        if asynchronous:
            await client.aclose()
        else:
            client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("timeout", [None, 2.5, httpx.Timeout(7.0, connect=1.0)])
async def test_refresh_inherits_originating_request_timeout(asynchronous, timeout):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=TOKEN_BODY)

    client_cls = httpx.AsyncClient if asynchronous else httpx.Client
    client = client_cls(
        auth=expired_auth(),
        transport=httpx.MockTransport(handler),
        timeout=99.0,
    )
    try:
        response = await invoke(client.get, RESOURCE_URL, timeout=timeout)
        assert response.status_code == 200
    finally:
        if asynchronous:
            await client.aclose()
        else:
            client.close()

    assert [str(request.url) for request in requests] == [TOKEN_URL, RESOURCE_URL]
    assert all(
        request.extensions["timeout"] == httpx.Timeout(timeout).as_dict()
        for request in requests
    )
    assert "Authorization" not in requests[0].headers
