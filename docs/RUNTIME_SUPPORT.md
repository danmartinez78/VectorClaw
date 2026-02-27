# VectorClaw v1.0 Runtime Support Policy

## Supported Runtime

| Python Version | Status | Notes |
|----------------|--------|-------|
| **3.11** | ✅ **Primary (supported)** | Fully tested; required to pass CI. |
| 3.12 | ⚗️ Experimental | CI runs but failures are non-blocking. |
| ≤ 3.10 | ❌ Unsupported | Not tested; `requires-python = ">=3.11"` enforces this. |

## Rationale

Python 3.11 is chosen as the primary supported runtime for v1.0 because:

- `wirepod_vector_sdk` (the canonical SDK distribution) is validated against Python 3.11.
- The legacy `anki_vector` package is brittle on newer runtimes; Wire-Pod + Python 3.11 provides the most stable base.
- Python 3.11 is an Active LTS release in the CPython lifecycle (security fixes until 2027-10).

## CI Enforcement

The CI matrix (`.github/workflows/ci.yml`) reflects this policy:

- **Python 3.11** — required job; PR merge is blocked on failure.
- **Python 3.12** — experimental job; `continue-on-error: true` means failures are surfaced but do not block merges.
- Older versions are not included in the matrix.

## Release Checklist Reference

Before cutting a release, verify:

- [ ] All tests pass on Python 3.11 (primary).
- [ ] Experimental matrix results reviewed; known failures documented in CHANGELOG.
- [ ] `requires-python` in `pyproject.toml` matches this policy.
