---
applyTo: ["**/api/**", "**/server/**", "**/routes/**", "**/controllers/**", "**/services/**"]
description: "Backend, service, API, and integration rules."
---

# Backend API Rules

- Validate input at trust boundaries.
- Keep API contracts stable unless migration is explicit.
- Use predictable error responses without leaking internals.
- Add idempotency where retries can duplicate side effects.
- Keep observability useful without logging sensitive payloads.

