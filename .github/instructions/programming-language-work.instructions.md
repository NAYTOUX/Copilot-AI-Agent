---
applyTo: ["**/*.py", "**/*.js", "**/*.jsx", "**/*.ts", "**/*.tsx", "**/*.java", "**/*.cs", "**/*.go", "**/*.rs", "**/*.sql"]
description: "General language-worker rules for implementation and refactoring."
---

# Programming Language Work Rules

- Preserve architecture and public contracts.
- Prefer readable, maintainable code over cleverness.
- Keep patches narrow and behavior-focused.
- Use project-native dependencies and tooling.
- Validate touched code with the strongest available local command.
- Add tests when behavior changes or risk is non-trivial.
- Do not hide uncertainty in code comments or vague fallback behavior.

