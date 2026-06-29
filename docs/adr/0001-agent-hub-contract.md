# 0001 Agent Hub Contract

Status: accepted

## Context

The repository must serve as a reusable source of Copilot personalities,
instructions, prompts, skills, memory governance, and relay tooling across
multiple projects.

## Decision

The root `AGENTS.md` is the canonical human contract. Machine-readable routing
and capability data live in `.github/agent-registry.json` and
`.github/routing-rules.json`. Generated docs must be regenerated from those
files, not edited manually.

The Universal Orchestrator is the only default entrypoint. It delegates to
managers and workers, reconciles specialist output, and returns a final answer
only after validation requirements are satisfied or a blocker is explicit.

## Consequences

- New agents require registry coverage and validation.
- Routing changes require deterministic eval cases.
- Cross-repo learning enters through structured reports, not raw log dumps.
- Memory files remain append-only unless a future ADR explicitly changes the
  governance model.

## Validation

```bash
python .github/scripts/run_orchestrator_checks.py
```
