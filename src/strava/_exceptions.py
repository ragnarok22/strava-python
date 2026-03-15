from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import httpx


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

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response: httpx.Response | None = None,
        fault: dict[str, Any] | None = None,
        limit_15min: int | None = None,
        limit_daily: int | None = None,
        usage_15min: int | None = None,
        usage_daily: int | None = None,
    ) -> None:
        super().__init__(
            message, status_code=status_code, response=response, fault=fault
        )
        self.limit_15min = limit_15min
        self.limit_daily = limit_daily
        self.usage_15min = usage_15min
        self.usage_daily = usage_daily


class ValidationError(StravaError):
    """400/422 Bad Request."""


class ServerError(StravaError):
    """5xx Server Error."""


def _parse_rate_limits(response: httpx.Response) -> dict[str, int | None]:
    result: dict[str, int | None] = {
        "limit_15min": None,
        "limit_daily": None,
        "usage_15min": None,
        "usage_daily": None,
    }
    limit_header = response.headers.get("X-RateLimit-Limit", "")
    usage_header = response.headers.get("X-RateLimit-Usage", "")
    if limit_header:
        parts = limit_header.split(",")
        if len(parts) >= 2:
            result["limit_15min"] = int(parts[0].strip())
            result["limit_daily"] = int(parts[1].strip())
    if usage_header:
        parts = usage_header.split(",")
        if len(parts) >= 2:
            result["usage_15min"] = int(parts[0].strip())
            result["usage_daily"] = int(parts[1].strip())
    return result


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
        rate_limits = _parse_rate_limits(response)
        raise RateLimitError(message, **kwargs, **rate_limits)
    elif response.status_code in (400, 422):
        raise ValidationError(message, **kwargs)
    elif response.status_code >= 500:
        raise ServerError(message, **kwargs)
    else:
        raise StravaError(message, **kwargs)
