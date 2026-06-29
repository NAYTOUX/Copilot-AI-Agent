"""Run the standard validation path for the agent hub."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / ".github" / "scripts"


def run(cmd: list[str]) -> int:
    print("+ " + " ".join(cmd))
    result = subprocess.run(cmd, cwd=REPO_ROOT, text=True)
    return result.returncode


def main() -> int:
    scripts_to_compile = [
        SCRIPTS / "validate_copilot_customizations.py",
        SCRIPTS / "check_memory_append_only.py",
        SCRIPTS / "update_orchestrator_adaptive_profile.py",
        SCRIPTS / "update_orchestrator_personality.py",
        SCRIPTS / "receive_agent_report.py",
        SCRIPTS / "relay_provenance.py",
        SCRIPTS / "export_agent_hub.py",
        SCRIPTS / "audit_agent_hub.py",
        SCRIPTS / "route_request.py",
        SCRIPTS / "evaluate_routing.py",
        SCRIPTS / "generate_capability_matrix.py",
        SCRIPTS / "generate_agent_catalog.py",
        SCRIPTS / "doctor_agent_hub.py",
        SCRIPTS / "validate_json_contracts.py",
        SCRIPTS / "validate_agent_relationships.py",
        SCRIPTS / "scan_sensitive_content.py",
        SCRIPTS / "validate_agent_report_payload.py",
        SCRIPTS / "create_agent_personality.py",
        SCRIPTS / "report_orchestrator_usage.py",
        SCRIPTS / "evolve_personalities_from_memory.py",
        SCRIPTS / "promote_personality_proposal.py",
        SCRIPTS / "update_agent_effectiveness_profile.py",
        SCRIPTS / "update_orchestrator_learning_profile.py",
        SCRIPTS / "create_downstream_reporting_kit.py",
        SCRIPTS / "copilot_hook_guard.py",
        SCRIPTS / "maintain_memory_inbox.py",
        SCRIPTS / "prepare_release.py",
        SCRIPTS / "run_orchestrator_checks.py",
    ]

    commands = [
        [sys.executable, "-m", "py_compile", *map(str, scripts_to_compile)],
        [sys.executable, str(SCRIPTS / "update_orchestrator_adaptive_profile.py")],
        [sys.executable, str(SCRIPTS / "update_orchestrator_personality.py")],
        [sys.executable, str(SCRIPTS / "validate_copilot_customizations.py")],
        [sys.executable, str(SCRIPTS / "validate_json_contracts.py")],
        [sys.executable, str(SCRIPTS / "validate_agent_relationships.py")],
        [sys.executable, str(SCRIPTS / "check_memory_append_only.py")],
        [sys.executable, str(SCRIPTS / "scan_sensitive_content.py")],
        [sys.executable, str(SCRIPTS / "generate_capability_matrix.py"), "--check"],
        [sys.executable, str(SCRIPTS / "generate_agent_catalog.py"), "--check"],
        [
            sys.executable,
            str(SCRIPTS / "validate_agent_report_payload.py"),
            "examples/agent-report.json",
        ],
        [
            sys.executable,
            str(SCRIPTS / "validate_agent_report_payload.py"),
            "examples/orchestrator-usage-report.json",
        ],
        [
            sys.executable,
            str(SCRIPTS / "create_agent_personality.py"),
            "--spec",
            "examples/personality-spec.json",
            "--dry-run",
        ],
        [
            sys.executable,
            str(SCRIPTS / "promote_personality_proposal.py"),
            "--proposal",
            "examples/personality-spec.json",
            "--allow-low-evidence",
        ],
        [
            sys.executable,
            str(SCRIPTS / "report_orchestrator_usage.py"),
            "--source-repo",
            "owner/repo",
            "--request",
            "Example request",
            "--selected-agents",
            "Universal Orchestrator,Memory Governor",
        ],
        [
            sys.executable,
            str(SCRIPTS / "create_downstream_reporting_kit.py"),
            "--target",
            ".",
            "--force",
        ],
        [sys.executable, str(SCRIPTS / "copilot_hook_guard.py"), "--event", "sessionStart"],
        [sys.executable, str(SCRIPTS / "evolve_personalities_from_memory.py")],
        [sys.executable, str(SCRIPTS / "update_agent_effectiveness_profile.py"), "--check"],
        [sys.executable, str(SCRIPTS / "update_orchestrator_learning_profile.py"), "--check"],
        [sys.executable, str(SCRIPTS / "maintain_memory_inbox.py")],
        [sys.executable, str(SCRIPTS / "audit_agent_hub.py")],
        [sys.executable, str(SCRIPTS / "evaluate_routing.py")],
        [sys.executable, str(SCRIPTS / "doctor_agent_hub.py"), "--no-run"],
        [
            sys.executable,
            str(SCRIPTS / "prepare_release.py"),
            "--allow-dirty",
            "--skip-checks",
        ],
        [sys.executable, "-m", "unittest", "discover", "-s", ".github/scripts/tests", "-v"],
    ]

    for command in commands:
        code = run(command)
        if code != 0:
            return code

    print("Orchestrator checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
