# Copilot Code Review

This hub includes a dedicated Copilot code review path.

## Surfaces

- `.github/skills/code-review/SKILL.md`: review workflow optimized for
  actionable findings.
- `.github/instructions/copilot-code-review.instructions.md`: repository-wide
  code review rules, scoped away from the cloud coding agent with
  `excludeAgent: "cloud-agent"`.
- `.github/agents/Quality-Governor.agent.md`: release-risk owner for reviews.

## Expected Review Behavior

- Lead with findings ordered by severity.
- Cite concrete files or behavior.
- Prefer correctness, security, regression, data integrity, workflow, and
  missing-test issues over style comments.
- State validation evidence or missing validation.
- If no issues are found, say so and list residual risk.

## Validation

Run:

```bash
python .github/scripts/validate_copilot_customizations.py
python .github/scripts/run_orchestrator_checks.py
```
