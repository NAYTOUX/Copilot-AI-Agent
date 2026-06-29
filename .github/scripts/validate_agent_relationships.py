"""Validate agent relationship map against the registry."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / ".github" / "agent-registry.json"
RELATIONSHIP_PATH = REPO_ROOT / ".github" / "agent-relationship-map.json"


def main() -> int:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    payload = json.loads(RELATIONSHIP_PATH.read_text(encoding="utf-8"))
    known = {entry["name"] for entry in registry["agents"]}
    errors: list[str] = []

    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if payload.get("default_entrypoint") not in known:
        errors.append("default_entrypoint must reference a registered agent")

    relationships = payload.get("relationships")
    if not isinstance(relationships, list) or not relationships:
        errors.append("relationships must be a non-empty list")
        relationships = []

    seen: set[str] = set()
    for index, relation in enumerate(relationships):
        if not isinstance(relation, dict):
            errors.append(f"relationships[{index}] must be an object")
            continue
        agent = relation.get("agent")
        if agent not in known:
            errors.append(f"unknown relationship agent: {agent}")
            continue
        if agent in seen:
            errors.append(f"duplicate relationship entry: {agent}")
        seen.add(agent)
        reports_to = relation.get("reports_to")
        if reports_to is not None and reports_to not in known:
            errors.append(f"{agent}: reports_to references unknown agent {reports_to}")
        for field in ("manages", "collaborates_with", "escalates_to"):
            value = relation.get(field)
            if not isinstance(value, list):
                errors.append(f"{agent}: {field} must be a list")
                continue
            for target in value:
                if target not in known:
                    errors.append(f"{agent}: {field} references unknown agent {target}")
                if target == agent:
                    errors.append(f"{agent}: {field} must not reference itself")

    if "Universal Orchestrator" not in seen:
        errors.append("Universal Orchestrator must have an explicit relationship entry")

    if errors:
        print("Agent relationship validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Agent relationship validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
