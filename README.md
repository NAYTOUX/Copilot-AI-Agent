# Universal Copilot Agent Hub

This repository stores a reusable, GitHub-ready hierarchy of Copilot agents,
instructions, prompts, skills, memory governance, and validation scripts.

Use it as the source repository for agent personalities that can be copied,
vendored, or synchronized into other repositories.

## Structure

- `AGENTS.md`: canonical operating contract and routing hierarchy.
- `.github/copilot-instructions.md`: short global Copilot rules.
- `.github/agents/`: specialist agent personalities.
- `.github/agent-registry.json`: machine-readable capability map.
- `.github/instructions/`: scoped coding and governance rules.
- `.github/prompts/`: reusable task entrypoints.
- `.github/skills/`: reusable multi-step workflows.
- `.github/hooks/`: Copilot lifecycle guardrails for safety and validation.
- `.github/memory/`: append-only orchestration memory and routing state.
- `.github/personality-proposals/`: generated personality spec drafts.
- `.github/scripts/`: validators, memory refreshers, and relay tools.
- `.github/workflows/`: GitHub Actions for validation and maintenance.
- `.vscode/settings.json`: workspace Copilot discovery, generation, and AI
  security settings.
- `docs/`: human-facing guides.
- `examples/`: payload examples for other repositories.

## Recommended Entry Point

Start with `Universal Orchestrator`.

It classifies the request, builds a manager brief, routes to the right
specialists, reconciles their outputs, validates the result, and updates memory
when the session creates reusable learning.

## Local Validation

```bash
python .github/scripts/validate_copilot_customizations.py
python .github/scripts/validate_json_contracts.py
python .github/scripts/validate_agent_relationships.py
python .github/scripts/run_orchestrator_checks.py
python .github/scripts/audit_agent_hub.py
python .github/scripts/route_request.py --text "Fix a Python regression"
python .github/scripts/generate_capability_matrix.py --check
python .github/scripts/evaluate_routing.py
python .github/scripts/generate_agent_catalog.py --check
python .github/scripts/validate_agent_report_payload.py examples/agent-report.json
python .github/scripts/validate_agent_report_payload.py examples/orchestrator-usage-report.json
python .github/scripts/create_agent_personality.py --spec examples/personality-spec.json --dry-run
python .github/scripts/promote_personality_proposal.py --proposal examples/personality-spec.json --allow-low-evidence
python .github/scripts/report_orchestrator_usage.py --source-repo owner/repo --request "Example request"
python .github/scripts/create_downstream_reporting_kit.py --target C:/path/to/target-repo
python .github/scripts/copilot_hook_guard.py --event sessionStart
python .github/scripts/evolve_personalities_from_memory.py
python .github/scripts/update_agent_effectiveness_profile.py --check
python .github/scripts/prepare_release.py --allow-dirty
```

## Import Into Another Repository

Copy these files first:

```text
AGENTS.md
.github/copilot-instructions.md
.github/agents/
.github/instructions/
.github/prompts/
.github/skills/
.github/hooks/
.github/memory/MEMORY_INDEX.md
.github/memory/ORCHESTRATOR_ROUTING_SCORECARD.md
.github/scripts/validate_copilot_customizations.py
.vscode/settings.json
```

Then adapt project-specific validation commands, file paths, and domain workers.

Or preview an automated export:

```bash
python .github/scripts/export_agent_hub.py --target C:/path/to/target-repo
```

## Information Relay

Other repositories should send concise structured reports instead of dumping raw
logs. Use:

```bash
python .github/scripts/receive_agent_report.py \
  --source-repo owner/repo \
  --agent "Repo Orchestrator" \
  --category implementation \
  --confidence high \
  --summary "Fixed stale cache invalidation in dashboard worker." \
  --details-file report.md
```

See `docs/INFORMATION_RELAY.md`.

For usage feedback after each downstream Orchestrator session:

```bash
python .github/scripts/report_orchestrator_usage.py \
  --source-repo owner/repo \
  --request "Short session summary" \
  --selected-agents "Universal Orchestrator,Testing Worker" \
  --outcome completed \
  --validation "project tests" \
  --write
```

Then relay the generated JSON to this hub and run
`python .github/scripts/evolve_personalities_from_memory.py`.

## Core Guides

- `docs/HIERARCHY.md`: hierarchy model.
- `docs/CAPABILITY_MATRIX.md`: human-readable capability map.
- `docs/AGENT_CATALOG.md`: generated catalog of all agents.
- `docs/HANDOFF_PROTOCOL.md`: manager brief and specialist report contract.
- `docs/AGENT_RELATIONSHIPS.md`: relationship map between personalities.
- `docs/COPILOT_CODE_REVIEW.md`: dedicated Copilot code review behavior.
- `docs/VS_CODE_COPILOT_SETTINGS.md`: VS Code Copilot discovery, generation,
  and AI security settings.
- `docs/ORCHESTRATOR_PLAYBOOK.md`: default Orchestrator operating loop.
- `docs/ROUTING_ENGINE.md`: deterministic local request router.
- `docs/ADOPTION_GUIDE.md`: import path for another repository.
- `docs/CROSS_REPO_USAGE_REPORTING.md`: downstream usage feedback loop.
- `docs/DOWNSTREAM_REPORTING_KIT.md`: bootstrap kit for downstream repos.
- `docs/MICROSOFT_COPILOT_ALIGNMENT.md`: official Copilot customization
  alignment map.
- `docs/PERSONALITY_EVOLUTION.md`: controlled personality creation loop.
- `docs/RELEASE_PROCESS.md`: release gate and versioning.
- `docs/PUBLISH_TO_GITHUB.md`: first publish checklist.
- `docs/DECISION_RECORDS.md`: durable architecture decisions.
- `docs/OWNERSHIP.md`: accountable agent owners by surface.
- `docs/CHANGE_CONTROL.md`: required evidence by change type.

## Doctor

```bash
python .github/scripts/doctor_agent_hub.py
```
