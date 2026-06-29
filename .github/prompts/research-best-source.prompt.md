---
name: "research-best-source"
description: "Research current external facts, libraries, APIs, standards, or market data with source verification."
agent: "Research Worker"
tools: ["read", "search", "execute", "web"]
argument-hint: "<research question>"
---

Research the user's question using authoritative, privacy-safe sources.

Context:
- #file:AGENTS.md
- #file:.github/agents/Research-Worker.agent.md

Cross-check decision-critical claims, report confidence, and give an
implementation-ready recommendation.
