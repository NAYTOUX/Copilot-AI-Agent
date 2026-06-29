---
name: "quality-release-gate"
description: "Workflow for review, validation, regression checks, and release readiness."
allowed-tools: ["read", "search", "execute", "agent"]
---

# Quality Release Gate

## When To Use

- The user asks for a review.
- A change is ready for final validation.
- The task affects production, security, finance, data integrity, workflows, or
  user-visible behavior.

## Workflow

1. Identify the behavior under review.
2. Inspect changed and adjacent files.
3. Check correctness, tests, security, performance, and maintainability.
4. Run or recommend validation.
5. State release recommendation and residual risk.

## Output Contract

- Findings
- Validation
- Release recommendation
- Residual risk

