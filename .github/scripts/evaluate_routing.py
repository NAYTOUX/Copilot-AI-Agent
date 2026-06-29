"""Evaluate deterministic request routing against curated scenarios."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = REPO_ROOT / ".github" / "evals" / "routing-cases.json"
ROUTER_PATH = REPO_ROOT / ".github" / "scripts" / "route_request.py"
CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}


def load_router():
    spec = importlib.util.spec_from_file_location("route_request", ROUTER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def load_cases(path: Path = CASES_PATH) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("routing eval file must contain a non-empty cases list")
    return cases


def evaluate_cases(cases: list[dict]) -> tuple[list[dict], list[str]]:
    router = load_router()
    results: list[dict] = []
    failures: list[str] = []

    for case in cases:
        case_id = str(case.get("id", "unnamed"))
        result = router.route_request(str(case.get("text", "")))
        selected = set(result["selected_agents"])
        expected = set(case.get("expected_agents", []))
        forbidden = set(case.get("forbidden_agents", []))
        missing = sorted(expected - selected)
        forbidden_hits = sorted(forbidden & selected)
        min_confidence = str(case.get("min_confidence", "low"))
        confidence_ok = (
            CONFIDENCE_RANK.get(result["confidence"], -1)
            >= CONFIDENCE_RANK.get(min_confidence, 0)
        )

        if missing:
            failures.append(f"{case_id}: missing expected agents: {', '.join(missing)}")
        if forbidden_hits:
            failures.append(
                f"{case_id}: selected forbidden agents: {', '.join(forbidden_hits)}"
            )
        if not confidence_ok:
            failures.append(
                f"{case_id}: confidence {result['confidence']} below {min_confidence}"
            )

        results.append(
            {
                "id": case_id,
                "confidence": result["confidence"],
                "selected_agents": result["selected_agents"],
                "missing": missing,
                "forbidden_hits": forbidden_hits,
                "passed": not missing and not forbidden_hits and confidence_ok,
            }
        )

    return results, failures


def print_markdown(results: list[dict], failures: list[str]) -> None:
    print("# Routing Evaluation")
    print()
    print("| Case | Result | Confidence | Selected agents |")
    print("| --- | --- | --- | --- |")
    for result in results:
        status = "pass" if result["passed"] else "fail"
        agents = ", ".join(result["selected_agents"])
        print(f"| {result['id']} | {status} | {result['confidence']} | {agents} |")
    print()
    print("## Failures")
    print()
    if failures:
        for failure in failures:
            print(f"- {failure}")
    else:
        print("- None.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args()

    try:
        results, failures = evaluate_cases(load_cases())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Could not evaluate routing: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({"results": results, "failures": failures}, indent=2))
    else:
        print_markdown(results, failures)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

