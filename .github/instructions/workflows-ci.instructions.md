---
applyTo: ".github/workflows/**"
description: "GitHub Actions, CI, scheduled automation, and workflow-safety rules."
---

# Workflow CI Rules

- Use minimum permissions.
- Use `concurrency` for scheduled or manually repeatable jobs.
- Keep jobs idempotent.
- Avoid broad `git add -A`; stage owned paths only.
- Use deterministic commit messages for automation.
- Do not print secrets.
- Summarize operator-relevant results in `GITHUB_STEP_SUMMARY`.

