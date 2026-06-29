# Adoption Guide

## Use This Hub In Another Repository

### Option A - Export Script

Preview the export:

```bash
python .github/scripts/export_agent_hub.py --target C:/path/to/target-repo
```

Apply it:

```bash
python .github/scripts/export_agent_hub.py --target C:/path/to/target-repo --apply
```

Use `--force` only when you intentionally want to overwrite existing target
files.

### Option B - Manual Copy

1. Copy the root `AGENTS.md`.
2. Copy `.github/copilot-instructions.md`.
3. Copy `.github/agents/`, `.github/instructions/`, `.github/prompts/`, and
   `.github/skills/`.
4. Copy `.github/hooks/` if the target repo can run Copilot hooks.
5. Copy `.github/memory/MEMORY_INDEX.md` and
   `.github/memory/ORCHESTRATOR_ROUTING_SCORECARD.md`.
6. Copy `.github/agent-registry.json`.
7. Copy the relay, hook, and validation scripts:
   - `.github/scripts/validate_copilot_customizations.py`
   - `.github/scripts/copilot_hook_guard.py`
   - `.github/scripts/report_orchestrator_usage.py`
   - `.github/scripts/receive_agent_report.py`
   - `.github/scripts/route_request.py`
8. Adapt project-specific validation commands in:
   - `AGENTS.md`
   - `.github/instructions/*`
   - `.github/skills/*/references/validation.md`
9. Run:

```bash
python .github/scripts/validate_copilot_customizations.py
```

## Usage Feedback

After meaningful Orchestrator sessions in the downstream repo, generate a
report:

```bash
python .github/scripts/report_orchestrator_usage.py \
  --source-repo owner/repo \
  --request "Short session summary" \
  --selected-agents "Universal Orchestrator,Testing Worker" \
  --outcome completed \
  --validation "project-native test command" \
  --write
```

Relay the JSON payload back to this hub so the central Orchestrator and
sub-personalities can improve.

## Recommended Customization

- Keep the hierarchy.
- Add project-specific workers only when a real recurring domain appears.
- Use `create_agent_personality.py` and a personality spec when a new worker is
  justified.
- Replace generic validation commands with native project commands.
- Keep memory append-only from day one.
- Keep hooks deterministic, fast, and privacy-preserving.
- In downstream repos, adjust hook validation reminders to the native test
  command before relying on them.

## Anti-Patterns

- One giant global instruction file.
- Many overlapping agents with unclear ownership.
- Memory that stores raw logs instead of decisions.
- Workflows that commit broad file sets.
- Prompts that reference non-existent files.
