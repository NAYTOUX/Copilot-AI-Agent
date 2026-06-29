---
name: "agent-hub-health-audit"
description: "Audit the agent hub health, registry coverage, validation, and memory governance."
agent: "Agent System Governor"
tools: ["read", "search", "execute", "agent"]
argument-hint: "<audit scope>"
---

Run a health audit of the agent hub.

Context:
- #file:AGENTS.md
- #file:.github/agent-registry.json
- #file:.github/memory/ORCHESTRATOR_ROUTING_SCORECARD.md
- #file:.github/scripts/audit_agent_hub.py
- #file:.github/scripts/validate_copilot_customizations.py

Check registry coverage, routing coherence, validation health, memory safety,
and remaining governance risks. Run the relevant checks before reporting.
