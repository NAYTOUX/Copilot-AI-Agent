# Agent Relationships

`.github/agent-relationship-map.json` defines how personalities work together.

## Rules

- `Universal Orchestrator` is the only top-level owner.
- Level 1 governors report directly to Orchestrator.
- Managers coordinate; workers execute.
- Specialists escalate risk to the closest accountable governor.
- If a relationship is not explicit, use the defaults in the map.

## Relationship Types

- `reports_to`: normal accountability path.
- `manages`: agents this personality may coordinate directly.
- `collaborates_with`: common peer or support agents.
- `escalates_to`: agents that receive unresolved risk or conflict.

## Conflict Handling

- Scope conflict: Orchestrator decides from the manager brief.
- Quality conflict: Quality Governor decides validation requirements.
- Security/privacy conflict: Security Worker can block until risk is resolved.
- Memory/personality conflict: Memory Governor and Personality Evolution
  Governor must agree before durable personality changes.
