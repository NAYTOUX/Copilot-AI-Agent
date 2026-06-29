# VS Code Copilot Settings

The workspace settings in `.vscode/settings.json` make the hub's reusable
Copilot surfaces discoverable after import into another repository.

## Enabled Surfaces

| Setting | Purpose |
| --- | --- |
| `chat.useAgentsMdFile` | Loads the root `AGENTS.md` operating contract. |
| `github.copilot.chat.codeGeneration.useInstructionFiles` | Enables instruction files for code generation. |
| `chat.includeApplyingInstructions` | Shows which instruction files applied to a request. |
| `chat.includeReferencedInstructions` | Allows referenced instruction files to be included explicitly. |
| `chat.useCustomizationsInParentRepositories` | Lets nested workspaces inherit hub customizations from parent repositories. |
| `chat.instructionsFilesLocations` | Discovers `.github/instructions/*.instructions.md`. |
| `chat.promptFiles` | Enables reusable prompt files. |
| `chat.promptFilesLocations` | Discovers `.github/prompts/*.prompt.md`. |
| `chat.agentFilesLocations` | Discovers `.github/agents/*.agent.md`. |
| `chat.agentSkillsLocations` | Discovers `.github/skills/*/SKILL.md`. |
| `chat.useAgentSkills` | Enables skill usage for custom agents. |
| `chat.hookFilesLocations` | Discovers `.github/hooks/*.json`. |
| `github.copilot.chat.reviewSelection.instructions` | Routes review selection behavior to the code-review instruction file. |
| `github.copilot.chat.commitMessageGeneration.instructions` | Routes generated commit messages to the commit instruction file. |
| `github.copilot.chat.pullRequestDescriptionGeneration.instructions` | Routes generated PR descriptions to the PR instruction file. |

## Security Baseline

The hub keeps automation useful without granting broad silent execution.

| Setting | Required posture |
| --- | --- |
| `chat.tools.global.autoApprove` | `false`; no global silent tool approval. |
| `chat.permissions.default` | `default`; let the host apply normal permission prompts. |
| `chat.tools.terminal.blockDetectedFileWrites` | `outsideWorkspace`; block detected writes outside the current workspace. |
| `chat.tools.terminal.ignoreDefaultAutoApproveRules` | `false`; retain VS Code's default terminal safety rules. |
| `chat.tools.terminal.autoApprove` | Explicitly requires approval for destructive shell, forced Git, network-pipe, permission, and execution-policy commands. |
| `chat.tools.edits.autoApprove` | Explicitly requires approval for secrets, governance files, workflows, hooks, scripts, skills, agents, prompts, and memory. |
| `chat.tools.urls.autoApprove` | Empty list; no persistent URL allowlist by default. |
| `github.copilot.chat.additionalReadAccessFolders` | Empty list; no extra read roots by default. |
| `chat.mcp.discovery.enabled` | `false`; MCP discovery should be an explicit repository decision. |
| `github.copilot.chat.otel.captureContent` | `false`; do not capture prompt or response content in telemetry. |
| `github.copilot.chat.agentDebugLog.fileLogging.enabled` | `false`; avoid persistent local debug logs by default. |
| `github.copilot.chat.claudeAgent.allowDangerouslySkipPermissions` | `false`; never bypass permission checks through workspace settings. |

## Policy

- Keep settings JSON strict: no comments, no trailing commas.
- Prefer file-based instructions over inline text so changes are reviewable.
- Every referenced instruction file must live under `.github/instructions/`.
- Do not add broad `true` entries to `chat.tools.terminal.autoApprove` or
  `chat.tools.edits.autoApprove` in this reusable hub.
- Add project-specific tool approvals only in downstream repositories after a
  security review.
- Keep additional read folders empty unless a downstream repo has a documented
  cross-workspace requirement.
- Run `python .github/scripts/validate_copilot_customizations.py` after editing
  settings or referenced instruction files.
- Downstream repositories may add project-specific settings, but should keep the
  hub discovery paths unless intentionally removing that Copilot surface.
