"""Scan repository text files for high-confidence secret patterns."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EXCLUDED_DIRS = {".git", "__pycache__", "(Inspiration) .github"}
EXCLUDED_SUFFIXES = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip"}
PATTERNS = [
    ("private_key", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("github_token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b")),
    ("github_pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    (
        "assigned_secret",
        re.compile(
            r"(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token|client[_-]?secret)\b\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{24,}"
        ),
    ),
]


def is_excluded(path: Path) -> bool:
    relative_parts = path.relative_to(REPO_ROOT).parts
    if any(part in EXCLUDED_DIRS for part in relative_parts):
        return True
    return path.suffix.lower() in EXCLUDED_SUFFIXES


def iter_files(paths: list[str]) -> list[Path]:
    roots = [REPO_ROOT / path for path in paths] if paths else [REPO_ROOT]
    files: list[Path] = []
    for root in roots:
        if root.is_file() and not is_excluded(root):
            files.append(root)
        elif root.is_dir():
            for path in root.rglob("*"):
                if path.is_file() and not is_excluded(path):
                    files.append(path)
    return sorted(set(files))


def scan_file(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    findings: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for name, pattern in PATTERNS:
            if pattern.search(line):
                rel = path.relative_to(REPO_ROOT)
                findings.append(f"{rel}:{line_number}: {name}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", help="Optional files or directories to scan")
    args = parser.parse_args()

    findings: list[str] = []
    for path in iter_files(args.paths):
        findings.extend(scan_file(path))

    if findings:
        print("Sensitive content scan failed:")
        for finding in findings[:50]:
            print(f"- {finding}")
        if len(findings) > 50:
            print(f"- ... and {len(findings) - 50} more")
        return 1

    print("Sensitive content scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
