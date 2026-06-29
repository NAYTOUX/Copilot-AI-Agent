# Change Control

Use this process for changes to the hub after the first commit.

## Classification

| Change type | Required evidence |
| --- | --- |
| Agent personality | registry validation, catalog check |
| New personality | personality spec, overlap review, routing eval or rationale, full hub checks |
| VS Code Copilot settings | settings validator, referenced instruction files, security baseline review, full hub checks |
| Copilot code review | code-review skill validation, review instruction check, quality-gate evidence |
| Routing behavior | routing eval case, route output sample |
| Memory governance | append-only check, privacy review |
| Copilot hooks | hook JSON validation, hook guard tests, privacy review |
| Release or export | doctor, prepare release, dry-run export |
| Security or workflow | sensitive-content scan, least-privilege review |
| Docs only | link check by reviewer, no generated-doc drift |

## Required Commands

```bash
python .github/scripts/run_orchestrator_checks.py
python .github/scripts/prepare_release.py --allow-dirty
```

After the first commit, run strict doctor before publishing:

```bash
python .github/scripts/doctor_agent_hub.py --strict
```

## Decision Rule

Do not accept a change just because an agent produced a plausible answer. Accept
it only when the responsible owner, validation evidence, and rollback path are
clear.
