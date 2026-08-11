#!/usr/bin/env python3
"""Run a generator and fail when its declared UTF-8 text outputs change."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import subprocess
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class FileState:
    path: str
    digest: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="project root and generator working directory")
    parser.add_argument("--include", action="append", required=True, help="generated text glob relative to root; repeatable")
    parser.add_argument("--exclude", action="append", default=[], help="excluded relative glob; repeatable")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="generator command after --")
    return parser.parse_args()


def stable_path_key(value: str) -> tuple[str, str]:
    return value.casefold(), value


def normalize_generated_text(path: Path) -> bytes:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError(f"{path} is not valid UTF-8 text: {error}") from error
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return normalized.encode("utf-8")


def normalize_glob(pattern: str) -> str:
    normalized = pattern.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if not normalized or normalized.startswith("/") or any(part == ".." for part in normalized.split("/")):
        raise ValueError(f"glob must be a non-empty relative pattern without '..': {pattern!r}")
    return normalized


def glob_matches(relative_path: str, pattern: str) -> bool:
    """Match a relative POSIX path with OS-independent, case-sensitive glob rules.

    ``*``, ``?``, and character classes operate within one path segment. A
    segment consisting only of ``**`` can consume zero or more segments.
    """
    path_parts = tuple(relative_path.split("/"))
    pattern_parts = tuple(pattern.split("/"))

    @lru_cache(maxsize=None)
    def match(path_index: int, pattern_index: int) -> bool:
        if pattern_index == len(pattern_parts):
            return path_index == len(path_parts)
        segment = pattern_parts[pattern_index]
        if segment == "**":
            return match(path_index, pattern_index + 1) or (
                path_index < len(path_parts) and match(path_index + 1, pattern_index)
            )
        return (
            path_index < len(path_parts)
            and fnmatch.fnmatchcase(path_parts[path_index], segment)
            and match(path_index + 1, pattern_index + 1)
        )

    return match(0, 0)


def is_excluded(relative_path: str, patterns: list[str]) -> bool:
    return any(glob_matches(relative_path, pattern) for pattern in patterns)


def snapshot(root: Path, includes: list[str], excludes: list[str]) -> tuple[dict[str, FileState], list[str]]:
    normalized_includes = [normalize_glob(pattern) for pattern in includes]
    normalized_excludes = [normalize_glob(pattern) for pattern in excludes]
    match_counts = [0] * len(normalized_includes)
    discovered: dict[str, Path] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if is_excluded(relative, normalized_excludes):
            continue
        for index, pattern in enumerate(normalized_includes):
            if glob_matches(relative, pattern):
                match_counts[index] += 1
                discovered[relative] = path
    states: dict[str, FileState] = {}
    for relative in sorted(discovered, key=stable_path_key):
        digest = hashlib.sha256(normalize_generated_text(discovered[relative])).hexdigest()
        states[relative] = FileState(relative, digest)
    unmatched = [includes[index] for index, count in enumerate(match_counts) if count == 0]
    return states, unmatched


def normalize_command(command: list[str]) -> list[str]:
    if command and command[0] == "--":
        command = command[1:]
    return command


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    command = normalize_command(args.command)
    if not root.is_dir():
        raise SystemExit(f"--root is not a directory: {root}")
    if not command:
        raise SystemExit("generator command is required after --")

    try:
        before, unmatched_before = snapshot(root, args.include, args.exclude)
    except ValueError as error:
        print(f"ERROR: {error}")
        return 1
    if unmatched_before:
        for pattern in unmatched_before:
            print(f"ERROR: include pattern matched no protected files before generation: {pattern}")
        return 1

    print(f"Files before generation: {len(before)}")
    try:
        completed = subprocess.run(command, cwd=root, check=False)
    except OSError as error:
        print(f"ERROR: generator could not start: {error}")
        return 1
    if completed.returncode != 0:
        print(f"ERROR: generator exited with status {completed.returncode}")
        return completed.returncode or 1

    try:
        after, unmatched_after = snapshot(root, args.include, args.exclude)
    except ValueError as error:
        print(f"ERROR: {error}")
        return 1

    before_paths = set(before)
    after_paths = set(after)
    added = sorted(after_paths - before_paths, key=stable_path_key)
    removed = sorted(before_paths - after_paths, key=stable_path_key)
    changed = sorted(
        (path for path in before_paths & after_paths if before[path].digest != after[path].digest),
        key=stable_path_key,
    )

    for path in added:
        print(f"ADDED: {path}")
    for path in removed:
        print(f"REMOVED: {path}")
    for path in changed:
        print(f"CHANGED: {path}")
    for pattern in unmatched_after:
        print(f"ERROR: include pattern matched no protected files after generation: {pattern}")
    print(f"Files after generation: {len(after)}")
    print(f"Added: {len(added)}")
    print(f"Removed: {len(removed)}")
    print(f"Changed: {len(changed)}")

    failed = bool(added or removed or changed or unmatched_after)
    print("RESULT: FAIL" if failed else "RESULT: PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(errors="backslashreplace")
    except (AttributeError, ValueError):
        pass
    sys.exit(main())
