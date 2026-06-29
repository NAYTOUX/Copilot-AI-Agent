# .github Folder Guide

This folder contains the reusable Copilot orchestration system.

## Navigation

- `AGENTS.md`: pointer to the canonical root `AGENTS.md`.
- `copilot-instructions.md`: short global Copilot instructions.
- `agents/`: specialist agents and hierarchy roles.
- `agent-registry.json`: machine-readable registry of all agents and primary
  capabilities.
- `instructions/`: scoped operational rules.
- `prompts/`: reusable prompt entrypoints.
- `skills/`: detailed reusable workflows.
- `hooks/`: deterministic lifecycle guardrails.
- `memory/`: append-only governance and learning state.
- `scripts/`: validators and memory utilities.
- `workflows/`: GitHub Actions for validation and maintenance.

## Rules

- Keep root `AGENTS.md` authoritative.
- Keep `copilot-instructions.md` short.
- Prefer updating existing agents or instructions before adding new ones.
- Keep `.github/memory/` append-only.
- Validate after every `.github` customization change.
