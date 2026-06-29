# Copilot Instructions

## Repository Purpose

This repo is a reusable GitHub Copilot agent hub. It stores agent profiles,
repository instructions, prompt files, agent skills, append-only memory,
cross-repo relay tooling, hooks, and validation scripts for reuse in other
repositories.

## Start Here

- Load `AGENTS.md` first; it is the canonical operating contract.
- Use `.github/agents/` for named specialist personalities.
- Use `.github/instructions/` for path-scoped rules with `applyTo`.
- Use `.github/prompts/` for reusable task entrypoints.
- Use `.github/skills/` for portable multi-step workflows.
- Use `.github/memory/` for append-only learning and routing context.
- Use `.github/hooks/` for deterministic Copilot lifecycle guardrails.

## Working Rules

- Match the user's language and keep responses direct.
- Ask only when ambiguity creates meaningful correctness, safety, financial,
  legal, security, or user-visible risk.
- Prefer targeted search and minimal edits.
- Preserve the existing hierarchy, registry, routing rules, and memory policy.
- Never expose secrets, tokens, private keys, environment values, raw prompts,
  private logs, or private payloads in prompts, docs, memory, or external
  research.
- Do not claim validation that was not run.

## Code Review

- For PR, diff, patch, or changed-file review, use
  `#file:.github/skills/code-review/SKILL.md`.
- Lead with findings ordered by severity.
- Prefer actionable defects, missing tests, security/privacy risk, data
  integrity issues, workflow permission problems, and release blockers over
  style comments.
- If no issues are found, say so and state residual risk.

## Validation

- For `.github` customization changes, run:
  `python .github/scripts/validate_copilot_customizations.py`.
- For governance, memory, hooks, routing, skills, or agent changes, run:
  `python .github/scripts/run_orchestrator_checks.py`.
- For downstream repos, replace generic commands with the native test,
  typecheck, lint, or release commands before accepting results.
