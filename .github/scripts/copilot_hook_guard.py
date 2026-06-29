"""Copilot hook guardrails for the reusable agent hub."""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any, Iterable


SESSION_CONTEXT = (
    "Repository policy: load AGENTS.md first, then .github/copilot-instructions.md. "
    "Use .github/agents for personalities, .github/instructions for applyTo rules, "
    ".github/skills for reusable workflows, and .github/memory as append-only "
    "learning state. If you change agents, prompts, skills, hooks, routing, or "
    "memory, run python .github/scripts/run_orchestrator_checks.py before final "
    "handoff and report the result."
)

CUSTOMIZATION_PATH_MARKERS = (
    "AGENTS.md",
    ".github/AGENTS.md",
    ".github/copilot-instructions.md",
    ".github/agent-registry.json",
    ".github/agent-relationship-map.json",
    ".github/routing-rules.json",
    ".github/agents/",
    ".github/hooks/",
    ".github/instructions/",
    ".github/prompts/",
    ".github/skills/",
    ".github/memory/",
    ".github/scripts/",
    ".github/workflows/",
)

TARGETED_COMMAND_KEYS = {
    "command",
    "cmd",
    "script",
    "shell",
    "code",
    "bash",
    "powershell",
}

BLOCKED_COMMAND_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"\bgit\s+reset\s+--hard\b", re.IGNORECASE),
        "git reset --hard can erase uncommitted user work.",
    ),
    (
        re.compile(r"\bgit\s+clean\s+-[^\r\n;]*[fxd][^\r\n;]*", re.IGNORECASE),
        "git clean with force can delete untracked repository files.",
    ),
    (
        re.compile(r"\brm\s+-[^\r\n;]*r[^\r\n;]*f[^\r\n;]*\s+(?:/|~|\*|\.|\$HOME)\b"),
        "Recursive forced deletion against broad paths is blocked.",
    ),
    (
        re.compile(r"\bRemove-Item\b[^\r\n;]*\b-Recurse\b[^\r\n;]*\b-Force\b[^\r\n;]*(?:[A-Za-z]:\\|~|\.|\*)", re.IGNORECASE),
        "Recursive forced deletion against broad paths is blocked.",
    ),
    (
        re.compile(r"\b(?:cat|type|Get-Content)\b[^\r\n;]*(?:^|\s)(?:\.env|.*[/\\]\.env)\b", re.IGNORECASE),
        "Reading dotenv files is blocked to prevent secret exposure.",
    ),
    (
        re.compile(r"\b(?:Get-ChildItem|dir|ls)\b[^\r\n;]*\bEnv:", re.IGNORECASE),
        "Enumerating environment variables is blocked to prevent secret exposure.",
    ),
    (
        re.compile(r"\bgh\s+auth\s+token\b", re.IGNORECASE),
        "Printing GitHub auth tokens is blocked.",
    ),
    (
        re.compile(r"\baz\s+account\s+get-access-token\b", re.IGNORECASE),
        "Printing cloud access tokens is blocked.",
    ),
    (
        re.compile(r"\bgcloud\s+auth\s+print-access-token\b", re.IGNORECASE),
        "Printing cloud access tokens is blocked.",
    ),
    (
        re.compile(r"\bDROP\s+(?:DATABASE|SCHEMA)\b", re.IGNORECASE),
        "Destructive database commands require explicit human review outside hooks.",
    ),
)


def load_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_strings(item)


def command_strings(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower()
            if normalized in TARGETED_COMMAND_KEYS and isinstance(item, str):
                found.append(item)
            else:
                found.extend(command_strings(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(command_strings(item))
    return found


def tool_arguments(payload: dict[str, Any]) -> Any:
    for key in ("toolArgs", "tool_input", "toolInput", "input", "arguments"):
        if key in payload:
            value = payload[key]
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                except json.JSONDecodeError:
                    return value
                return parsed
            return value
    return payload


def deny(reason: str) -> dict[str, str]:
    return {
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }


def pre_tool_use(payload: dict[str, Any]) -> dict[str, Any]:
    args = tool_arguments(payload)
    commands = command_strings(args)
    if not commands and isinstance(args, str):
        commands = [args]

    for command in commands:
        for pattern, reason in BLOCKED_COMMAND_PATTERNS:
            if pattern.search(command):
                return deny(reason)
    return {}


def post_tool_use(payload: dict[str, Any]) -> dict[str, str]:
    text = "\n".join(iter_strings(tool_arguments(payload)))
    if any(marker in text.replace("\\", "/") for marker in CUSTOMIZATION_PATH_MARKERS):
        return {
            "additionalContext": (
                "A Copilot customization surface changed. Before final handoff, "
                "run python .github/scripts/run_orchestrator_checks.py and report "
                "whether it passed. Keep memory append-only and do not claim "
                "validation without command evidence."
            )
        }
    return {}


def post_tool_use_failure() -> dict[str, str]:
    return {
        "additionalContext": (
            "A tool failed. Identify the likely root cause, avoid repeating the "
            "same failing command unchanged, and use the smallest diagnostic that "
            "can confirm the next fix."
        )
    }


def run(event: str, payload: dict[str, Any]) -> dict[str, Any]:
    if event == "sessionStart":
        return {"additionalContext": SESSION_CONTEXT}
    if event == "preToolUse":
        return pre_tool_use(payload)
    if event == "postToolUse":
        return post_tool_use(payload)
    if event == "postToolUseFailure":
        return post_tool_use_failure()
    return {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--event",
        choices=("sessionStart", "preToolUse", "postToolUse", "postToolUseFailure"),
        required=True,
    )
    args = parser.parse_args()
    output = run(args.event, load_payload())
    sys.stdout.write(json.dumps(output, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
