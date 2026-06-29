"""Generate docs/AGENT_CATALOG.md from the registry and agent frontmatter."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / ".github" / "agent-registry.json"
OUTPUT_PATH = REPO_ROOT / "docs" / "AGENT_CATALOG.md"


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    if not match:
        return {}
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep:
            data[key.strip()] = value.strip().strip("'\"")
    return data


def build_catalog() -> str:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    grouped: dict[str, list[dict]] = {}
    for entry in registry["agents"]:
        category = str(entry.get("category", "uncategorized"))
        grouped.setdefault(category, []).append(entry)

    lines = [
        "# Agent Catalog",
        "",
        "Generated from `.github/agent-registry.json` and `.github/agents/*.agent.md`.",
        "Do not edit by hand; run `python .github/scripts/generate_agent_catalog.py --write`.",
        "",
    ]

    for category in sorted(grouped):
        lines.extend([f"## {category.title()}", ""])
        for entry in sorted(grouped[category], key=lambda item: (item.get("level", 99), item["name"])):
            agent_path = REPO_ROOT / entry["file"]
            frontmatter = parse_frontmatter(agent_path)
            description = frontmatter.get("description", "")
            capabilities = ", ".join(entry.get("primary_capabilities", []))
            lines.extend(
                [
                    f"### {entry['name']}",
                    "",
                    f"- File: `{entry['file']}`",
                    f"- Level: `{entry.get('level', '')}`",
                    f"- Description: {description}",
                    f"- Capabilities: {capabilities}",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    expected = build_catalog()
    current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
    if args.write:
        OUTPUT_PATH.write_text(expected, encoding="utf-8")
        print(f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)}")
        return 0
    if args.check:
        if current != expected:
            print(
                f"{OUTPUT_PATH.relative_to(REPO_ROOT)} is stale. Run "
                "python .github/scripts/generate_agent_catalog.py --write",
                file=sys.stderr,
            )
            return 1
        print("Agent catalog is current.")
        return 0
    print(expected, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

