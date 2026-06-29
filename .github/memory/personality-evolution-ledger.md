# Personality Evolution Ledger

Append-only record for decisions that create, tune, merge, reject, or defer
agent personality changes.

## Policy

- A new personality requires durable evidence, not just a single weak signal.
- Prefer tuning existing agents when the capability is already represented.
- Every accepted change must identify validation evidence.
- Every rejected change must state why the existing hierarchy is sufficient.

## Entries

### 2026-06-28 - Initialize personality evolution loop

- Decision: create controlled evolution surface.
- Evidence: user requested memory-aware personality creation and cross-repo
  usage feedback so Orchestrator and sub-personalities improve over time.
- Action:
  - Add `Personality Evolution Governor`.
  - Add personality spec, creation, usage-report, and memory-analysis tooling.
  - Add cross-repo reporting docs.
- Validation: pending in current implementation pass.
