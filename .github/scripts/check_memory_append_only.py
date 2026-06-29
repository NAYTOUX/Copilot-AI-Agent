"""Fail when .github/memory changes delete lines."""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout


def is_git_repo_with_head() -> bool:
    inside = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if inside.returncode != 0:
        return False
    head = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return head.returncode == 0


def diff_text(base: str | None, head: str | None) -> str:
    if not is_git_repo_with_head():
        return ""
    if base and head:
        if base.strip("0") == "":
            return ""
        return run_git(
            ["diff", "--no-color", "--unified=0", base, head, "--", ".github/memory"]
        )
    return run_git(["diff", "--no-color", "--unified=0", "HEAD", "--", ".github/memory"])


def deleted_payload_lines(text: str) -> list[str]:
    deleted_by_file: dict[str, Counter[str]] = defaultdict(Counter)
    added_by_file: dict[str, Counter[str]] = defaultdict(Counter)
    current_file = ""

    for line in text.splitlines():
        if line.startswith("diff --git "):
            parts = line.split()
            current_file = parts[-1][2:] if len(parts) >= 4 else ""
            continue
        if line.startswith("---") or line.startswith("+++"):
            continue
        if line.startswith("-"):
            deleted_by_file[current_file][line[1:]] += 1
        elif line.startswith("+"):
            added_by_file[current_file][line[1:]] += 1

    deleted: list[str] = []
    for path, deleted_lines in deleted_by_file.items():
        added_lines = added_by_file[path]
        for payload, count in deleted_lines.items():
            remaining = count - added_lines[payload]
            deleted.extend([f"{path}: -{payload}"] * max(0, remaining))
    return deleted


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="")
    parser.add_argument("--head", default="")
    args = parser.parse_args()

    try:
        text = diff_text(args.base or None, args.head or None)
    except RuntimeError as exc:
        print(f"Memory append-only check could not run: {exc}")
        return 1

    deleted = deleted_payload_lines(text)
    if not deleted:
        print("Memory append-only check passed.")
        return 0

    print("Memory append-only check failed: deleted lines detected.")
    for line in deleted[:20]:
        print(f"- {line}")
    if len(deleted) > 20:
        print(f"- ... and {len(deleted) - 20} more")
    return 1


if __name__ == "__main__":
    sys.exit(main())
