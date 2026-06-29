---
name: "finance-market-analysis"
description: "Analyze finance, market, macro, KPI, or quantitative logic rigorously."
agent: "Data Finance Worker"
tools: ["read", "search", "execute", "web", "agent"]
argument-hint: "<finance question>"
---

Handle this finance or data-analysis task with explicit formulas, assumptions,
sources, dates, units, and caveats.

Context:
- #file:AGENTS.md
- #file:.github/agents/Data-Finance-Worker.agent.md
- #file:.github/agents/Macro-Economist-Worker.agent.md
- #file:.github/instructions/data-finance.instructions.md

Do not invent data or financial logic. State missing-data behavior.
