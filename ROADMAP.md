# VectorClaw Roadmap

Milestone-based development plan from alpha to public release.

---

## Current State: Alpha (v0.1.0)

**What we have:**
- ✅ MCP server scaffold (8 tools)
- ✅ Basic test suite (mocked SDK)
- ✅ README with setup instructions
- ✅ Copilot-generated PR #1 (awaiting merge)

**What we need:**
- ⚠️ Real hardware testing
- ⚠️ Security review
- ⚠️ Edge case handling

---

## Milestone 1: Hardware Validation

**Goal:** Verify all tools work with real Vector robot

**Exit Criteria:**
- [ ] Wire-Pod running (platform of choice)
- [ ] Vector robot configured (firmware, WiFi, SDK auth)
- [ ] All 8 tools tested and working:
  - [ ] `vector_say` — TTS
  - [ ] `vector_animate` — Animations
  - [ ] `vector_drive` — Movement
  - [ ] `vector_look` — Camera capture
  - [ ] `vector_face` — Face display
  - [ ] `vector_pose` — Position
  - [ ] `vector_cube` — Cube interaction
  - [ ] `vector_status` — Battery/status
- [ ] No crashes on happy path

**Version:** v0.2.0

---

## Milestone 2: Code Quality

**Goal:** Production-ready code

**Exit Criteria:**
- [ ] All Copilot review comments addressed
- [ ] Thread-safe connection management
- [ ] Input validation on all tool parameters
- [ ] Graceful error handling (robot offline, SDK errors)
- [ ] Connection resilience (reconnect on failure)
- [ ] Test coverage ≥ 80%

**Version:** v0.3.0

---

## Milestone 3: Security Hardening

**Goal:** Safe for public use

**Exit Criteria:**
- [ ] Threat model documented
- [ ] Credential handling audited (no leaks in logs/responses)
- [ ] Input sanitization (base64, distances, durations)
- [ ] Movement safety limits (rate limiting, max distances)
- [ ] SECURITY.md with best practices

**Version:** v0.4.0

---

## Milestone 4: Beta Release

**Goal:** External validation with trusted testers

**Exit Criteria:**
- [ ] Public GitHub repo
- [ ] Beta documentation complete
- [ ] 3+ beta testers with positive feedback
- [ ] No critical bugs reported
- [ ] 2+ weeks of stable beta period

**Version:** v0.5.0-beta

---

## Milestone 5: Release Candidate

**Goal:** Final polish

**Exit Criteria:**
- [ ] All beta feedback addressed
- [ ] Documentation finalized (README, SETUP, TROUBLESHOOTING)
- [ ] CHANGELOG.md created
- [ ] 1 week RC period with no changes

**Version:** v1.0.0-rc1

---

## Milestone 6: Public Release

**Goal:** Available to all users

**Exit Criteria:**
- [ ] PyPI package published (`pip install vectorclaw-mcp`)
- [ ] ClawHub skill published
- [ ] Documentation complete and validated
- [ ] mcporter config documented

**Version:** v1.0.0

---

## Future Considerations

**Not in v1.0:**
- Audio recording from microphones
- Object detection via camera
- Multiple robot support
- Personality modes
- Voice command passthrough

---

## Version Scheme

- `0.x.x` — Alpha/Beta/RC
- `1.0.0` — First public release
- `1.x.x` — Feature additions (non-breaking)
- `x.0.0` — Breaking changes

---

*Last updated: 2026-02-26*
