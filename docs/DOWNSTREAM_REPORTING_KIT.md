# Downstream Reporting Kit

Use this when importing the hub into another repository.

## Bootstrap

Preview:

```bash
python .github/scripts/create_downstream_reporting_kit.py --target C:/path/to/repo
```

Apply:

```bash
python .github/scripts/create_downstream_reporting_kit.py --target C:/path/to/repo --apply
```

The kit creates:

- `.github/memory/outbox/README.md`
- `docs/ORCHESTRATOR_USAGE_REPORTING.md`

## Reporting Rule

Every meaningful Orchestrator session should produce one concise JSON usage
report when it creates reusable learning. Include per-agent feedback when a
sub-personality was notably useful, noisy, missing, or harmful.

Recommended feedback file shape is available in `examples/agent-feedback.json`.
