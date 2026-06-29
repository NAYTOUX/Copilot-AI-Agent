# Publish to GitHub

Use this checklist when this folder becomes the canonical GitHub repository for
the reusable Copilot agent hub.

## Preconditions

- The target repository is private unless all memory and examples are reviewed
  for public release.
- The default branch is `main`.
- No generated docs are stale.
- No memory file was rewritten destructively.

## Local Release Gate

```bash
python .github/scripts/run_orchestrator_checks.py
python .github/scripts/prepare_release.py --allow-dirty
```

Use `--allow-dirty` while preparing the first commit. Remove it once the first
commit exists and the branch is clean.

## First Commit

```bash
git add .gitignore AGENTS.md README.md CHANGELOG.md CONTRIBUTING.md SECURITY.md .github docs examples
git commit -m "Initialize universal Copilot agent hub"
```

## Remote

```bash
git remote add origin <github-repo-url>
git push -u origin main
```

Do not push until the release gate passes and the memory/privacy review is done.

