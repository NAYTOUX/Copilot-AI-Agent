---
name: "programming-language-work"
description: "Workflow for routing and executing implementation work by language with project-native validation."
allowed-tools: ["read", "search", "edit", "execute", "agent"]
---

# Programming Language Work

## When To Use

- The request asks for code, refactoring, debugging, tests, or implementation.
- The right language worker is not obvious.

## Workflow

1. Identify language, framework, and project tooling.
2. Select the narrowest worker.
3. Preserve public contracts.
4. Implement the smallest complete patch.
5. Run project-native validation.

## Output Contract

- Worker selected
- Implementation summary
- Validation evidence
- Edge cases

