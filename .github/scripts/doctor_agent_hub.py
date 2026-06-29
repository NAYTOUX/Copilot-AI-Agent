"""Run local readiness checks for publishing or exporting the agent hub."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / ".github" / "agent-hub-manifest.json"


def run_command(command: str) -> dict:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        shell=True,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "passed": result.returncode == 0,
    }


def git_summary() -> dict:
    inside = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "is_git_repo": inside.returncode == 0,
        "branch": branch.stdout.strip(),
        "status_lines": [line for line in status.stdout.splitlines() if line.strip()],
    }


def collect_readiness(*, run_commands: bool) -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    missing_files = [
        path for path in manifest["canonical_files"] if not (REPO_ROOT / path).exists()
    ]
    stale_generated_docs = [
        path for path in manifest["generated_docs"] if not (REPO_ROOT / path).exists()
    ]
    command_results = (
        [run_command(command) for command in manifest["required_commands"]]
        if run_commands
        else []
    )
    git = git_summary()

    warnings: list[str] = []
    if git["branch"] != manifest["default_branch"]:
        warnings.append(
            f"current branch '{git['branch']}' differs from manifest default '{manifest['default_branch']}'"
        )
    if git["status_lines"]:
        warnings.append("working tree has uncommitted changes")

    failures: list[str] = []
    if missing_files:
        failures.extend(f"missing canonical file: {path}" for path in missing_files)
    if stale_generated_docs:
        failures.extend(f"missing generated doc: {path}" for path in stale_generated_docs)
    for result in command_results:
        if not result["passed"]:
            failures.append(f"command failed: {result['command']}")

    return {
        "manifest": {
            "hub_name": manifest["hub_name"],
            "version": manifest["version"],
            "status": manifest["status"],
        },
        "git": git,
        "missing_files": missing_files,
        "command_results": command_results,
        "warnings": warnings,
        "failures": failures,
        "ready": not failures,
    }


def to_markdown(payload: dict) -> str:
    lines = [
        "# Agent Hub Doctor",
        "",
        f"- Hub: `{payload['manifest']['hub_name']}`",
        f"- Version: `{payload['manifest']['version']}`",
        f"- Status: `{payload['manifest']['status']}`",
        f"- Ready: `{str(payload['ready']).lower()}`",
        f"- Git branch: `{payload['git']['branch']}`",
        f"- Uncommitted status lines: {len(payload['git']['status_lines'])}",
        "",
        "## Warnings",
        "",
    ]
    if payload["warnings"]:
        lines.extend(f"- {warning}" for warning in payload["warnings"])
    else:
        lines.append("- None.")
    lines.extend(["", "## Failures", ""])
    if payload["failures"]:
        lines.extend(f"- {failure}" for failure in payload["failures"])
    else:
        lines.append("- None.")
    if payload["command_results"]:
        lines.extend(["", "## Commands", ""])
        for result in payload["command_results"]:
            status = "pass" if result["passed"] else "fail"
            lines.append(f"- `{result['command']}`: {status}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--no-run",
        action="store_true",
        help="Only check manifest/files/git without running commands",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures",
    )
    args = parser.parse_args()

    payload = collect_readiness(run_commands=not args.no_run)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(to_markdown(payload), end="")

    if payload["failures"] or (args.strict and payload["warnings"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

