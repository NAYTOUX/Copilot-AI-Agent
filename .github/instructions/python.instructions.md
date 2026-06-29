---
applyTo: "**/*.py"
description: "Python implementation, debugging, and validation rules."
---

# Python Rules

- Keep functions small enough to read without unnecessary abstraction.
- Prefer explicit error handling at IO, parsing, and external-service boundaries.
- Avoid mutable default arguments.
- Use `pathlib` for path logic when it improves clarity.
- Preserve public signatures unless a breaking change is requested.
- Validate with:

```bash
python -m py_compile <touched_files>
```

