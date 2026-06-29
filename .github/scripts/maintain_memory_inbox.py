"""Inspect structured reports in .github/memory/inbox and summarize actions."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INBOX_DIR = REPO_ROOT / ".github" / "memory" / "inbox"
INDEX_PATH = INBOX_DIR / "_INDEX.md"


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    if not match:
        return {}
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep:
            values[key.strip()] = value.strip()
    return values


def collect_reports() -> list[dict[str, str]]:
    reports: list[dict[str, str]] = []
    for path in sorted(INBOX_DIR.glob("*.md")):
        if path.name.upper() == "README.MD" or path.name == INDEX_PATH.name:
            continue
        frontmatter = parse_frontmatter(path)
        reports.append(
            {
                "file": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
                "timestamp": frontmatter.get("timestamp", ""),
                "source_repo": frontmatter.get("source_repo", ""),
                "agent": frontmatter.get("agent", ""),
                "category": frontmatter.get("category", ""),
                "confidence": frontmatter.get("confidence", ""),
                "severity": frontmatter.get("severity", ""),
                "requested_action": frontmatter.get("requested_action", ""),
                "privacy": frontmatter.get("privacy", ""),
            }
        )
    return reports


def render_index(reports: list[dict[str, str]]) -> str:
    lines = [
        "# Inbox Report Index",
        "",
        "Generated from structured report frontmatter. Do not use this as proof; open the original report before updating durable memory.",
        "",
        f"- Reports: {len(reports)}",
        "",
    ]
    for label, field in (
        ("By requested action", "requested_action"),
        ("By severity", "severity"),
        ("By category", "category"),
        ("By confidence", "confidence"),
    ):
        lines.extend([f"## {label}", ""])
        counts = Counter(report.get(field, "") or "unknown" for report in reports)
        if counts:
            for key, count in sorted(counts.items()):
                lines.append(f"- `{key}`: {count}")
        else:
            lines.append("- None.")
        lines.append("")

    lines.extend(["## Reports", ""])
    if not reports:
        lines.append("- None.")
    else:
        for report in reports:
            lines.append(
                "- "
                f"[{Path(report['file']).name}]({Path(report['file']).name})"
                f" | action=`{report['requested_action'] or 'unknown'}`"
                f" | severity=`{report['severity'] or 'unknown'}`"
                f" | category=`{report['category'] or 'unknown'}`"
                f" | confidence=`{report['confidence'] or 'unknown'}`"
            )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-index", action="store_true")
    args = parser.parse_args()

    reports = collect_reports()
    index = render_index(reports)
    if args.write_index:
        INDEX_PATH.write_text(index, encoding="utf-8")
        print(f"Wrote {INDEX_PATH.relative_to(REPO_ROOT)}")
    else:
        print(index, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
