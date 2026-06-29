---
name: "new-chat-default"
description: "Default entrypoint for a new session with the Universal Orchestrator."
agent: "Universal Orchestrator"
tools: ["read", "search", "edit", "execute", "agent", "web", "github"]
argument-hint: "<user request>"
---

Load the core operating context and handle the user's request through the normal
orchestration protocol.

Context:
- #file:AGENTS.md
- #file:.github/copilot-instructions.md
- #file:.github/memory/MEMORY_INDEX.md
- #file:.github/memory/ORCHESTRATOR_ROUTING_SCORECARD.md

Return the answer in the user's language, concise and validated when needed.
