# Code Review Rules

- Findings first, ordered by severity.
- Every finding needs a concrete file or behavior reference.
- Prefer bugs, regressions, security/privacy risk, data integrity issues,
  workflow permission problems, and missing validation.
- Do not block on formatting or subjective style unless it creates real
  maintainability or correctness risk.
- If validation is absent, say exactly which command or evidence is missing.
- If there are no findings, say so and list residual risk.
