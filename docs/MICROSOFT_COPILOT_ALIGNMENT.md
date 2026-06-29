# Microsoft Copilot Alignment

This hub follows the current GitHub/Microsoft Copilot customization model:
repository instructions, path-scoped instructions, custom agents, agent skills,
prompt files, and hooks.

## Applied Mapping

| Recommendation surface | Hub implementation |
| --- | --- |
| Repository-wide instructions | `.github/copilot-instructions.md` gives concise repo purpose, entrypoints, and validation commands. |
| Agent instructions | `AGENTS.md` is the canonical operating contract; `.github/AGENTS.md` points back to it. |
| Path-specific instructions | `.github/instructions/*.instructions.md` use `applyTo` frontmatter. |
| VS Code workspace settings | `.vscode/settings.json` enables discovery for AGENTS, instructions, prompts, agents, skills, hooks, review, commit, and PR generation rules. |
| VS Code AI security settings | `.vscode/settings.json` disables global auto-approval, keeps additional read roots empty, requires approval for sensitive edits and risky commands, disables MCP discovery by default, and blocks detected terminal writes outside the workspace. |
| Custom agents | `.github/agents/*.agent.md` use YAML frontmatter with `description`, scoped `tools`, and `user-invocable`. |
| Agent skills | `.github/skills/*/SKILL.md` package reusable workflows with metadata and references. |
| Copilot code review | `.github/skills/code-review/SKILL.md` and `.github/instructions/copilot-code-review.instructions.md` define review behavior and skill routing. |
| Commit and PR generation | `.github/instructions/commit-message.instructions.md` and `.github/instructions/pull-request-description.instructions.md` define generated message contracts. |
| Prompt files | `.github/prompts/*.prompt.md` provide task entrypoints with `name`, `agent`, `tools`, `argument-hint`, and required file references. |
| Hooks | `.github/hooks/orchestrator-guardrails.json` injects startup context, blocks risky commands, and reminds validation after customization edits. |
| Validation | `python .github/scripts/run_orchestrator_checks.py` covers customization files, JSON contracts, hooks, routing, memory, docs, and unit tests. |

## VS Code Settings Policy

- Keep `.vscode/settings.json` tracked and strict JSON.
- Enable instruction files, prompt files, root `AGENTS.md`, custom agents,
  skills, and hooks through workspace settings.
- Reference review, commit, and pull request generation instructions by file
  instead of inline text.
- Keep every referenced instruction file under `.github/instructions/`.
- Keep global tool auto-approval disabled in this reusable hub.
- Require approval for edits to secrets, governance files, scripts, workflows,
  hooks, memory, prompts, skills, and agent definitions.
- Require approval for destructive terminal commands, forced Git operations,
  permission changes, execution-policy changes, and network-pipe execution.
- Keep MCP discovery and additional read access disabled unless a downstream
  repository explicitly reviews and enables them.
- Validate settings references through
  `python .github/scripts/validate_copilot_customizations.py`.
- When exporting to another repository, copy `.vscode/settings.json` with the
  agent hub files unless the target repo intentionally disables a surface.

## Hook Policy

Hooks must stay deterministic and privacy-preserving.

- Do not persist raw prompts, tool payloads, secrets, or environment values.
- Use `preToolUse` only for concrete safety checks.
- Return empty JSON when no decision is needed.
- Prefer `additionalContext` reminders over automatic edits.
- Keep hook scripts fast enough for repeated use.
- Treat hook output as guardrail context, not as durable memory.

## Agent Profile Policy

- Prefer explicit `tools` over all-tools access.
- Use `agents` on manager profiles when a manager should delegate only to a
  known specialist set.
- Use `handoffs` on manager profiles to expose explicit next-agent transitions
  with labels, prompts, and send behavior.
- Use `argument-hint` on user-invocable agents so requests start with clear
  task context.
- Do not use retired `infer`; use `disable-model-invocation` and
  `user-invocable` when manual-only or programmatic-only behavior is needed.
- Keep each agent mission narrow enough to avoid overlap.
- Use the relationship map and routing rules before adding a new personality.

## Prompt File Policy

- Use `name` to define the slash-command name and keep it aligned with the
  `.prompt.md` filename.
- Use `agent` to select the responsible built-in or custom agent.
- Declare `tools` explicitly instead of inheriting broad tool access.
- Include `argument-hint` so the command exposes the expected input.
- Keep prompt bodies focused on context references and task instructions.
- Do not add unsupported frontmatter such as `mode`; validate against current
  VS Code/GitHub Copilot docs.
- Validate prompt metadata through
  `python .github/scripts/validate_copilot_customizations.py`.

## Code Review Policy

- Use a dedicated `code-review` skill so Copilot can select review-specific
  behavior during PR, diff, and patch review.
- Keep review findings actionable and ordered by severity.
- Prefer correctness, security/privacy, data integrity, workflow permissions,
  missing tests, and release blockers over style comments.
- Use `excludeAgent: "cloud-agent"` for review-only instructions that should
  not steer the cloud coding agent.
- State when no issues are found and identify residual validation risk.

## Handoff Policy

- Define handoffs only on manager agents that naturally transfer work to a
  smaller specialist.
- Each handoff must include `label`, `agent`, `prompt`, and boolean `send`.
- Handoffs must target known agents and must not target the same agent.
- Use handoffs for intentional transitions, not as a replacement for routing.

## Source References

- GitHub Docs:
  <https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot>
- GitHub Docs:
  <https://docs.github.com/en/copilot/reference/custom-agents-configuration>
- GitHub Docs:
  <https://docs.github.com/en/copilot/reference/hooks-reference>
- GitHub Docs:
  <https://docs.github.com/en/copilot/tutorials/customize-code-review>
- Visual Studio Code Docs:
  <https://code.visualstudio.com/docs/copilot/customization/custom-instructions>
- Visual Studio Code Docs:
  <https://code.visualstudio.com/docs/copilot/customization/prompt-files>
- Visual Studio Code Docs:
  <https://code.visualstudio.com/docs/copilot/customization/custom-agents>
- Visual Studio Code Docs:
  <https://code.visualstudio.com/docs/copilot/customization/agent-skills>
- Visual Studio Code Docs:
  <https://code.visualstudio.com/docs/agents/reference/ai-settings>
- Visual Studio Code Docs:
  <https://code.visualstudio.com/docs/agents/security>
