---
applyTo: ".github/memory/**"
description: "Append-only memory, feedback-loop, provenance, and durable-learning rules."
---

# Memory Governance Rules

- Append-only: never delete or rewrite historical entries.
- Store durable learning only: decisions, reusable lessons, validation evidence,
  routing changes, and accepted constraints.
- Do not store secrets, private raw logs, personal data, or unredacted customer
  content.
- Mark source, confidence, timestamp, and privacy classification.
- Add correction notes instead of editing old facts.
- Register new memory files in `.github/memory/MEMORY_INDEX.md`.
- Run:

```bash
python .github/scripts/check_memory_append_only.py
python .github/scripts/run_orchestrator_checks.py
```

