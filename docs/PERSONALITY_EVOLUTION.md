# Personality Evolution

The hub improves personalities through controlled memory-driven changes.

## Loop

1. A repository uses `Universal Orchestrator`.
2. The repository creates a usage report with
   `python .github/scripts/report_orchestrator_usage.py`.
3. The hub receives the report with
   `python .github/scripts/receive_agent_report.py --json-file <report.json>`.
4. `Personality Evolution Governor` reviews recurring gaps.
5. The hub either tunes an existing personality or creates a new one from a
   validated spec.
6. Routing rules, eval cases, docs, and memory are updated together.

## Creation Threshold

Create a new personality only when at least one is true:

- the user explicitly asks for a durable new role;
- repeated reports show the same specialist gap;
- routing evals repeatedly require an agent that does not exist;
- an existing agent would become too broad if expanded further.

Reject creation when the need is one-off, vague, already covered, or based on
unverified claims.

## Commands

Dry-run a new personality:

```bash
python .github/scripts/create_agent_personality.py --spec examples/personality-spec.json --dry-run
```

Analyze memory for personality changes:

```bash
python .github/scripts/evolve_personalities_from_memory.py
```

Generate proposal specs from repeated named memory signals:

```bash
python .github/scripts/evolve_personalities_from_memory.py --write-proposals --min-signals 2
```

Promote a proposal after evidence review:

```bash
python .github/scripts/promote_personality_proposal.py \
  --proposal .github/personality-proposals/<spec>.json \
  --min-evidence 2 \
  --update-routing \
  --apply
```

Update the generated effectiveness profile:

```bash
python .github/scripts/update_agent_effectiveness_profile.py --write
```

Generate a downstream usage report:

```bash
python .github/scripts/report_orchestrator_usage.py \
  --source-repo owner/repo \
  --request "Fix routing gap after API task" \
  --selected-agents "Universal Orchestrator,Backend API Worker,Testing Worker" \
  --outcome completed \
  --validation "pytest"
```
