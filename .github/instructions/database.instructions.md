---
applyTo: ["**/*.sql", "**/migrations/**", "**/schema/**", "**/models/**"]
description: "Database schema, migration, query, and data-integrity rules."
---

# Database Rules

- Preserve data integrity before performance.
- Avoid destructive migrations without explicit approval.
- Use parameterized queries.
- Explain indexes by the query pattern they support.
- Include rollback or recovery notes for risky migrations.

