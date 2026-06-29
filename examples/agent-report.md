---
source_repo: owner/repo
source_channel: manual
agent: Repo Orchestrator
category: quality
confidence: medium
privacy: internal
requested_action: review
severity: medium
---

## Summary

The test suite repeatedly failed because the workflow used a stale dependency
cache key.

## Evidence

- Workflow: `.github/workflows/ci.yml`
- Failure: dependency import error after lockfile change
- Validation: rerun passed after cache key included lockfile hash

## Reusable Lesson

CI dependency cache keys should include the lockfile hash.

## Next Action

Consider adding this to workflow rules.
