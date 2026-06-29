"""Export this agent hub into another repository."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_PATHS = [
    "AGENTS.md",
    "README.md",
    ".gitignore",
    ".github/AGENTS.md",
    ".github/README.md",
    ".github/copilot-instructions.md",
    ".github/agent-registry.json",
    ".github/agent-relationship-map.json",
    ".github/agents",
    ".github/instructions",
    ".github/prompts",
    ".github/skills",
    ".github/schemas",
    ".github/personality-proposals",
    ".github/scripts",
    ".github/workflows",
    "docs",
    "examples",
]

MEMORY_BOOTSTRAP_PATHS = [
    ".github/memory/MEMORY_INDEX.md",
    ".github/memory/self-improvement-protocol.md",
    ".github/memory/ORCHESTRATOR_ROUTING_SCORECARD.md",
    ".github/memory/ORCHESTRATOR_AUDIT.md",
    ".github/memory/ORCHESTRATOR_ROADMAP.md",
    ".github/memory/ORCHESTRATOR_IMPROVEMENT_LOG.md",
    ".github/memory/personality-evolution-ledger.md",
    ".github/memory/orchestrator-feedback-loop.md",
    ".github/memory/orchestrator-adaptive-profile.md",
    ".github/memory/orchestrator-personality.md",
    ".github/memory/agent-effectiveness-profile.md",
    ".github/memory/orchestrator-learning-profile.md",
    ".github/memory/inbox/README.md",
    ".github/memory/outbox/README.md",
    ".github/memory/provenance/README.md",
]


def copy_path(source: Path, destination: Path, *, force: bool, dry_run: bool) -> None:
    if destination.exists() and not force:
        if dry_run:
            print(f"Would skip existing {destination} (use --force to overwrite)")
            return
        raise FileExistsError(f"{destination} exists; rerun with --force to overwrite")
    action = "Would copy" if dry_run else "Copying"
    print(f"{action} {source.relative_to(REPO_ROOT)} -> {destination}")
    if dry_run:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__"))
    else:
        shutil.copy2(source, destination)


def validate_target(target: Path, *, allow_inside_source: bool) -> None:
    repo = REPO_ROOT.resolve()
    target = target.resolve()
    if target == repo:
        raise ValueError("target must not be the source repository root")
    if repo in target.parents and not allow_inside_source:
        raise ValueError(
            "target is inside the source repository; use a separate target repo path"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Target repository path")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--apply", action="store_true", help="Actually copy files")
    parser.add_argument(
        "--allow-inside-source",
        action="store_true",
        help="Allow target paths inside this repository for controlled local tests",
    )
    parser.add_argument(
        "--include-memory",
        action="store_true",
        help="Include bootstrap memory files; inbox/provenance payloads are not copied",
    )
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    dry_run = not args.apply
    paths = list(DEFAULT_PATHS)
    if args.include_memory:
        paths.extend(MEMORY_BOOTSTRAP_PATHS)

    try:
        validate_target(target, allow_inside_source=args.allow_inside_source)
    except ValueError as exc:
        print(f"Unsafe export target: {exc}", file=sys.stderr)
        return 2

    if not target.exists():
        print(f"Target does not exist: {target}", file=sys.stderr)
        return 2
    if not target.is_dir():
        print(f"Target is not a directory: {target}", file=sys.stderr)
        return 2

    for relative in paths:
        source = REPO_ROOT / relative
        if not source.exists():
            print(f"Missing source path: {relative}", file=sys.stderr)
            return 3
        try:
            copy_path(source, target / relative, force=args.force, dry_run=dry_run)
        except FileExistsError as exc:
            print(str(exc), file=sys.stderr)
            return 4

    if dry_run:
        print("Dry run only. Rerun with --apply to copy files.")
    else:
        print("Agent hub export complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
