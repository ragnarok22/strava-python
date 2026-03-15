# Repository Guidelines

## Project Structure & Module Organization

This repository is a small `src`-layout Python package. Application code lives in `src/strava/`, with the public package entry point currently in `src/strava/__init__.py`. Project metadata and dependencies are defined in `pyproject.toml`. Developer shortcuts live in `Makefile`, and the project overview belongs in `README.md`.

There is no `tests/` directory yet. When tests are added, place them under `tests/` and mirror the package structure, for example `tests/test_client.py` or `tests/models/test_activity.py`.

## Build, Test, and Development Commands

- `uv sync`: create/update the local environment from `pyproject.toml` and `uv.lock`.
- `make help`: list available developer commands.
- `make format`: run Ruff formatting across the repository.
- `make lint`: run Ruff checks across the repository.
- `uv run python -c "from strava import hello; print(hello())"`: smoke-test the package import.

There is no dedicated test command yet because the repository does not include a test suite.

## Coding Style & Naming Conventions

Target Python is `>=3.14`. Use 4-space indentation, type hints for public APIs, and small, explicit modules. Prefer `snake_case` for functions, variables, and module names; use `PascalCase` for classes; keep constants in `UPPER_SNAKE_CASE`.

Formatting and linting are handled with Ruff. Run `make format` before opening a PR and `make lint` before merging.

## Testing Guidelines

Add tests for new behavior, not just bug fixes. Prefer `pytest` when the test suite is introduced, and name files `test_*.py`. Keep unit tests close to the public API they validate and cover authentication, HTTP error handling, and model parsing as those pieces are added.

## Commit & Pull Request Guidelines

Recent history uses short, conventional-style commits such as `docs: ...` and `chore(dev): ...`. Follow that pattern: `type(scope): summary` when a scope helps, otherwise `type: summary`.

PRs should include a clear description, the reason for the change, any follow-up work, and the commands you ran locally. Link the related issue when one exists. Screenshots are unnecessary unless documentation or generated output makes them useful.

## Security & Configuration Tips

Do not commit Strava client secrets, refresh tokens, or access tokens. Keep credentials in environment variables or local `.env` files that remain untracked.
