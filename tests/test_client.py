from __future__ import annotations

import httpx
import pytest
import respx

from strava import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    RateLimitInfo,
    ServerError,
    Strava,
    ValidationError,
)


BASE = "https://www.api-v3.strava.com"


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
                    "X-ReadRateLimit-Limit": "100,1000",
                    "X-ReadRateLimit-Usage": "101,200",
                },
            )
        )
        with pytest.raises(RateLimitError) as exc_info:
            client.athletes.retrieve_authenticated()
        err = exc_info.value
        assert err.limit_15min == 600
        assert err.limit_daily == 30000
        assert err.usage_15min == 601
        assert err.usage_daily == 500
        assert err.read_limit_15min == 100
        assert err.read_limit_daily == 1000
        assert err.read_usage_15min == 101
        assert err.read_usage_daily == 200

    @respx.mock
    def test_429_with_malformed_rate_limit_headers_still_raises(self, client: Strava):
        respx.get(f"{BASE}/athlete").mock(
            return_value=httpx.Response(
                429,
                json={"message": "Rate Limit Exceeded"},
                headers={
                    "X-RateLimit-Limit": "600,not-an-int",
                    "X-RateLimit-Usage": "bad,500",
                    "X-ReadRateLimit-Limit": "100",
                    "X-ReadRateLimit-Usage": "malformed",
                },
            )
        )
        with pytest.raises(RateLimitError) as exc_info:
            client.athletes.retrieve_authenticated()

        err = exc_info.value
        assert err.limit_15min == 600
        assert err.limit_daily is None
        assert err.usage_15min is None
        assert err.usage_daily == 500
        assert err.read_limit_15min == 100
        assert err.read_limit_daily is None
        assert err.read_usage_15min is None
        assert err.read_usage_daily is None

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


class TestRateLimitTracking:
    @respx.mock
    def test_rate_limits_updated_on_success(self, client: Strava):
        respx.get(f"{BASE}/athlete").mock(
            return_value=httpx.Response(
                200,
                json={"id": 1, "firstname": "Test"},
                headers={
                    "X-RateLimit-Limit": "600,30000",
                    "X-RateLimit-Usage": "42,100",
                    "X-ReadRateLimit-Limit": "100,1000",
                    "X-ReadRateLimit-Usage": "10,50",
                },
            )
        )
        client.athletes.retrieve_authenticated()
        rl = client.rate_limits
        assert rl.limit_15min == 600
        assert rl.limit_daily == 30000
        assert rl.usage_15min == 42
        assert rl.usage_daily == 100
        assert rl.read_limit_15min == 100
        assert rl.read_limit_daily == 1000
        assert rl.read_usage_15min == 10
        assert rl.read_usage_daily == 50

    @respx.mock
    def test_rate_limits_with_malformed_headers_keep_invalid_fields_empty(
        self, client: Strava
    ):
        respx.get(f"{BASE}/athlete").mock(
            return_value=httpx.Response(
                200,
                json={"id": 1, "firstname": "Test"},
                headers={
                    "X-RateLimit-Limit": "600,not-an-int",
                    "X-RateLimit-Usage": "bad,500",
                    "X-ReadRateLimit-Limit": "100",
                    "X-ReadRateLimit-Usage": "malformed",
                },
            )
        )
        client.athletes.retrieve_authenticated()

        rl = client.rate_limits
        assert rl.limit_15min == 600
        assert rl.limit_daily is None
        assert rl.usage_15min is None
        assert rl.usage_daily == 500
        assert rl.read_limit_15min == 100
        assert rl.read_limit_daily is None
        assert rl.read_usage_15min is None
        assert rl.read_usage_daily is None

    @respx.mock
    def test_rate_limits_updated_on_error(self, client: Strava):
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
        with pytest.raises(RateLimitError):
            client.athletes.retrieve_authenticated()
        rl = client.rate_limits
        assert rl.usage_15min == 601

    def test_rate_limits_default_empty(self, client: Strava):
        rl = client.rate_limits
        assert rl.limit_15min is None
        assert rl.usage_15min is None
        assert not rl.exceeded


class TestRateLimitInfo:
    def test_exceeded_when_over_overall_limit(self):
        info = RateLimitInfo(limit_15min=600, usage_15min=600)
        assert info.exceeded is True

    def test_exceeded_when_over_daily_limit(self):
        info = RateLimitInfo(limit_daily=30000, usage_daily=30001)
        assert info.exceeded is True

    def test_exceeded_when_over_read_limit(self):
        info = RateLimitInfo(read_limit_15min=100, read_usage_15min=100)
        assert info.exceeded is True

    def test_not_exceeded_when_under(self):
        info = RateLimitInfo(
            limit_15min=600, usage_15min=42, limit_daily=30000, usage_daily=100
        )
        assert info.exceeded is False

    def test_not_exceeded_when_empty(self):
        info = RateLimitInfo()
        assert info.exceeded is False


class TestContextManager:
    def test_sync_context_manager(self):
        with Strava(access_token="test") as client:
            assert client is not None
