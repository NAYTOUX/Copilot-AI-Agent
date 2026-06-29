"""Analyze memory and inbox reports for personality evolution signals."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INBOX_DIR = REPO_ROOT / ".github" / "memory" / "inbox"
FEEDBACK_PATH = REPO_ROOT / ".github" / "memory" / "orchestrator-feedback-loop.md"
LEDGER_PATH = REPO_ROOT / ".github" / "memory" / "personality-evolution-ledger.md"
PROPOSAL_DIR = REPO_ROOT / ".github" / "personality-proposals"


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    values: dict[str, str] = {}
    if not match:
        return values
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep:
            values[key.strip()] = value.strip()
    return values


def collect_reports() -> list[dict[str, str]]:
    reports: list[dict[str, str]] = []
    for path in sorted(INBOX_DIR.glob("*.md")):
        if path.name.upper() == "README.MD" or path.name.startswith("_"):
            continue
        frontmatter = parse_frontmatter(path)
        text = path.read_text(encoding="utf-8")
        frontmatter["file"] = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        frontmatter["text"] = text
        reports.append(frontmatter)
    return reports


def collect_feedback_text() -> str:
    return FEEDBACK_PATH.read_text(encoding="utf-8") if FEEDBACK_PATH.exists() else ""


def build_signals(reports: list[dict[str, str]], feedback_text: str) -> dict:
    category_counts = Counter(report.get("category", "unknown") for report in reports)
    action_counts = Counter(report.get("requested_action", "unknown") for report in reports)
    text = "\n".join(report.get("text", "") for report in reports) + "\n" + feedback_text
    normalized = text.lower()
    gap_terms = Counter()
    for term in (
        "missing agent",
        "new personality",
        "personality gap",
        "wrong route",
        "routing gap",
        "specialist gap",
        "too broad",
        "overlap",
    ):
        gap_terms[term] = normalized.count(term)
    candidates = extract_personality_candidates(text)
    return {
        "report_count": len(reports),
        "category_counts": dict(sorted(category_counts.items())),
        "action_counts": dict(sorted(action_counts.items())),
        "gap_terms": {key: value for key, value in sorted(gap_terms.items()) if value},
        "candidates": dict(sorted(candidates.items())),
    }


def extract_personality_candidates(text: str) -> Counter[str]:
    candidates: Counter[str] = Counter()
    patterns = (
        r"(?im)^\s*(?:suggested personality|missing agent|new personality)\s*:\s*([A-Za-z][A-Za-z0-9 /_-]{2,80})\s*$",
        r"(?im)^\s*-\s*(?:suggested personality|missing agent|new personality)\s*:\s*([A-Za-z][A-Za-z0-9 /_-]{2,80})\s*$",
    )
    for pattern in patterns:
        for match in re.findall(pattern, text):
            name = normalize_personality_name(match)
            if name:
                candidates[name] += 1
    return candidates


def normalize_personality_name(value: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", value)
    if not words:
        return ""
    normalized = " ".join(word[:1].upper() + word[1:] for word in words[:6])
    if not normalized.endswith(("Worker", "Governor", "Lead", "Architect", "Optimizer")):
        normalized += " Worker"
    return normalized


def recommend(signals: dict) -> list[str]:
    recommendations: list[str] = []
    categories = signals["category_counts"]
    actions = signals["action_counts"]
    gaps = signals["gap_terms"]
    if categories.get("personality", 0) or gaps:
        recommendations.append(
            "Review Personality Evolution Governor output before creating or tuning personalities."
        )
    if actions.get("update-routing", 0) or gaps.get("wrong route", 0) or gaps.get("routing gap", 0):
        recommendations.append("Add or update routing eval cases before changing routing rules.")
    if gaps.get("missing agent", 0) or gaps.get("new personality", 0):
        recommendations.append(
            "Create a personality spec only after overlap check against the registry."
        )
    if signals.get("candidates"):
        recommendations.append("Generate proposal specs for repeated named candidates that meet the evidence threshold.")
    if not recommendations:
        recommendations.append("No personality change recommended from current memory signals.")
    return recommendations


def render_report(signals: dict, recommendations: list[str]) -> str:
    lines = [
        "# Personality Evolution Analysis",
        "",
        f"- Reports analyzed: {signals['report_count']}",
        "",
        "## Category Counts",
        "",
    ]
    if signals["category_counts"]:
        lines.extend(f"- `{key}`: {value}" for key, value in signals["category_counts"].items())
    else:
        lines.append("- None.")
    lines.extend(["", "## Requested Actions", ""])
    if signals["action_counts"]:
        lines.extend(f"- `{key}`: {value}" for key, value in signals["action_counts"].items())
    else:
        lines.append("- None.")
    lines.extend(["", "## Gap Terms", ""])
    if signals["gap_terms"]:
        lines.extend(f"- `{key}`: {value}" for key, value in signals["gap_terms"].items())
    else:
        lines.append("- None.")
    lines.extend(["", "## Candidate Personalities", ""])
    if signals.get("candidates"):
        lines.extend(f"- `{key}`: {value}" for key, value in signals["candidates"].items())
    else:
        lines.append("- None.")
    lines.extend(["", "## Recommendations", ""])
    lines.extend(f"- {item}" for item in recommendations)
    return "\n".join(lines) + "\n"


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:80] or "personality"


def proposal_for(name: str, evidence_count: int) -> dict:
    lower = name.lower()
    if "security" in lower or "privacy" in lower:
        category = "security"
        collaborators = ["Security Worker", "Quality Governor", "Memory Governor"]
    elif "finance" in lower or "risk" in lower or "trading" in lower:
        category = "finance"
        collaborators = ["Data Finance Worker", "Testing Worker", "Security Worker"]
    elif "data" in lower or "analytics" in lower:
        category = "data"
        collaborators = ["Database Worker", "Data Finance Worker", "Testing Worker"]
    elif "ui" in lower or "frontend" in lower:
        category = "frontend"
        collaborators = ["Frontend UI Worker", "Product Strategy Worker", "Quality Governor"]
    else:
        category = "governance"
        collaborators = ["Agent System Governor", "Memory Governor", "Quality Governor"]
    keywords = sorted(set([*name.lower().split(), name.lower()]))
    return {
        "name": name,
        "description": f"Proposed specialist generated from repeated memory signals for {name}.",
        "level": 3,
        "category": category,
        "primary_capabilities": [name.lower(), "memory-derived specialization"],
        "mission": f"Handle recurring work identified by memory signals for {name} with explicit evidence and validation.",
        "scope": [
            "recurring tasks matching the proposed personality name",
            "evidence-backed specialist recommendations",
            "validation requirements for the delegated domain",
        ],
        "collaboration": collaborators,
        "quality_gates": [
            "cite the memory evidence that justified specialist routing",
            "state assumptions and boundaries",
            "provide validation evidence or an explicit validation gap",
        ],
        "routing_keywords": keywords,
        "secondary_agents": collaborators[:2],
        "evidence_count": evidence_count,
    }


def write_proposals(signals: dict, *, min_signals: int) -> list[Path]:
    PROPOSAL_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, count in signals.get("candidates", {}).items():
        if count < min_signals:
            continue
        path = PROPOSAL_DIR / f"{slugify(name)}.json"
        if path.exists():
            continue
        payload = proposal_for(name, count)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        written.append(path)
    return written


def signature(report: str) -> str:
    return hashlib.sha1(report.encode("utf-8"), usedforsecurity=False).hexdigest()[:12]


def append_ledger(report: str) -> bool:
    sig = signature(report)
    existing = LEDGER_PATH.read_text(encoding="utf-8") if LEDGER_PATH.exists() else ""
    if f"Signature: `{sig}`" in existing:
        return False
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = [
        f"### {now} - Automated personality signal analysis",
        "",
        f"- Signature: `{sig}`",
        "- Decision: analysis only.",
        "- Evidence:",
        "",
        report.strip(),
        "",
    ]
    LEDGER_PATH.write_text(existing.rstrip() + "\n\n" + "\n".join(entry), encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-ledger", action="store_true")
    parser.add_argument("--write-proposals", action="store_true")
    parser.add_argument("--min-signals", type=int, default=2)
    args = parser.parse_args()

    reports = collect_reports()
    signals = build_signals(reports, collect_feedback_text())
    recommendations = recommend(signals)
    report = render_report(signals, recommendations)
    print(report, end="")
    if args.write_ledger:
        changed = append_ledger(report)
        print("Ledger updated." if changed else "Ledger already contains this analysis.")
    if args.write_proposals:
        written = write_proposals(signals, min_signals=max(1, args.min_signals))
        if written:
            for path in written:
                print(f"Wrote {path.relative_to(REPO_ROOT)}")
        else:
            print("No personality proposals met the evidence threshold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
