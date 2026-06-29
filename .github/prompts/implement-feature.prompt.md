---
name: "implement-feature"
description: "Implement a feature with scoped routing, minimal patching, and validation."
agent: "Delivery Lead"
tools: ["read", "search", "edit", "execute", "agent"]
argument-hint: "<feature request>"
---

Implement the requested feature.

Context:
- #file:AGENTS.md
- #file:.github/copilot-instructions.md
- #file:.github/instructions/programming-language-work.instructions.md

Map the impacted files, preserve architecture, implement the smallest complete
patch, run targeted validation, and report residual risk.
