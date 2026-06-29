# Memory Index

This index lists the memory files the Orchestrator must consider. Memory is
append-only: add new entries or correction notes instead of deleting history.

## Core Governance Memory

- [orchestrator-feedback-loop.md](orchestrator-feedback-loop.md): prompt log,
  validation outcomes, reusable lessons, and durable improvement rules.
- [self-improvement-protocol.md](self-improvement-protocol.md): how to classify
  and persist learning.
- [orchestrator-adaptive-profile.md](orchestrator-adaptive-profile.md):
  generated adaptive routing and delivery rules.
- [orchestrator-personality.md](orchestrator-personality.md): generated active
  language, tone, risk, and delegation profile.
- [ORCHESTRATOR_ROUTING_SCORECARD.md](ORCHESTRATOR_ROUTING_SCORECARD.md):
  canonical routing matrix.
- [ORCHESTRATOR_AUDIT.md](ORCHESTRATOR_AUDIT.md): current architecture map,
  strengths, weaknesses, and governance risks.
- [ORCHESTRATOR_ROADMAP.md](ORCHESTRATOR_ROADMAP.md): prioritized governance
  improvements.
- [ORCHESTRATOR_IMPROVEMENT_LOG.md](ORCHESTRATOR_IMPROVEMENT_LOG.md): completed
  governance changes and validation evidence.
- [personality-evolution-ledger.md](personality-evolution-ledger.md):
  append-only decisions for creating, tuning, merging, rejecting, or deferring
  agent personality changes.
- [agent-effectiveness-profile.md](agent-effectiveness-profile.md): generated
  effectiveness signals from downstream usage reports.
- [orchestrator-learning-profile.md](orchestrator-learning-profile.md):
  generated learning rules from relationships, effectiveness, and personality
  evolution memory.

## Intake Memory

- [inbox/README.md](inbox/README.md): structured reports received from other
  repositories, agents, or channels.
- [provenance/README.md](provenance/README.md): append-only provenance payloads
  relayed by automation.
- [outbox/README.md](outbox/README.md): downstream usage report payloads before
  relay back to the hub.

## Loading Rules

- Always load core governance memory before Orchestrator decisions.
- Load inbox/provenance files only when the current task depends on external
  reports, prior cross-repo learnings, or memory synchronization.
- Do not treat unverified inbox reports as confirmed facts. Check confidence,
  source, and evidence first.
