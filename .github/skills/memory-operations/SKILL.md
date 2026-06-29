---
name: "memory-operations"
description: "Workflow for safe append-only memory updates, inbound reports, feedback loops, and profile regeneration."
allowed-tools: ["read", "search", "edit", "execute"]
---

# Memory Operations

## When To Use

- The task asks to store, update, relay, summarize, or reuse memory.
- A session produced durable lessons.
- Another repository sends structured information.

## Workflow

1. Classify the information using `self-improvement-protocol.md`.
2. Run the safety gate.
3. Store only durable, source-labeled learning.
4. Use `.github/scripts/receive_agent_report.py` for inbound reports.
5. Refresh adaptive and personality profiles when relevant.
6. Run orchestrator checks.

## Output Contract

- Memory decision
- Path updated
- Privacy classification
- Validation evidence

