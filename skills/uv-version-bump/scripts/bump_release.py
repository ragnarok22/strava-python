#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

VALID_BUMPS = (
    "major",
    "minor",
    "patch",
    "stable",
    "alpha",
    "beta",
    "rc",
    "post",
    "dev",
)


class CommandError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Bump a uv-managed package version, update CHANGELOG.md, create a release "
            "commit, and create a matching git tag."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--project-dir", default=".", help="Path to the target uv project."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--version", help="Exact version to release, e.g. 0.2.0.")
    mode.add_argument(
        "--bump", choices=VALID_BUMPS, help="Semver component to bump with uv."
    )
    parser.add_argument(
        "--changelog",
        default="CHANGELOG.md",
        help="Path to the changelog file, relative to the project directory.",
    )
    parser.add_argument(
        "--change",
        action="append",
        default=[],
        help="A changelog bullet without the leading dash. Repeat for multiple bullets.",
    )
    parser.add_argument(
        "--release-date",
        default=date.today().isoformat(),
        help="Release date used in the changelog heading.",
    )
    parser.add_argument(
        "--commit-message",
        default="bump version from {old} to {new}",
        help="Commit message template. Available fields: {old}, {new}, {tag}.",
    )
    parser.add_argument(
        "--tag-prefix", default="v", help="Prefix used for the release tag."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the target version and changelog entry without editing files.",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Create a git commit containing the release changes.",
    )
    parser.add_argument(
        "--tag",
        action="store_true",
        help="Create an annotated git tag after committing the release.",
    )
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow pre-existing worktree changes. By default the script requires a clean repo.",
    )
    args = parser.parse_args()
    if args.tag and not args.commit:
        parser.error("--tag requires --commit so the tag points at a release commit.")
    return args


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).resolve()
    pyproject = project_dir / "pyproject.toml"
    if not pyproject.exists():
        print(f"Error: {pyproject} was not found.", file=sys.stderr)
        return 1

    try:
        repo_root = find_git_root(project_dir)
    except CommandError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not args.allow_dirty:
        try:
            ensure_clean_worktree(repo_root)
        except CommandError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    try:
        current_version = get_uv_version(project_dir)
        target_version = resolve_target_version(
            project_dir, version=args.version, bump=args.bump
        )
    except CommandError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if current_version == target_version:
        print(
            f"Error: current version is already {current_version}; nothing to release.",
            file=sys.stderr,
        )
        return 1

    tag_name = f"{args.tag_prefix}{target_version}"
    try:
        ensure_tag_absent(repo_root, tag_name)
    except CommandError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    changelog_path = (project_dir / args.changelog).resolve()
    change_lines = args.change or [f"Release {tag_name}."]

    if args.dry_run:
        print(f"Current version: {current_version}")
        print(f"Target version:  {target_version}")
        print(f"Changelog:       {relative_to_root(changelog_path, project_dir)}")
        print(
            "Commit message:  "
            + render_commit_message(
                args.commit_message, current_version, target_version, tag_name
            )
        )
        print(f"Tag:             {tag_name}")
        print("Changes:")
        for line in change_lines:
            print(f"- {line}")
        return 0

    try:
        apply_uv_version(project_dir, target_version)
        update_changelog(
            changelog_path=changelog_path,
            version=target_version,
            release_date=args.release_date,
            change_lines=change_lines,
        )
    except (CommandError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    release_files = collect_release_files(project_dir, changelog_path, repo_root)
    commit_message = render_commit_message(
        args.commit_message, current_version, target_version, tag_name
    )

    try:
        if args.commit:
            git_add(repo_root, release_files)
            git_commit(repo_root, commit_message)
            if args.tag:
                git_tag(repo_root, tag_name)
    except CommandError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Released {current_version} -> {target_version}")
    print("Updated files:")
    for path in release_files:
        print(f"- {path}")
    if args.commit:
        print(f"Commit: {commit_message}")
    if args.tag:
        print(f"Tag:    {tag_name}")
    return 0


def run_command(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        message = "\n".join(
            part.strip() for part in (result.stderr, result.stdout) if part.strip()
        )
        raise CommandError(message or f"command failed: {' '.join(args)}")
    return result


def find_git_root(start: Path) -> Path:
    result = run_command(["git", "rev-parse", "--show-toplevel"], cwd=start)
    return Path(result.stdout.strip())


def ensure_clean_worktree(repo_root: Path) -> None:
    result = run_command(["git", "status", "--porcelain"], cwd=repo_root)
    if result.stdout.strip():
        raise CommandError(
            "git worktree is not clean. Commit or stash existing changes first, or rerun "
            "with --allow-dirty if a partial release commit is intentional."
        )


def ensure_tag_absent(repo_root: Path, tag_name: str) -> None:
    result = subprocess.run(
        ["git", "rev-parse", "-q", "--verify", f"refs/tags/{tag_name}"],
        cwd=repo_root,
        text=True,
        capture_output=True,
    )
    if result.returncode == 0:
        raise CommandError(f"git tag {tag_name} already exists.")


def get_uv_version(project_dir: Path) -> str:
    result = run_command(["uv", "version", "--output-format", "json"], cwd=project_dir)
    data = json.loads(result.stdout)
    version = data.get("version")
    if not isinstance(version, str) or not version:
        raise CommandError("unable to parse current version from `uv version`.")
    return version


def resolve_target_version(
    project_dir: Path, version: str | None, bump: str | None
) -> str:
    cmd = ["uv", "version", "--dry-run", "--output-format", "json"]
    if version is not None:
        cmd.append(version)
    elif bump is not None:
        cmd.extend(["--bump", bump])
    else:
        raise CommandError("either version or bump is required.")
    result = run_command(cmd, cwd=project_dir)
    data = json.loads(result.stdout)
    target = data.get("version")
    if not isinstance(target, str) or not target:
        raise CommandError(
            "unable to parse target version from `uv version --dry-run`."
        )
    return target


def apply_uv_version(project_dir: Path, target_version: str) -> None:
    run_command(["uv", "version", target_version, "--no-sync"], cwd=project_dir)


def update_changelog(
    changelog_path: Path,
    version: str,
    release_date: str,
    change_lines: list[str],
) -> None:
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", release_date):
        raise ValueError("--release-date must use YYYY-MM-DD.")

    release_heading = f"## {version} - {release_date}"
    release_block = [release_heading, ""]
    release_block.extend(f"- {line}" for line in change_lines)
    release_block.append("")

    if not changelog_path.exists() or not changelog_path.read_text().strip():
        content = (
            "\n".join(
                [
                    "# Changelog",
                    "",
                    "All notable changes to this project will be documented in this file.",
                    "",
                    *release_block,
                ]
            ).rstrip()
            + "\n"
        )
        changelog_path.write_text(content)
        return

    original = changelog_path.read_text()
    lines = original.splitlines()
    version_pattern = re.compile(
        rf"^##\s+(?:\[)?v?{re.escape(version)}(?:\])?(?:\s+-.*)?$",
        re.IGNORECASE,
    )
    if any(version_pattern.match(line.strip()) for line in lines):
        raise ValueError(
            f"{changelog_path.name} already contains an entry for {version}."
        )

    h2_indices = [i for i, line in enumerate(lines) if re.match(r"^##\s+", line)]
    unreleased_index = next(
        (
            i
            for i in h2_indices
            if re.match(r"^##\s+\[?unreleased\]?\s*$", lines[i], re.IGNORECASE)
        ),
        None,
    )
    if unreleased_index is not None:
        later_h2 = [i for i in h2_indices if i > unreleased_index]
        insert_at = later_h2[0] if later_h2 else len(lines)
    elif h2_indices:
        insert_at = h2_indices[0]
    else:
        insert_at = len(lines)

    before = lines[:insert_at]
    after = lines[insert_at:]
    if before and before[-1] != "":
        before.append("")

    updated = "\n".join(before + release_block + after).rstrip() + "\n"
    changelog_path.write_text(updated)


def collect_release_files(
    project_dir: Path, changelog_path: Path, repo_root: Path
) -> list[str]:
    candidates = [
        project_dir / "pyproject.toml",
        project_dir / "uv.lock",
        changelog_path,
    ]
    unique_paths: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if not candidate.exists():
            continue
        rel = relative_to_root(candidate, repo_root)
        if rel not in seen:
            seen.add(rel)
            unique_paths.append(rel)
    return unique_paths


def git_add(repo_root: Path, release_files: list[str]) -> None:
    if not release_files:
        raise CommandError("no release files were collected for git add.")
    run_command(["git", "add", "--", *release_files], cwd=repo_root)


def git_commit(repo_root: Path, message: str) -> None:
    run_command(["git", "commit", "-m", message], cwd=repo_root)


def git_tag(repo_root: Path, tag_name: str) -> None:
    run_command(["git", "tag", "-a", tag_name, "-m", tag_name], cwd=repo_root)


def render_commit_message(template: str, old: str, new: str, tag_name: str) -> str:
    return template.format(old=old, new=new, tag=tag_name)


def relative_to_root(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    sys.exit(main())
