"""Validate an agent report JSON payload against the local report contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / ".github" / "schemas" / "agent-report.schema.json"


def load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")
    return payload


def validate(payload: dict, schema: dict) -> list[str]:
    errors: list[str] = []
    required = schema.get("required", [])
    for field in required:
        if field not in payload:
            errors.append(f"missing required field: {field}")

    properties = schema.get("properties", {})
    allowed = set(properties)
    for field in payload:
        if field not in allowed:
            errors.append(f"unsupported field: {field}")

    for field, rules in properties.items():
        if field not in payload:
            continue
        value = payload[field]
        expected_type = rules.get("type")
        if expected_type == "string":
            if not isinstance(value, str):
                errors.append(f"{field}: must be a string")
                continue
            if rules.get("minLength") and not value.strip():
                errors.append(f"{field}: must not be empty")
        elif expected_type == "array":
            if not isinstance(value, list):
                errors.append(f"{field}: must be an array")
                continue
            item_type = rules.get("items", {}).get("type")
            if item_type == "string":
                for index, item in enumerate(value):
                    if not isinstance(item, str):
                        errors.append(f"{field}[{index}]: must be a string")
            elif item_type == "object":
                item_rules = rules.get("items", {})
                allowed_item_fields = set(item_rules.get("properties", {}))
                required_item_fields = item_rules.get("required", [])
                for index, item in enumerate(value):
                    if not isinstance(item, dict):
                        errors.append(f"{field}[{index}]: must be an object")
                        continue
                    for required_field in required_item_fields:
                        if required_field not in item:
                            errors.append(
                                f"{field}[{index}]: missing required field {required_field}"
                            )
                    for item_field, item_value in item.items():
                        if item_field not in allowed_item_fields:
                            errors.append(
                                f"{field}[{index}]: unsupported field {item_field}"
                            )
                            continue
                        item_schema = item_rules["properties"][item_field]
                        if item_schema.get("type") == "string" and not isinstance(
                            item_value, str
                        ):
                            errors.append(
                                f"{field}[{index}].{item_field}: must be a string"
                            )
                        if item_schema.get("minLength") and isinstance(
                            item_value, str
                        ) and not item_value.strip():
                            errors.append(
                                f"{field}[{index}].{item_field}: must not be empty"
                            )
                        enum = item_schema.get("enum")
                        if enum and item_value not in enum:
                            errors.append(
                                f"{field}[{index}].{item_field}: unsupported value '{item_value}'"
                            )

        enum = rules.get("enum")
        if enum and value not in enum:
            errors.append(f"{field}: unsupported value '{value}'")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", help="Path to a JSON report payload")
    parser.add_argument("--schema", default=str(SCHEMA_PATH))
    args = parser.parse_args()

    try:
        payload = load_json(Path(args.payload))
        schema = load_json(Path(args.schema))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Could not load report payload: {exc}", file=sys.stderr)
        return 2

    errors = validate(payload, schema)
    if errors:
        print("Agent report payload validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Agent report payload validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
