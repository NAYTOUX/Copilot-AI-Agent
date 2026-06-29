"""Promote a generated personality proposal into a real agent."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CREATE_SCRIPT = REPO_ROOT / ".github" / "scripts" / "create_agent_personality.py"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proposal", required=True, help="Path to proposal JSON")
    parser.add_argument("--min-evidence", type=int, default=2)
    parser.add_argument("--allow-low-evidence", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--update-routing", action="store_true")
    args = parser.parse_args()

    path = Path(args.proposal)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read proposal: {exc}", file=sys.stderr)
        return 2

    evidence_count = int(payload.get("evidence_count", 0))
    if evidence_count < args.min_evidence and not args.allow_low_evidence:
        print(
            f"Proposal evidence_count={evidence_count} is below required {args.min_evidence}.",
            file=sys.stderr,
        )
        return 1

    command = [
        sys.executable,
        str(CREATE_SCRIPT),
        "--spec",
        str(path),
    ]
    if args.apply:
        command.append("--apply")
    else:
        command.append("--dry-run")
    if args.update_routing:
        command.append("--update-routing")

    result = subprocess.run(command, cwd=REPO_ROOT, text=True)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
