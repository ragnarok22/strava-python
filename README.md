# strava

[![CI](https://github.com/ragnarok22/strava-python/actions/workflows/ci.yml/badge.svg)](https://github.com/ragnarok22/strava-python/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ragnarok22/strava-python/graph/badge.svg?token=1b94OIiVCD)](https://codecov.io/gh/ragnarok22/strava-python)
[![PyPI](https://img.shields.io/pypi/v/strava)](https://pypi.org/project/strava/)
[![Python](https://img.shields.io/pypi/pyversions/strava)](https://pypi.org/project/strava/)
[![License](https://img.shields.io/github/license/ragnarok22/strava-python)](https://github.com/ragnarok22/strava-python/blob/main/LICENSE)

A modern, fully-typed Python SDK for the [Strava API v3](https://developers.strava.com/docs/reference/).

## Features

- Sync and async clients built on [httpx](https://www.python-httpx.org/)
- Full type annotations and `py.typed` support
- 34 API endpoints across 9 resource groups
- 50+ dataclass models with automatic serialization
- OAuth2 authentication with automatic token refresh
- Lazy pagination iterators
- Custom exception hierarchy with rate limit details

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
```

### Async

```python
from strava import AsyncStrava

async with AsyncStrava(access_token="your_token") as client:
    athlete = await client.athletes.retrieve_authenticated()
    activities = await client.activities.list(per_page=10).collect()
```

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
```

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

### Deauthorize

```python
from strava import deauthorize

deauthorize(access_token="your_token")
```

## API Coverage

| Resource | Methods |
|----------|---------|
| **Activities** | `create`, `retrieve`, `update`, `list`, `list_comments`, `list_kudoers`, `list_laps`, `list_zones` |
| **Athletes** | `retrieve_authenticated`, `update_authenticated`, `retrieve_zones`, `retrieve_stats` |
| **Clubs** | `retrieve`, `list_activities`, `list_admins`, `list_members`, `list_authenticated` |
| **Gear** | `retrieve` |
| **Routes** | `retrieve`, `export_gpx`, `export_tcx`, `list_by_athlete` |
| **Segments** | `retrieve`, `explore`, `list_starred`, `star` |
| **Segment Efforts** | `retrieve`, `list` |
| **Streams** | `get_activity_streams`, `get_route_streams`, `get_segment_effort_streams`, `get_segment_streams` |
| **Uploads** | `create`, `retrieve` |

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

## Error Handling

```python
from strava import (
    StravaError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    TokenExpiredError,
    ValidationError,
    ServerError,
)

try:
    activity = client.activities.retrieve(123)
except TokenExpiredError:
    print("Access token has expired — refresh it")
except AuthenticationError:
    print("Invalid or missing access token")
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
