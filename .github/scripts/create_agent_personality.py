"""Create a new agent personality from a validated JSON spec."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
REGISTRY_PATH = REPO_ROOT / ".github" / "agent-registry.json"
ROUTING_PATH = REPO_ROOT / ".github" / "routing-rules.json"

REQUIRED_FIELDS = {
    "name",
    "description",
    "level",
    "category",
    "primary_capabilities",
    "mission",
    "scope",
    "collaboration",
    "quality_gates",
    "routing_keywords",
}


def slugify_name(name: str) -> str:
    parts = re.findall(r"[A-Za-z0-9]+", name)
    return "-".join(part[:1].upper() + part[1:] for part in parts)


def load_spec(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("personality spec must be a JSON object")
    return payload


def validate_spec(spec: dict) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_FIELDS - set(spec))
    for field in missing:
        errors.append(f"missing required field: {field}")

    name = str(spec.get("name", "")).strip()
    if not re.fullmatch(r"[A-Z][A-Za-z0-9 ]+", name):
        errors.append("name must be title-style words using letters, digits, and spaces")
    level = spec.get("level")
    if not isinstance(level, int) or level < 1 or level > 3:
        errors.append("level must be an integer from 1 to 3")
    for field in (
        "primary_capabilities",
        "scope",
        "collaboration",
        "quality_gates",
        "routing_keywords",
    ):
        value = spec.get(field)
        if not isinstance(value, list) or not value:
            errors.append(f"{field} must be a non-empty list")
        elif not all(isinstance(item, str) and item.strip() for item in value):
            errors.append(f"{field} must contain only non-empty strings")
    for field in ("description", "category", "mission"):
        if not str(spec.get(field, "")).strip():
            errors.append(f"{field} must be a non-empty string")
    secondary = spec.get("secondary_agents", [])
    if secondary and not isinstance(secondary, list):
        errors.append("secondary_agents must be a list when provided")
    evidence_count = spec.get("evidence_count")
    if evidence_count is not None and (
        not isinstance(evidence_count, int) or evidence_count < 0
    ):
        errors.append("evidence_count must be a non-negative integer when provided")
    return errors


def load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def load_routing() -> dict:
    return json.loads(ROUTING_PATH.read_text(encoding="utf-8"))


def agent_path_for(name: str) -> Path:
    return AGENTS_DIR / f"{slugify_name(name)}.agent.md"


def render_agent(spec: dict) -> str:
    scope = "\n".join(f"- {item}" for item in spec["scope"])
    collaboration = "\n".join(f"- {item}" for item in spec["collaboration"])
    gates = "\n".join(f"- {item}" for item in spec["quality_gates"])
    return f"""---
name: "{spec['name']}"
description: "{spec['description']}"
tools: ["read", "search", "edit", "execute", "agent"]
user-invocable: true
---

You are the {spec['name']}.

Mission: {spec['mission']}

## Scope

{scope}

## Collaboration

{collaboration}

## Rules

- Stay inside the mission unless the Orchestrator explicitly expands scope.
- Ask for missing assumptions only when proceeding would create material risk.
- Return concise, validated specialist output to the coordinating manager.
- Surface overlap with existing agents instead of silently duplicating work.

## Quality Gates

{gates}

## Output Contract

- Decision or specialist recommendation
- Evidence used
- Assumptions and gaps
- Validation performed or required
"""


def update_registry(spec: dict, agent_file: Path) -> None:
    registry = load_registry()
    agents = registry["agents"]
    entry = {
        "name": spec["name"],
        "file": str(agent_file.relative_to(REPO_ROOT)).replace("\\", "/"),
        "level": spec["level"],
        "category": spec["category"],
        "primary_capabilities": spec["primary_capabilities"],
    }
    agents.append(entry)
    agents.sort(key=lambda item: (item.get("level", 99), item.get("category", ""), item["name"]))
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")


def update_routing(spec: dict) -> None:
    routing = load_routing()
    rule_id = re.sub(r"[^a-z0-9]+", "_", spec["name"].lower()).strip("_")
    if any(rule.get("id") == rule_id for rule in routing["rules"]):
        return
    routing["rules"].append(
        {
            "id": rule_id,
            "description": spec["description"],
            "keywords": spec["routing_keywords"],
            "primary": spec["name"],
            "secondary": spec.get("secondary_agents", []),
            "validation": "agent-specific validation and hub checks",
        }
    )
    ROUTING_PATH.write_text(json.dumps(routing, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True, help="Path to personality spec JSON")
    parser.add_argument("--apply", action="store_true", help="Create files and update registry")
    parser.add_argument("--dry-run", action="store_true", help="Print planned changes")
    parser.add_argument("--update-routing", action="store_true", help="Add a routing rule when applying")
    parser.add_argument("--force", action="store_true", help="Overwrite existing agent file")
    args = parser.parse_args()

    try:
        spec = load_spec(Path(args.spec))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Could not read personality spec: {exc}", file=sys.stderr)
        return 2

    errors = validate_spec(spec)
    if errors:
        print("Personality spec validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    registry = load_registry()
    existing_names = {entry["name"] for entry in registry["agents"]}
    agent_file = agent_path_for(spec["name"])
    if spec["name"] in existing_names and not args.force:
        print(f"Agent already exists in registry: {spec['name']}", file=sys.stderr)
        return 1
    if agent_file.exists() and not args.force:
        print(f"Agent file already exists: {agent_file.relative_to(REPO_ROOT)}", file=sys.stderr)
        return 1

    rendered = render_agent(spec)
    if args.dry_run or not args.apply:
        print(f"Would create {agent_file.relative_to(REPO_ROOT)}")
        print(f"Would add registry entry for {spec['name']}")
        if args.update_routing:
            print(f"Would add routing rule for {spec['name']}")
        print("")
        print(rendered)
        return 0

    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    agent_file.write_text(rendered, encoding="utf-8")
    update_registry(spec, agent_file)
    if args.update_routing:
        update_routing(spec)
    print(f"Created {agent_file.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
