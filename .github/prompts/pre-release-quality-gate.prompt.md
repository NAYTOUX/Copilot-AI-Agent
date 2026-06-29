---
name: "pre-release-quality-gate"
description: "Run a final readiness check before release, merge, deployment, or handoff."
agent: "Quality Governor"
tools: ["read", "search", "execute", "agent"]
argument-hint: "<release scope>"
---

Assess release readiness.

Context:
- #file:AGENTS.md
- #file:.github/copilot-instructions.md
- #file:.github/agents/Quality-Governor.agent.md
- #file:.github/instructions/testing-quality.instructions.md
- #file:.github/instructions/workflows-ci.instructions.md

Check correctness, regression risk, test evidence, workflow safety, and
remaining blockers.
