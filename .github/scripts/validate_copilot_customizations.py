"""Validate reusable Copilot customization files."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover
    yaml = None


REPO_ROOT = Path(__file__).resolve().parents[2]

ALLOWED_AGENT_KEYS = {
    "name",
    "description",
    "target",
    "tools",
    "agents",
    "handoffs",
    "argument-hint",
    "context",
    "model",
    "disable-model-invocation",
    "user-invocable",
    "infer",
    "mcp-servers",
    "metadata",
}
ALLOWED_PROMPT_KEYS = {
    "name",
    "description",
    "agent",
    "tools",
    "model",
    "argument-hint",
}
ALLOWED_INSTRUCTION_KEYS = {"applyTo", "description", "excludeAgent"}
ALLOWED_EXCLUDED_AGENTS = {"cloud-agent", "code-review", "copilot-coding-agent"}
ALLOWED_SKILL_KEYS = {"name", "description", "allowed-tools"}
REQUIRED_VSCODE_LOCATION_SETTINGS = {
    "chat.instructionsFilesLocations": ".github/instructions",
    "chat.promptFilesLocations": ".github/prompts",
    "chat.agentFilesLocations": ".github/agents",
    "chat.agentSkillsLocations": ".github/skills",
    "chat.hookFilesLocations": ".github/hooks",
}
REQUIRED_COPILOT_INSTRUCTION_SETTINGS = {
    "github.copilot.chat.reviewSelection.instructions": (
        ".github/instructions/copilot-code-review.instructions.md"
    ),
    "github.copilot.chat.commitMessageGeneration.instructions": (
        ".github/instructions/commit-message.instructions.md"
    ),
    "github.copilot.chat.pullRequestDescriptionGeneration.instructions": (
        ".github/instructions/pull-request-description.instructions.md"
    ),
}
REQUIRED_VSCODE_BOOLEAN_SETTINGS = {
    "chat.useAgentsMdFile": True,
    "github.copilot.chat.codeGeneration.useInstructionFiles": True,
    "chat.includeApplyingInstructions": True,
    "chat.includeReferencedInstructions": True,
    "chat.useCustomizationsInParentRepositories": True,
    "chat.promptFiles": True,
    "chat.useAgentSkills": True,
    "github.copilot.chat.skillTool.enabled": True,
    "github.copilot.chat.organizationInstructions.enabled": True,
    "github.copilot.chat.organizationCustomAgents.enabled": True,
    "chat.mcp.discovery.enabled": False,
    "chat.tools.compressOutput.enabled": True,
    "chat.tools.riskAssessment.enabled": True,
    "chat.tools.global.autoApprove": False,
    "chat.tools.terminal.ignoreDefaultAutoApproveRules": False,
    "github.copilot.chat.reviewSelection.enabled": True,
    "github.copilot.chat.otel.enabled": False,
    "github.copilot.chat.otel.captureContent": False,
    "github.copilot.chat.agentDebugLog.enabled": False,
    "github.copilot.chat.agentDebugLog.fileLogging.enabled": False,
    "github.copilot.chat.claudeAgent.allowDangerouslySkipPermissions": False,
}
REQUIRED_VSCODE_VALUE_SETTINGS = {
    "chat.permissions.default": "default",
    "chat.tools.terminal.blockDetectedFileWrites": "outsideWorkspace",
}
REQUIRED_TERMINAL_APPROVAL_BLOCKS = (
    "rm",
    "rmdir",
    "del",
    "kill",
    "curl",
    "wget",
    "eval",
    "chmod",
    "chown",
    "/^Remove-Item\\b/i",
    "/\\bgit\\s+reset\\b/i",
    "/\\bgit\\s+clean\\b/i",
    "/\\bgit\\s+push\\s+--force(?:-with-lease)?\\b/i",
    "/\\bSet-ExecutionPolicy\\b/i",
    "/\\bInvoke-Expression\\b/i",
    "/\\b(?:curl|wget)\\b.*\\|\\s*(?:sh|bash|powershell|pwsh|python)\\b/i",
)
REQUIRED_EDIT_APPROVAL_BLOCKS = (
    "**/.env",
    "**/.env.*",
    "**/*.pem",
    "**/*.key",
    "**/*.p12",
    "**/*.pfx",
    "**/.ssh/**",
    "**/secrets/**",
    "AGENTS.md",
    ".vscode/settings.json",
    ".github/copilot-instructions.md",
    ".github/agents/**",
    ".github/instructions/**",
    ".github/prompts/**",
    ".github/skills/**",
    ".github/hooks/**",
    ".github/workflows/**",
    ".github/scripts/**",
    ".github/memory/**",
)
ALLOWED_HOOK_EVENTS = {
    "sessionStart",
    "sessionEnd",
    "userPromptSubmitted",
    "preToolUse",
    "postToolUse",
    "postToolUseFailure",
    "errorOccurred",
    "agentStop",
    "subagentStart",
    "subagentStop",
    "permissionRequest",
    "notification",
    "preCompact",
}
ALLOWED_HOOK_KEYS = {
    "type",
    "matcher",
    "bash",
    "powershell",
    "command",
    "timeoutSec",
    "env",
    "url",
    "headers",
    "body",
    "prompt",
}

REQUIRED_MEMORY_FILES = [
    ".github/memory/MEMORY_INDEX.md",
    ".github/memory/orchestrator-feedback-loop.md",
    ".github/memory/orchestrator-adaptive-profile.md",
    ".github/memory/orchestrator-personality.md",
    ".github/memory/self-improvement-protocol.md",
    ".github/memory/ORCHESTRATOR_AUDIT.md",
    ".github/memory/ORCHESTRATOR_IMPROVEMENT_LOG.md",
    ".github/memory/ORCHESTRATOR_ROADMAP.md",
    ".github/memory/ORCHESTRATOR_ROUTING_SCORECARD.md",
    ".github/memory/personality-evolution-ledger.md",
    ".github/memory/outbox/README.md",
    ".github/memory/agent-effectiveness-profile.md",
    ".github/memory/orchestrator-learning-profile.md",
]

REQUIRED_AGENT_FILES = [
    ".github/agents/Universal-Orchestrator.agent.md",
    ".github/agents/Chief-of-Staff.agent.md",
    ".github/agents/Agent-System-Governor.agent.md",
    ".github/agents/Memory-Governor.agent.md",
    ".github/agents/Personality-Evolution-Governor.agent.md",
    ".github/agents/Delivery-Lead.agent.md",
    ".github/agents/Quality-Governor.agent.md",
]

CORE_ENTRYPOINT_REQUIRED_REFS = {
    ".github/prompts/new-chat-default.prompt.md": (
        "#file:AGENTS.md",
        "#file:.github/copilot-instructions.md",
        "#file:.github/memory/MEMORY_INDEX.md",
        "#file:.github/memory/ORCHESTRATOR_ROUTING_SCORECARD.md",
    ),
    ".github/prompts/super-best-result.prompt.md": (
        "#file:AGENTS.md",
        "#file:.github/copilot-instructions.md",
        "#file:.github/memory/ORCHESTRATOR_ROUTING_SCORECARD.md",
        "#file:.github/skills/universal-super-delivery/SKILL.md",
    ),
    ".github/prompts/orchestrator-governance-upgrade.prompt.md": (
        "#file:AGENTS.md",
        "#file:.github/agents/Universal-Orchestrator.agent.md",
        "#file:.github/memory/ORCHESTRATOR_AUDIT.md",
        "#file:.github/scripts/validate_copilot_customizations.py",
    ),
}


def _parse_simple_list(value: str) -> list[str]:
    if not (value.startswith("[") and value.endswith("]")):
        raise ValueError(f"not a list: {value}")
    content = value[1:-1].strip()
    if not content:
        return []
    items: list[str] = []
    current = ""
    quote: str | None = None
    for char in content:
        if char in {"'", '"'} and (not current or current[-1] != "\\"):
            quote = None if quote == char else char if quote is None else quote
            current += char
        elif char == "," and quote is None:
            items.append(current.strip().strip("'\""))
            current = ""
        else:
            current += char
    if current:
        items.append(current.strip().strip("'\""))
    return items


def _simple_yaml_scalar(value: str):
    value = value.strip()
    if value == "":
        return ""
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.startswith("[") and value.endswith("]"):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return _parse_simple_list(value)
    if value.startswith("{"):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return ast.literal_eval(value)
    if value.startswith(('"', "'")):
        return ast.literal_eval(value)
    return value


def _simple_yaml_load(text: str) -> dict:
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        key, sep, remainder = line.partition(":")
        if not sep:
            raise ValueError(f"invalid YAML line: {raw_line!r}")
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        current = stack[-1][1]
        value = remainder.strip()
        if value == "":
            child: dict = {}
            current[key] = child
            stack.append((indent, child))
        else:
            current[key] = _simple_yaml_scalar(value)
    return root


def yaml_load(text: str) -> dict:
    if yaml is not None:
        data = yaml.safe_load(text) or {}
        if not isinstance(data, dict):
            raise ValueError("YAML must parse to a mapping")
        return data
    return _simple_yaml_load(text)


def parse_markdown_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError("missing YAML frontmatter")
    return yaml_load(match.group(1)), match.group(2)


def validate_file_references(body: str, path: Path, errors: list[str]) -> None:
    for ref in re.findall(r"#file:([^\s`]+)", body):
        if not (REPO_ROOT / ref).exists():
            errors.append(f"{path}: missing #file reference target '{ref}'")


def validate_agent_file(path: Path, errors: list[str]) -> None:
    frontmatter, body = parse_markdown_frontmatter(path)
    unknown = sorted(set(frontmatter) - ALLOWED_AGENT_KEYS)
    if unknown:
        errors.append(f"{path}: unsupported agent keys: {', '.join(unknown)}")
    if not frontmatter.get("name"):
        errors.append(f"{path}: missing required 'name'")
    if not frontmatter.get("description"):
        errors.append(f"{path}: missing required 'description'")
    tools = frontmatter.get("tools")
    if tools is not None and not isinstance(tools, (list, str)):
        errors.append(f"{path}: 'tools' must be a list or string")
    delegated_agents = frontmatter.get("agents")
    if delegated_agents is not None and not isinstance(delegated_agents, list):
        errors.append(f"{path}: 'agents' must be a list")
    handoffs = frontmatter.get("handoffs")
    if handoffs is not None and not isinstance(handoffs, list):
        errors.append(f"{path}: 'handoffs' must be a list")
    if len(body.strip()) < 50:
        errors.append(f"{path}: agent body is too thin to be operational")


def validate_prompt_file(path: Path, errors: list[str]) -> None:
    frontmatter, body = parse_markdown_frontmatter(path)
    unknown = sorted(set(frontmatter) - ALLOWED_PROMPT_KEYS)
    if unknown:
        errors.append(f"{path}: unsupported prompt keys: {', '.join(unknown)}")
    name = str(frontmatter.get("name", "")).strip()
    expected_name = path.name.removesuffix(".prompt.md")
    if not name:
        errors.append(f"{path}: missing required 'name'")
    elif name != expected_name:
        errors.append(
            f"{path}: prompt name '{name}' must match file stem '{expected_name}'"
        )
    if not frontmatter.get("description"):
        errors.append(f"{path}: missing required 'description'")
    if not frontmatter.get("agent"):
        errors.append(f"{path}: missing required 'agent'")
    tools = frontmatter.get("tools")
    if not isinstance(tools, list) or not tools:
        errors.append(f"{path}: tools must be a non-empty list")
    if not frontmatter.get("argument-hint"):
        errors.append(f"{path}: missing required 'argument-hint'")
    validate_file_references(body, path, errors)


def validate_instruction_file(path: Path, errors: list[str]) -> None:
    frontmatter, _ = parse_markdown_frontmatter(path)
    unknown = sorted(set(frontmatter) - ALLOWED_INSTRUCTION_KEYS)
    if unknown:
        errors.append(
            f"{path}: unsupported instruction keys: {', '.join(unknown)}"
        )
    if not frontmatter.get("applyTo"):
        errors.append(f"{path}: missing required 'applyTo'")
    if not frontmatter.get("description"):
        errors.append(f"{path}: missing required 'description'")
    exclude_agent = frontmatter.get("excludeAgent")
    if exclude_agent is not None:
        if isinstance(exclude_agent, str):
            excluded = [exclude_agent]
        elif isinstance(exclude_agent, list):
            excluded = exclude_agent
        else:
            errors.append(f"{path}: excludeAgent must be a string or list")
            excluded = []
        for agent in excluded:
            if agent not in ALLOWED_EXCLUDED_AGENTS:
                errors.append(f"{path}: unsupported excludeAgent '{agent}'")


def validate_skill_file(path: Path, errors: list[str]) -> None:
    frontmatter, _ = parse_markdown_frontmatter(path)
    unknown = sorted(set(frontmatter) - ALLOWED_SKILL_KEYS)
    if unknown:
        errors.append(f"{path}: unsupported skill keys: {', '.join(unknown)}")
    name = str(frontmatter.get("name", "")).strip()
    if not name:
        errors.append(f"{path}: missing required 'name'")
    elif name != path.parent.name:
        errors.append(
            f"{path}: skill name '{name}' must match directory '{path.parent.name}'"
        )
    if not frontmatter.get("description"):
        errors.append(f"{path}: missing required 'description'")

    metadata_path = path.parent / "agents" / "openai.yaml"
    if not metadata_path.exists():
        errors.append(
            f"{path}: missing skill metadata file {metadata_path.relative_to(REPO_ROOT)}"
        )
        return

    try:
        metadata = yaml_load(metadata_path.read_text(encoding="utf-8"))
    except (ValueError, SyntaxError) as exc:
        errors.append(f"{metadata_path}: invalid YAML ({exc})")
        return

    interface = metadata.get("interface")
    if not isinstance(interface, dict):
        errors.append(f"{metadata_path}: missing interface section")
        return
    for key in ("display_name", "short_description", "default_prompt"):
        if not interface.get(key):
            errors.append(f"{metadata_path}: missing interface.{key}")
    if name and f"${name}" not in str(interface.get("default_prompt", "")):
        errors.append(f"{metadata_path}: default_prompt must mention ${name}")


def validate_required_paths(errors: list[str]) -> None:
    required = [
        "AGENTS.md",
        ".github/AGENTS.md",
        ".github/copilot-instructions.md",
        ".github/README.md",
        ".github/agent-hub-manifest.json",
        ".github/agent-registry.json",
        ".github/agent-relationship-map.json",
        ".github/routing-rules.json",
        ".vscode/settings.json",
        ".github/evals/routing-cases.json",
        ".github/schemas/agent-report.schema.json",
        ".github/schemas/personality-spec.schema.json",
        ".github/personality-proposals/README.md",
        ".github/ISSUE_TEMPLATE/config.yml",
        ".github/ISSUE_TEMPLATE/agent-improvement.yml",
        ".github/ISSUE_TEMPLATE/routing-gap.yml",
        ".github/instructions/commit-message.instructions.md",
        ".github/instructions/copilot-code-review.instructions.md",
        ".github/instructions/pull-request-description.instructions.md",
        ".github/hooks/orchestrator-guardrails.json",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/workflows/validate_copilot_customizations.yml",
        ".github/workflows/check_memory_append_only.yml",
        ".github/workflows/receive_agent_report.yml",
        ".github/workflows/refresh_orchestrator_profiles.yml",
        ".github/workflows/release_gate.yml",
        "docs/CROSS_REPO_USAGE_REPORTING.md",
        "docs/COPILOT_CODE_REVIEW.md",
        "docs/DOWNSTREAM_REPORTING_KIT.md",
        "docs/VS_CODE_COPILOT_SETTINGS.md",
        "docs/MICROSOFT_COPILOT_ALIGNMENT.md",
        "docs/AGENT_RELATIONSHIPS.md",
        "docs/INFORMATION_RELAY.md",
        "docs/HANDOFF_PROTOCOL.md",
        "docs/ORCHESTRATOR_PLAYBOOK.md",
        "docs/CAPABILITY_MATRIX.md",
        "docs/AGENT_CATALOG.md",
        "docs/ROUTING_ENGINE.md",
        "docs/PUBLISH_TO_GITHUB.md",
        "docs/DECISION_RECORDS.md",
        "docs/PERSONALITY_EVOLUTION.md",
        "docs/adr/0001-agent-hub-contract.md",
        "docs/OWNERSHIP.md",
        "docs/CHANGE_CONTROL.md",
        "examples/agent-report.json",
        "examples/agent-feedback.json",
        "examples/orchestrator-usage-report.json",
        "examples/personality-spec.json",
        *REQUIRED_MEMORY_FILES,
        *REQUIRED_AGENT_FILES,
    ]
    for relative_path in required:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"{relative_path}: required file is missing")


def validate_memory_index(errors: list[str]) -> None:
    index_path = REPO_ROOT / ".github" / "memory" / "MEMORY_INDEX.md"
    if not index_path.exists():
        return
    text = index_path.read_text(encoding="utf-8")
    for relative_path in REQUIRED_MEMORY_FILES:
        if relative_path.endswith("MEMORY_INDEX.md"):
            continue
        name = Path(relative_path).name
        if f"({name})" not in text and f"/{name})" not in text:
            errors.append(f"{index_path}: missing index entry for {name}")


def validate_orchestrator_wiring(errors: list[str]) -> None:
    path = REPO_ROOT / ".github" / "agents" / "Universal-Orchestrator.agent.md"
    if not path.exists():
        return
    _, body = parse_markdown_frontmatter(path)
    required_refs = [
        ".github/memory/MEMORY_INDEX.md",
        ".github/memory/orchestrator-feedback-loop.md",
        ".github/memory/self-improvement-protocol.md",
        ".github/memory/orchestrator-adaptive-profile.md",
        ".github/memory/orchestrator-personality.md",
        ".github/memory/ORCHESTRATOR_ROUTING_SCORECARD.md",
        ".github/memory/personality-evolution-ledger.md",
        ".github/memory/agent-effectiveness-profile.md",
        ".github/memory/orchestrator-learning-profile.md",
        ".github/agent-relationship-map.json",
        ".github/hooks/orchestrator-guardrails.json",
    ]
    for ref in required_refs:
        if ref not in body:
            errors.append(f"{path}: missing orchestrator reference '{ref}'")


def validate_core_entrypoints(errors: list[str]) -> None:
    for relative_path, refs in CORE_ENTRYPOINT_REQUIRED_REFS.items():
        path = REPO_ROOT / relative_path
        if not path.exists():
            errors.append(f"{relative_path}: required prompt is missing")
            continue
        text = path.read_text(encoding="utf-8")
        for ref in refs:
            if ref not in text:
                errors.append(f"{relative_path}: missing required ref '{ref}'")


def validate_profiles(errors: list[str]) -> None:
    adaptive = REPO_ROOT / ".github" / "memory" / "orchestrator-adaptive-profile.md"
    personality = REPO_ROOT / ".github" / "memory" / "orchestrator-personality.md"
    if adaptive.exists():
        text = adaptive.read_text(encoding="utf-8")
        if "Last generated:" not in text:
            errors.append(f"{adaptive}: missing 'Last generated:' marker")
        if "Adaptive Orchestrator Rules" not in text:
            errors.append(
                f"{adaptive}: missing 'Adaptive Orchestrator Rules' section"
            )
    if personality.exists():
        text = personality.read_text(encoding="utf-8")
        if "## Snapshot Log" not in text:
            errors.append(f"{personality}: missing Snapshot Log section")
        if "#### Active Personality Traits" not in text:
            errors.append(
                f"{personality}: missing Active Personality Traits section"
            )
        if "#### Personality Delta" not in text:
            errors.append(f"{personality}: missing Personality Delta section")


def load_agent_frontmatter(errors: list[str]) -> dict[str, Path]:
    agents: dict[str, Path] = {}
    for path in sorted((REPO_ROOT / ".github" / "agents").glob("*.agent.md")):
        try:
            frontmatter, _ = parse_markdown_frontmatter(path)
        except (ValueError, SyntaxError) as exc:
            errors.append(f"{path}: could not parse agent frontmatter ({exc})")
            continue
        name = str(frontmatter.get("name", "")).strip()
        if not name:
            continue
        if name in agents:
            errors.append(f"{path}: duplicate agent name '{name}'")
        agents[name] = path
    return agents


def validate_prompt_agents(errors: list[str], agents: dict[str, Path]) -> None:
    for path in sorted((REPO_ROOT / ".github" / "prompts").glob("*.prompt.md")):
        try:
            frontmatter, _ = parse_markdown_frontmatter(path)
        except (ValueError, SyntaxError):
            continue
        agent = str(frontmatter.get("agent", "")).strip()
        if agent and agent not in agents:
            errors.append(f"{path}: prompt references unknown agent '{agent}'")


def validate_agent_delegation(errors: list[str], agents: dict[str, Path]) -> None:
    for name, path in agents.items():
        try:
            frontmatter, _ = parse_markdown_frontmatter(path)
        except (ValueError, SyntaxError):
            continue
        delegated = frontmatter.get("agents", [])
        if not delegated:
            continue
        if not isinstance(delegated, list):
            continue
        seen: set[str] = set()
        for delegated_name in delegated:
            if not isinstance(delegated_name, str) or not delegated_name.strip():
                errors.append(f"{path}: agents entries must be non-empty strings")
                continue
            if delegated_name == name:
                errors.append(f"{path}: agent must not delegate to itself")
            if delegated_name in seen:
                errors.append(f"{path}: duplicate delegated agent '{delegated_name}'")
            seen.add(delegated_name)
            if delegated_name not in agents:
                errors.append(f"{path}: unknown delegated agent '{delegated_name}'")


def validate_agent_handoffs(errors: list[str], agents: dict[str, Path]) -> None:
    required = {"label", "agent", "prompt"}
    for name, path in agents.items():
        try:
            frontmatter, _ = parse_markdown_frontmatter(path)
        except (ValueError, SyntaxError):
            continue
        handoffs = frontmatter.get("handoffs", [])
        if not handoffs:
            continue
        if not isinstance(handoffs, list):
            continue
        labels: set[str] = set()
        for index, handoff in enumerate(handoffs):
            if not isinstance(handoff, dict):
                errors.append(f"{path}: handoffs[{index}] must be an object")
                continue
            unknown = sorted(set(handoff) - {"label", "agent", "prompt", "send"})
            if unknown:
                errors.append(
                    f"{path}: handoffs[{index}] unsupported keys: {', '.join(unknown)}"
                )
            missing = sorted(key for key in required if not handoff.get(key))
            if missing:
                errors.append(
                    f"{path}: handoffs[{index}] missing fields: {', '.join(missing)}"
                )
                continue
            label = str(handoff["label"]).strip()
            target = str(handoff["agent"]).strip()
            if label in labels:
                errors.append(f"{path}: duplicate handoff label '{label}'")
            labels.add(label)
            if target == name:
                errors.append(f"{path}: handoff '{label}' must not target itself")
            if target not in agents:
                errors.append(f"{path}: handoff '{label}' targets unknown agent '{target}'")
            if "send" in handoff and not isinstance(handoff["send"], bool):
                errors.append(f"{path}: handoff '{label}' send must be boolean")


def validate_agent_registry(errors: list[str], agents: dict[str, Path]) -> None:
    registry_path = REPO_ROOT / ".github" / "agent-registry.json"
    if not registry_path.exists():
        errors.append(".github/agent-registry.json: required registry is missing")
        return
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{registry_path}: invalid JSON ({exc})")
        return

    entries = registry.get("agents")
    if not isinstance(entries, list) or not entries:
        errors.append(f"{registry_path}: 'agents' must be a non-empty list")
        return

    registered: dict[str, str] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"{registry_path}: agents[{index}] must be an object")
            continue
        name = str(entry.get("name", "")).strip()
        file_name = str(entry.get("file", "")).strip()
        capabilities = entry.get("primary_capabilities")
        if not name:
            errors.append(f"{registry_path}: agents[{index}] missing name")
            continue
        if name in registered:
            errors.append(f"{registry_path}: duplicate registry agent '{name}'")
        registered[name] = file_name
        if name not in agents:
            errors.append(f"{registry_path}: registered unknown agent '{name}'")
        if not file_name:
            errors.append(f"{registry_path}: agent '{name}' missing file")
        else:
            path = REPO_ROOT / file_name
            if not path.exists():
                errors.append(f"{registry_path}: agent '{name}' file missing: {file_name}")
            elif name in agents and path.resolve() != agents[name].resolve():
                errors.append(
                    f"{registry_path}: agent '{name}' file does not match frontmatter path"
                )
        if not isinstance(entry.get("level"), int):
            errors.append(f"{registry_path}: agent '{name}' missing integer level")
        if not entry.get("category"):
            errors.append(f"{registry_path}: agent '{name}' missing category")
        if not isinstance(capabilities, list) or not capabilities:
            errors.append(
                f"{registry_path}: agent '{name}' missing primary_capabilities"
            )

    missing = sorted(set(agents) - set(registered))
    for name in missing:
        errors.append(f"{registry_path}: missing registry entry for agent '{name}'")

    default_entrypoint = str(registry.get("default_entrypoint", "")).strip()
    if default_entrypoint not in agents:
        errors.append(
            f"{registry_path}: default_entrypoint '{default_entrypoint}' is not a known agent"
        )


def validate_routing_rules(errors: list[str], agents: dict[str, Path]) -> None:
    rules_path = REPO_ROOT / ".github" / "routing-rules.json"
    if not rules_path.exists():
        errors.append(".github/routing-rules.json: required routing rules are missing")
        return
    try:
        payload = json.loads(rules_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{rules_path}: invalid JSON ({exc})")
        return

    if payload.get("default_agent") not in agents:
        errors.append(
            f"{rules_path}: default_agent '{payload.get('default_agent')}' is not a known agent"
        )
    fallback_agents = payload.get("fallback_agents")
    if not isinstance(fallback_agents, list) or not fallback_agents:
        errors.append(f"{rules_path}: fallback_agents must be a non-empty list")
    else:
        for agent in fallback_agents:
            if agent not in agents:
                errors.append(f"{rules_path}: unknown fallback agent '{agent}'")

    rules = payload.get("rules")
    if not isinstance(rules, list) or not rules:
        errors.append(f"{rules_path}: rules must be a non-empty list")
        return

    seen_ids: set[str] = set()
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            errors.append(f"{rules_path}: rules[{index}] must be an object")
            continue
        rule_id = str(rule.get("id", "")).strip()
        if not rule_id:
            errors.append(f"{rules_path}: rules[{index}] missing id")
        elif rule_id in seen_ids:
            errors.append(f"{rules_path}: duplicate rule id '{rule_id}'")
        seen_ids.add(rule_id)

        primary = str(rule.get("primary", "")).strip()
        if primary not in agents:
            errors.append(f"{rules_path}: rule '{rule_id}' unknown primary '{primary}'")
        secondary = rule.get("secondary", [])
        if not isinstance(secondary, list):
            errors.append(f"{rules_path}: rule '{rule_id}' secondary must be a list")
            secondary = []
        for agent in secondary:
            if agent not in agents:
                errors.append(f"{rules_path}: rule '{rule_id}' unknown secondary '{agent}'")
        keywords = rule.get("keywords")
        if not isinstance(keywords, list) or not keywords:
            errors.append(f"{rules_path}: rule '{rule_id}' missing keywords")
        exclude_patterns = rule.get("exclude_patterns", [])
        if exclude_patterns and not isinstance(exclude_patterns, list):
            errors.append(
                f"{rules_path}: rule '{rule_id}' exclude_patterns must be a list"
            )
        if not rule.get("validation"):
            errors.append(f"{rules_path}: rule '{rule_id}' missing validation")


def validate_json_files(errors: list[str]) -> None:
    json_paths = [
        REPO_ROOT / ".vscode" / "settings.json",
        REPO_ROOT / ".github" / "agent-hub-manifest.json",
        REPO_ROOT / ".github" / "agent-registry.json",
        REPO_ROOT / ".github" / "routing-rules.json",
        *sorted((REPO_ROOT / ".github" / "schemas").glob("*.json")),
        *sorted((REPO_ROOT / ".github" / "evals").glob("*.json")),
        *sorted((REPO_ROOT / ".github" / "hooks").glob("*.json")),
    ]
    for path in json_paths:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: invalid JSON ({exc})")


def validate_vscode_settings(errors: list[str]) -> None:
    settings_path = REPO_ROOT / ".vscode" / "settings.json"
    if not settings_path.exists():
        errors.append(".vscode/settings.json: required workspace settings are missing")
        return
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{settings_path}: invalid JSON ({exc})")
        return
    if not isinstance(settings, dict):
        errors.append(f"{settings_path}: settings must be a JSON object")
        return

    for key, expected in REQUIRED_VSCODE_BOOLEAN_SETTINGS.items():
        if settings.get(key) is not expected:
            errors.append(f"{settings_path}: {key} must be {str(expected).lower()}")

    for key, expected in REQUIRED_VSCODE_VALUE_SETTINGS.items():
        if settings.get(key) != expected:
            errors.append(f"{settings_path}: {key} must be {expected!r}")

    for key in (
        "chat.tools.urls.autoApprove",
        "github.copilot.chat.additionalReadAccessFolders",
    ):
        if settings.get(key) != []:
            errors.append(f"{settings_path}: {key} must be an empty list")

    terminal_auto_approve = settings.get("chat.tools.terminal.autoApprove")
    if not isinstance(terminal_auto_approve, dict):
        errors.append(
            f"{settings_path}: chat.tools.terminal.autoApprove must be an object"
        )
    else:
        for command in REQUIRED_TERMINAL_APPROVAL_BLOCKS:
            if terminal_auto_approve.get(command) is not False:
                errors.append(
                    f"{settings_path}: terminal auto-approve must require approval for {command}"
                )

    edit_auto_approve = settings.get("chat.tools.edits.autoApprove")
    if not isinstance(edit_auto_approve, dict):
        errors.append(f"{settings_path}: chat.tools.edits.autoApprove must be an object")
    else:
        for pattern in REQUIRED_EDIT_APPROVAL_BLOCKS:
            if edit_auto_approve.get(pattern) is not False:
                errors.append(
                    f"{settings_path}: edit auto-approve must require approval for {pattern}"
                )

    for key, required_location in REQUIRED_VSCODE_LOCATION_SETTINGS.items():
        value = settings.get(key)
        if not isinstance(value, dict):
            errors.append(f"{settings_path}: {key} must be an object")
            continue
        if value.get(required_location) is not True:
            errors.append(
                f"{settings_path}: {key} must enable {required_location}"
            )
        if not (REPO_ROOT / required_location).exists():
            errors.append(
                f"{settings_path}: {key} target is missing: {required_location}"
            )

    for key, required_file in REQUIRED_COPILOT_INSTRUCTION_SETTINGS.items():
        value = settings.get(key)
        if not isinstance(value, list) or not value:
            errors.append(f"{settings_path}: {key} must be a non-empty list")
            continue
        files: list[str] = []
        for index, entry in enumerate(value):
            if not isinstance(entry, dict):
                errors.append(f"{settings_path}: {key}[{index}] must be an object")
                continue
            if not entry.get("file") and not entry.get("text"):
                errors.append(
                    f"{settings_path}: {key}[{index}] must contain file or text"
                )
            file_name = str(entry.get("file", "")).strip()
            if not file_name:
                continue
            files.append(file_name)
            if not file_name.startswith(".github/instructions/"):
                errors.append(
                    f"{settings_path}: {key}[{index}] file must be under .github/instructions"
                )
            if not file_name.endswith(".instructions.md"):
                errors.append(
                    f"{settings_path}: {key}[{index}] file must end with .instructions.md"
                )
            if not (REPO_ROOT / file_name).exists():
                errors.append(
                    f"{settings_path}: {key}[{index}] file is missing: {file_name}"
                )
        if required_file not in files:
            errors.append(f"{settings_path}: {key} must include {required_file}")


def validate_hook_files(errors: list[str]) -> None:
    hook_dir = REPO_ROOT / ".github" / "hooks"
    if not hook_dir.exists():
        errors.append(".github/hooks: required hook directory is missing")
        return

    for path in sorted(hook_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if payload.get("version") != 1:
            errors.append(f"{path}: hook config version must be 1")
        if payload.get("disableAllHooks") is True:
            errors.append(f"{path}: disableAllHooks must not be true")
        hooks = payload.get("hooks")
        if not isinstance(hooks, dict) or not hooks:
            errors.append(f"{path}: hooks must be a non-empty object")
            continue

        for event, entries in hooks.items():
            if event not in ALLOWED_HOOK_EVENTS:
                errors.append(f"{path}: unsupported hook event '{event}'")
            if not isinstance(entries, list) or not entries:
                errors.append(f"{path}: hook event '{event}' must be a non-empty list")
                continue
            for index, entry in enumerate(entries):
                if not isinstance(entry, dict):
                    errors.append(f"{path}: hooks.{event}[{index}] must be an object")
                    continue
                unknown = sorted(set(entry) - ALLOWED_HOOK_KEYS)
                if unknown:
                    errors.append(
                        f"{path}: hooks.{event}[{index}] unsupported keys: {', '.join(unknown)}"
                    )
                hook_type = entry.get("type")
                if hook_type != "command":
                    errors.append(
                        f"{path}: hooks.{event}[{index}] must use type 'command'"
                    )
                command_fields = [
                    field
                    for field in ("command", "bash", "powershell")
                    if str(entry.get(field, "")).strip()
                ]
                if not command_fields:
                    errors.append(
                        f"{path}: hooks.{event}[{index}] missing command field"
                    )
                if event in {"preToolUse", "postToolUse"} and not entry.get("matcher"):
                    errors.append(
                        f"{path}: hooks.{event}[{index}] missing matcher"
                    )
                timeout = entry.get("timeoutSec")
                if timeout is not None and (
                    not isinstance(timeout, int) or not (1 <= timeout <= 60)
                ):
                    errors.append(
                        f"{path}: hooks.{event}[{index}] timeoutSec must be 1..60"
                    )

    guard = REPO_ROOT / ".github" / "scripts" / "copilot_hook_guard.py"
    if not guard.exists():
        errors.append(".github/scripts/copilot_hook_guard.py: required hook guard is missing")


def validate_manifest(errors: list[str]) -> None:
    manifest_path = REPO_ROOT / ".github" / "agent-hub-manifest.json"
    if not manifest_path.exists():
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    for field in ("hub_name", "version", "status", "default_entrypoint"):
        if not manifest.get(field):
            errors.append(f"{manifest_path}: missing {field}")
    for collection in ("canonical_files", "required_commands", "generated_docs"):
        if not isinstance(manifest.get(collection), list) or not manifest[collection]:
            errors.append(f"{manifest_path}: {collection} must be a non-empty list")
    for path in manifest.get("canonical_files", []):
        if not (REPO_ROOT / str(path)).exists():
            errors.append(f"{manifest_path}: canonical file missing: {path}")
    for path in manifest.get("generated_docs", []):
        if not (REPO_ROOT / str(path)).exists():
            errors.append(f"{manifest_path}: generated doc missing: {path}")


def validate_github_templates(errors: list[str]) -> None:
    issue_templates = [
        REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "agent-improvement.yml",
        REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "routing-gap.yml",
    ]
    for path in issue_templates:
        text = path.read_text(encoding="utf-8")
        for required in ("name:", "description:", "title:", "labels:", "body:"):
            if required not in text:
                errors.append(f"{path}: issue template missing '{required}'")
        if "- type:" not in text:
            errors.append(f"{path}: issue template body must contain fields")
        if "validations:" not in text or "required: true" not in text:
            errors.append(f"{path}: issue template must require core fields")

    pr_template = REPO_ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md"
    if pr_template.exists():
        text = pr_template.read_text(encoding="utf-8")
        for required in (
            "python .github/scripts/run_orchestrator_checks.py",
            "Memory changes are append-only",
            "No secrets",
        ):
            if required not in text:
                errors.append(f"{pr_template}: missing checklist item '{required}'")


def main() -> int:
    errors: list[str] = []
    validate_required_paths(errors)

    copilot = REPO_ROOT / ".github" / "copilot-instructions.md"
    if copilot.exists() and len(copilot.read_text(encoding="utf-8")) > 4000:
        errors.append(
            ".github/copilot-instructions.md: keep under 4000 characters"
        )

    for path in sorted((REPO_ROOT / ".github" / "agents").glob("*.agent.md")):
        validate_agent_file(path, errors)
    for path in sorted((REPO_ROOT / ".github" / "prompts").glob("*.prompt.md")):
        validate_prompt_file(path, errors)
    for path in sorted(
        (REPO_ROOT / ".github" / "instructions").glob("*.instructions.md")
    ):
        validate_instruction_file(path, errors)
    for path in sorted((REPO_ROOT / ".github" / "skills").glob("*/SKILL.md")):
        validate_skill_file(path, errors)

    agents = load_agent_frontmatter(errors)
    validate_prompt_agents(errors, agents)
    validate_agent_delegation(errors, agents)
    validate_agent_handoffs(errors, agents)
    validate_agent_registry(errors, agents)
    validate_routing_rules(errors, agents)
    validate_json_files(errors)
    validate_vscode_settings(errors)
    validate_hook_files(errors)
    validate_manifest(errors)
    validate_github_templates(errors)
    validate_memory_index(errors)
    validate_orchestrator_wiring(errors)
    validate_core_entrypoints(errors)
    validate_profiles(errors)

    if errors:
        print("Copilot customization validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Copilot customization validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
