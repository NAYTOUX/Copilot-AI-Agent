# Orchestrator Roadmap

Updated: 2026-06-27

## Done

- Bootstrap reusable Copilot agent hierarchy.
- Add routing scorecard and manager-brief contract.
- Add append-only memory and information relay design.
- Add validation scripts and GitHub workflow plan.
- Add machine-readable agent registry and registry validation.
- Add handoff protocol, Orchestrator playbook, and capability matrix.
- Add high-value missing specialists: Software Architect, Cloud Infrastructure,
  Machine Learning, Observability, Legal Compliance, Mobile, and Dependency
  Supply Chain.
- Add health audit script and regression tests for registry, validation, export,
  and report generation.
- Add deterministic routing rules, local request router, route-request prompt,
  and generated capability matrix.
- Add routing evaluation corpus with negative cases and generated agent
  catalog.
- Add hub manifest, doctor readiness command, release process, contribution
  rules, and security policy.

## Next Priorities

1. Make the first commit and run doctor in strict mode on a clean tree.
2. Expand routing eval cases from real downstream usage.
3. Add stronger schema validation for inbound reports if payload volume grows.
4. Test the relay scripts against the first real external repository
   integration.
5. Adapt this hub to the first real downstream repository and record gaps.
6. Add repo-specific workers only when a real domain requires them.
7. Review GitHub Copilot custom-agent schema periodically and update validator
   allowed keys if the platform changes.

## Backlog

- Optional report compactor for large inbox directories.
- Optional dashboard of routing frequency and validation failures.
