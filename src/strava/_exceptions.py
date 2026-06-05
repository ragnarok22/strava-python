from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import httpx


def _parse_header_int(value: str) -> int | None:
    try:
        return int(value.strip())
    except ValueError:
        return None


def _parse_header_pair(header: str) -> tuple[int | None, int | None]:
    """Parse a comma-separated pair of ints from a rate limit header."""
    if not header:
        return None, None
    parts = header.split(",")
    first = _parse_header_int(parts[0]) if len(parts) >= 1 else None
    second = _parse_header_int(parts[1]) if len(parts) >= 2 else None
    return first, second


@dataclass(slots=True)
class RateLimitInfo:
    """Rate limit state extracted from Strava API response headers.

    Updated after every API call and accessible via ``client.rate_limits``.
    """

    limit_15min: int | None = None
    limit_daily: int | None = None
    usage_15min: int | None = None
    usage_daily: int | None = None
    read_limit_15min: int | None = None
    read_limit_daily: int | None = None
    read_usage_15min: int | None = None
    read_usage_daily: int | None = None

    @property
    def exceeded(self) -> bool:
        """True if any usage value meets or exceeds its corresponding limit."""
        for usage, limit in (
            (self.usage_15min, self.limit_15min),
            (self.usage_daily, self.limit_daily),
            (self.read_usage_15min, self.read_limit_15min),
            (self.read_usage_daily, self.read_limit_daily),
        ):
            if usage is not None and limit is not None and usage >= limit:
                return True
        return False


def extract_rate_limits(response: httpx.Response) -> RateLimitInfo:
    """Build a RateLimitInfo from the four Strava rate-limit header pairs."""
    headers = response.headers
    l15, ld = _parse_header_pair(headers.get("X-RateLimit-Limit", ""))
    u15, ud = _parse_header_pair(headers.get("X-RateLimit-Usage", ""))
    rl15, rld = _parse_header_pair(headers.get("X-ReadRateLimit-Limit", ""))
    ru15, rud = _parse_header_pair(headers.get("X-ReadRateLimit-Usage", ""))
    return RateLimitInfo(
        limit_15min=l15,
        limit_daily=ld,
        usage_15min=u15,
        usage_daily=ud,
        read_limit_15min=rl15,
        read_limit_daily=rld,
        read_usage_15min=ru15,
        read_usage_daily=rud,
    )


class StravaError(Exception):
    message: str
    status_code: int | None
    response: httpx.Response | None
    fault: dict[str, Any] | None

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response: httpx.Response | None = None,
        fault: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response
        self.fault = fault


class AuthenticationError(StravaError):
    """401 Unauthorized."""


class TokenExpiredError(AuthenticationError):
    """401 specifically due to expired token."""


class AuthorizationError(StravaError):
    """403 Forbidden."""


class NotFoundError(StravaError):
    """404 Not Found."""


class RateLimitError(StravaError):
    """429 Too Many Requests."""

    limit_15min: int | None
    limit_daily: int | None
    usage_15min: int | None
    usage_daily: int | None
    read_limit_15min: int | None
    read_limit_daily: int | None
    read_usage_15min: int | None
    read_usage_daily: int | None

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response: httpx.Response | None = None,
        fault: dict[str, Any] | None = None,
        rate_limit_info: RateLimitInfo | None = None,
    ) -> None:
        super().__init__(
            message, status_code=status_code, response=response, fault=fault
        )
        info = rate_limit_info or RateLimitInfo()
        self.limit_15min = info.limit_15min
        self.limit_daily = info.limit_daily
        self.usage_15min = info.usage_15min
        self.usage_daily = info.usage_daily
        self.read_limit_15min = info.read_limit_15min
        self.read_limit_daily = info.read_limit_daily
        self.read_usage_15min = info.read_usage_15min
        self.read_usage_daily = info.read_usage_daily


class ValidationError(StravaError):
    """400/422 Bad Request."""


class ServerError(StravaError):
    """5xx Server Error."""


def raise_for_status(response: httpx.Response) -> None:
    if response.status_code < 400:
        return

    fault: dict[str, Any] | None = None
    message = f"HTTP {response.status_code}"
    try:
        body = response.json()
        if isinstance(body, dict):
            fault = body
            message = body.get("message", message)
    except Exception:
        message = response.text or message

    kwargs: dict[str, Any] = {
        "status_code": response.status_code,
        "response": response,
        "fault": fault,
    }

    if response.status_code == 401:
        raise AuthenticationError(message, **kwargs)
    elif response.status_code == 403:
        raise AuthorizationError(message, **kwargs)
    elif response.status_code == 404:
        raise NotFoundError(message, **kwargs)
    elif response.status_code == 429:
        info = extract_rate_limits(response)
        raise RateLimitError(message, **kwargs, rate_limit_info=info)
    elif response.status_code in (400, 422):
        raise ValidationError(message, **kwargs)
    elif response.status_code >= 500:
        raise ServerError(message, **kwargs)
    else:
        raise StravaError(message, **kwargs)
