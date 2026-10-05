# strava

[![CI](https://github.com/ragnarok22/strava-python/actions/workflows/ci.yml/badge.svg)](https://github.com/ragnarok22/strava-python/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ragnarok22/strava-python/graph/badge.svg?token=1b94OIiVCD)](https://codecov.io/gh/ragnarok22/strava-python)
[![PyPI](https://img.shields.io/pypi/v/strava)](https://pypi.org/project/strava/)
[![Python](https://img.shields.io/pypi/pyversions/strava)](https://pypi.org/project/strava/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/strava)
[![License](https://img.shields.io/github/license/ragnarok22/strava-python)](https://github.com/ragnarok22/strava-python/blob/main/LICENSE)

A modern, fully-typed Python SDK for the [Strava API v3](https://developers.strava.com/docs/reference/).

## Features

- Sync and async clients built on [httpx](https://www.python-httpx.org/)
- Full type annotations and `py.typed` support
- 34 API endpoints across 10 resource groups (31 main API endpoints + 3 webhook endpoints)
- 50+ dataclass models with automatic serialization
- OAuth2 authentication with automatic token refresh
- Lazy pagination iterators
- Custom exception hierarchy with rate limit details

`SportType` includes Strava's April 2026 additions: `BASKETBALL`, `CRICKET`,
`DANCE`, `PADEL`, `PHYSICAL_THERAPY`, and `VOLLEYBALL`.

## Installation

```bash
pip install strava
```

## Quick Start

```python
from strava import Strava

with Strava(access_token="your_token") as client:
    # Get authenticated athlete
    athlete = client.athletes.retrieve_authenticated()
    print(f"{athlete.firstname} {athlete.lastname}")

    # List recent activities
    for activity in client.activities.list(per_page=10):
        print(f"{activity.name} - {activity.distance}m")
        print(activity.device_name)  # Recording device, when supplied by Strava
```

### Async

```python
from strava import AsyncStrava

async with AsyncStrava(access_token="your_token") as client:
    athlete = await client.athletes.retrieve_authenticated()
    activities = await client.activities.list(per_page=10).collect()
```

### Supplying an HTTPX client

Pass `http_client=httpx.Client(...)` to `Strava`, or an `httpx.AsyncClient` to
`AsyncStrava`, to reuse a transport, connection pool, event hooks, and custom
default headers. The SDK applies its own settings to each resource request:

- `access_token` and the SDK's OAuth refresh credentials control authentication,
  overriding the supplied client's auth handler and default `Authorization`
  header. Webhook requests disable token authentication and remove
  `Authorization` entirely.
- `base_url` controls the API destination, including its path prefix. Its default
  is `https://www.strava.com/api/v3`, even if the supplied client has another URL.
- `timeout` controls requests and automatic OAuth refresh, defaulting to 30 seconds
  even if the supplied client has another timeout. OAuth refresh uses Strava's
  token endpoint independently of the API base URL.

The SDK does not mutate the supplied client's `base_url`, `timeout`, `auth`, or
default headers. Other custom default headers are retained on resource requests.
You own the supplied client: SDK `close()` and context exit leave it open.
SDK-created HTTP clients are closed by the SDK.

```python
import httpx
from strava import Strava

with httpx.Client(headers={"X-App": "my-app"}) as http:
    with Strava(access_token="your_token", timeout=10.0, http_client=http) as client:
        athlete = client.athletes.retrieve_authenticated()
    # `http` remains open until its own context exits.
```

The same ownership rules apply to `AsyncStrava`; use `async with` for both clients
or close the supplied client yourself with `await http.aclose()`.

**Migration:** Previously, a supplied HTTPX client's auth, base URL, and timeout
could take precedence, and closing the SDK closed that client. Move API URL and
timeout overrides to the SDK constructor, provide token and refresh settings to
the SDK, and explicitly manage the supplied HTTPX client's lifetime.

## OAuth2 Authentication

### Get an authorization URL

```python
from strava import build_authorization_url

url = build_authorization_url(
    client_id="your_client_id",
    redirect_uri="http://localhost:8000/callback",
    scopes=["read", "activity:read_all"],
)
# Redirect the user to `url`
```

### Exchange the code for tokens

```python
from strava import exchange_token

tokens = exchange_token(
    client_id="your_client_id",
    client_secret="your_secret",
    code="code_from_callback",
)
print(tokens.access_token, tokens.refresh_token, tokens.expires_at)
print(tokens.scope)  # Granted scopes, e.g. "activity:read activity:write"
if tokens.athlete is not None:
    print(tokens.athlete.id, tokens.athlete.firstname)
```

`TokenResponse.scope` preserves the space-delimited scopes actually granted by
the athlete; these can differ from the requested scopes. `TokenResponse.athlete`
contains a typed `SummaryAthlete` when returned. Both fields default to `None`
when omitted, including in token refresh responses.

### Refresh a token manually

```python
from strava import refresh_access_token

tokens = refresh_access_token(
    client_id="your_client_id",
    client_secret="your_secret",
    refresh_token="current_refresh_token",
)
print(tokens.access_token, tokens.refresh_token, tokens.expires_at)
```

### Automatic token refresh

```python
from strava import Strava


def save_tokens(access_token, refresh_token, expires_at):
    # Persist the new tokens to your database
    ...


client = Strava(
    access_token="...",
    client_id="your_client_id",
    client_secret="your_secret",
    refresh_token="...",
    expires_at=1700000000,
    on_token_refresh=save_tokens,
)
```

If automatic refresh fails with an HTTP error, the SDK raises the error from the
OAuth response before sending the original API request. Tokens remain unchanged
and `on_token_refresh` is not called. This applies to both sync and async clients.

### Revoke tokens

```python
from strava import revoke_token

revoke_token(
    client_id="your_client_id",
    client_secret="your_secret",
    token="access_or_refresh_token",
    token_type_hint="access_token",
)
```

`deauthorize(access_token=...)` remains available for compatibility, but it is deprecated because Strava will retire `oauth/deauthorize` on June 1, 2027. Prefer `revoke_token()` for new code.

## API Coverage

| Resource | Methods |
|----------|---------|
| **Activities** | `create`, `retrieve`, `update`, `list`, `list_comments`, `list_kudoers`, `list_laps`, `list_zones` |
| **Athletes** | `retrieve_authenticated`, `update_authenticated`, `retrieve_zones`, `retrieve_stats` |
| **Clubs** | `retrieve`, `list_authenticated` |
| **Gear** | `retrieve` |
| **Routes** | `retrieve`, `export_gpx`, `export_tcx`, `list_by_athlete` |
| **Segments** | `retrieve`, `explore`, `list_starred`, `star` |
| **Segment Efforts** | `retrieve`, `list` |
| **Streams** | `get_activity_streams`, `get_route_streams`, `get_segment_effort_streams`, `get_segment_streams` |
| **Uploads** | `create`, `retrieve` |
| **Webhooks** | `create`, `list`, `delete` |

### Activity and segment response fields

Both `SummaryActivity` and `DetailedActivity` expose optional `resource_state`,
`has_heartrate`, `average_heartrate`, `max_heartrate`, `average_cadence`,
`average_temp`, `pr_count`, `suffer_score`, and `utc_offset` (seconds) fields.
Both `SummarySegment` and `DetailedSegment` expose optional `resource_state`,
`starred`, and `hazardous` fields. Omitted or null fields default to `None`;
`to_dict()` omits `None` but preserves `False` and zero values.

`athlete_segment_stats` remains a `SummarySegmentEffort` on both segment models.
It preserves the documented effort fields (`id`, `activity_id`, `elapsed_time`,
`start_date`, `start_date_local`, `distance`, and `is_kom`) and also accepts the
PR fields returned by Strava's reference examples: `pr_elapsed_time`, `pr_date`,
and `effort_count`, plus optional `pr_activity_id`. Responses can contain either
shape or both together, without losing fields or changing
`isinstance(stats, SummarySegmentEffort)` compatibility. `athlete_pr_effort`
continues to use `SummaryPRSegmentEffort`.

`pr_date` is parsed as a UTC-aware `datetime`, consistent with other model dates;
a date-only value such as `"1993-04-03"` becomes midnight UTC. `to_dict()` emits
an ISO timestamp with a UTC offset. These fields are based on the
[official API reference](https://developers.strava.com/docs/reference/), whose
segment stats sample and schema use different shapes; both are supported.

### Streams

All four stream methods return a typed `StreamSet`, accepting both responses
keyed by stream type and legacy lists of stream objects. Empty responses produce
an empty `StreamSet`; unknown stream types are ignored. Keyed stream values do
not need an inner `type` field.

```python
with Strava(access_token="your_token") as client:
    streams = client.streams.get_activity_streams(123, keys=["time", "heartrate"])
    if streams.heartrate is not None:
        print(streams.heartrate.data)
    route_streams = client.streams.get_route_streams(456)
```

Activity, segment-effort, and segment stream requests send `keys` as a
comma-separated string and `key_by_type=true`. Route stream requests send no
query parameters. The same methods are available on `AsyncStrava` with `await`.

**Compatibility note:** `key_by_type=False` is no longer allowed and raises a
`ValueError` before sending an HTTP request. Remove that argument or pass `True`;
legacy list responses are still supported. `StreamSet.from_stream_list()` also
remains available, and `StreamSet.from_response()` handles either response shape.

### Webhook subscriptions

Manage subscriptions with your application's credentials. These requests bypass
athlete-token authentication and automatic token refresh. Strava permits one
subscription per application.

```python
with Strava(
    access_token="your_token", base_url="https://www.strava.com/api/v3"
) as client:
    subscription = client.webhooks.create(
        client_id="your_client_id",
        client_secret="your_client_secret",
        callback_url="https://your-app.example/webhooks/strava",
        verify_token="your_verification_token",
    )
    subscriptions = client.webhooks.list(
        client_id="your_client_id", client_secret="your_client_secret"
    )
    client.webhooks.delete(
        subscription.id,
        client_id="your_client_id",
        client_secret="your_client_secret",
    )
```

Your callback must answer Strava's verification request within two seconds with
the JSON body `{"hub.challenge": "<received challenge>"}`. The same methods are
available on `AsyncStrava` with `await`. See the
[official webhook guide](https://developers.strava.com/docs/webhooks/) for callback
and event handling.

### Strength-training uploads

`uploads.create()` accepts `sport_type` as a `SportType` member or a string to
override the sport detected from a file. If omitted, Strava uses file metadata.

Strava accepts JSON strength-training files for `WeightTraining`,
`HighIntensityIntervalTraining`, `Workout`, and `Crossfit`. The sample
[`examples/strength-training.json`](examples/strength-training.json) contains
repetition-based and timed sets, weights in kilograms, and optional heart-rate
and active-time streams.

```python
from strava import SportType, Strava

with Strava(
    access_token="your_token", base_url="https://www.strava.com/api/v3"
) as client:
    with open("examples/strength-training.json", "rb") as file:
        upload = client.uploads.create(
            file=file,
            data_type="json",
            sport_type=SportType.WEIGHT_TRAINING,
            name="Strength session",
        )
    print(upload.id, upload.status)
```

Use `data_type="fit"` to upload a FIT strength-training file containing set
messages. For example, replace the file above with `strength.fit` and the sport
with `SportType.CROSSFIT`. The SDK transmits file bytes without modifying them.
FIT files with sets do not need timestamped record messages, but must include
the activity timestamp and session total elapsed time required by Strava.

JSON files require version `"1.0"`, a timezone-aware `start_time`, `utc_offset`
in seconds, `elapsed_time`, and at least one set. If streams are provided,
`time` is required and all stream arrays must have equal lengths. These upload
streams are part of the file format, separate from the read-only streams API.
See the [uploads guide](https://developers.strava.com/docs/uploads/) for the
complete specification and supported exercises.

Uploads require `activity:write` and are processed asynchronously. Poll
`uploads.retrieve(upload.id)` no more than once per second until `activity_id`
is populated or `error` is set. Async applications can use
`await client.uploads.create(...)` and `await client.uploads.retrieve(...)`.

## Strava API Changes

The default API base URL is the current official `https://www.strava.com/api/v3`.
Strava's future API host, `https://api-v3.strava.com` (without `www`), will be
available starting January 4, 2027. The SDK keeps the current default and does
not switch hosts automatically based on the clock. Once the future host is
available, you can opt in explicitly with `base_url="https://api-v3.strava.com"`
on either `Strava` or `AsyncStrava`.

### Breaking change: retired club endpoints

Strava removed club activities, club members, and club administrators endpoints
on September 1, 2026. The SDK has removed `clubs.list_activities()`,
`clubs.list_members()`, and `clubs.list_admins()` from both `Strava` and
`AsyncStrava`. Accessing these methods now raises `AttributeError`.

**Migration:** Remove calls to these methods and any application features that
depend on them. Strava provides no documented replacement endpoints.
`clubs.retrieve()` and `clubs.list_authenticated()` remain supported.
`ClubActivity` and `ClubAthlete` models and their public exports remain available
for parsing existing data.

Other methods are affected by Strava's 2026 Developer Program changes:

- `segments.explore()` is restricted to approved Extended Access applications effective September 1, 2026.
- `deauthorize()` is deprecated; use `revoke_token()` with your client credentials instead.

## Pagination

List endpoints return lazy paginators:

```python
# Iterate one item at a time (fetches pages on demand)
for activity in client.activities.list():
    print(activity.name)

# Collect all results eagerly
all_activities = client.activities.list().collect()

# Limit results
first_50 = client.activities.list().collect(max_items=50)

# Iterate page by page
for page in client.activities.list(per_page=50).pages():
    print(f"Got {len(page)} activities")
```

Page-number pagination continues until Strava returns an empty page, even if an
intermediate page contains fewer than `per_page` items. No requests are made
until iteration begins. `collect(max_items=0)` returns an empty list without a
request; negative limits raise `ValueError`. A positive limit stops as soon as
enough items have been collected, without fetching another page.

### Comment cursors

`activities.list_comments()` uses cursor pagination and sends only `page_size`
and, when present, `after_cursor`. The default page size is 30. `per_page` remains
a backward-compatible alias for `page_size`; **`page_size` wins when both are
supplied**.

```python
comments = client.activities.list_comments(123, page_size=50)
for comment in comments:
    print(comment.text)

# Resume after a previously saved comment cursor, passed through unchanged.
next_comments = client.activities.list_comments(
    123, page_size=50, after_cursor=saved_cursor
).collect(max_items=20)
```

Each `Comment` exposes an optional `cursor`. The paginator uses the last raw
comment's cursor to fetch the next page, preserving opaque tokens without
decoding or modifying them. Short pages still continue until an empty response.
If continuation requires a missing, invalid, repeated, or cycling cursor, it
raises `RuntimeError` rather than looping indefinitely. Cursor validation is
deferred until another page is needed, so bounded collection and stopping
iteration after the current page do not raise unnecessarily.

Async paginators provide the same behavior via `async for`,
`async for page in paginator.pages()`, and `await paginator.collect(...)`,
including for comments:

```python
async for comment in async_client.activities.list_comments(123, page_size=50):
    print(comment.text)

comments = await async_client.activities.list_comments(123).collect(max_items=20)
```

## Error Handling

```python
from strava import (
    StravaError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    ServerError,
)

try:
    activity = client.activities.retrieve(123)
except AuthenticationError:
    print("Authentication failed — check your credentials and tokens")
except AuthorizationError:
    print("Insufficient permissions")
except NotFoundError:
    print("Activity not found")
except ValidationError as e:
    print(f"Bad request: {e.message}")
except RateLimitError as e:
    print(f"Rate limited. 15-min usage: {e.usage_15min}/{e.limit_15min}")
except ServerError:
    print("Strava server error — try again later")
except StravaError as e:
    print(f"API error {e.status_code}: {e.message}")
```

API requests and OAuth operations (`exchange_token()`, `refresh_access_token()`,
`revoke_token()`, deprecated `deauthorize()`, and automatic refresh) use the same
SDK exception hierarchy:

| HTTP status | Exception |
|-------------|-----------|
| 400, 422 | `ValidationError` |
| 401 | `AuthenticationError` |
| 403 | `AuthorizationError` |
| 404 | `NotFoundError` |
| 429 | `RateLimitError` |
| 5xx | `ServerError` |
| Other 4xx | `StravaError` |

These exceptions preserve `status_code`, `message`, the original HTTP `response`,
and the JSON `fault` dictionary when available. Non-JSON error responses use the
response text as the message. `RateLimitError` also exposes the general and read
rate-limit limits and usage from the error response headers.

A 401 maps to `AuthenticationError`; it does not reliably identify an expired
token. `TokenExpiredError` remains exported as an `AuthenticationError` subclass
for compatibility, but the SDK does not automatically raise it.

**Compatibility change:** OAuth HTTP failures now raise SDK exceptions instead
of `httpx.HTTPStatusError`. Update handlers that catch `httpx.HTTPStatusError` for
OAuth operations to catch `StravaError` or the appropriate subclass.

## Development

```bash
# Install dependencies
uv sync

# Run tests
make test

# Run tests with coverage
make coverage

# Lint and format
make lint
make format
```

## Python Version

Supports Python 3.11 through 3.14.

## Contributing

Contributions are welcome! Please read the [Contributing Guide](CONTRIBUTING.md) before opening a pull request.

Found a bug? [Open an issue](https://github.com/ragnarok22/strava-python/issues/new?template=bug_report.yml). Have an idea? [Request a feature](https://github.com/ragnarok22/strava-python/issues/new?template=feature_request.yml).
