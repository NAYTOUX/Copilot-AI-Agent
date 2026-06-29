---
name: "agent-system-governance"
description: "Workflow for creating, reviewing, or upgrading agents, prompts, instructions, skills, routing, and validation."
allowed-tools: ["read", "search", "edit", "execute", "agent"]
---

# Agent System Governance

## When To Use

- The task touches `.github/agents`, `.github/prompts`, `.github/instructions`,
  `.github/skills`, routing scorecards, or validators.
- The user wants a new agent personality or hierarchy change.

## Workflow

1. Load `AGENTS.md`, `.github/copilot-instructions.md`, and
   `.github/memory/ORCHESTRATOR_ROUTING_SCORECARD.md`.
2. Map existing ownership before adding anything.
3. Prefer updating an existing artifact.
4. Keep frontmatter schema valid.
5. Update memory when routing or governance behavior changed.
6. Run customization validation.

## Output Contract

- Governance change
- Artifacts updated
- Validation evidence
- Remaining overlap or drift risk

