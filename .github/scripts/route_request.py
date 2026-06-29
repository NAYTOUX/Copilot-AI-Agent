"""Route a user request to the most relevant agents using deterministic rules."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RULES_PATH = REPO_ROOT / ".github" / "routing-rules.json"
REGISTRY_PATH = REPO_ROOT / ".github" / "agent-registry.json"


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def count_keyword(text: str, keyword: str) -> int:
    keyword = keyword.lower().strip()
    if not keyword:
        return 0
    if " " in keyword or keyword.startswith("."):
        return text.count(keyword)
    return len(re.findall(rf"\b{re.escape(keyword)}\b", text))


def load_rules() -> dict:
    return json.loads(RULES_PATH.read_text(encoding="utf-8"))


def load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def route_request(text: str, *, max_rules: int = 5, max_agents: int = 6) -> dict:
    rules_payload = load_rules()
    registry = load_registry()
    known_agents = {entry["name"] for entry in registry["agents"]}
    normalized = normalize(text)

    matches: list[dict] = []
    for rule in rules_payload["rules"]:
        excluded = False
        for pattern in rule.get("exclude_patterns", []):
            if str(pattern).lower() in normalized:
                excluded = True
                break
        if excluded:
            continue
        keyword_hits: dict[str, int] = {}
        score = 0
        for keyword in rule.get("keywords", []):
            hits = count_keyword(normalized, str(keyword))
            if hits:
                keyword_hits[str(keyword)] = hits
                score += hits
        if score:
            primary = rule["primary"]
            secondary = list(rule.get("secondary", []))
            unknown = [agent for agent in [primary, *secondary] if agent not in known_agents]
            matches.append(
                {
                    "id": rule["id"],
                    "description": rule["description"],
                    "score": score,
                    "primary": primary,
                    "secondary": secondary,
                    "validation": rule.get("validation", ""),
                    "keyword_hits": keyword_hits,
                    "unknown_agents": unknown,
                }
            )

    matches.sort(key=lambda item: (-item["score"], item["id"]))
    selected = matches[:max_rules]
    if not selected:
        selected_agents = list(rules_payload.get("fallback_agents", []))
        agent_scores: dict[str, int] = {agent: 0 for agent in selected_agents}
        confidence = "low"
    else:
        agent_scores = {}
        first_seen: dict[str, int] = {}
        ordinal = 0
        for match in selected:
            primary = match["primary"]
            if primary not in first_seen:
                first_seen[primary] = ordinal
                ordinal += 1
            agent_scores[primary] = agent_scores.get(primary, 0) + match["score"] * 3
            for agent in match["secondary"]:
                if agent not in first_seen:
                    first_seen[agent] = ordinal
                    ordinal += 1
                agent_scores[agent] = agent_scores.get(agent, 0) + match["score"]
        selected_agents = [
            agent
            for agent, _ in sorted(
                agent_scores.items(),
                key=lambda item: (-item[1], first_seen.get(item[0], 999), item[0]),
            )[:max_agents]
        ]
        top_score = selected[0]["score"]
        confidence = "high" if top_score >= 3 else "medium"

    return {
        "request": text,
        "confidence": confidence,
        "selected_agents": selected_agents,
        "agent_scores": agent_scores,
        "matches": selected,
        "fallback_used": not bool(selected),
    }


def read_request(args: argparse.Namespace) -> str:
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if args.text:
        return args.text
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise ValueError("provide --text, --file, or stdin")


def to_markdown(result: dict) -> str:
    lines = [
        "# Routing Recommendation",
        "",
        f"- Confidence: `{result['confidence']}`",
        f"- Fallback used: `{str(result['fallback_used']).lower()}`",
        f"- Selected agents: {', '.join(result['selected_agents'])}",
        "",
        "## Matched Rules",
        "",
    ]
    if not result["matches"]:
        lines.append("- No rule matched; use fallback agents to clarify scope.")
    else:
        for match in result["matches"]:
            hits = ", ".join(f"{key}={value}" for key, value in match["keyword_hits"].items())
            lines.extend(
                [
                    f"### {match['id']}",
                    "",
                    f"- Score: {match['score']}",
                    f"- Primary: {match['primary']}",
                    f"- Secondary: {', '.join(match['secondary']) if match['secondary'] else 'none'}",
                    f"- Validation: {match['validation']}",
                    f"- Hits: {hits}",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", default="", help="Request text to route")
    parser.add_argument("--file", default="", help="Read request text from file")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    parser.add_argument("--max-rules", type=int, default=5)
    parser.add_argument("--max-agents", type=int, default=6)
    args = parser.parse_args()

    try:
        text = read_request(args)
    except (OSError, ValueError) as exc:
        print(f"Could not read request: {exc}", file=sys.stderr)
        return 2

    result = route_request(
        text,
        max_rules=max(1, args.max_rules),
        max_agents=max(1, args.max_agents),
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(to_markdown(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
