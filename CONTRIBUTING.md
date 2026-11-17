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

### Choose Validation by Risk

Run the checks relevant to the change. Add tests for meaningful bugs, critical
logic, and realistic regressions, not to exercise every changed line. Reuse
existing fixtures and tests before adding new ones.

- **Documentation only:** check local links and format the Markdown files you
  changed. Check that code examples parse and match the public API; do not run
  examples against real athlete accounts as part of validation.
- **Focused bug or endpoint change:** reproduce the problem first when practical,
  add a minimal regression test, and run the affected pytest cases. For example:

  ```bash
  uv run pytest tests/test_resources.py -k activities -v
  ```

- **Public API or model typing:** also run `make typecheck` and update relevant
  static consumer contracts under `tests/typing`.
- **Cross-cutting changes, releases, or explicit requests:** run the broader test
  suite and use coverage where it helps identify missing critical cases.

Format/lint changed Python files with Ruff, or use `make format` / `make lint`
when repository-wide checks are appropriate. Avoid unrelated formatting changes.
For documentation, pass only the files you changed, for example:

```bash
uv run ruff format README.md CONTRIBUTING.md docs/usage.md docs/api.md docs/migration.md
```

Local risk-based checks do **not** replace required CI. CI runs shared formatting
and lint checks, plus type checks and tests on Python 3.11, 3.12, 3.13, and 3.14.
The Python 3.14 job also collects coverage. Keep multiversion validation intact
and do not bypass failing checks. You do not need a full local coverage run for
every pull request.

### Available Commands

| Command | Purpose |
| --- | --- |
| `make test` | Run the full pytest suite when warranted |
| `make coverage` | Run the full suite with a coverage report |
| `make lint` | Run repository-wide Ruff checks |
| `make format` | Format the repository with Ruff |
| `make typecheck` | Check package types and static consumer contracts |

Strict mypy checks use Python 3.11 semantics and cover `src/strava` and
`tests/typing`. Add static consumer contracts there for public APIs, using
`typing.assert_type` to verify exact inferred types. These contracts are checked
without executing network calls; runtime pytest tests are outside the current
mypy scope. Fix underlying types rather than adding suppressions or weakening
strict checks.

Ruff's Python target, formatting conventions, Markdown inclusion, and lint rule
selection are explicit in `pyproject.toml`. The selected rules preserve the
existing Ruff 0.16.5 policy; review rule changes deliberately when upgrading
Ruff rather than relying on changing defaults.

Sync/async endpoint tests can use the shared `client` fixture from
`tests/conftest.py` and `invoke()` from `tests/_helpers.py`. Override
`client_options` in a test module for special token scenarios. Module-local
sync-only fixtures remain available where appropriate.

Before submitting, report the targeted checks you ran and any relevant
limitations. CI checks types on every supported Python version and before
building a release. The release workflow also validates the version/tag and
smoke-tests the installed wheel before publishing.

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
- **Models** — All models are `dataclass(slots=True, kw_only=True)` subclasses of `StravaModel` with automatic `from_dict`/`to_dict` serialization. `from_dict` returns `Self` to preserve concrete subclass types.
- **Enums** — Use `StrEnum` for API enum types and include a `str` fallback in model annotations (for example, `SportType | str | None`). Known strings parse as enum members; unknown API strings pass through unchanged. Test member identity, unknown strings, and serialization when updating these annotations.

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
- Cover relevant success paths and failure modes, including sync/async parity
  when changing shared behavior.
- Prefer a small regression test for an actual failure over redundant, trivial,
  or heavily mocked tests. Keep credentials and network access out of tests/CI.

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
- Summarize verification and any important compatibility or coverage impact.
- Make sure all CI checks pass before requesting review.
- If adding a new endpoint, include the Strava API reference link in the PR description.

## Code Style

- Target Python `>=3.11`.
- Use type hints on all public methods.
- Use `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Formatting and linting are handled by [Ruff](https://docs.astral.sh/ruff/).
- Static type checking is handled by strict [mypy](https://mypy.readthedocs.io/) through `make typecheck`.

## Security

- Never commit Strava API credentials, tokens, or secrets.
- Keep tests hermetic — use mocked HTTP responses only.
