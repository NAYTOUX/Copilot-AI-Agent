## Change

- 

## Validation

- [ ] `python .github/scripts/run_orchestrator_checks.py`
- [ ] `python .github/scripts/prepare_release.py --allow-dirty`
- [ ] `python .github/scripts/scan_sensitive_content.py`

## Agent Hub checklist

- [ ] Registry, routing rules, and generated docs are synchronized.
- [ ] New routing behavior has an eval case when applicable.
- [ ] Memory changes are append-only.
- [ ] No secrets, raw private logs, or personal data were added.
- [ ] Release notes or docs were updated when behavior changed.
