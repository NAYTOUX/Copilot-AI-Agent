---
applyTo: ".github/**"
description: "Rules for maintaining Copilot agents, prompts, instructions, skills, memory, scripts, and workflows."
---

# Copilot Customization Rules

## Scope Separation

- Keep `AGENTS.md` as the canonical root instruction file.
- Keep `.github/copilot-instructions.md` short and global.
- Use `.github/agents/` for specialist roles.
- Use `.github/instructions/` for scoped rules.
- Use `.github/prompts/` for reusable entrypoints.
- Use `.github/skills/` for multi-step workflows.
- Use `.github/memory/` for append-only learning and governance state.

## Frontmatter

- Agent files: `name`, `description`, `tools`, optional `user-invocable`.
- Prompt files: `description`, `agent`.
- Instruction files: `applyTo`, `description`.
- Skill files: `name`, `description`, optional `allowed-tools`.

## Validation

Run after customization edits:

```bash
python .github/scripts/validate_copilot_customizations.py
```

