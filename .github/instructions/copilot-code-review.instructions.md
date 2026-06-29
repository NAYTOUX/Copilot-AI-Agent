---
applyTo: ["**"]
excludeAgent: "cloud-agent"
description: "Copilot code review rules and skill routing."
---

# Copilot Code Review Rules

- Use `#file:.github/skills/code-review/SKILL.md` for PR, diff, or patch
  reviews.
- Lead with findings ordered by severity.
- Report actionable defects, regressions, missing tests, security/privacy risks,
  data integrity issues, and release blockers.
- Avoid generic praise, broad style opinions, and unsupported speculation.
- Cite the smallest relevant file or behavior reference.
- State validation evidence or the exact missing validation.
- If no issues are found, say so clearly and note residual risk.
