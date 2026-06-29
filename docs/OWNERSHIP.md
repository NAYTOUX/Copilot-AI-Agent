# Ownership

This hub uses agent ownership rather than human-only ownership. Each surface has
an accountable reviewer role so future changes can be routed consistently.

## Surfaces

| Surface | Accountable agent | Required support |
| --- | --- | --- |
| `AGENTS.md` | Agent System Governor | Universal Orchestrator, Quality Governor |
| `.github/agents/` | Agent System Governor | Documentation Worker |
| `.github/agent-registry.json` | Agent System Governor | Quality Governor |
| `.github/routing-rules.json` | Universal Orchestrator | Chief of Staff, Quality Governor |
| `.github/evals/` | Quality Governor | Agent System Governor |
| `.github/memory/` | Memory Governor | Security Worker |
| `.github/memory/personality-evolution-ledger.md` | Personality Evolution Governor | Memory Governor |
| `.github/personality-proposals/` | Personality Evolution Governor | Agent System Governor |
| `.github/scripts/` | Automation Workflow Worker | Testing Worker, Security Worker |
| `.github/scripts/create_agent_personality.py` | Personality Evolution Governor | Agent System Governor, Quality Governor |
| `.github/scripts/report_orchestrator_usage.py` | Memory Governor | Personality Evolution Governor |
| `.github/workflows/` | DevOps CI Worker | Security Worker |
| `.github/skills/` | Agent System Governor | Domain owner for the skill |
| `docs/` | Documentation Worker | Surface owner |
| `examples/` | Documentation Worker | Memory Governor for relay examples |

## Review Rules

- Routing changes require a routing eval case.
- Agent changes require registry and catalog validation.
- Personality creation requires memory evidence, a spec, overlap review, and
  full hub validation.
- Memory changes require append-only validation and sensitive-content scan.
- Publication changes require `prepare_release.py`.
- Security-sensitive changes require Security Worker review.
