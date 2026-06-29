# Release Process

## Pre-Release Gate

Run:

```bash
python .github/scripts/doctor_agent_hub.py
python .github/scripts/run_orchestrator_checks.py
python .github/scripts/check_memory_append_only.py
```

The doctor may warn about uncommitted files during active development. For an
actual release, the working tree should be clean after the release commit.

## Versioning

Update:

- `.github/agent-hub-manifest.json`
- `CHANGELOG.md`

Use semantic versioning:

- patch: docs, tests, validation, non-breaking agent wording
- minor: new agents, new routing capabilities, new scripts
- major: breaking import layout, renamed canonical files, incompatible schema

## Release Checklist

- Generated docs are current.
- Routing evaluation passes.
- Agent catalog and registry match.
- Memory append-only check passes.
- Workflows use least privilege.
- No secrets or private data are present.
- Downstream adoption notes are updated if import behavior changed.

