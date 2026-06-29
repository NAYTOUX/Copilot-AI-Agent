---
name: "route-request"
description: "Classify a user request and recommend the right agents before work starts."
agent: "Universal Orchestrator"
tools: ["read", "search", "execute", "agent"]
argument-hint: "<request to route>"
---

Route this request before implementation.

Context:
- #file:AGENTS.md
- #file:.github/routing-rules.json
- #file:.github/agent-registry.json
- #file:.github/scripts/route_request.py

Use the deterministic router when useful, then build a manager brief for the
recommended agents.
