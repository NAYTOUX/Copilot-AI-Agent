# Cross-Repo Usage Reporting

Every repository that imports this hub should report useful Orchestrator usage
back to the hub. Reports should be concise, redacted, and evidence-backed.

## What To Send

Send a report when any of these happened:

- Orchestrator selected the wrong agents.
- A specialist was missing.
- A specialist gave repeatedly useful behavior that should become durable.
- Validation failed or exposed a reusable risk.
- A new repo-specific workflow should improve the hub.

Do not send secrets, raw logs, personal data, private customer content, or long
unredacted transcripts.

## Downstream Command

From a downstream repository:

```bash
python .github/scripts/report_orchestrator_usage.py \
  --source-repo owner/repo \
  --request "Short request summary" \
  --selected-agents "Universal Orchestrator,Testing Worker" \
  --outcome completed \
  --validation "npm test" \
  --agent-feedback-file examples/agent-feedback.json \
  --reusable-lesson "Testing Worker should ask for fixture coverage on parser changes." \
  --write
```

This writes a redacted JSON payload under `.github/memory/outbox/`.

## Hub Intake

Copy or relay that JSON payload to the hub, then run:

```bash
python .github/scripts/receive_agent_report.py --json-file path/to/report.json
python .github/scripts/evolve_personalities_from_memory.py --write-ledger
python .github/scripts/evolve_personalities_from_memory.py --write-proposals --min-signals 2
python .github/scripts/update_agent_effectiveness_profile.py --write
python .github/scripts/run_orchestrator_checks.py
```

## Quality Rule

Reports are signals, not truth. The hub should update durable memory or create a
personality only after evidence, confidence, and overlap are checked.

## Per-Agent Feedback

Use `agent_feedback` when a sub-personality was notably useful, noisy, missing,
or harmful. Keep each item short:

```json
[
  {
    "agent": "Testing Worker",
    "role": "validation",
    "usefulness": "medium",
    "issue": "Needed stronger fixture guidance.",
    "lesson": "Parser changes should include fixture coverage."
  }
]
```
