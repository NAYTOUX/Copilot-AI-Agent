---
name: "super-best-result"
description: "Use when the user wants the strongest practical result with end-to-end validation."
agent: "Universal Orchestrator"
tools: ["read", "search", "edit", "execute", "agent", "web", "github"]
argument-hint: "<high-stakes task>"
---

Deliver the strongest practical result for the user's request.

Context:
- #file:AGENTS.md
- #file:.github/copilot-instructions.md
- #file:.github/memory/ORCHESTRATOR_ROUTING_SCORECARD.md
- #file:.github/skills/universal-super-delivery/SKILL.md

Use the relevant specialists, implement when appropriate, validate, and return
only the highest-signal result.
