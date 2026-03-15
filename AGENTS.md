# Repository Guidelines

## Project Structure & Module Organization

This repository is a `src`-layout Python package for the Strava API v3. Core package code lives in `src/strava/`, and public exports are assembled in `src/strava/__init__.py`.

Synchronous and asynchronous clients live in `src/strava/_client.py` and `src/strava/_async_client.py`. Authentication helpers live in `src/strava/_auth.py`, and shared plumbing such as exceptions, pagination, serialization, and sentinel types live in the other private `_*.py` modules.

Endpoint-specific request wrappers live under `src/strava/resources/`. Parsed API response models live under `src/strava/models/`. The package includes typing metadata via `src/strava/py.typed`.

Tests live in `tests/` and currently cover authentication, client behavior, resources, models, and pagination. Project metadata and dependencies live in `pyproject.toml`, developer shortcuts live in `Makefile`, release automation lives under `skills/uv-version-bump/`, and the project overview belongs in `README.md`.

## Build, Test, and Development Commands

- `uv sync`: install or update the project environment and development dependencies.
- `make help`: list available developer commands.
- `make format`: run Ruff formatting across the repository.
- `make lint`: run Ruff checks across the repository.
- `make test`: run the pytest suite.
- `make coverage`: run tests with coverage reporting for `strava`.
- `uv run python -c "from strava import Strava, AsyncStrava; print(Strava.__name__, AsyncStrava.__name__)"`: smoke-test public imports.

## Coding Style & Naming Conventions

Target Python is `>=3.11` according to `pyproject.toml`. Use 4-space indentation, type hints for public APIs, and small, explicit modules. Prefer `snake_case` for functions, variables, and module names, `PascalCase` for classes, and `UPPER_SNAKE_CASE` for constants.

Keep responsibilities separated: resource classes should focus on HTTP request orchestration, while model classes should focus on parsing and serialization. Prefer explicit parameter names and typed return values on public client and resource methods.

Formatting and linting are handled with Ruff. Run `make format` before opening a PR and `make lint` before merging.

## Testing Guidelines

Use `pytest` for new coverage and name files `test_*.py`. Keep tests under `tests/` and group them by concern, following the existing layout such as `tests/test_auth.py`, `tests/test_client.py`, `tests/test_resources.py`, `tests/test_models.py`, and `tests/test_paginator.py`.

Prefer `respx` for mocking `httpx` requests and `pytest.mark.asyncio` for async behavior. Add tests for new endpoints, request parameter handling, response parsing, pagination behavior, token refresh flows, and error mapping whenever those areas change.

## Commit & Pull Request Guidelines

Recent history uses conventional-style commits such as `ci(workflows): ...`, `docs: ...`, and `chore(dev): ...`. Follow that pattern: `type(scope): summary` when a scope helps, otherwise `type: summary`.

PRs should include a clear description, the reason for the change, and the commands you ran locally. Link the related issue when one exists. If a change affects the public client surface, call out any compatibility or test coverage impact explicitly.

## Security & Configuration Tips

Do not commit Strava client secrets, refresh tokens, or access tokens. Keep credentials in environment variables or local `.env` files that remain untracked.

Keep unit tests hermetic. Prefer mocked HTTP interactions and static fixtures over live API calls so local runs and CI do not depend on external credentials or network access.
