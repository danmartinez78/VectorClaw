# VectorClaw v1.0.0 Pre-Release Checklist

**Target Release:** Sunday 2026-03-02
**Status:** In Progress

---

## A) User Install Readiness

### Fresh Environment Validation
- [x] Clean venv install from branch works
- [x] Dependencies auto-resolve correctly (`wirepod_vector_sdk 0.8.1`)
- [x] Compat check passes with Python 3.12 (warning only)
- [x] Server startup succeeds without errors
- [x] Legacy SDK rejection works with actionable message
- [x] Old SDK version rejection works with upgrade guidance

### Documentation Verification
- [ ] README.md matches actual install flow
- [ ] SKILL.md prerequisites are accurate
- [ ] Troubleshooting covers top failure modes:
  - [ ] Missing `VECTOR_SERIAL` env var
  - [ ] Legacy `anki_vector` package installed
  - [ ] Old SDK version (< 0.8.0)
  - [ ] Wire-Pod not running / robot offline

---

## B) ClawHub Skill Readiness

### Skill Metadata
- [x] `skill/SKILL.md` exists with proper frontmatter
- [x] Description clearly states capability scope
- [x] Prerequisites documented (Wire-Pod, Vector, Python 3.11+)
- [x] Emoji defined: 🤖

### Capability Scope Review
- [x] Supported capabilities clearly listed:
  - Speech (TTS)
  - Motion (drive, head, lift, off-charger)
  - Camera capture
  - Sensor reading (battery, touch, proximity)
  - Basic autonomy workflows
- [x] Known limitations documented:
  - No SLAM/NAV2
  - Face/object detection limited
  - Charger return unreliable
  - `vector_head` has runtime issues (documented as FAIL)
- [x] No hidden side-effects in default behavior

### Security Posture
- [x] Least-privilege scope (only required env: `VECTOR_SERIAL`)
- [x] No network exposure beyond local SDK connection
- [x] No persistent data storage

---

## C) Final Security Audit

### Credential Handling
| Check | Status | Notes |
|-------|--------|-------|
| No hardcoded secrets | ✅ Pass | Searched all `.py` files |
| No credentials in logs | ✅ Pass | Logger calls reviewed |
| `VECTOR_SERIAL` via env only | ✅ Pass | Standard pattern |
| SDK auth handled by wirepod | ✅ Pass | No credential exposure |

### Input Validation
| Tool | Parameter | Validation | Status |
|------|-----------|------------|--------|
| `vector_head` | `angle_deg` | Clamped `-22°` to `45°` | ✅ |
| `vector_lift` | `height` | Clamped `0.0` to `1.0` | ✅ |
| `vector_face` | `duration_sec` | Clamped `0.1` to `60.0` | ✅ |
| `vector_face` | `image_base64` | Try/except decode | ✅ |
| `vector_drive_on_charger` | `timeout_sec` | Non-negative check | ✅ |

### Motion Safety
| Feature | Status | Notes |
|---------|--------|-------|
| Emergency stop | ✅ `vector_emergency_stop` | Stops all motors |
| Charger timeout | ✅ `timeout_sec` param | Motor stop fallback |
| Rate limiting | ⚠️ None | MVP acceptable, v1.1 target |
| Motion precheck | ✅ Charger state check | Prevents stuck commands |

### Dependencies
| Package | Version | Risk | Notes |
|---------|---------|------|-------|
| `mcp` | `>=1.0.0` | ✅ Low | Official MCP SDK |
| `wirepod_vector_sdk` | `>=0.1.0` | ✅ Low | Canonical Wire-Pod SDK |
| `Pillow` | `>=9.0.0` | ✅ Low | Standard imaging library |
| `packaging` | `>=21.0` | ✅ Low | Standard version parsing |

### Security Documentation
| File | Status | Notes |
|------|--------|-------|
| `SECURITY.md` | ✅ Exists | Contact email, scope, response SLA |
| Repo visibility | ✅ Public | Already visible |

### Known Gaps (Deferred to v1.1)
- [ ] Rate limiting on motion commands
- [ ] Input sanitization audit for all string parameters
- [ ] Supply-chain dependency pinning (requirements.lock)

---

## D) Hardware Validation Summary

### Smoke Test (2026-02-28)
**Robot:** Vector-S9R3 (serial `00a1546c`)
**SDK:** wirepod_vector_sdk 0.8.1

| Tool | Result | Notes |
|------|--------|-------|
| `vector_status` | ✅ PASS | Battery, charging state |
| `vector_drive_off_charger` | ✅ PASS | Reliable |
| `vector_say` | ✅ PASS | TTS works |
| `vector_lift` | ✅ PASS | Height control |
| `vector_touch_status` | ✅ PASS | Sensor reading |
| `vector_charger_status` | ✅ PASS | Charging state |
| `vector_capture_image` | ✅ PASS | Image capture |
| `vector_look` | ✅ PASS | Camera feed |
| `vector_proximity_status` | ✅ PASS | Distance sensing |
| `vector_head` | ❌ FAIL | Runtime error (Angle comparison) |
| `vector_drive_on_charger` | ⚠️ UNRELIABLE | Timeout path observed |
| Perception detections | ⚠️ LIMITED | Empty results for faces/objects |

### Release-Usable Subset
- ✅ `vector_status`, `vector_drive_off_charger`, `vector_say`, `vector_lift`
- ✅ `vector_touch_status`, `vector_charger_status`, `vector_capture_image`
- ✅ `vector_look`, `vector_proximity_status`
- ⚠️ `vector_drive_on_charger` (documented as unreliable)
- ❌ `vector_head` (documented as FAIL)

---

## E) Publishing Checklist

### PyPI
- [ ] Build package: `python -m build`
- [ ] Check distribution: `twine check dist/*`
- [ ] Upload to TestPyPI (optional): `twine upload --repository testpypi dist/*`
- [ ] Upload to PyPI: `twine upload dist/*`
- [ ] Verify install: `pip install vectorclaw-mcp`

### ClawHub
- [ ] Review `skill/SKILL.md` one final time
- [ ] Submit skill via ClawHub process (PR or form)
- [ ] Verify skill appears in ClawHub directory

### Post-Release
- [ ] Tag release: `git tag v1.0.0`
- [ ] Push tag: `git push origin v1.0.0`
- [ ] Create GitHub release with notes
- [ ] Update ROADMAP.md with release date

---

## F) Merged PRs for v1.0.0

| PR | Title | Merged |
|----|-------|--------|
| #129 | Hardware smoke test docs | 2026-02-28 |
| #130 | MCP vs SDK naming, release decision matrix | 2026-02-28 |
| #132 | Head angle fix | 2026-02-28 |
| #133 | Pose metadata fields | 2026-02-28 |
| #134 | ClawHub skill definition | 2026-02-28 |
| #135 | Legacy SDK compat fix | 2026-02-28 |

---

## Sign-Off

- [ ] Security audit reviewed and approved
- [ ] Hardware validation results acceptable for MVP
- [ ] Documentation verified
- [ ] Ready for public release

**Approved by:** ________________
**Date:** ________________
