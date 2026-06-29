"""Generate docs/CAPABILITY_MATRIX.md from .github/agent-registry.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / ".github" / "agent-registry.json"
OUTPUT_PATH = REPO_ROOT / "docs" / "CAPABILITY_MATRIX.md"


CAPABILITY_LABELS = {
    "Universal Orchestrator": "Orchestration and final synthesis",
    "Chief of Staff": "Scope clarification",
    "Agent System Governor": "Agent/prompt/skill governance",
    "Memory Governor": "Memory and information relay",
    "Delivery Lead": "Multi-file delivery",
    "Quality Governor": "Review and release quality",
    "Repo Explorer": "Read-only repository discovery",
    "Software Architect": "Architecture decisions",
    "Programming Language Lead": "Language routing",
    "Python Worker": "Python",
    "JavaScript TypeScript Worker": "JavaScript/TypeScript",
    "Frontend UI Worker": "Frontend UI",
    "Mobile App Worker": "Mobile apps",
    "Backend API Worker": "Backend/API",
    "Database Worker": "Database/SQL",
    "Debugger": "Debugging",
    "Testing Worker": "Testing",
    "Performance Optimizer": "Performance",
    "AI Architect": "AI routing/prompts/models",
    "Machine Learning Worker": "Machine learning",
    "Data Finance Worker": "Finance/data/markets",
    "Macro Economist Worker": "Macro/country data",
    "Research Worker": "External research",
    "Security Worker": "Security/privacy",
    "Dependency Supply Chain Worker": "Dependencies/supply chain",
    "Legal Compliance Worker": "Legal/compliance",
    "DevOps CI Worker": "CI/CD",
    "Cloud Infrastructure Worker": "Cloud infrastructure",
    "Observability Worker": "Observability/incidents",
    "Documentation Worker": "Documentation",
    "Product Strategy Worker": "Product requirements",
    "Automation Workflow Worker": "Automation scripts",
    "Translation Localization Worker": "Translation/localization",
}


def build_matrix() -> str:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    agents = registry["agents"]
    lines = [
        "# Capability Matrix",
        "",
        "Generated from `.github/agent-registry.json`.",
        "",
        "Routing rules live in `.github/routing-rules.json` and can be tested with",
        "`.github/scripts/route_request.py`.",
        "",
        "| Capability | Primary agent | Category | Level |",
        "| --- | --- | --- | ---: |",
    ]
    for entry in agents:
        name = entry["name"]
        capability = CAPABILITY_LABELS.get(name)
        if not capability:
            capability = ", ".join(entry.get("primary_capabilities", [])) or name
        lines.append(
            f"| {capability} | {name} | {entry.get('category', '')} | {entry.get('level', '')} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if output is stale")
    parser.add_argument("--write", action="store_true", help="Write the output file")
    args = parser.parse_args()

    expected = build_matrix()
    current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""

    if args.write:
        OUTPUT_PATH.write_text(expected, encoding="utf-8")
        print(f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)}")
        return 0

    if args.check:
        if current != expected:
            print(
                f"{OUTPUT_PATH.relative_to(REPO_ROOT)} is stale. Run "
                "python .github/scripts/generate_capability_matrix.py --write",
                file=sys.stderr,
            )
            return 1
        print("Capability matrix is current.")
        return 0

    print(expected, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

