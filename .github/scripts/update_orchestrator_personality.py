"""Build an Orchestrator personality profile from feedback-loop history."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FEEDBACK_PATH = REPO_ROOT / ".github" / "memory" / "orchestrator-feedback-loop.md"
OUTPUT_PATH = REPO_ROOT / ".github" / "memory" / "orchestrator-personality.md"

FRENCH_HINTS = (
    "je ",
    "tu ",
    "vous ",
    "avec",
    "pour",
    "dans",
    "agent",
    "memoire",
    "hierarchie",
    "repondre",
)
ENGLISH_HINTS = ("the ", "you ", "with", "for", "agent", "memory", "routing")


def normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(char for char in text if not unicodedata.combining(char))


def extract_prompt_log(text: str) -> str:
    marker = "## Prompt Log"
    index = text.find(marker)
    return text[index + len(marker) :] if index >= 0 else ""


def split_sessions(prompt_log: str) -> list[str]:
    entries = re.split(r"\n### ", prompt_log)
    return [entry.strip() for entry in entries if entry.strip()]


def extract_field(entry: str, name: str) -> str:
    match = re.search(rf"- \*\*{re.escape(name)}\*\*: (.+)", entry)
    return match.group(1).strip() if match else ""


def detect_language(prompts: list[str]) -> str:
    text = normalize("\n".join(prompts))
    fr = sum(text.count(hint) for hint in FRENCH_HINTS)
    en = sum(text.count(hint) for hint in ENGLISH_HINTS)
    if fr > en:
        return "match-user-fr-default"
    if en > fr:
        return "match-user-en-default"
    return "match-user"


def signature(values: dict[str, str]) -> str:
    payload = "|".join(f"{key}={value}" for key, value in sorted(values.items()))
    return hashlib.sha1(payload.encode("utf-8"), usedforsecurity=False).hexdigest()[:12]


def header() -> str:
    return "\n".join(
        [
            "# Orchestrator Personality Profile",
            "",
            "Generated automatically from `.github/memory/orchestrator-feedback-loop.md`.",
            "Append-only policy: each run appends a new snapshot unless the signature already",
            "exists.",
            "",
            "## Purpose",
            "",
            "This file captures active behavioral traits for the Orchestrator: language,",
            "tone, communication style, risk posture, and delegation tendency.",
            "",
            "## Snapshot Log",
            "",
        ]
    )


def build_profile() -> str:
    feedback = FEEDBACK_PATH.read_text(encoding="utf-8")
    sessions = split_sessions(extract_prompt_log(feedback))
    prompts = [extract_field(entry, "Prompt") for entry in sessions]
    sentiments: Counter[str] = Counter()
    for entry in sessions:
        sentiment = extract_field(entry, "Sentiment").lower().strip().rstrip(".!")
        if sentiment in {"liked", "neutral", "disliked"}:
            sentiments[sentiment] += 1

    language = detect_language(prompts)
    total = max(1, sum(sentiments.values()))
    liked_ratio = sentiments["liked"] / total
    disliked_ratio = sentiments["disliked"] / total

    communication = "concise-direct" if disliked_ratio < 0.15 else "explicit-careful"
    risk = "moderate" if disliked_ratio < 0.15 else "conservative"
    delegation = "route-when-useful"
    archetype = "Senior Operator" if liked_ratio < 0.5 else "Trusted Operator"

    traits = {
        "Language": language,
        "Archetype": archetype,
        "Communication style": communication,
        "Tone": "professional",
        "Risk posture": risk,
        "Delegation tendency": delegation,
    }
    sig = signature(traits)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"### Snapshot {now}",
        f"- Signature: `{sig}`",
        f"- Total sessions analyzed: {len(sessions)}",
        f"- Sentiment: liked={sentiments['liked']}, neutral={sentiments['neutral']}, disliked={sentiments['disliked']}",
        "",
        "#### Active Personality Traits",
        "",
        "| Trait | Value | Applied Instruction |",
        "| --- | --- | --- |",
        f"| Language | `{language}` | Match the user's language; default to French when the request is French or mixed French. |",
        f"| Archetype | `{archetype}` | Be direct, rigorous, and execution-focused. |",
        f"| Communication style | `{communication}` | Start with the answer or action; avoid filler. |",
        "| Tone | `professional` | No hype, no emojis, no unnecessary reassurance. |",
        f"| Risk posture | `{risk}` | Verify key assumptions and validate meaningful changes. |",
        f"| Delegation tendency | `{delegation}` | Delegate only when a specialist improves correctness or speed. |",
        "",
        "#### Personality Delta",
        "",
        "- Generated from current feedback-loop signals.",
        "",
        "#### Integration Notes",
        "",
        "- Derived artifact; regenerate with `python .github/scripts/update_orchestrator_personality.py`.",
        "",
    ]

    existing = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
    base = existing if existing.strip() else header()
    if f"- Signature: `{sig}`" in base:
        return base if base.endswith("\n") else f"{base}\n"
    return base.rstrip() + "\n\n" + "\n".join(lines)


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
