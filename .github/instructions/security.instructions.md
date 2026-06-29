---
applyTo: ["**/*auth*", "**/*secret*", "**/*token*", "**/.env*", ".github/workflows/**", "**/security/**"]
description: "Security, secrets, privacy, permissions, and dependency-risk rules."
---

# Security Rules

- Never print or commit secrets.
- Use least privilege for tokens, workflow permissions, and service accounts.
- Validate external inputs and untrusted files.
- Avoid logging personal, financial, or customer data.
- Flag dependency and supply-chain risk when adding packages or actions.
- Prefer official actions and pinned versions for high-risk workflows.

