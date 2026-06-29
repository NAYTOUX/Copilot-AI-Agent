# Orchestrator Audit

Last audited: 2026-06-27
Scope: root `AGENTS.md` plus the reusable `.github` Copilot system.

## Current Architecture

- Root `AGENTS.md` is canonical.
- `.github/copilot-instructions.md` is a short global pointer.
- `.github/agents/` contains hierarchy roles and domain workers.
- `.github/instructions/` contains scoped operational rules.
- `.github/prompts/` contains reusable entrypoints.
- `.github/skills/` contains multi-step workflows.
- `.github/memory/` contains append-only governance memory.
- `.github/scripts/` validates customization, memory, and derived profiles.
- `.github/workflows/` runs validation and memory maintenance.

## Strengths

- Clear Orchestrator -> bosses -> leads -> workers hierarchy.
- Dedicated Memory Governor and relay intake.
- Dedicated Agent System Governor for customization drift.
- Explicit routing scorecard and delegation quality gate.
- Validation scripts make the system GitHub-ready instead of document-only.
- Machine-readable agent registry now gives automation a canonical capability
  map.
- Additional specialist coverage exists for architecture, cloud, ML,
  observability, legal/compliance, mobile, and dependency supply chain.

## Risks

- GitHub custom agent/tool support may vary by environment.
- Imported repositories must adapt validation commands and domain paths.
- Memory quality depends on concise, structured reports.
- Generated profiles are heuristic and should not override verified evidence.
- Registry and routing must stay synchronized as agents are added.

## Current Priority

Keep the system coherent, portable, append-only, easy to validate, and easy to
export into downstream repositories without accidental overwrites.
