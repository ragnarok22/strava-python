# strava

[![CI](https://github.com/ragnarok22/strava-python/actions/workflows/ci.yml/badge.svg)](https://github.com/ragnarok22/strava-python/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ragnarok22/strava-python/graph/badge.svg?token=1b94OIiVCD)](https://codecov.io/gh/ragnarok22/strava-python)
[![PyPI](https://img.shields.io/pypi/v/strava)](https://pypi.org/project/strava/)
[![Python](https://img.shields.io/pypi/pyversions/strava)](https://pypi.org/project/strava/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/strava)
[![License](https://img.shields.io/github/license/ragnarok22/strava-python)](https://github.com/ragnarok22/strava-python/blob/main/LICENSE)

A fully typed Python SDK for the [Strava API v3](https://developers.strava.com/docs/reference/).
Supports Python 3.11–3.14, sync and async [HTTPX](https://www.python-httpx.org/)
clients, typed dataclass models, automatic OAuth refresh, and lazy pagination.

## Installation

```bash
pip install strava
```

## Quick Start

[Register an application](https://developers.strava.com/docs/getting-started/#account)
and obtain an access token with the scopes your app needs. For this example,
request `read` and `activity:read` (`activity:read_all` to include Only Me
activities). Set `STRAVA_ACCESS_TOKEN` in your environment; do not put real tokens
in source code.

```python
import os

from strava import Strava

with Strava(access_token=os.environ["STRAVA_ACCESS_TOKEN"]) as client:
    athlete = client.athletes.retrieve_authenticated()
    print(f"{athlete.firstname} {athlete.lastname}")

    # Fetch at most 10 activities, not the athlete's entire history.
    activities = client.activities.list(per_page=10).collect(max_items=10)
    for activity in activities:
        print(f"{activity.name} - {activity.distance}m")
        print(activity.device_name)  # Recording device, when supplied by Strava
```

`per_page` sets the **page size**, not a total result limit. Iterating
`client.activities.list(per_page=10)` without a bound continues fetching pages.
Use `collect(max_items=10)` to limit the returned results.

### Async

```python
import asyncio
import os

from strava import AsyncStrava


async def main() -> None:
    async with AsyncStrava(access_token=os.environ["STRAVA_ACCESS_TOKEN"]) as client:
        athlete = await client.athletes.retrieve_authenticated()
        activities = await client.activities.list(per_page=10).collect(max_items=10)
        print(athlete.firstname, len(activities))


asyncio.run(main())
```

Creating an async paginator does not need `await`; collecting it does. Keep the
client open while consuming a paginator.

## Next Steps

- [Usage guide](https://github.com/ragnarok22/strava-python/blob/main/docs/usage.md): secure OAuth with one-time `state` validation,
  token storage and refresh, custom HTTPX clients, pagination, uploads, and webhooks.
- [Practical API reference](https://github.com/ragnarok22/strava-python/blob/main/docs/api.md): all 34 endpoints across 10 resource
  groups, return types, scopes, units, errors, and rate limits.
- [Migration guide](https://github.com/ragnarok22/strava-python/blob/main/docs/migration.md): compatibility changes and Strava's
  announced 2026–2027 API changes.

The API covers activities, athletes, clubs, gear, routes, segments, segment
efforts, streams, uploads, and webhook subscriptions. Both clients expose the
same resource methods. Activity creation, updates, and uploads support
[`visibility` and activity `tags`](https://github.com/ragnarok22/strava-python/blob/main/docs/usage.md#activity-visibility-and-tags).

### OAuth and HTTP configuration

Use `build_authorization_url()` with unpredictable, server-stored `state`, then
validate and consume that state before exchanging the callback code. Do not log
tokens or client secrets. The [OAuth example](https://github.com/ragnarok22/strava-python/blob/main/docs/usage.md#oauth-authorization)
shows the required application-side checks.

The SDK provides `exchange_token()`, `refresh_access_token()`, and `revoke_token()`,
plus their `async_` counterparts. Helpers accept configurable `timeout` and
caller-owned `http_client` arguments. For automatic refresh, give `Strava` or
`AsyncStrava` the refresh credentials, expiration timestamp, and a token
persistence callback.

Pass a custom HTTPX client for connection pooling, transports, or event hooks.
The SDK controls request authentication, API `base_url`, and `timeout` without
mutating or closing your HTTPX client. See
[HTTP client ownership and configuration](https://github.com/ragnarok22/strava-python/blob/main/docs/usage.md#http-client-ownership-and-configuration).

### Errors and rate limits

HTTP API errors raise `StravaError` subclasses; HTTPX transport and timeout
exceptions propagate separately. `client.rate_limits` exposes the most recent
rate-limit headers, including an `exceeded` flag. The SDK does **not** retry or
sleep automatically. See [errors](https://github.com/ragnarok22/strava-python/blob/main/docs/api.md#errors) and
[rate limits](https://github.com/ragnarok22/strava-python/blob/main/docs/api.md#rate-limits) for handling guidance.

## Compatibility Notes

- Activity and athlete endpoint IDs accept `int | str`. Models preserve both
  `id` and optional `id_str` without synthesizing either. Python integers retain
  64-bit IDs exactly; prefer strings at JavaScript boundaries. See
  [ID migration](https://github.com/ragnarok22/strava-python/blob/main/docs/migration.md#activity-and-athlete-identifiers).
- The default API URL remains `https://www.strava.com/api/v3`. Strava's announced
  `https://api-v3.strava.com` host becomes available January 4, 2027; the SDK
  does not switch automatically.
- Strava retired club activity/member/admin endpoints September 1, 2026.
  `segments.explore()` now requires approved Extended Access.
- `deauthorize()` is deprecated ahead of its June 1, 2027 retirement. Use
  `revoke_token()` or `async_revoke_token()` for new code.

See the [migration guide](https://github.com/ragnarok22/strava-python/blob/main/docs/migration.md) before upgrading existing code and
the [changelog](https://github.com/ragnarok22/strava-python/blob/main/CHANGELOG.md) for release history.

## Development and Contributing

```bash
uv sync
make help
```

Read [CONTRIBUTING.md](https://github.com/ragnarok22/strava-python/blob/main/CONTRIBUTING.md) for targeted validation commands, testing
guidelines, and the Python 3.11–3.14 CI matrix.

Found a bug? [Open an issue](https://github.com/ragnarok22/strava-python/issues/new?template=bug_report.yml).
Have an idea? [Request a feature](https://github.com/ragnarok22/strava-python/issues/new?template=feature_request.yml).
