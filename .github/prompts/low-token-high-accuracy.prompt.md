---
name: "low-token-high-accuracy"
description: "Answer accurately with minimal context, compact reasoning, and explicit uncertainty."
agent: "Universal Orchestrator"
tools: ["read", "search", "agent"]
argument-hint: "<question>"
---

Answer the user's request with the smallest sufficient context.

Context:
- #file:AGENTS.md
- #file:.github/copilot-instructions.md

Use targeted search only when needed. Be concise, concrete, and explicit about
uncertainty.
