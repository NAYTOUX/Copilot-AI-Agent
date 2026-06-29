"""Validate machine-readable Agent Hub contracts beyond basic JSON parsing."""

from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}


def load_json(relative_path: str) -> dict:
    path = REPO_ROOT / relative_path
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{relative_path}: top-level payload must be an object")
    return payload


def validate_agent_registry(errors: list[str]) -> set[str]:
    path = ".github/agent-registry.json"
    payload = load_json(path)
    agents = payload.get("agents")
    if payload.get("schema_version") != 1:
        errors.append(f"{path}: schema_version must be 1")
    if not isinstance(agents, list) or not agents:
        errors.append(f"{path}: agents must be a non-empty list")
        return set()

    names: set[str] = set()
    files: set[str] = set()
    for index, agent in enumerate(agents):
        if not isinstance(agent, dict):
            errors.append(f"{path}: agents[{index}] must be an object")
            continue
        name = str(agent.get("name", "")).strip()
        file_name = str(agent.get("file", "")).strip()
        level = agent.get("level")
        capabilities = agent.get("primary_capabilities")
        if not re.fullmatch(r"[A-Z][A-Za-z0-9 ]+", name):
            errors.append(f"{path}: invalid agent name at agents[{index}]")
        if name in names:
            errors.append(f"{path}: duplicate agent name '{name}'")
        names.add(name)
        if file_name in files:
            errors.append(f"{path}: duplicate agent file '{file_name}'")
        files.add(file_name)
        if not isinstance(level, int) or level < 0 or level > 3:
            errors.append(f"{path}: agent '{name}' level must be an integer from 0 to 3")
        if not isinstance(capabilities, list) or not capabilities:
            errors.append(f"{path}: agent '{name}' primary_capabilities must be non-empty")
        elif not all(isinstance(item, str) and item.strip() for item in capabilities):
            errors.append(f"{path}: agent '{name}' primary_capabilities must be strings")

    if payload.get("default_entrypoint") not in names:
        errors.append(f"{path}: default_entrypoint must reference a registered agent")
    return names


def validate_routing_cases(errors: list[str], known_agents: set[str]) -> None:
    path = ".github/evals/routing-cases.json"
    payload = load_json(path)
    if payload.get("schema_version") != 1:
        errors.append(f"{path}: schema_version must be 1")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append(f"{path}: cases must be a non-empty list")
        return

    seen_ids: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"{path}: cases[{index}] must be an object")
            continue
        case_id = str(case.get("id", "")).strip()
        if not re.fullmatch(r"[a-z0-9_]+", case_id):
            errors.append(f"{path}: cases[{index}] id must use lowercase snake_case")
        if case_id in seen_ids:
            errors.append(f"{path}: duplicate case id '{case_id}'")
        seen_ids.add(case_id)
        if not str(case.get("text", "")).strip():
            errors.append(f"{path}: case '{case_id}' missing text")

        expected = case.get("expected_agents")
        forbidden = case.get("forbidden_agents", [])
        if not isinstance(expected, list) or not expected:
            errors.append(f"{path}: case '{case_id}' expected_agents must be non-empty")
            expected = []
        if not isinstance(forbidden, list):
            errors.append(f"{path}: case '{case_id}' forbidden_agents must be a list")
            forbidden = []
        for agent in [*expected, *forbidden]:
            if agent not in known_agents:
                errors.append(f"{path}: case '{case_id}' references unknown agent '{agent}'")
        overlap = sorted(set(expected).intersection(forbidden))
        if overlap:
            errors.append(
                f"{path}: case '{case_id}' has agents both expected and forbidden: {', '.join(overlap)}"
            )
        if case.get("min_confidence") not in CONFIDENCE_ORDER:
            errors.append(f"{path}: case '{case_id}' min_confidence must be low, medium, or high")


def validate_manifest(errors: list[str]) -> None:
    path = ".github/agent-hub-manifest.json"
    payload = load_json(path)
    commands = payload.get("required_commands")
    if payload.get("schema_version") != 1:
        errors.append(f"{path}: schema_version must be 1")
    if not isinstance(commands, list) or not commands:
        errors.append(f"{path}: required_commands must be a non-empty list")
        return
    seen: set[str] = set()
    for command in commands:
        if not isinstance(command, str) or not command.startswith("python "):
            errors.append(f"{path}: required command must be a python command: {command}")
        if command in seen:
            errors.append(f"{path}: duplicate required command: {command}")
        seen.add(command)
    release_gate = payload.get("release_gate")
    if not isinstance(release_gate, dict):
        errors.append(f"{path}: release_gate must be an object")
        return
    for key in (
        "requires_clean_generated_docs",
        "requires_routing_eval",
        "requires_memory_append_only",
        "requires_sensitive_content_scan",
        "requires_no_audit_warnings",
        "requires_tests",
    ):
        if release_gate.get(key) is not True:
            errors.append(f"{path}: release_gate.{key} must be true")


def validate_personality_spec_example(errors: list[str]) -> None:
    path = "examples/personality-spec.json"
    payload = load_json(path)
    required = {
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
    missing = sorted(required - set(payload))
    for field in missing:
        errors.append(f"{path}: missing required field {field}")
    if not isinstance(payload.get("level"), int) or payload.get("level") not in {1, 2, 3}:
        errors.append(f"{path}: level must be 1, 2, or 3")
    for field in (
        "primary_capabilities",
        "scope",
        "collaboration",
        "quality_gates",
        "routing_keywords",
    ):
        value = payload.get(field)
        if not isinstance(value, list) or not value:
            errors.append(f"{path}: {field} must be a non-empty list")
        elif not all(isinstance(item, str) and item.strip() for item in value):
            errors.append(f"{path}: {field} must contain non-empty strings")


def main() -> int:
    errors: list[str] = []
    try:
        known_agents = validate_agent_registry(errors)
        validate_routing_cases(errors, known_agents)
        validate_manifest(errors)
        validate_personality_spec_example(errors)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"JSON contract validation could not run: {exc}")
        return 2

    if errors:
        print("JSON contract validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("JSON contract validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
