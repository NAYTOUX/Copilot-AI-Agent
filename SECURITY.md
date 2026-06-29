# Security Policy

## Scope

This repository stores agent instructions, routing rules, scripts, workflows,
and memory governance. Treat it as security-sensitive because it can influence
automation and code-generation behavior in downstream repositories.

## Rules

- Do not commit secrets, tokens, private keys, or environment values.
- Do not store raw private logs, customer data, or personal data in memory.
- Keep workflow permissions least-privilege.
- Review dependency and workflow changes for supply-chain risk.
- Redact inbound reports before storing them in `.github/memory/inbox/`.

## Reporting

Open a private security issue or contact the repository owner directly. Include:

- affected file or workflow
- risk summary
- reproduction or evidence
- recommended mitigation

Before publishing or relaying memory, run:

```bash
python .github/scripts/scan_sensitive_content.py
```
