# Repository Guidelines

## Project Structure & Module Organization

This repository is a `src`-layout Python package for the Strava API v3. Core package code lives in `src/strava/`, and public exports are assembled in `src/strava/__init__.py`.

```
src/strava/
├── __init__.py              # Public API re-exports
├── py.typed                 # PEP 561 type marker
├── _types.py                # Type aliases, NOT_GIVEN sentinel
├── _exceptions.py           # Exception hierarchy (StravaError, NotFoundError, etc.)
├── _serialization.py        # dict↔dataclass utilities
├── _auth.py                 # OAuth2 auth (httpx.Auth subclass) + token helpers
├── _paginator.py            # SyncPaginator / AsyncPaginator
├── _base_client.py          # Shared client logic
├── _client.py               # Strava (sync client)
├── _async_client.py         # AsyncStrava (async client)
├── models/                  # 40+ dataclass models matching API schemas
│   ├── _enums.py            # SportType, ActivityType (StrEnum)
│   ├── _base.py             # StravaModel base with from_dict/to_dict
│   ├── activities.py        # Activity, Lap, Comment, ActivityZone, etc.
│   ├── athletes.py          # MetaAthlete, SummaryAthlete, DetailedAthlete
│   ├── clubs.py             # MetaClub, SummaryClub, DetailedClub
│   ├── common.py            # PolylineMap, Split, Waypoint, ZoneRange, Fault
│   ├── gear.py              # SummaryGear, DetailedGear
│   ├── routes.py            # Route
│   ├── segments.py          # Segment, SegmentEffort, ExplorerResponse
│   ├── stats.py             # ActivityStats, ActivityTotal, Zones
│   ├── streams.py           # StreamSet + 11 stream types
│   └── uploads.py           # Upload
└── resources/               # Endpoint wrappers (sync + async pairs)
    ├── activities.py        # 8 endpoints
    ├── athletes.py          # 4 endpoints
    ├── clubs.py             # 5 endpoints
    ├── gear.py              # 1 endpoint
    ├── routes.py            # 4 endpoints
    ├── segments.py          # 4 endpoints
    ├── segment_efforts.py   # 2 endpoints
    ├── streams.py           # 4 endpoints
    └── uploads.py           # 2 endpoints
```

Tests live in `tests/` and cover authentication, client behavior, resources, models, and pagination. CI workflows live in `.github/workflows/`.

## Build, Test, and Development Commands

- `uv sync` — install or update the project environment and development dependencies
- `make help` — list available developer commands
- `make format` — run Ruff formatting across the repository
- `make lint` — run Ruff checks across the repository
- `make test` — run the pytest suite
- `make coverage` — run tests with coverage reporting for `strava`

## Coding Style & Naming Conventions

Target Python is `>=3.11`. Use 4-space indentation, type hints for public APIs, and small explicit modules. Naming: `snake_case` for functions/variables/modules, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.

Key patterns used throughout:
- `NOT_GIVEN` sentinel to distinguish "not provided" from `None` in optional API parameters
- `dataclass(slots=True, kw_only=True)` for all models
- `StrEnum` for API enum types (SportType, ActivityType)
- `httpx.Auth` subclass for OAuth2 with automatic token refresh
- Resource classes group endpoints: `client.activities.list()`, `client.athletes.retrieve_authenticated()`
- Paginator objects for lazy iteration over list endpoints

Keep responsibilities separated: resource classes handle HTTP orchestration, model classes handle parsing/serialization. Formatting and linting are handled with Ruff. Run `make format` and `make lint` before committing.

## Testing Guidelines

Use `pytest` and name files `test_*.py` under `tests/`. Existing test files:

- `tests/test_auth.py` — OAuth2 auth flows and token refresh
- `tests/test_client.py` — Error handling, resource availability, context manager
- `tests/test_models.py` — Model from_dict/to_dict, enums, nested models, round-trips
- `tests/test_paginator.py` — Sync and async pagination behavior
- `tests/test_resources.py` — Each resource endpoint with mocked responses

Use `respx` for mocking `httpx` requests and `pytest.mark.asyncio` for async tests. Add tests for new endpoints, request parameter handling, response parsing, pagination behavior, token refresh flows, and error mapping.

## Commit & Pull Request Guidelines

Use conventional-style commits: `type(scope): summary` when a scope helps, otherwise `type: summary`. Examples: `feat(activities): add list_photos endpoint`, `fix(auth): handle refresh with expired token`, `test: add segment streams coverage`.

PRs should include a clear description, the reason for the change, and the commands run locally. If a change affects the public API surface, call out compatibility or test coverage impact.

## Security & Configuration Tips

Do not commit Strava client secrets, refresh tokens, or access tokens. Keep credentials in environment variables or local `.env` files (already in `.gitignore`).

Keep tests hermetic — use mocked HTTP interactions via `respx` and static fixtures. Tests and CI must not depend on external credentials or network access.
