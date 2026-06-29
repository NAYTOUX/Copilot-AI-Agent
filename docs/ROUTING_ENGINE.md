# Routing Engine

The hub includes a deterministic local router for quick triage.

## Command

```bash
python .github/scripts/route_request.py --text "Fix the failing Python tests"
```

JSON output:

```bash
python .github/scripts/route_request.py --text "Fix the failing Python tests" --json
```

## Inputs

- `.github/routing-rules.json`: keyword rules and validation hints.
- `.github/agent-registry.json`: known agents and capabilities.
- `docs/CAPABILITY_MATRIX.md`: generated human-readable summary from the
  registry.

## Output

- confidence
- fallback status
- selected agents
- matched rules
- validation hints

## Design

This is not a replacement for the Orchestrator's judgment. It is a deterministic
pre-router that catches obvious ownership and prevents avoidable delegation
drift.

## Evaluation

Routing scenarios live in `.github/evals/routing-cases.json`.

Run:

```bash
python .github/scripts/evaluate_routing.py
```

The evaluator checks expected agents, forbidden agents, and minimum confidence.
