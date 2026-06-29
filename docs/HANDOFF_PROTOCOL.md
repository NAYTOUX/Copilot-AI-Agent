# Agent Handoff Protocol

This protocol standardizes how the Orchestrator delegates work and how
specialists report back.

## Manager Brief

Every delegation must include:

```markdown
## Manager Brief

- Objective:
- Context:
- Constraints:
- Non-goals:
- Target files or systems:
- Acceptance criteria:
- Required validation:
- Risk level: low | medium | high
- Deadline or token constraint:
```

## Specialist Response

Specialists must return:

```markdown
## Specialist Report

- Owner:
- Decision:
- Work performed:
- Evidence:
- Validation:
- Risks:
- Follow-up:
```

## Escalation

Escalate back to the Orchestrator when:

- the requested change conflicts with evidence
- the task crosses into another specialist's primary risk area
- validation cannot be run
- secrets, legal risk, financial risk, or destructive operations are involved
- the original done criteria are no longer sufficient

## Conflict Resolution

When specialists disagree, the Orchestrator decides by priority:

1. user-stated requirement
2. verified repository/runtime evidence
3. safety and data integrity
4. existing architecture
5. maintainability
6. speed or convenience

