# Self-Improvement Protocol

This protocol controls how the agent system learns.

## Step 1 - Classify The Learning

Use the narrowest durable bucket:

- `feedback`: user reaction, preferred delivery style, or recurring frustration.
- `routing`: a better mapping between task signals and specialist ownership.
- `governance`: changes to agents, prompts, skills, instructions, or validators.
- `memory`: changes to intake, retention, privacy, or profile generation.
- `quality`: validation, regression, release, or testing improvement.
- `domain`: reusable domain rule such as finance, UI, security, or DevOps.
- `provenance`: external repo report or automation payload.

Reject transient details that will not help future work.

## Step 2 - Decide Where It Goes

- Feedback and reusable lessons -> `orchestrator-feedback-loop.md`.
- Routing changes -> `ORCHESTRATOR_ROUTING_SCORECARD.md`.
- Architecture or current-state assessment -> `ORCHESTRATOR_AUDIT.md`.
- Planned improvements -> `ORCHESTRATOR_ROADMAP.md`.
- Completed changes and validation -> `ORCHESTRATOR_IMPROVEMENT_LOG.md`.
- External reports -> `.github/memory/inbox/`.
- Automation provenance -> `.github/memory/provenance/`.

## Step 3 - Safety Gate

Do not store:

- secrets
- private keys
- environment values
- raw private logs
- personal data
- customer content
- full proprietary source snippets from other repositories

Redact or summarize before storing.

## Step 4 - Append Format

Use this shape for durable entries:

```markdown
### YYYY-MM-DD - Short title

- **Source**: user | repo | workflow | external-report
- **Category**: routing | governance | memory | quality | domain | provenance
- **Summary**: one sentence
- **Evidence**: command, file, report, or observation
- **Decision**: what changed or what should be reused
- **Confidence**: high | medium | low
- **Privacy**: public | internal | sensitive-redacted
- **Next action**: concrete follow-up or none
```

## Step 5 - Refresh Derived Profiles

Run after feedback/governance updates:

```bash
python .github/scripts/update_orchestrator_adaptive_profile.py
python .github/scripts/update_orchestrator_personality.py
python .github/scripts/validate_copilot_customizations.py
```

## Step 6 - Closeout

A governance session is not done until:

- memory is updated when durable behavior changed
- generated profiles are refreshed when relevant
- validators pass or failures are reported clearly

