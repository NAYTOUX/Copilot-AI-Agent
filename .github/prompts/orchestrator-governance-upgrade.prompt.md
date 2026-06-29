---
name: "orchestrator-governance-upgrade"
description: "Improve the agent hierarchy, routing, memory, prompts, skills, or validation system."
agent: "Universal Orchestrator"
tools: ["read", "search", "edit", "execute", "agent"]
argument-hint: "<governance improvement>"
---

Run orchestrator audit mode and improve the governance system.

Context:
- #file:AGENTS.md
- #file:.github/copilot-instructions.md
- #file:.github/agents/Universal-Orchestrator.agent.md
- #file:.github/agents/Agent-System-Governor.agent.md
- #file:.github/agents/Memory-Governor.agent.md
- #file:.github/memory/MEMORY_INDEX.md
- #file:.github/memory/ORCHESTRATOR_AUDIT.md
- #file:.github/memory/ORCHESTRATOR_IMPROVEMENT_LOG.md
- #file:.github/memory/ORCHESTRATOR_ROADMAP.md
- #file:.github/memory/ORCHESTRATOR_ROUTING_SCORECARD.md
- #file:.github/memory/orchestrator-adaptive-profile.md
- #file:.github/memory/orchestrator-feedback-loop.md
- #file:.github/memory/orchestrator-personality.md
- #file:.github/memory/self-improvement-protocol.md
- #file:.github/scripts/validate_copilot_customizations.py
- #file:.github/scripts/update_orchestrator_adaptive_profile.py
- #file:.github/scripts/update_orchestrator_personality.py

Patch only the artifacts needed, update memory if behavior changed, then run
the orchestrator checks.
