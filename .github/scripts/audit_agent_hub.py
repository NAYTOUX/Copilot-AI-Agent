"""Audit the agent hub control surface and report high-level health."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def parse_frontmatter_name(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    if not match:
        return ""
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip() == "name":
            return value.strip().strip("'\"")
    return ""


def collect_health() -> dict:
    registry_path = REPO_ROOT / ".github" / "agent-registry.json"
    routing_path = REPO_ROOT / ".github" / "routing-rules.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    routing = json.loads(routing_path.read_text(encoding="utf-8"))
    agents = sorted((REPO_ROOT / ".github" / "agents").glob("*.agent.md"))
    prompts = sorted((REPO_ROOT / ".github" / "prompts").glob("*.prompt.md"))
    instructions = sorted(
        (REPO_ROOT / ".github" / "instructions").glob("*.instructions.md")
    )
    skills = sorted((REPO_ROOT / ".github" / "skills").glob("*/SKILL.md"))
    workflows = sorted((REPO_ROOT / ".github" / "workflows").glob("*.yml"))
    scripts = sorted((REPO_ROOT / ".github" / "scripts").glob("*.py"))

    registry_entries = registry.get("agents", [])
    routing_rules = routing.get("rules", [])
    categories = Counter(str(entry.get("category", "")) for entry in registry_entries)
    levels = Counter(str(entry.get("level", "")) for entry in registry_entries)
    agent_names = [parse_frontmatter_name(path) for path in agents]

    warnings: list[str] = []
    if len(agents) < 20:
        warnings.append("agent coverage is unexpectedly small")
    if len(prompts) < 8:
        warnings.append("prompt entrypoint coverage is thin")
    if len(skills) < 5:
        warnings.append("skill coverage is thin")
    if not any(entry.get("name") == registry.get("default_entrypoint") for entry in registry_entries):
        warnings.append("default entrypoint is not present in registry")
    if len(routing_rules) < 20:
        warnings.append("routing rule coverage is thin")
    missing_names = [path.name for path, name in zip(agents, agent_names) if not name]
    if missing_names:
        warnings.append(f"agents missing names: {', '.join(missing_names)}")

    return {
        "agents": len(agents),
        "prompts": len(prompts),
        "instructions": len(instructions),
        "skills": len(skills),
        "workflows": len(workflows),
        "scripts": len(scripts),
        "registry_agents": len(registry_entries),
        "routing_rules": len(routing_rules),
        "registry_categories": dict(sorted(categories.items())),
        "registry_levels": dict(sorted(levels.items())),
        "warnings": warnings,
    }


def to_markdown(health: dict) -> str:
    lines = [
        "# Agent Hub Health",
        "",
        "| Surface | Count |",
        "| --- | ---: |",
        f"| Agents | {health['agents']} |",
        f"| Registry agents | {health['registry_agents']} |",
        f"| Routing rules | {health['routing_rules']} |",
        f"| Prompts | {health['prompts']} |",
        f"| Instructions | {health['instructions']} |",
        f"| Skills | {health['skills']} |",
        f"| Workflows | {health['workflows']} |",
        f"| Scripts | {health['scripts']} |",
        "",
        "## Registry Categories",
        "",
    ]
    for category, count in health["registry_categories"].items():
        lines.append(f"- {category}: {count}")
    lines.extend(["", "## Warnings", ""])
    if health["warnings"]:
        lines.extend(f"- {warning}" for warning in health["warnings"])
    else:
        lines.append("- None.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Print JSON instead of markdown")
    args = parser.parse_args()

    health = collect_health()
    if args.json:
        print(json.dumps(health, indent=2, sort_keys=True))
    else:
        print(to_markdown(health), end="")

    if health["warnings"]:
        print("Agent hub audit produced warnings.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
