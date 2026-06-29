"""Create reporting guidance files in a downstream repository."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


OUTBOX_README = """# Orchestrator Usage Outbox

This directory stores redacted JSON usage reports before they are relayed back
to the central agent hub.

Generate a report after meaningful Orchestrator sessions:

```bash
python .github/scripts/report_orchestrator_usage.py --source-repo owner/repo --request "Short session summary" --write
```

Do not store secrets, raw logs, personal data, private customer content, or long
unredacted transcripts here.
"""


GUIDE = """# Orchestrator Usage Reporting

Use this repo-level guide after importing the Universal Copilot Agent Hub.

## When To Report

Create a usage report when:

- Orchestrator chose the wrong or right agents in a reusable way.
- A specialist was missing or too broad.
- Validation exposed a reusable lesson.
- A sub-personality produced low, harmful, or high-value behavior.

## Command

```bash
python .github/scripts/report_orchestrator_usage.py \\
  --source-repo owner/repo \\
  --request "Short session summary" \\
  --selected-agents "Universal Orchestrator,Testing Worker" \\
  --outcome completed \\
  --validation "project-native test command" \\
  --agent-feedback-file examples/agent-feedback.json \\
  --write
```

Relay the generated `.github/memory/outbox/*.json` file back to the hub.
"""


def write_file(path: Path, text: str, *, force: bool, dry_run: bool) -> None:
    if path.exists() and not force:
        print(f"Would skip existing {path}" if dry_run else f"Skipping existing {path}")
        return
    print(f"Would write {path}" if dry_run else f"Writing {path}")
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Downstream repository path")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    if not target.exists() or not target.is_dir():
        print(f"Target must be an existing directory: {target}", file=sys.stderr)
        return 2
    if target == REPO_ROOT.resolve() and args.apply:
        print("Refusing to bootstrap the source hub as a downstream target.", file=sys.stderr)
        return 2

    dry_run = not args.apply
    write_file(target / ".github" / "memory" / "outbox" / "README.md", OUTBOX_README, force=args.force, dry_run=dry_run)
    write_file(target / "docs" / "ORCHESTRATOR_USAGE_REPORTING.md", GUIDE, force=args.force, dry_run=dry_run)
    if dry_run:
        print("Dry run only. Rerun with --apply to write files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
