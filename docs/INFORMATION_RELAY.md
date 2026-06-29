# Information Relay Guide

Use this guide when another repository, agent, workflow, or chat channel needs
to send information back to this hub.

## Goal

Send small, structured, evidence-backed reports. Do not send raw logs or broad
conversation dumps.

## Good Report

```markdown
---
source_repo: owner/repo
source_channel: github-actions
agent: Repo Orchestrator
category: implementation
confidence: high
privacy: internal
requested_action: store
severity: medium
---

## Summary

Fixed stale cache invalidation by tying cache keys to source file signatures.

## Evidence

- Changed: `components/data/cache.py`
- Validation: `python -m py_compile components/data/cache.py`
- Result: local compile passed

## Reusable Lesson

Cache invalidation should be tied to stable source signatures, not runtime-only
state that changes every execution.

## Next Action

Consider adding a cache-invalidation checklist to Python/data workers.
```

## Required Fields

- `source_repo`: repository or system that produced the report.
- `source_channel`: chat, workflow, PR, issue, manual, or external.
- `agent`: agent or workflow sending the report.
- `category`: routing, governance, memory, quality, implementation, finance,
  research, security, DevOps, docs, provenance, or personality.
- `confidence`: high, medium, or low.
- `privacy`: public, internal, sensitive-redacted.
- `requested_action`: store, review, update-routing, update-memory,
  create-follow-up, or none.
- `severity`: critical, high, medium, low, or info.

## What To Include

- One-sentence summary.
- Concrete evidence.
- Validation commands and pass/fail status.
- Files or modules affected.
- Reusable lesson if one exists.
- Next action.

## What Not To Include

- Secrets or tokens.
- Private keys.
- Raw environment values.
- Full private logs.
- Personal data.
- Customer content.
- Large source files from another repo.
- Unverified claims presented as facts.

## CLI Intake

```bash
python .github/scripts/receive_agent_report.py \
  --source-repo owner/repo \
  --source-channel github-actions \
  --agent "Repo Orchestrator" \
  --category implementation \
  --confidence high \
  --privacy internal \
  --severity medium \
  --requested-action store \
  --summary "Fixed stale cache invalidation." \
  --details-file report.md
```

## Usage Report Shortcut

Downstream repositories should prefer the usage-report command after meaningful
Orchestrator sessions:

```bash
python .github/scripts/report_orchestrator_usage.py \
  --source-repo owner/repo \
  --request "Short session summary" \
  --selected-agents "Universal Orchestrator,Testing Worker" \
  --outcome completed \
  --validation "pytest" \
  --reusable-lesson "Testing Worker should require parser fixture coverage." \
  --write
```

Then relay the generated JSON to this hub:

```bash
python .github/scripts/receive_agent_report.py --json-file path/to/report.json
```

## Efficient Remontage

For the Orchestrator to use reports effectively:

- summarize first
- provide evidence second
- state confidence explicitly
- separate facts from interpretation
- include validation commands
- include severity so the Orchestrator can prioritize
- include exactly one reusable lesson when relevant
- redact before sending

## JSON Schema

Use `.github/schemas/agent-report.schema.json` when an external repo can emit
JSON before converting the payload into an inbox markdown entry.
