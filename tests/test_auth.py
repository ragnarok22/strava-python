from __future__ import annotations

import time

import httpx
import pytest
import respx

from strava._auth import (
    AUTHORIZE_URL,
    DEAUTHORIZE_URL,
    REVOKE_URL,
    TOKEN_URL,
    OAuth2Auth,
    build_authorization_url,
    deauthorize,
    revoke_token,
)


class TestBuildAuthorizationUrl:
    def test_basic(self):
        url = build_authorization_url("12345", "http://localhost/callback")
        assert "client_id=12345" in url
        assert "redirect_uri=http" in url
        assert "response_type=code" in url
        assert AUTHORIZE_URL in url

    def test_with_scopes(self):
        url = build_authorization_url(
            "12345",
            "http://localhost/callback",
            scopes=["read", "activity:read_all"],
        )
        assert "scope=read%2Cactivity%3Aread_all" in url

    def test_with_state(self):
        url = build_authorization_url(
            "12345",
            "http://localhost/callback",
            state="my_state",
        )
        assert "state=my_state" in url

    def test_force_approval(self):
        url = build_authorization_url(
            "12345",
            "http://localhost/callback",
            approval_prompt="force",
        )
        assert "approval_prompt=force" in url


class TestOAuth2Auth:
    def test_adds_bearer_token(self):
        auth = OAuth2Auth("test_token")
        request = httpx.Request("GET", "https://example.com")
        flow = auth.sync_auth_flow(request)
        outgoing = next(flow)
        assert outgoing.headers["Authorization"] == "Bearer test_token"

    def test_not_expired_when_no_expiry(self):
        auth = OAuth2Auth("test_token")
        assert auth._is_expired() is False

    def test_expired_when_past(self):
        auth = OAuth2Auth("test_token", expires_at=0)
        assert auth._is_expired() is True

    def test_not_expired_when_future(self):
        auth = OAuth2Auth("test_token", expires_at=int(time.time()) + 3600)
        assert auth._is_expired() is False

    def test_can_refresh(self):
        auth = OAuth2Auth(
            "test_token",
            client_id="id",
            client_secret="secret",
            refresh_token="refresh",
        )
        assert auth._can_refresh() is True

    def test_cannot_refresh_without_credentials(self):
        auth = OAuth2Auth("test_token")
        assert auth._can_refresh() is False

    @respx.mock
    def test_auto_refresh_on_expired(self):
        respx.post(TOKEN_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "access_token": "new_token",
                    "refresh_token": "new_refresh",
                    "expires_at": int(time.time()) + 21600,
                    "expires_in": 21600,
                    "token_type": "Bearer",
                },
            )
        )

        refreshed = {}

        def on_refresh(access, refresh, expires):
            refreshed["access_token"] = access
            refreshed["refresh_token"] = refresh

        auth = OAuth2Auth(
            "old_token",
            client_id="id",
            client_secret="secret",
            refresh_token="old_refresh",
            expires_at=0,
            on_token_refresh=on_refresh,
        )

        with httpx.Client(auth=auth) as client:
            respx.get("https://example.com/test").mock(
                return_value=httpx.Response(200, json={"ok": True})
            )
            response = client.get("https://example.com/test")
            assert response.status_code == 200

        assert auth.access_token == "new_token"
        assert auth.refresh_token == "new_refresh"
        assert refreshed["access_token"] == "new_token"


class TestRevokeToken:
    @respx.mock
    def test_revoke_token_uses_basic_auth(self):
        route = respx.post(REVOKE_URL).mock(return_value=httpx.Response(200))

        revoke_token(
            "12345",
            "secret",
            "token",
            token_type_hint="access_token",
        )

        request = route.calls.last.request
        assert request.headers["Authorization"] == "Basic MTIzNDU6c2VjcmV0"
        assert request.content == b"token=token&token_type_hint=access_token"

    @respx.mock
    def test_deauthorize_with_credentials_uses_revoke(self):
        route = respx.post(REVOKE_URL).mock(return_value=httpx.Response(200))

        with pytest.warns(DeprecationWarning):
            deauthorize("token", client_id="12345", client_secret="secret")

        request = route.calls.last.request
        assert request.headers["Authorization"] == "Basic MTIzNDU6c2VjcmV0"
        assert request.content == b"token=token&token_type_hint=access_token"

    def test_deauthorize_requires_both_credentials(self):
        with pytest.warns(DeprecationWarning), pytest.raises(ValueError):
            deauthorize("token", client_id="12345")

    @respx.mock
    def test_deauthorize_without_credentials_uses_legacy_endpoint(self):
        route = respx.post(DEAUTHORIZE_URL).mock(return_value=httpx.Response(200))

        with pytest.warns(DeprecationWarning):
            deauthorize("token")

        request = route.calls.last.request
        assert request.content == b"access_token=token"
