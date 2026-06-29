"""Generate an effectiveness profile from inbox usage reports."""

from __future__ import annotations

import argparse
import hashlib
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INBOX_DIR = REPO_ROOT / ".github" / "memory" / "inbox"
OUTPUT_PATH = REPO_ROOT / ".github" / "memory" / "agent-effectiveness-profile.md"


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    values: dict[str, str] = {}
    if not match:
        return values
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep:
            values[key.strip()] = value.strip()
    return values


def parse_section_list(text: str, heading: str) -> list[str]:
    pattern = rf"## {re.escape(heading)}\r?\n\r?\n(.*?)(?:\r?\n## |\Z)"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return []
    section = match.group(1)
    items: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip().strip("`"))
    return items


def parse_section_text(text: str, heading: str) -> str:
    pattern = rf"## {re.escape(heading)}\r?\n\r?\n(.*?)(?:\r?\n## |\Z)"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""


def parse_agent_feedback(text: str) -> list[dict[str, str]]:
    pattern = r"## Agent Feedback\r?\n\r?\n(.*?)(?:\r?\n## |\Z)"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return []
    feedback: list[dict[str, str]] = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        parts = [part.strip() for part in stripped[2:].split("|")]
        if not parts:
            continue
        item = {"agent": parts[0]}
        for part in parts[1:]:
            key, sep, value = part.partition("=")
            if sep:
                item[key.strip()] = value.strip()
        feedback.append(item)
    return feedback


def collect_reports() -> list[dict]:
    reports: list[dict] = []
    for path in sorted(INBOX_DIR.glob("*.md")):
        if path.name.upper() == "README.MD" or path.name.startswith("_"):
            continue
        text = path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)
        reports.append(
            {
                "file": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
                "frontmatter": frontmatter,
                "selected_agents": parse_section_list(text, "Selected Agents"),
                "outcome": parse_section_text(text, "Outcome"),
                "validation": parse_section_text(text, "Validation"),
                "summary": parse_section_text(text, "Summary"),
                "agent_feedback": parse_agent_feedback(text),
            }
        )
    return reports


def score_reports(reports: list[dict]) -> dict:
    outcome_counts: Counter[str] = Counter()
    agent_counts: Counter[str] = Counter()
    agent_outcomes: dict[str, Counter[str]] = defaultdict(Counter)
    usefulness_counts: dict[str, Counter[str]] = defaultdict(Counter)
    validation_mentions: Counter[str] = Counter()

    for report in reports:
        outcome = report["outcome"] or "unknown"
        outcome_counts[outcome] += 1
        validation = report["validation"].lower()
        if validation and validation != "not provided.":
            validation_mentions["provided"] += 1
        else:
            validation_mentions["missing"] += 1
        for agent in report["selected_agents"]:
            agent_counts[agent] += 1
            agent_outcomes[agent][outcome] += 1
        for item in report.get("agent_feedback", []):
            agent = item.get("agent", "").strip()
            usefulness = item.get("usefulness", "").strip() or "unknown"
            if agent:
                agent_counts[agent] += 0
                usefulness_counts[agent][usefulness] += 1

    return {
        "outcome_counts": outcome_counts,
        "agent_counts": agent_counts,
        "agent_outcomes": agent_outcomes,
        "usefulness_counts": usefulness_counts,
        "validation_mentions": validation_mentions,
    }


def render_profile(reports: list[dict], scores: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    outcome_counts = scores["outcome_counts"]
    agent_counts = scores["agent_counts"]
    validation_mentions = scores["validation_mentions"]
    lines = [
        "# Agent Effectiveness Profile",
        "",
        "Generated from downstream usage reports and inbox metadata.",
        "",
        f"Last generated: {now}",
        f"Signal signature: `{signal_signature(reports, scores)}`",
        "",
        "## Snapshot",
        "",
        f"- Reports analyzed: {len(reports)}",
        f"- Agents observed: {', '.join(sorted(agent_counts)) if agent_counts else 'none'}",
        f"- Outcome counts: {', '.join(f'{k}={v}' for k, v in sorted(outcome_counts.items())) if outcome_counts else 'none'}",
        f"- Validation evidence: provided={validation_mentions['provided']}, missing={validation_mentions['missing']}",
        "",
        "## Agent Signals",
        "",
    ]
    if agent_counts:
        for agent, count in sorted(agent_counts.items()):
            outcomes = scores["agent_outcomes"][agent]
            outcome_text = ", ".join(f"{key}={value}" for key, value in sorted(outcomes.items()))
            usefulness = scores["usefulness_counts"][agent]
            usefulness_text = (
                ", ".join(f"{key}={value}" for key, value in sorted(usefulness.items()))
                if usefulness
                else "none"
            )
            lines.append(
                f"- `{agent}`: uses={count}; outcomes={outcome_text or 'none'}; usefulness={usefulness_text}"
            )
    else:
        lines.append("- None.")

    recommendations: list[str] = []
    if validation_mentions["missing"] > validation_mentions["provided"]:
        recommendations.append("Require stronger validation evidence in usage reports.")
    if outcome_counts["blocked"] or outcome_counts["failed"]:
        recommendations.append("Review blocked or failed sessions for routing or personality gaps.")
    harmful_agents = [
        agent
        for agent, counts in scores["usefulness_counts"].items()
        if counts["harmful"] or counts["low"]
    ]
    if harmful_agents:
        recommendations.append(
            "Review low-usefulness agent signals: " + ", ".join(sorted(harmful_agents))
        )
    if not recommendations:
        recommendations.append("No usage evidence requiring action yet.")

    lines.extend(["", "## Recommendations", ""])
    lines.extend(f"- {item}" for item in recommendations)
    return "\n".join(lines) + "\n"


def signal_signature(reports: list[dict], scores: dict) -> str:
    payload = "|".join(
        [
            f"reports={len(reports)}",
            "outcomes="
            + ",".join(f"{k}:{v}" for k, v in sorted(scores["outcome_counts"].items())),
            "agents="
            + ",".join(f"{k}:{v}" for k, v in sorted(scores["agent_counts"].items())),
            "usefulness="
            + ",".join(
                f"{agent}:{kind}:{value}"
                for agent, counts in sorted(scores["usefulness_counts"].items())
                for kind, value in sorted(counts.items())
            ),
            "validation="
            + ",".join(
                f"{k}:{v}" for k, v in sorted(scores["validation_mentions"].items())
            ),
        ]
    )
    return hashlib.sha1(payload.encode("utf-8"), usedforsecurity=False).hexdigest()[:12]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    reports = collect_reports()
    scores = score_reports(reports)
    expected = render_profile(reports, scores)
    current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
    signature = signal_signature(reports, scores)
    if f"Signal signature: `{signature}`" in current:
        expected = current if current.endswith("\n") else f"{current}\n"

    if args.write:
        OUTPUT_PATH.write_text(expected, encoding="utf-8")
        print(f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)}")
        return 0
    if args.check:
        if current != expected:
            print(
                f"{OUTPUT_PATH.relative_to(REPO_ROOT)} is stale. Run "
                "python .github/scripts/update_agent_effectiveness_profile.py --write"
            )
            return 1
        print("Agent effectiveness profile is current.")
        return 0
    print(expected, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
