# Contributing to VectorClaw

Thanks for helping improve VectorClaw.

## Development Environment

Use the devcontainer as the default contributor environment:

1. Open the repository in VS Code.
2. Run `Dev Containers: Reopen in Container`.
3. Wait for setup to complete (`pip install -e .[dev]`).

## Local Checks

Run these before opening a pull request:

```bash
pytest -q
python -m build
```

## Branch and PR Workflow

1. Create a feature branch from `main`.
2. Keep commits focused and small.
3. Open a pull request with a clear summary and testing notes.
4. Ensure GitHub Actions checks pass.

## Testing Guidance

- Add or update tests for behavior changes.
- Prefer deterministic unit tests.
- If a change cannot be fully tested in CI (for example, physical robot behavior), include manual test steps in the PR.

## Commit Style

Prefer concise Conventional Commit style prefixes:

- `feat:` new functionality
- `fix:` bug fixes
- `docs:` documentation changes
- `test:` test-only changes
- `chore:` maintenance and tooling

## Releases

Releases are published from GitHub Releases via `.github/workflows/release.yml`.
Use a tagged release with release notes after CI passes on `main`.
