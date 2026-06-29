# Personality Proposals

This directory is for generated personality spec drafts.

Use it for candidates created from memory evidence before they are promoted to
`.github/agents/*.agent.md`.

Promotion flow:

```bash
python .github/scripts/create_agent_personality.py --spec .github/personality-proposals/<spec>.json --dry-run
python .github/scripts/create_agent_personality.py --spec .github/personality-proposals/<spec>.json --apply
python .github/scripts/run_orchestrator_checks.py
```
