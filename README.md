# strava

A Python library for the Strava API v3.

This project is intended to provide a clean, typed, and practical interface for working with Strava from Python applications and services.

## Status

The package is in early development.

Current state:

- Project scaffold is in place
- `httpx` is installed as the HTTP client dependency
- No public Strava API client has been implemented yet

Until the first client release lands, treat the package as work in progress.

## Goals

- Cover the Strava API v3 with a Python-first interface
- Provide typed request and response models where useful
- Support both simple scripts and larger applications
- Keep authentication flows straightforward
- Build on top of `httpx` for modern HTTP support

## Installation

```bash
pip install strava
```

For local development:

```bash
uv sync
```

## Python Version

This project currently targets Python `>=3.14`.

## Planned Features

- OAuth token exchange and refresh helpers
- Authenticated API client
- Athlete, activities, clubs, routes, and segments endpoints
- Pagination helpers
- Sensible error types for API failures
- Type hints throughout the public interface

## Usage

There is no stable public API yet.

At the moment, the package only exposes a placeholder function:

```python
from strava import hello

print(hello())
```

Future usage will look more like a real client library, for example:

```python
# Planned API example only. Not implemented yet.
from strava import StravaClient

client = StravaClient(access_token="...")
athlete = client.get_authenticated_athlete()
print(athlete.firstname)
```

## Development

Repository layout:

```text
src/
  strava/
```

Typical workflow:

```bash
uv sync
uv run python -c "from strava import hello; print(hello())"
```

## Roadmap

1. Add configuration and authentication primitives
2. Implement a minimal HTTP client
3. Ship athlete and activity endpoints first
4. Add models, pagination, and better error handling
5. Expand endpoint coverage across Strava API v3

## Contributing

Contributions are welcome once the initial client shape is in place. For now, issues and early design feedback are the most useful.
