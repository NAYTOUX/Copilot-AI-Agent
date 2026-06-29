"""Build an adaptive Orchestrator profile from feedback-loop history."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FEEDBACK_PATH = REPO_ROOT / ".github" / "memory" / "orchestrator-feedback-loop.md"
OUTPUT_PATH = REPO_ROOT / ".github" / "memory" / "orchestrator-adaptive-profile.md"

SCOPE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "orchestration": ("orchestrator", "agent", "routing", "delegate", "scorecard"),
    "memory": ("memory", "feedback", "profile", "inbox", "provenance", "relay"),
    "validation": ("validate", "validation", "test", "py_compile", "checks"),
    "programming": ("code", "implementation", "python", "typescript", "refactor"),
    "finance": ("finance", "market", "macro", "portfolio", "trading"),
    "security": ("security", "secret", "token", "privacy", "auth"),
    "devops": ("workflow", "github action", "ci", "deploy", "automation"),
}


def extract_prompt_log(text: str) -> str:
    marker = "## Prompt Log"
    index = text.find(marker)
    return text[index + len(marker) :] if index >= 0 else ""


def split_sessions(prompt_log: str) -> list[str]:
    entries = re.split(r"\n### ", prompt_log)
    result: list[str] = []
    for index, entry in enumerate(entries):
        clean = entry.strip()
        if clean:
            result.append(clean if index == 0 else f"### {clean}")
    return result


def extract_field(entry: str, name: str) -> str:
    match = re.search(rf"- \*\*{re.escape(name)}\*\*: (.+)", entry)
    return match.group(1).strip() if match else ""


def infer_scopes(text: str) -> list[str]:
    normalized = text.lower()
    return [
        scope
        for scope, keywords in SCOPE_KEYWORDS.items()
        if any(keyword in normalized for keyword in keywords)
    ]


def signature(sentiments: Counter[str], scopes: list[str], rules: list[str]) -> str:
    payload = "|".join(
        [
            f"liked={sentiments['liked']}",
            f"neutral={sentiments['neutral']}",
            f"disliked={sentiments['disliked']}",
            f"scopes={','.join(scopes)}",
            f"rules={'||'.join(rules)}",
        ]
    )
    return hashlib.sha1(payload.encode("utf-8"), usedforsecurity=False).hexdigest()[:12]


def profile_header() -> str:
    return "\n".join(
        [
            "# Orchestrator Adaptive Profile",
            "",
            "Generated automatically from `.github/memory/orchestrator-feedback-loop.md`.",
            "Append-only policy: each run appends a new snapshot unless the signature already",
            "exists.",
            "",
            "Last generated: generated-by-script",
            "",
            "## Snapshot Log",
            "",
        ]
    )


def build_profile() -> str:
    feedback_text = FEEDBACK_PATH.read_text(encoding="utf-8")
    sessions = split_sessions(extract_prompt_log(feedback_text))
    sentiments: Counter[str] = Counter()
    scope_counts: Counter[str] = Counter()

    for entry in sessions:
        sentiment = extract_field(entry, "Sentiment").lower().strip().rstrip(".!")
        if sentiment in {"liked", "neutral", "disliked"}:
            sentiments[sentiment] += 1
        combined = f"{extract_field(entry, 'Prompt')}\n{extract_field(entry, 'Action')}"
        scope_counts.update(infer_scopes(combined))

    top_scopes = [scope for scope, _ in scope_counts.most_common(5)]
    rules = [
        "Front-load routing before implementation for broad or multi-domain requests.",
        "Use only relevant specialists and keep Orchestrator accountable for synthesis.",
        "Run concrete validation before closeout when files changed.",
    ]
    if "memory" in top_scopes:
        rules.append("Classify durable learning and keep memory append-only.")
    if "finance" in top_scopes:
        rules.append("State formulas, data sources, units, dates, and assumptions for finance work.")
    if "security" in top_scopes:
        rules.append("Apply least-privilege and no-secret-exposure checks for security-sensitive work.")

    sig = signature(sentiments, top_scopes, rules)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    snapshot = [
        f"### Snapshot {now}",
        f"- Signature: `{sig}`",
        "- Usage signals:",
        f"  - Total logged sessions: {len(sessions)}",
        f"  - Sentiment counts: liked={sentiments['liked']}, neutral={sentiments['neutral']}, disliked={sentiments['disliked']}",
        f"  - Top scopes: {', '.join(top_scopes) if top_scopes else 'none'}",
        "- Adaptive Orchestrator Rules:",
        *[f"  - {rule}" for rule in rules],
        "- Integration notes:",
        "  - Derived artifact; regenerate with `python .github/scripts/update_orchestrator_adaptive_profile.py`.",
        "",
    ]

    existing = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
    base = existing if existing.strip() else profile_header()
    if f"- Signature: `{sig}`" in base:
        return base if base.endswith("\n") else f"{base}\n"
    else:
        result = base.rstrip() + "\n\n" + "\n".join(snapshot)

    result = re.sub(r"Last generated: .+", f"Last generated: {now}", result, count=1)
    return result if result.endswith("\n") else f"{result}\n"


def main() -> int:
    new_text = build_profile()
    old_text = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
    if old_text == new_text:
        print(f"No changes for {OUTPUT_PATH.relative_to(REPO_ROOT)}")
        return 0
    OUTPUT_PATH.write_text(new_text, encoding="utf-8")
    print(f"Updated {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
