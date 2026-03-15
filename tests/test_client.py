from __future__ import annotations

import httpx
import pytest
import respx

from strava import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    Strava,
    ValidationError,
)


BASE = "https://www.strava.com/api/v3"


@pytest.fixture
def client():
    with Strava(access_token="test_token") as c:
        yield c


class TestErrorHandling:
    @respx.mock
    def test_401_raises_authentication_error(self, client: Strava):
        respx.get(f"{BASE}/athlete").mock(
            return_value=httpx.Response(
                401, json={"message": "Authorization Error", "errors": []}
            )
        )
        with pytest.raises(AuthenticationError) as exc_info:
            client.athletes.retrieve_authenticated()
        assert exc_info.value.status_code == 401

    @respx.mock
    def test_404_raises_not_found(self, client: Strava):
        respx.get(f"{BASE}/activities/999").mock(
            return_value=httpx.Response(
                404, json={"message": "Resource Not Found", "errors": []}
            )
        )
        with pytest.raises(NotFoundError):
            client.activities.retrieve(999)

    @respx.mock
    def test_429_raises_rate_limit(self, client: Strava):
        respx.get(f"{BASE}/athlete").mock(
            return_value=httpx.Response(
                429,
                json={"message": "Rate Limit Exceeded"},
                headers={
                    "X-RateLimit-Limit": "600,30000",
                    "X-RateLimit-Usage": "601,500",
                },
            )
        )
        with pytest.raises(RateLimitError) as exc_info:
            client.athletes.retrieve_authenticated()
        err = exc_info.value
        assert err.limit_15min == 600
        assert err.limit_daily == 30000
        assert err.usage_15min == 601

    @respx.mock
    def test_400_raises_validation_error(self, client: Strava):
        respx.post(f"{BASE}/activities").mock(
            return_value=httpx.Response(400, json={"message": "Bad Request"})
        )
        with pytest.raises(ValidationError):
            client.activities.create(
                name="Test",
                sport_type="Run",
                start_date_local="2024-01-01T00:00:00Z",
                elapsed_time=3600,
            )

    @respx.mock
    def test_500_raises_server_error(self, client: Strava):
        respx.get(f"{BASE}/athlete").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(ServerError):
            client.athletes.retrieve_authenticated()


class TestClientResources:
    def test_has_all_resources(self, client: Strava):
        assert client.activities is not None
        assert client.athletes is not None
        assert client.clubs is not None
        assert client.gear is not None
        assert client.routes is not None
        assert client.segments is not None
        assert client.segment_efforts is not None
        assert client.streams is not None
        assert client.uploads is not None


class TestContextManager:
    def test_sync_context_manager(self):
        with Strava(access_token="test") as client:
            assert client is not None
