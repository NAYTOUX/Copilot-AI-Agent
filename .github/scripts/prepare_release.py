"""Prepare a local release candidate for the agent hub."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / ".github" / "agent-hub-manifest.json"


def run(command: list[str]) -> int:
    print("+ " + " ".join(command))
    return subprocess.run(command, cwd=REPO_ROOT, text=True).returncode


def git_status_lines() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow uncommitted changes while preparing the first commit.",
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Only print release metadata and git readiness.",
    )
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    print(f"Preparing {manifest['hub_name']} {manifest['version']} ({manifest['status']})")

    if not args.skip_checks:
        commands = [
            [sys.executable, ".github/scripts/run_orchestrator_checks.py"],
            [sys.executable, ".github/scripts/doctor_agent_hub.py", "--no-run"],
        ]
        for command in commands:
            code = run(command)
            if code:
                return code

    status_lines = git_status_lines()
    if status_lines and not args.allow_dirty:
        print("Release candidate is not clean. Commit or stash changes, or use --allow-dirty for first-commit preparation.")
        for line in status_lines:
            print(f"- {line}")
        return 1

    print("Release candidate checks passed.")
    print("Next commands:")
    print("git add .gitignore .vscode AGENTS.md README.md CHANGELOG.md CONTRIBUTING.md SECURITY.md .github docs examples")
    print('git commit -m "Initialize universal Copilot agent hub"')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
