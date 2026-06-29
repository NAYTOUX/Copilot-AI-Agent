"""Write append-only provenance payloads into .github/memory/provenance."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[2]
PROVENANCE_DIR = REPO_ROOT / ".github" / "memory" / "provenance"


def read_payload(source_file: str | None) -> str:
    if source_file:
        path = Path(source_file)
        if not path.exists():
            raise FileNotFoundError(f"source file not found: {path}")
        return path.read_text(encoding="utf-8")
    if sys.stdin and not sys.stdin.isatty():
        return sys.stdin.read()
    raise ValueError("provide --source-file or pipe payload on stdin")


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-file", default="")
    parser.add_argument("--source", default="relay")
    parser.add_argument("--message", default="")
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--push", action="store_true")
    args = parser.parse_args()

    try:
        payload = read_payload(args.source_file or None)
    except (OSError, ValueError) as exc:
        print(f"Could not read payload: {exc}", file=sys.stderr)
        return 2

    PROVENANCE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    out_path = PROVENANCE_DIR / f"{timestamp}-{uuid4().hex[:8]}.md"
    content = "\n".join(
        [
            "---",
            f"source: {args.source}",
            f"timestamp: {timestamp}",
            "---",
            "",
            payload.strip(),
            "",
        ]
    )
    out_path.write_text(content, encoding="utf-8")
    print(f"Wrote {out_path.relative_to(REPO_ROOT)}")

    if args.commit or args.push:
        check = REPO_ROOT / ".github" / "scripts" / "check_memory_append_only.py"
        run([sys.executable, str(check)])
        run(["git", "add", str(out_path)])
        message = args.message or f"chore(memory): add provenance {timestamp}"
        run(["git", "commit", "-m", message])
    if args.push:
        run(["git", "push", "origin", "HEAD"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

