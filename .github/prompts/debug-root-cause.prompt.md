---
name: "debug-root-cause"
description: "Diagnose and fix runtime failures or regressions root-cause first."
agent: "Debugger"
tools: ["read", "search", "edit", "execute", "agent"]
argument-hint: "<failure or traceback>"
---

Debug the reported issue root-cause first.

Context:
- #file:AGENTS.md
- #file:.github/copilot-instructions.md
- #file:.github/agents/Debugger.agent.md

Identify what is broken, why it breaks, apply the minimal fix, and validate the
failing path.
