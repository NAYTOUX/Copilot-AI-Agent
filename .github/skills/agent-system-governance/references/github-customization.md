# GitHub Customization Reference

## Artifact Roles

- `AGENTS.md`: canonical behavior.
- `.github/copilot-instructions.md`: short global rules.
- `.github/agents/*.agent.md`: specialist personalities.
- `.github/instructions/*.instructions.md`: scoped file/domain rules.
- `.github/prompts/*.prompt.md`: reusable entrypoints.
- `.github/skills/**/SKILL.md`: deep workflows.

## Validation

Run:

```bash
python .github/scripts/validate_copilot_customizations.py
```

