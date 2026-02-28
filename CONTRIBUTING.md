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

1. Create a feature branch from `dev`.
2. Keep commits focused and small.
3. Open a pull request targeting `dev` with a clear summary and testing notes.
4. Ensure GitHub Actions checks pass.
5. If behavior changes for users, add an entry under `## [Unreleased]` in `CHANGELOG.md`.

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

Always validate publishing on TestPyPI before publishing to production PyPI.

1. Run `.github/workflows/release-testpypi.yml` from GitHub Actions (`workflow_dispatch`).
2. Verify the package can be installed from TestPyPI.
3. Publish a GitHub Release to trigger `.github/workflows/release.yml` for real PyPI.

Both workflows use Trusted Publishing (OIDC), so configure pending publishers in both PyPI and TestPyPI.

Before publishing a release, move relevant `## [Unreleased]` items from `CHANGELOG.md`
into a new version section and include that summary in GitHub Release notes.

## Community and Security

- Follow the project Code of Conduct in `CODE_OF_CONDUCT.md`.
- Report vulnerabilities via `SECURITY.md` instead of public issues.
