# Contributing

## Rules

- Keep `AGENTS.md` canonical.
- Update `.github/agent-registry.json` when adding or renaming agents.
- Update `.github/routing-rules.json` when routing ownership changes.
- Add or update `.github/evals/routing-cases.json` for routing changes.
- Regenerate generated docs:

```bash
python .github/scripts/generate_capability_matrix.py --write
python .github/scripts/generate_agent_catalog.py --write
```

- Run before handoff:

```bash
python .github/scripts/run_orchestrator_checks.py
```

## Pull Request Standard

- Explain why the agent-system change is needed.
- List agents, prompts, skills, memory, scripts, or docs changed.
- Include validation output.
- Keep memory append-only.

