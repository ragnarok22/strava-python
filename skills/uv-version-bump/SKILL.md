---
name: uv-version-bump
description: Bump a Python package version in a uv-managed project, update or create CHANGELOG.md, create a release commit, and create a matching git tag like v1.2.3. Use when a user asks to cut a release, bump patch/minor/major, prepare a versioned changelog entry, or create release commits and tags for a pyproject.toml project.
---

# Uv Version Bump

## Overview

Use this skill for small Python package releases where the version source of truth is `pyproject.toml` and the project is managed with `uv`. The bundled script wraps the standard flow: compute the next version with `uv version`, update `CHANGELOG.md`, create a scoped git commit, and create an annotated `vX.Y.Z` tag.

## Workflow

1. Inspect the repository state first.
   - Confirm the repo contains `pyproject.toml`.
   - Check for duplicate version literals before relying on `uv version`, for example:
     - `rg -n "__version__|version\\s*=\\s*\\\"" .`
   - Prefer a clean git worktree. If unrelated edits are already present, stop and ask unless the user explicitly wants a partial release commit.
2. Preview the release target.
   - Exact version:
     - `python "<path-to-skill>/scripts/bump_release.py" --project-dir . --version 0.2.0 --dry-run`
   - Semantic bump:
     - `python "<path-to-skill>/scripts/bump_release.py" --project-dir . --bump minor --dry-run`
3. Apply the release.
   - Include one or more changelog bullets with `--change`.
   - Create the release commit and tag in the same invocation:
     - `python "<path-to-skill>/scripts/bump_release.py" --project-dir . --bump minor --change "Add OAuth client." --change "Document rate-limit handling." --commit --tag`
   - For an explicit version:
     - `python "<path-to-skill>/scripts/bump_release.py" --project-dir . --version 0.2.0 --change "Initial public release." --commit --tag`
4. Verify the result.
   - Check the version:
     - `uv version --short`
   - Check the commit and touched files:
     - `git show --stat --oneline HEAD`
   - Check the tag:
     - `git tag --list "v*" --sort=-version:refname | head`

## Behavior Notes

- The script uses `uv version <target> --no-sync` so `pyproject.toml` and `uv.lock` are updated without syncing `.venv`.
- If `CHANGELOG.md` is missing, the script creates a simple changelog with the new release entry.
- If the changelog contains an `Unreleased` section, the new release entry is inserted after it. Otherwise the new release is inserted before the first existing version entry.
- The default commit message is `bump version from {old} to {new}`. Override it with `--commit-message` when the project uses a different convention.
- The default tag is `v{new}` and it is created as an annotated tag.
- If sandboxing blocks `uv version` because it needs access to the uv cache under the home directory, rerun the command with escalated permissions.

## Bundled Resource

### scripts/bump_release.py

Run the full release bump for a uv-managed project.

Common invocations:
- `python "<path-to-skill>/scripts/bump_release.py" --project-dir . --bump patch --dry-run`
- `python "<path-to-skill>/scripts/bump_release.py" --project-dir . --version 1.0.0 --change "Stabilize the public API." --commit --tag`
- `python "<path-to-skill>/scripts/bump_release.py" --project-dir . --bump minor --allow-dirty --commit --tag`
