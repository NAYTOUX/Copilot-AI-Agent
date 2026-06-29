from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def agent_name(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    if not match:
        return ""
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip() == "name":
            return value.strip().strip("'\"")
    return ""


class AgentHubTests(unittest.TestCase):
    def test_customization_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, ".github/scripts/validate_copilot_customizations.py"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_json_contract_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, ".github/scripts/validate_json_contracts.py"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_agent_relationship_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, ".github/scripts/validate_agent_relationships.py"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_registry_covers_all_agents(self) -> None:
        registry = json.loads(
            (REPO_ROOT / ".github" / "agent-registry.json").read_text(encoding="utf-8")
        )
        registered = {entry["name"] for entry in registry["agents"]}
        discovered = {
            agent_name(path)
            for path in (REPO_ROOT / ".github" / "agents").glob("*.agent.md")
        }
        self.assertEqual(discovered, registered)
        self.assertIn(registry["default_entrypoint"], registered)

    def test_orchestrator_declares_all_subagents(self) -> None:
        module = load_module(
            "validate_copilot_customizations_for_agents",
            REPO_ROOT / ".github" / "scripts" / "validate_copilot_customizations.py",
        )
        frontmatter, _ = module.parse_markdown_frontmatter(
            REPO_ROOT / ".github" / "agents" / "Universal-Orchestrator.agent.md"
        )
        delegated = set(frontmatter["agents"])
        discovered = {
            agent_name(path)
            for path in (REPO_ROOT / ".github" / "agents").glob("*.agent.md")
        }
        discovered.discard("Universal Orchestrator")
        self.assertEqual(delegated, discovered)

    def test_prompt_files_have_official_metadata(self) -> None:
        module = load_module(
            "validate_copilot_customizations_for_prompts",
            REPO_ROOT / ".github" / "scripts" / "validate_copilot_customizations.py",
        )
        for path in (REPO_ROOT / ".github" / "prompts").glob("*.prompt.md"):
            frontmatter, _ = module.parse_markdown_frontmatter(path)
            self.assertEqual(frontmatter["name"], path.name.removesuffix(".prompt.md"))
            self.assertNotIn("mode", frontmatter, path.name)
            self.assertIsInstance(frontmatter["tools"], list, path.name)
            self.assertTrue(frontmatter["tools"], path.name)
            self.assertTrue(frontmatter["argument-hint"], path.name)

    def test_code_review_skill_and_instruction_are_wired(self) -> None:
        module = load_module(
            "validate_copilot_customizations_for_code_review",
            REPO_ROOT / ".github" / "scripts" / "validate_copilot_customizations.py",
        )
        skill = REPO_ROOT / ".github" / "skills" / "code-review" / "SKILL.md"
        instruction = (
            REPO_ROOT
            / ".github"
            / "instructions"
            / "copilot-code-review.instructions.md"
        )
        self.assertTrue(skill.exists())
        self.assertTrue(instruction.exists())
        skill_frontmatter, skill_body = module.parse_markdown_frontmatter(skill)
        instruction_frontmatter, instruction_body = module.parse_markdown_frontmatter(
            instruction
        )
        self.assertEqual(skill_frontmatter["name"], "code-review")
        self.assertIn("Findings ordered by severity", skill_body)
        self.assertEqual(instruction_frontmatter["excludeAgent"], "cloud-agent")
        self.assertIn("#file:.github/skills/code-review/SKILL.md", instruction_body)

    def test_vscode_copilot_settings_are_wired(self) -> None:
        settings = json.loads(
            (REPO_ROOT / ".vscode" / "settings.json").read_text(encoding="utf-8")
        )
        expected_locations = {
            "chat.instructionsFilesLocations": ".github/instructions",
            "chat.promptFilesLocations": ".github/prompts",
            "chat.agentFilesLocations": ".github/agents",
            "chat.agentSkillsLocations": ".github/skills",
            "chat.hookFilesLocations": ".github/hooks",
        }
        for key, location in expected_locations.items():
            self.assertTrue(settings[key][location], key)
            self.assertTrue((REPO_ROOT / location).exists(), location)
        self.assertTrue(settings["chat.useAgentsMdFile"])
        self.assertTrue(
            settings["github.copilot.chat.codeGeneration.useInstructionFiles"]
        )
        for key in (
            "github.copilot.chat.reviewSelection.instructions",
            "github.copilot.chat.commitMessageGeneration.instructions",
            "github.copilot.chat.pullRequestDescriptionGeneration.instructions",
        ):
            for entry in settings[key]:
                path = entry.get("file")
                self.assertTrue(path, key)
                self.assertTrue(path.startswith(".github/instructions/"), path)
                self.assertTrue((REPO_ROOT / path).exists(), path)

    def test_vscode_ai_security_baseline_is_wired(self) -> None:
        settings = json.loads(
            (REPO_ROOT / ".vscode" / "settings.json").read_text(encoding="utf-8")
        )
        self.assertTrue(settings["chat.includeReferencedInstructions"])
        self.assertTrue(settings["chat.useCustomizationsInParentRepositories"])
        self.assertTrue(settings["chat.useAgentSkills"])
        self.assertFalse(settings["chat.mcp.discovery.enabled"])
        self.assertFalse(settings["chat.tools.global.autoApprove"])
        self.assertEqual(settings["chat.permissions.default"], "default")
        self.assertEqual(
            settings["chat.tools.terminal.blockDetectedFileWrites"],
            "outsideWorkspace",
        )
        self.assertEqual(settings["chat.tools.urls.autoApprove"], [])
        self.assertEqual(settings["github.copilot.chat.additionalReadAccessFolders"], [])
        self.assertFalse(settings["github.copilot.chat.otel.captureContent"])
        terminal_blocks = settings["chat.tools.terminal.autoApprove"]
        for command in (
            "rm",
            "curl",
            "/\\bgit\\s+reset\\b/i",
            "/\\bgit\\s+push\\s+--force(?:-with-lease)?\\b/i",
            "/\\b(?:curl|wget)\\b.*\\|\\s*(?:sh|bash|powershell|pwsh|python)\\b/i",
        ):
            self.assertFalse(terminal_blocks[command])
        edit_blocks = settings["chat.tools.edits.autoApprove"]
        for pattern in (
            "**/.env",
            "**/*.pem",
            "AGENTS.md",
            ".vscode/settings.json",
            ".github/scripts/**",
            ".github/memory/**",
        ):
            self.assertFalse(edit_blocks[pattern])

    def test_commit_and_pr_generation_instructions_are_wired(self) -> None:
        module = load_module(
            "validate_copilot_customizations_for_generation_instructions",
            REPO_ROOT / ".github" / "scripts" / "validate_copilot_customizations.py",
        )
        for relative_path in (
            ".github/instructions/commit-message.instructions.md",
            ".github/instructions/pull-request-description.instructions.md",
        ):
            frontmatter, body = module.parse_markdown_frontmatter(
                REPO_ROOT / relative_path
            )
            self.assertEqual(frontmatter["applyTo"], ["**"])
            self.assertIn("description", frontmatter)
            self.assertIn("validation", body.lower())
            self.assertIn("secrets", body.lower())

    def test_agent_handoffs_target_known_agents(self) -> None:
        module = load_module(
            "validate_copilot_customizations_for_handoffs",
            REPO_ROOT / ".github" / "scripts" / "validate_copilot_customizations.py",
        )
        discovered = {
            agent_name(path)
            for path in (REPO_ROOT / ".github" / "agents").glob("*.agent.md")
        }
        handoff_count = 0
        for path in (REPO_ROOT / ".github" / "agents").glob("*.agent.md"):
            frontmatter, _ = module.parse_markdown_frontmatter(path)
            for handoff in frontmatter.get("handoffs", []):
                handoff_count += 1
                self.assertIn(handoff["agent"], discovered, path.name)
                self.assertIn("label", handoff)
                self.assertIn("prompt", handoff)
                self.assertIsInstance(handoff.get("send", False), bool)
        self.assertGreaterEqual(handoff_count, 20)

    def test_receive_agent_report_builds_expected_markdown(self) -> None:
        module = load_module(
            "receive_agent_report",
            REPO_ROOT / ".github" / "scripts" / "receive_agent_report.py",
        )
        args = argparse.Namespace(
            source_repo="owner/repo",
            source_channel="manual",
            agent="Repo Orchestrator",
            category="quality",
            confidence="high",
            privacy="internal",
            severity="medium",
            requested_action="review",
            summary="Validated registry coverage.",
            evidence="Unit test.",
            validation="passed",
            reusable_lesson="Keep registry tested.",
            next_action="none",
        )
        report = module.build_report(args, "Extra details.")
        self.assertIn("severity: medium", report)
        self.assertIn("## Summary", report)
        self.assertIn("Validated registry coverage.", report)
        self.assertIn("Extra details.", report)

    def test_export_dry_run_to_empty_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [
                    sys.executable,
                    ".github/scripts/export_agent_hub.py",
                    "--target",
                    directory,
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Dry run only", result.stdout)

    def test_export_refuses_source_repository_target(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                ".github/scripts/export_agent_hub.py",
                "--target",
                str(REPO_ROOT),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("Unsafe export target", result.stderr)

    def test_receive_agent_report_accepts_json_payload(self) -> None:
        module = load_module(
            "receive_agent_report_json",
            REPO_ROOT / ".github" / "scripts" / "receive_agent_report.py",
        )
        with tempfile.TemporaryDirectory() as directory:
            payload_path = Path(directory) / "report.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "source_repo": "owner/repo",
                        "source_channel": "workflow",
                        "agent": "Repo Orchestrator",
                        "category": "routing",
                        "confidence": "medium",
                        "privacy": "sensitive-redacted",
                        "severity": "high",
                        "requested_action": "update-routing",
                        "summary": "Routing gap found.",
                    }
                ),
                encoding="utf-8",
            )
            args = argparse.Namespace(
                json_file=str(payload_path),
                source_repo="",
                source_channel="manual",
                agent="",
                category="",
                confidence="",
                privacy="internal",
                severity="medium",
                requested_action="review",
                summary="",
                evidence="",
                validation="",
                reusable_lesson="",
                next_action="",
            )
            loaded = module.apply_json_payload(args)
        self.assertEqual(loaded.source_channel, "workflow")
        self.assertEqual(loaded.privacy, "sensitive-redacted")
        self.assertFalse(module.validate_args(loaded))

    def test_agent_hub_audit_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, ".github/scripts/audit_agent_hub.py", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertGreaterEqual(payload["agents"], 30)
        self.assertGreaterEqual(payload["routing_rules"], 20)
        self.assertFalse(payload["warnings"])

    def test_route_request_finds_memory_and_agent_governance(self) -> None:
        module = load_module(
            "route_request",
            REPO_ROOT / ".github" / "scripts" / "route_request.py",
        )
        result = module.route_request(
            "Update the orchestrator memory and agent routing instructions."
        )
        self.assertIn("Memory Governor", result["selected_agents"])
        self.assertIn("Agent System Governor", result["selected_agents"])
        self.assertIn(result["confidence"], {"medium", "high"})

    def test_route_request_uses_fallback_for_unknown_scope(self) -> None:
        module = load_module(
            "route_request_fallback",
            REPO_ROOT / ".github" / "scripts" / "route_request.py",
        )
        result = module.route_request("xyzzy plugh unmatched tokens only")
        self.assertTrue(result["fallback_used"])
        self.assertEqual(result["selected_agents"], ["Chief of Staff", "Repo Explorer"])

    def test_capability_matrix_is_current(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                ".github/scripts/generate_capability_matrix.py",
                "--check",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_routing_eval_corpus_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, ".github/scripts/evaluate_routing.py", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["failures"])

    def test_agent_catalog_is_current(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                ".github/scripts/generate_agent_catalog.py",
                "--check",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_doctor_no_run_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, ".github/scripts/doctor_agent_hub.py", "--no-run", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ready"])

    def test_agent_report_payload_example_is_valid(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                ".github/scripts/validate_agent_report_payload.py",
                "examples/agent-report.json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_orchestrator_usage_report_example_is_valid(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                ".github/scripts/validate_agent_report_payload.py",
                "examples/orchestrator-usage-report.json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_agent_feedback_example_is_accepted_by_usage_report(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                ".github/scripts/report_orchestrator_usage.py",
                "--source-repo",
                "owner/repo",
                "--request",
                "Validate per-agent feedback.",
                "--agent-feedback-file",
                "examples/agent-feedback.json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["agent_feedback"][0]["agent"], "Universal Orchestrator")

    def test_personality_creation_dry_run(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                ".github/scripts/create_agent_personality.py",
                "--spec",
                "examples/personality-spec.json",
                "--dry-run",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Would create .github", result.stdout)
        self.assertIn("Quant Risk Worker", result.stdout)

    def test_personality_proposal_promotion_dry_run(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                ".github/scripts/promote_personality_proposal.py",
                "--proposal",
                "examples/personality-spec.json",
                "--allow-low-evidence",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Would create", result.stdout)

    def test_report_orchestrator_usage_outputs_valid_payload(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                ".github/scripts/report_orchestrator_usage.py",
                "--source-repo",
                "owner/repo",
                "--request",
                "Improve a repeated routing gap.",
                "--selected-agents",
                "Universal Orchestrator,Personality Evolution Governor",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["category"], "personality")
        self.assertIn("Personality Evolution Governor", payload["evidence"])

    def test_personality_memory_analysis_runs(self) -> None:
        result = subprocess.run(
            [sys.executable, ".github/scripts/evolve_personalities_from_memory.py"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("# Personality Evolution Analysis", result.stdout)

    def test_personality_memory_writes_threshold_proposals(self) -> None:
        module = load_module(
            "evolve_personalities_from_memory",
            REPO_ROOT / ".github" / "scripts" / "evolve_personalities_from_memory.py",
        )
        with tempfile.TemporaryDirectory() as directory:
            module.PROPOSAL_DIR = Path(directory)
            written = module.write_proposals(
                {"candidates": {"Quant Risk Worker": 2}},
                min_signals=2,
            )
            self.assertEqual(len(written), 1)
            payload = json.loads(written[0].read_text(encoding="utf-8"))
        self.assertEqual(payload["name"], "Quant Risk Worker")
        self.assertEqual(payload["evidence_count"], 2)

    def test_agent_effectiveness_profile_is_current(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                ".github/scripts/update_agent_effectiveness_profile.py",
                "--check",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_orchestrator_learning_profile_is_current(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                ".github/scripts/update_orchestrator_learning_profile.py",
                "--check",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_downstream_reporting_kit_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [
                    sys.executable,
                    ".github/scripts/create_downstream_reporting_kit.py",
                    "--target",
                    directory,
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Dry run only", result.stdout)

    def test_copilot_hook_guard_blocks_destructive_command(self) -> None:
        module = load_module(
            "copilot_hook_guard",
            REPO_ROOT / ".github" / "scripts" / "copilot_hook_guard.py",
        )
        output = module.run(
            "preToolUse",
            {"toolArgs": {"command": "git reset --hard HEAD"}},
        )
        self.assertEqual(output["permissionDecision"], "deny")

    def test_copilot_hook_guard_allows_standard_validation(self) -> None:
        module = load_module(
            "copilot_hook_guard_allow",
            REPO_ROOT / ".github" / "scripts" / "copilot_hook_guard.py",
        )
        output = module.run(
            "preToolUse",
            {"toolArgs": {"command": "python .github/scripts/run_orchestrator_checks.py"}},
        )
        self.assertEqual(output, {})

    def test_copilot_hook_guard_reminds_after_customization_edit(self) -> None:
        module = load_module(
            "copilot_hook_guard_post",
            REPO_ROOT / ".github" / "scripts" / "copilot_hook_guard.py",
        )
        output = module.run(
            "postToolUse",
            {"toolArgs": {"path": ".github/agents/Universal-Orchestrator.agent.md"}},
        )
        self.assertIn("additionalContext", output)
        self.assertIn("run_orchestrator_checks.py", output["additionalContext"])

    def test_copilot_hook_guard_session_context(self) -> None:
        module = load_module(
            "copilot_hook_guard_session",
            REPO_ROOT / ".github" / "scripts" / "copilot_hook_guard.py",
        )
        output = module.run("sessionStart", {})
        self.assertIn("additionalContext", output)
        self.assertIn("AGENTS.md", output["additionalContext"])

    def test_sensitive_content_scan_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, ".github/scripts/scan_sensitive_content.py"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_memory_inbox_maintenance_runs_without_writing(self) -> None:
        result = subprocess.run(
            [sys.executable, ".github/scripts/maintain_memory_inbox.py"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("# Inbox Report Index", result.stdout)

    def test_prepare_release_skip_checks_allows_dirty_first_commit(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                ".github/scripts/prepare_release.py",
                "--allow-dirty",
                "--skip-checks",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(".vscode", result.stdout)

    def test_profile_generators_are_idempotent_without_new_feedback(self) -> None:
        profile_paths = [
            REPO_ROOT / ".github/memory/orchestrator-adaptive-profile.md",
            REPO_ROOT / ".github/memory/orchestrator-personality.md",
        ]
        before = [path.read_text(encoding="utf-8") for path in profile_paths]
        for script in (
            ".github/scripts/update_orchestrator_adaptive_profile.py",
            ".github/scripts/update_orchestrator_personality.py",
        ):
            result = subprocess.run(
                [sys.executable, script],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = [path.read_text(encoding="utf-8") for path in profile_paths]
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
