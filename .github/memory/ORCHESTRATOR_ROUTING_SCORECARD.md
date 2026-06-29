# Orchestrator Routing Scorecard

Purpose: decide who owns a request before work starts.

## Routing Principles

- Use the narrowest competent owner.
- Keep Orchestrator accountable for synthesis and validation.
- Delegate only with a complete manager brief.
- If two specialists overlap, choose the one closest to the primary risk.
- Escalate to `Quality Governor` for release, review, or high-regression risk.

## Scorecard

| Task signal | Primary owner | Secondary owner | Validation |
| --- | --- | --- | --- |
| Ambiguous broad request | Chief of Staff | Repo Explorer | Manager brief |
| Agent, prompt, skill, instruction changes | Agent System Governor | Memory Governor | Customization validator |
| Memory, feedback, relay, profile updates | Memory Governor | Agent System Governor | Orchestrator checks |
| New personalities, specialist gaps, usage-report learning | Personality Evolution Governor | Agent System Governor, Memory Governor | personality spec and hub checks |
| Architecture, public contracts, module boundaries | Software Architect | Delivery Lead | architecture decision and migration plan |
| Multi-file implementation | Delivery Lead | Programming Language Lead | Project tests |
| Language-specific implementation | Programming Language Lead | Matching worker | Native toolchain |
| Python | Python Worker | Testing Worker | `python -m py_compile` |
| JavaScript/TypeScript | JavaScript TypeScript Worker | Frontend UI Worker | typecheck/lint/test |
| Frontend/UI | Frontend UI Worker | Product Strategy Worker | UI/browser check |
| Mobile app/platform behavior | Mobile App Worker | Frontend UI Worker | native build/test/simulator check |
| Backend/API | Backend API Worker | Security Worker | tests/import checks |
| Database/SQL | Database Worker | Data Finance Worker | migration/query validation |
| Debugging/regression | Debugger | Testing Worker | failing path validation |
| Performance | Performance Optimizer | Debugger | benchmark or targeted check |
| AI prompts/models/routing | AI Architect | Research Worker | eval or output contract check |
| Machine learning/model pipeline | Machine Learning Worker | Data Finance Worker | evaluation split and metric evidence |
| Finance/data/markets | Data Finance Worker | Macro Economist Worker | formula/source validation |
| Macro/country/geopolitical data | Macro Economist Worker | Research Worker | source/date/unit check |
| External facts/current sources | Research Worker | Security Worker | citations and safety gate |
| Security/privacy/auth/secrets | Security Worker | DevOps CI Worker | risk verification |
| Dependency/version/license/supply-chain risk | Dependency Supply Chain Worker | Security Worker | lockfile and advisory check |
| Legal/compliance/terms/data-retention risk | Legal Compliance Worker | Research Worker | primary-source compliance note |
| CI/CD/workflows/deploy | DevOps CI Worker | Security Worker | workflow validation |
| Cloud/IaC/networking/environment | Cloud Infrastructure Worker | DevOps CI Worker | plan/smoke test/rollback note |
| Logs/metrics/tracing/alerts/incidents | Observability Worker | DevOps CI Worker | signal and sensitive-data check |
| Tests/release/review | Quality Governor | Testing Worker | test evidence |
| Docs/runbooks | Documentation Worker | Delivery Lead | command/path check |
| Automation/scripts | Automation Workflow Worker | DevOps CI Worker | dry run/sample input |
| Translation/localization | Translation Localization Worker | Documentation Worker | terminology check |

## Delegation Quality Gate

A delegation is invalid unless it includes:

- objective
- constraints
- non-goals
- acceptance criteria
- target files or unknowns
- validation evidence required
- risk level
