"""Generate Orchestrator learning profile from relationships and memory signals."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RELATIONSHIP_PATH = REPO_ROOT / ".github" / "agent-relationship-map.json"
EFFECTIVENESS_PATH = REPO_ROOT / ".github" / "memory" / "agent-effectiveness-profile.md"
LEDGER_PATH = REPO_ROOT / ".github" / "memory" / "personality-evolution-ledger.md"
OUTPUT_PATH = REPO_ROOT / ".github" / "memory" / "orchestrator-learning-profile.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def signature(parts: list[str]) -> str:
    payload = "\n---part---\n".join(parts)
    return hashlib.sha1(payload.encode("utf-8"), usedforsecurity=False).hexdigest()[:12]


def extract_recommendations(effectiveness: str) -> list[str]:
    marker = "## Recommendations"
    if marker not in effectiveness:
        return []
    section = effectiveness.split(marker, 1)[1]
    recommendations: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            recommendations.append(stripped[2:])
    return recommendations


def render() -> str:
    relationships = read(RELATIONSHIP_PATH)
    effectiveness = read(EFFECTIVENESS_PATH)
    ledger = read(LEDGER_PATH)
    sig = signature([relationships, effectiveness, ledger])
    recommendations = extract_recommendations(effectiveness)
    lines = [
        "# Orchestrator Learning Profile",
        "",
        "Generated from relationship, effectiveness, and personality-evolution memory.",
        "",
        "## Snapshot",
        "",
        f"- Signal signature: `{sig}`",
        f"- Relationship map bytes: {len(relationships)}",
        f"- Effectiveness profile bytes: {len(effectiveness)}",
        f"- Personality ledger bytes: {len(ledger)}",
        "",
        "## Active Learning Rules",
        "",
        "- Prefer agents with strong validation-backed usage signals.",
        "- Route repeated low-usefulness signals to Personality Evolution Governor.",
        "- Treat missing validation in downstream reports as a quality gap.",
        "- Do not auto-promote personality proposals without evidence threshold.",
        "- Use `.github/agent-relationship-map.json` to resolve collaboration and escalation.",
        "",
        "## Current Recommendations",
        "",
    ]
    if recommendations:
        lines.extend(f"- {item}" for item in recommendations)
    else:
        lines.append("- No generated recommendations yet.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    expected = render()
    current = read(OUTPUT_PATH)
    if args.write:
        OUTPUT_PATH.write_text(expected, encoding="utf-8")
        print(f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)}")
        return 0
    if args.check:
        if current != expected:
            print(
                f"{OUTPUT_PATH.relative_to(REPO_ROOT)} is stale. Run "
                "python .github/scripts/update_orchestrator_learning_profile.py --write"
            )
            return 1
        print("Orchestrator learning profile is current.")
        return 0
    print(expected, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
