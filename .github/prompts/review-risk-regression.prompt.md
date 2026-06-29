---
name: "review-risk-regression"
description: "Review code or changes for bugs, regressions, missing tests, and release risk."
agent: "Quality Governor"
tools: ["read", "search", "execute", "agent"]
argument-hint: "<review scope>"
---

Review the provided code or current changes.

Context:
- #file:AGENTS.md
- #file:.github/copilot-instructions.md
- #file:.github/agents/Quality-Governor.agent.md
- #file:.github/instructions/testing-quality.instructions.md

Lead with findings ordered by severity. Include concrete file references and
missing validation.
