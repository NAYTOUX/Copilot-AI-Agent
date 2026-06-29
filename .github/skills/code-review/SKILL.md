---
name: "code-review"
description: "Workflow for Copilot code review: find actionable defects, missing tests, security risks, and release blockers."
allowed-tools: ["read", "search", "execute", "agent"]
---

# Code Review

## When To Use

- A pull request, diff, patch, or changed file set needs review.
- The user asks for review, regression risk, release readiness, or hidden bugs.
- Copilot code review needs repository-specific review discipline.

## Workflow

1. Identify the changed behavior and affected contracts.
2. Inspect the changed files and the nearest callers, tests, configs, and docs.
3. Lead with concrete findings ordered by severity.
4. For each finding, cite the file and line when available.
5. Check missing tests, validation gaps, security/privacy exposure, data loss,
   performance risk, and rollback path.
6. State what validation was run or why it was not run.

## Review Rules

- Report actionable defects, not style preferences.
- Do not invent runtime behavior, test results, or vulnerability impact.
- Prefer one precise finding over broad generic advice.
- Treat secrets, auth, permissions, workflows, financial logic, and data
  migrations as high-risk surfaces.
- If no issues are found, say that clearly and state residual test risk.

## Output Contract

- Findings ordered by severity
- Missing tests or validation
- Residual risk
- Release recommendation
