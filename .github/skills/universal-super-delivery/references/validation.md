# Validation Reference

Use the strongest available command that matches the changed surface.

- `.github` customization: `python .github/scripts/validate_copilot_customizations.py`
- Governance/memory: `python .github/scripts/run_orchestrator_checks.py`
- Python: `python -m py_compile <touched_files>`
- JavaScript/TypeScript: project `typecheck`, `lint`, `test`, or `build`
- Workflows: inspect permissions, triggers, path scope, and idempotence
- Docs: verify paths and commands exist

If validation cannot run, report exactly why.

