from __future__ import annotations

from strava.models.webhooks import WebhookSubscription
from strava.resources._base import AsyncAPIResource, SyncAPIResource


class Webhooks(SyncAPIResource):
    """Manage webhook subscriptions using application credentials, not athlete tokens."""

    def create(
        self,
        *,
        client_id: str,
        client_secret: str,
        callback_url: str,
        verify_token: str,
    ) -> WebhookSubscription:
        """Create a subscription after Strava validates the callback URL."""
        response = self._client._request(
            "POST",
            "/push_subscriptions",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "callback_url": callback_url,
                "verify_token": verify_token,
            },
            auth=None,
        )
        return WebhookSubscription.from_dict(response.json())

    def list(self, *, client_id: str, client_secret: str) -> list[WebhookSubscription]:
        """List the application's subscriptions (Strava permits one per application)."""
        response = self._client._request(
            "GET",
            "/push_subscriptions",
            params={"client_id": client_id, "client_secret": client_secret},
            auth=None,
        )
        return [WebhookSubscription.from_dict(item) for item in response.json()]

    def delete(
        self, subscription_id: int, *, client_id: str, client_secret: str
    ) -> None:
        """Delete a subscription; a successful response has no body."""
        self._client._request(
            "DELETE",
            f"/push_subscriptions/{subscription_id}",
            params={"client_id": client_id, "client_secret": client_secret},
            auth=None,
        )


class AsyncWebhooks(AsyncAPIResource):
    """Asynchronously manage webhook subscriptions using application credentials."""

    async def create(
        self,
        *,
        client_id: str,
        client_secret: str,
        callback_url: str,
        verify_token: str,
    ) -> WebhookSubscription:
        """Create a subscription after Strava validates the callback URL."""
        response = await self._client._request(
            "POST",
            "/push_subscriptions",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "callback_url": callback_url,
                "verify_token": verify_token,
            },
            auth=None,
        )
        return WebhookSubscription.from_dict(response.json())

    async def list(
        self, *, client_id: str, client_secret: str
    ) -> list[WebhookSubscription]:
        """List the application's subscriptions (Strava permits one per application)."""
        response = await self._client._request(
            "GET",
            "/push_subscriptions",
            params={"client_id": client_id, "client_secret": client_secret},
            auth=None,
        )
        return [WebhookSubscription.from_dict(item) for item in response.json()]

    async def delete(
        self, subscription_id: int, *, client_id: str, client_secret: str
    ) -> None:
        """Delete a subscription; a successful response has no body."""
        await self._client._request(
            "DELETE",
            f"/push_subscriptions/{subscription_id}",
            params={"client_id": client_id, "client_secret": client_secret},
            auth=None,
        )
