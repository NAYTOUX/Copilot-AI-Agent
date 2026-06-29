# Orchestrator Feedback Loop

Purpose: preserve useful learning from sessions without turning every chat into
durable noise.

## Permanent Improvement Rules

- Match the user's language and keep delivery concise.
- Convert broad requests into objective, constraints, done criteria, and routing
  before editing.
- Use specialists only when they improve correctness or speed.
- Validate `.github` customization changes before closeout.
- Keep memory append-only and source-labeled.

## Sentiment Heuristics

- `liked`: user explicitly approves, asks to reuse pattern, or requests more of
  the same behavior.
- `neutral`: no clear feedback.
- `disliked`: user rejects result, says it missed intent, or asks for a major
  correction.

## Prompt Log

### 2026-06-27 - Initial universal agent hub build

- **Prompt**: Build a GitHub-ready repository for reusable Copilot agent
  personalities inspired by an existing `.github` agent system, with
  Orchestrator, bosses, workers, language coverage, memory, reception of
  information, and update flow.
- **Action**: Created the universal hierarchy, governance memory, relay design,
  validation scripts, workflows, prompts, skills, and documentation.
- **Validation**: Run local orchestrator checks before closeout.
- **Sentiment**: neutral
- **Praised behavior**: none recorded yet
- **Reusable lesson**: Broad agent-system requests need a concrete hierarchy,
  routing scorecard, append-only memory, and validation tooling to be useful
  outside one repository.

### 2026-06-27 - Bootstrap validation closeout

- **Prompt**: Validate the newly created universal agent hub.
- **Action**: Ran customization validation, Python compile checks, append-only
  memory check, orchestrator profile refresh, and full orchestrator checks.
- **Validation**: `python .github/scripts/validate_copilot_customizations.py`
  passed; `python -m py_compile ...` passed;
  `python .github/scripts/check_memory_append_only.py` passed;
  `python .github/scripts/run_orchestrator_checks.py` passed.
- **Sentiment**: neutral
- **Praised behavior**: none recorded yet
- **Reusable lesson**: Bootstrap repositories need append-only checks that pass
  even before the first commit exists.

### 2026-06-27 - Extended reflection hardening pass

- **Prompt**: Continue thinking deeper and extend the universal agent hub.
- **Action**: Added missing high-value specialists, a machine-readable agent
  registry, registry/prompt validation, handoff protocol, Orchestrator playbook,
  capability matrix, inbound report schema with severity, and an export script
  for downstream repositories.
- **Validation**: `python .github/scripts/validate_copilot_customizations.py`
  passed; `python -m py_compile .github/scripts/export_agent_hub.py` passed;
  `python .github/scripts/export_agent_hub.py --target .` dry-run passed.
- **Sentiment**: neutral
- **Praised behavior**: none recorded yet
- **Reusable lesson**: A reusable agent hub needs machine-checkable capability
  registry validation; otherwise routing docs and agent files drift quickly.

### 2026-06-27 - Health audit and regression test pass

- **Prompt**: Continue extending the reflection and harden the hub further.
- **Action**: Added an agent hub health audit script, a unit test suite for
  validation/registry/export/report generation, a health-audit prompt, and
  integrated tests into the standard orchestrator checks.
- **Validation**: `python .github/scripts/audit_agent_hub.py` passed with no
  warnings; `python -m unittest discover -s .github/scripts/tests -v` passed
  5 tests; `python .github/scripts/run_orchestrator_checks.py` passed.
- **Sentiment**: neutral
- **Praised behavior**: none recorded yet
- **Reusable lesson**: Once an agent hub has generated registries and relay
  scripts, governance checks should include real regression tests, not only
  schema validation.

### 2026-06-27 - Deterministic routing engine pass

- **Prompt**: Continue extending the reflection and make the hub more useful.
- **Action**: Added `.github/routing-rules.json`, a deterministic
  `.github/scripts/route_request.py` router, a route-request prompt, routing
  docs, generated capability-matrix checks, and tests for routing fallback and
  ownership detection.
- **Validation**: `python .github/scripts/route_request.py --text ...` produced
  coherent agent recommendations; `python .github/scripts/generate_capability_matrix.py --check`
  passed; `python .github/scripts/run_orchestrator_checks.py` passed 8 tests.
- **Sentiment**: neutral
- **Praised behavior**: none recorded yet
- **Reusable lesson**: A reusable Orchestrator should have a deterministic
  pre-router so obvious ownership can be tested without relying on chat-only
  judgment.

### 2026-06-27 - Routing evaluation and generated catalog pass

- **Prompt**: Continue extending the agent hub with deeper operational checks.
- **Action**: Added `.github/evals/routing-cases.json`,
  `.github/scripts/evaluate_routing.py`, negative routing cases, weighted
  agent scoring in the router, exclusion patterns for noisy matches, and
  `.github/scripts/generate_agent_catalog.py` for generated agent docs.
- **Validation**: `python .github/scripts/evaluate_routing.py` passed all
  curated cases; `python .github/scripts/generate_agent_catalog.py --check`
  passed; `python .github/scripts/run_orchestrator_checks.py` passed 10 tests.
- **Sentiment**: neutral
- **Praised behavior**: none recorded yet
- **Reusable lesson**: Routing systems need negative examples and forbidden
  agents, not only expected positives, to prevent broad noisy delegation.

### 2026-06-27 - Release readiness and doctor pass

- **Prompt**: Continue extending the agent hub with deeper readiness checks.
- **Action**: Added `.github/agent-hub-manifest.json`,
  `.github/scripts/doctor_agent_hub.py`, release/contribution/security docs,
  and manifest validation. Integrated doctor readiness into the standard
  orchestrator checks and unit tests.
- **Validation**: `python .github/scripts/doctor_agent_hub.py --no-run` passed
  with only the expected uncommitted-working-tree warning;
  `python .github/scripts/run_orchestrator_checks.py` passed 11 tests.
- **Sentiment**: neutral
- **Praised behavior**: none recorded yet
- **Reusable lesson**: A reusable agent hub needs a manifest and doctor command
  so publication readiness is machine-checkable instead of inferred from many
  separate commands.
