"""Build a redacted usage report for relaying Orchestrator learning upstream."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTBOX_DIR = REPO_ROOT / ".github" / "memory" / "outbox"
VALID_OUTCOMES = {"completed", "partial", "blocked", "failed"}
VALID_CATEGORIES = {
    "routing",
    "governance",
    "memory",
    "quality",
    "implementation",
    "finance",
    "research",
    "security",
    "devops",
    "docs",
    "provenance",
    "architecture",
    "ml",
    "cloud",
    "observability",
    "compliance",
    "mobile",
    "dependency",
    "personality",
}
VALID_REQUESTED_ACTIONS = {
    "store",
    "review",
    "update-routing",
    "update-memory",
    "create-follow-up",
    "none",
}


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:50] or "orchestrator-usage"


def build_payload(args: argparse.Namespace) -> dict:
    selected_agents = split_csv(args.selected_agents)
    target_files = split_csv(args.target_files)
    agent_feedback = load_agent_feedback(args.agent_feedback_file)
    evidence = [
        f"Outcome: {args.outcome}.",
        f"Selected agents: {', '.join(selected_agents) if selected_agents else 'not provided'}.",
    ]
    if args.evidence:
        evidence.append(args.evidence.strip())
    return {
        "source_repo": args.source_repo,
        "source_channel": args.source_channel,
        "agent": "Universal Orchestrator",
        "category": args.category,
        "confidence": args.confidence,
        "privacy": args.privacy,
        "severity": args.severity,
        "requested_action": args.requested_action,
        "summary": args.summary
        or f"Orchestrator usage report: {args.request.strip()[:160]}",
        "evidence": " ".join(evidence),
        "validation": args.validation or "Not provided.",
        "reusable_lesson": args.reusable_lesson or "None.",
        "next_action": args.next_action or "Review for memory, routing, or personality update.",
        "target_files": target_files,
        "selected_agents": selected_agents,
        "outcome": args.outcome,
        "agent_feedback": agent_feedback,
    }


def load_agent_feedback(path: str) -> list[dict]:
    if not path:
        return []
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("agent feedback file must contain a JSON array")
    return payload


def validate_args(args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    if not args.source_repo.strip():
        errors.append("source_repo is required")
    if not args.request.strip():
        errors.append("request is required")
    if args.outcome not in VALID_OUTCOMES:
        errors.append(f"unsupported outcome: {args.outcome}")
    if args.category not in VALID_CATEGORIES:
        errors.append(f"unsupported category: {args.category}")
    if args.requested_action not in VALID_REQUESTED_ACTIONS:
        errors.append(f"unsupported requested-action: {args.requested_action}")
    if args.agent_feedback_file:
        try:
            feedback = load_agent_feedback(args.agent_feedback_file)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"invalid agent-feedback-file: {exc}")
        else:
            for index, item in enumerate(feedback):
                if not isinstance(item, dict):
                    errors.append(f"agent_feedback[{index}] must be an object")
                    continue
                if not str(item.get("agent", "")).strip():
                    errors.append(f"agent_feedback[{index}] missing agent")
                if item.get("usefulness") not in {"high", "medium", "low", "harmful"}:
                    errors.append(f"agent_feedback[{index}] has invalid usefulness")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-repo", required=True)
    parser.add_argument("--source-channel", default="orchestrator-usage")
    parser.add_argument("--request", required=True)
    parser.add_argument("--selected-agents", default="")
    parser.add_argument("--outcome", choices=sorted(VALID_OUTCOMES), default="completed")
    parser.add_argument("--category", choices=sorted(VALID_CATEGORIES), default="personality")
    parser.add_argument("--confidence", choices=["high", "medium", "low"], default="medium")
    parser.add_argument("--privacy", choices=["public", "internal", "sensitive-redacted"], default="internal")
    parser.add_argument("--severity", choices=["critical", "high", "medium", "low", "info"], default="info")
    parser.add_argument("--requested-action", choices=sorted(VALID_REQUESTED_ACTIONS), default="review")
    parser.add_argument("--summary", default="")
    parser.add_argument("--evidence", default="")
    parser.add_argument("--validation", default="")
    parser.add_argument("--reusable-lesson", default="")
    parser.add_argument("--next-action", default="")
    parser.add_argument("--target-files", default="")
    parser.add_argument("--agent-feedback-file", default="")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    errors = validate_args(args)
    if errors:
        print("Usage report validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2

    payload = build_payload(args)
    text = json.dumps(payload, indent=2) + "\n"
    if not args.write:
        print(text, end="")
        return 0

    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    filename = f"{timestamp}-{slugify(args.request)}-{uuid4().hex[:8]}.json"
    path = OUTBOX_DIR / filename
    path.write_text(text, encoding="utf-8")
    print(f"Wrote {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
