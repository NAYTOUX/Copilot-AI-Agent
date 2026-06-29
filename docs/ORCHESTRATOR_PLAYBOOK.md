# Orchestrator Playbook

## Default Loop

1. Load `AGENTS.md`, Copilot instructions, memory index, personality profile,
   adaptive profile, and routing scorecard.
2. Restate the objective internally.
3. Classify the concern.
4. Build a manager brief.
5. Delegate to the minimum useful specialist set.
6. Require evidence and validation.
7. Reconcile outputs.
8. Update memory if a durable lesson or governance change occurred.
9. For downstream repositories, generate a usage report when the session
   exposed reusable routing, memory, validation, or personality learning.
10. Return a concise final response.

## When To Ask The User

Ask only when continuing would risk:

- destructive file or data changes
- security exposure
- financial or legal error
- major user-visible behavior change
- large scope mismatch
- irreversible architecture direction

Otherwise, make a reasonable assumption and continue.

## Confidence Levels

- `high`: validated locally or confirmed by authoritative sources.
- `medium`: evidence is good but validation is partial.
- `low`: plausible but unverified; requires follow-up before high-risk use.

## Done Criteria

A task is done when:

- the requested artifact exists or the answer is complete
- relevant validation passed or the limitation is explicit
- memory was updated if durable learning occurred
- final answer states changed files and residual risk
- downstream usage report was generated when the session produced reusable hub
  learning

## Maintenance Command

Run the full health path after governance changes:

```bash
python .github/scripts/run_orchestrator_checks.py
```

For a readable health summary:

```bash
python .github/scripts/audit_agent_hub.py
```

For deterministic pre-routing:

```bash
python .github/scripts/route_request.py --text "Fix a Python regression"
```

For cross-repo usage feedback:

```bash
python .github/scripts/report_orchestrator_usage.py --source-repo owner/repo --request "Short session summary"
```

Include `--agent-feedback-file examples/agent-feedback.json` when individual
sub-personalities produced useful or problematic behavior.

For personality evolution review:

```bash
python .github/scripts/evolve_personalities_from_memory.py
```

For generated capability docs:

```bash
python .github/scripts/generate_capability_matrix.py --check
```
