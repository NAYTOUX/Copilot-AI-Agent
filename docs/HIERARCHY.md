# Agent Hierarchy

## Mental Model

The system behaves like a company:

- `Universal Orchestrator`: CEO/operator. Owns final answer quality.
- Bosses: Chief of Staff, Agent System Governor, Memory Governor, Personality
  Evolution Governor, Delivery Lead, Quality Governor.
- Domain leads: programming, AI, product/UX, data/finance, research, security,
  DevOps, documentation, automation.
- Workers: language, UI, backend, database, testing, debugging, performance,
  finance, macro, research, security, cloud, observability, compliance, mobile,
  CI, docs, localization.

## Request Flow

1. User talks to `Universal Orchestrator`.
2. Orchestrator loads memory and routing scorecard.
3. Orchestrator classifies the task and builds a manager brief.
4. Only relevant agents receive the task.
5. Specialists return evidence, not vague confidence.
6. Orchestrator reconciles results, validates, updates memory if needed, and
   returns the final response.
7. Downstream repositories can send usage reports back to the hub.
8. Personality Evolution Governor turns repeated gaps into tuned or new
   personalities only after memory evidence and validation.

## Why This Shape

One huge agent becomes vague and hard to validate. This hierarchy keeps a single
accountable Orchestrator while allowing precise specialists for real domains.

## Registry

`.github/agent-registry.json` is the machine-readable source for agent names,
files, levels, categories, and capabilities. The validator fails if the registry
and agent files drift apart.
