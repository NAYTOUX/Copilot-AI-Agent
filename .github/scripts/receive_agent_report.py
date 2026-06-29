"""Receive a structured report from another agent, repo, workflow, or channel."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[2]
INBOX_DIR = REPO_ROOT / ".github" / "memory" / "inbox"
VALID_CONFIDENCE = {"high", "medium", "low"}
VALID_PRIVACY = {"public", "internal", "sensitive-redacted"}
VALID_SEVERITY = {"critical", "high", "medium", "low", "info"}
VALID_CATEGORY = {
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
VALID_REQUESTED_ACTION = {
    "store",
    "review",
    "update-routing",
    "update-memory",
    "create-follow-up",
    "none",
}
VALID_OUTCOME = {"completed", "partial", "blocked", "failed"}


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:60] or "report"


def read_details(path: str | None) -> str:
    if not path:
        return ""
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"details file not found: {source}")
    return source.read_text(encoding="utf-8")


def load_json_payload(path: str) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON payload must be an object")
    return payload


def apply_json_payload(args: argparse.Namespace) -> argparse.Namespace:
    if not args.json_file:
        return args
    payload = load_json_payload(args.json_file)
    mapping = {
        "source_repo": "source_repo",
        "source_channel": "source_channel",
        "agent": "agent",
        "category": "category",
        "confidence": "confidence",
        "privacy": "privacy",
        "severity": "severity",
        "requested_action": "requested_action",
        "summary": "summary",
        "evidence": "evidence",
        "validation": "validation",
        "reusable_lesson": "reusable_lesson",
        "next_action": "next_action",
        "selected_agents": "selected_agents",
        "target_files": "target_files",
        "outcome": "outcome",
        "agent_feedback": "agent_feedback",
    }
    for source, target in mapping.items():
        if source in payload:
            setattr(args, target, payload[source])
    return args


def validate_args(args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    required = ["source_repo", "agent", "category", "confidence", "summary"]
    for field in required:
        if not str(getattr(args, field, "")).strip():
            errors.append(f"missing required field: {field.replace('_', '-')}")
    if args.category and args.category not in VALID_CATEGORY:
        errors.append(f"unsupported category: {args.category}")
    if args.confidence and args.confidence not in VALID_CONFIDENCE:
        errors.append(f"unsupported confidence: {args.confidence}")
    if args.privacy and args.privacy not in VALID_PRIVACY:
        errors.append(f"unsupported privacy: {args.privacy}")
    if args.severity and args.severity not in VALID_SEVERITY:
        errors.append(f"unsupported severity: {args.severity}")
    if args.requested_action and args.requested_action not in VALID_REQUESTED_ACTION:
        errors.append(f"unsupported requested-action: {args.requested_action}")
    if getattr(args, "outcome", "") and args.outcome not in VALID_OUTCOME:
        errors.append(f"unsupported outcome: {args.outcome}")
    for field in ("selected_agents", "target_files"):
        value = getattr(args, field, [])
        if value and not isinstance(value, list):
            errors.append(f"{field.replace('_', '-')}: must be a list")
    agent_feedback = getattr(args, "agent_feedback", [])
    if agent_feedback and not isinstance(agent_feedback, list):
        errors.append("agent-feedback: must be a list")
    for index, item in enumerate(agent_feedback or []):
        if not isinstance(item, dict):
            errors.append(f"agent-feedback[{index}]: must be an object")
            continue
        if not str(item.get("agent", "")).strip():
            errors.append(f"agent-feedback[{index}]: missing agent")
        if item.get("usefulness") not in {"high", "medium", "low", "harmful"}:
            errors.append(f"agent-feedback[{index}]: invalid usefulness")
    return errors


def build_report(args: argparse.Namespace, details: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    frontmatter = [
        "---",
        f"timestamp: {now}",
        f"source_repo: {args.source_repo}",
        f"source_channel: {args.source_channel}",
        f"agent: {args.agent}",
        f"category: {args.category}",
        f"confidence: {args.confidence}",
        f"privacy: {args.privacy}",
        f"severity: {args.severity}",
        f"requested_action: {args.requested_action}",
        "---",
        "",
    ]
    body = [
        "## Summary",
        "",
        args.summary.strip(),
        "",
        "## Evidence",
        "",
        args.evidence.strip() if args.evidence else "Not provided.",
        "",
        "## Validation",
        "",
        args.validation.strip() if args.validation else "Not provided.",
        "",
        "## Reusable Lesson",
        "",
        args.reusable_lesson.strip() if args.reusable_lesson else "None.",
        "",
        "## Next Action",
        "",
        args.next_action.strip() if args.next_action else "None.",
        "",
    ]
    outcome = getattr(args, "outcome", "")
    selected_agents = getattr(args, "selected_agents", [])
    target_files = getattr(args, "target_files", [])
    agent_feedback = getattr(args, "agent_feedback", [])
    if outcome:
        body.extend(["## Outcome", "", str(outcome).strip(), ""])
    if selected_agents:
        body.extend(["## Selected Agents", "", *[f"- {agent}" for agent in selected_agents], ""])
    if target_files:
        body.extend(["## Target Files", "", *[f"- `{path}`" for path in target_files], ""])
    if agent_feedback:
        body.extend(["## Agent Feedback", ""])
        for item in agent_feedback:
            body.append(
                "- "
                f"{item.get('agent', '')}"
                f" | role={item.get('role', '')}"
                f" | usefulness={item.get('usefulness', '')}"
                f" | issue={item.get('issue', '')}"
                f" | lesson={item.get('lesson', '')}"
            )
        body.append("")
    if details.strip():
        body.extend(["## Details", "", details.strip(), ""])
    return "\n".join(frontmatter + body)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-file", default="", help="Read report fields from JSON")
    parser.add_argument("--source-repo", default="")
    parser.add_argument("--source-channel", default="manual")
    parser.add_argument("--agent", default="")
    parser.add_argument("--category", choices=sorted(VALID_CATEGORY), default="")
    parser.add_argument("--confidence", choices=sorted(VALID_CONFIDENCE), default="")
    parser.add_argument("--privacy", choices=sorted(VALID_PRIVACY), default="internal")
    parser.add_argument("--severity", choices=sorted(VALID_SEVERITY), default="medium")
    parser.add_argument(
        "--requested-action",
        choices=sorted(VALID_REQUESTED_ACTION),
        default="review",
    )
    parser.add_argument("--summary", default="")
    parser.add_argument("--evidence", default="")
    parser.add_argument("--validation", default="")
    parser.add_argument("--reusable-lesson", default="")
    parser.add_argument("--next-action", default="")
    parser.add_argument("--outcome", choices=["", "completed", "partial", "blocked", "failed"], default="")
    parser.add_argument("--selected-agents", default="")
    parser.add_argument("--target-files", default="")
    parser.add_argument("--details-file", default="")
    args = parser.parse_args()
    args.selected_agents = [
        item.strip() for item in args.selected_agents.split(",") if item.strip()
    ]
    args.target_files = [
        item.strip() for item in args.target_files.split(",") if item.strip()
    ]
    args.agent_feedback = []

    try:
        args = apply_json_payload(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Could not read JSON payload: {exc}", file=sys.stderr)
        return 2

    errors = validate_args(args)
    if errors:
        print("Invalid agent report:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2

    try:
        details = read_details(args.details_file or None)
    except OSError as exc:
        print(f"Could not read details: {exc}", file=sys.stderr)
        return 2

    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    filename = f"{timestamp}-{slugify(args.category)}-{uuid4().hex[:8]}.md"
    out_path = INBOX_DIR / filename
    out_path.write_text(build_report(args, details), encoding="utf-8")
    print(f"Wrote {out_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
