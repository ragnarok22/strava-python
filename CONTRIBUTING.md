# Contributing

Thanks for your interest in contributing to the Strava Python SDK! This guide will help you get started.

## Setup

1. Fork and clone the repository:

```bash
git clone git@github.com:your-username/strava-python.git
cd strava-python
```

2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if you don't have it.

3. Install dependencies:

```bash
uv sync
```

## Development Workflow

### Running Tests

```bash
make test
```

### Running Tests with Coverage

```bash
make coverage
```

### Linting

```bash
make lint
```

### Formatting

```bash
make format
```

Always run `make format` and `make lint` before submitting a PR. CI will reject unformatted or unlinted code.

## Project Structure

```
src/strava/
├── _client.py / _async_client.py   # Sync and async clients
├── _auth.py                        # OAuth2 authentication
├── _exceptions.py                  # Exception hierarchy
├── _paginator.py                   # Pagination iterators
├── _serialization.py               # dict↔dataclass utilities
├── _types.py                       # Shared types and sentinels
├── models/                         # API response dataclasses
└── resources/                      # Endpoint wrappers (sync + async)
```

### Key Patterns

- **`NOT_GIVEN` sentinel** — Used to distinguish "not provided" from `None` in optional API parameters. Use it as the default for optional method arguments.
- **Resource classes** — Each API resource group has a sync and async class pair. Methods follow the naming convention: `create`, `retrieve`, `update`, `list`.
- **Models** — All models are `dataclass(slots=True, kw_only=True)` subclasses of `StravaModel` with automatic `from_dict`/`to_dict` serialization.
- **Enums** — Use `StrEnum` for API enum types.

## Adding a New Endpoint

1. Add or update the resource method in the appropriate file under `src/strava/resources/`.
2. Add both sync and async versions.
3. Add or update models under `src/strava/models/` if the endpoint uses new response types.
4. Export new models from `src/strava/models/__init__.py` and `src/strava/__init__.py`.
5. Add tests using `respx` to mock HTTP responses.

## Adding a New Model

1. Create the dataclass in the appropriate file under `src/strava/models/`.
2. Inherit from `StravaModel` and use `@dataclass(slots=True, kw_only=True)`.
3. All fields should default to `None` (or `field(default_factory=list)` for lists).
4. Export from `src/strava/models/__init__.py`.
5. Add `from_dict` round-trip tests in `tests/test_models.py`.

## Testing Guidelines

- Use `pytest` and name test files `test_*.py` under `tests/`.
- Use `respx` to mock `httpx` requests — never make real API calls in tests.
- Use `@pytest.mark.asyncio` for async tests.
- Test both success paths and error handling.

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): summary
```

Examples:

- `feat(activities): add list_photos endpoint`
- `fix(auth): handle refresh with expired token`
- `test: add segment streams coverage`
- `docs: update API coverage table`

## Pull Requests

- Keep PRs focused — one feature or fix per PR.
- Include a clear description of what changed and why.
- Make sure all CI checks pass before requesting review.
- If adding a new endpoint, include the Strava API reference link in the PR description.

## Code Style

- Target Python `>=3.11`.
- Use type hints on all public methods.
- Use `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Formatting and linting are handled by [Ruff](https://docs.astral.sh/ruff/).

## Security

- Never commit Strava API credentials, tokens, or secrets.
- Keep tests hermetic — use mocked HTTP responses only.
