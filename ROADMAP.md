# VectorClaw Roadmap

Milestone-based development plan from alpha to public release.

**v1.0.0 released** on PyPI — 2026-03-01

---

## Completed: v1.0.0

- ✅ MCP server with 23 tools (16 verified, 7 experimental)
- ✅ Real hardware smoke-tested on production Vector + Wire-Pod
- ✅ Full test suite (mocked SDK, CI green on Python 3.11)
- ✅ Security review and threat model documented
- ✅ Published to PyPI (`pip install vectorclaw-mcp`)
- ✅ Guided setup wizard (`vectorclaw-setup`)
- ✅ Wire-Pod SDK compatibility layer (no fork required)

---

## Milestone 1: Hardware Validation

**Goal:** Verify all tools work with real Vector robot

**Exit Criteria:**
- [ ] Wire-Pod running (platform of choice)
- [ ] Vector robot configured (firmware, WiFi, SDK auth)
- [ ] All 12 tools tested and working:
  - [ ] `vector_say` — TTS
  - [ ] `vector_animate` — Animations
  - [ ] `vector_drive` — Movement
  - [ ] `vector_look` — Camera capture
  - [ ] `vector_face` — Face display
  - [ ] `vector_pose` — Position
  - [ ] `vector_cube` — Cube interaction
  - [ ] `vector_status` — Battery/status
  - [ ] `vector_scan` — Look around in place (perception discovery)
  - [ ] `vector_find_faces` — Find faces behavior (perception discovery)
  - [ ] `vector_list_visible_faces` — List currently visible faces (perception discovery)
  - [ ] `vector_list_visible_objects` — List currently visible objects (perception discovery)
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

## Milestone 4: Release Candidate

**Goal:** Final polish + release readiness gates

**Exit Criteria:**
- [ ] All feedback addressed
- [ ] Documentation finalized (README, SETUP, TROUBLESHOOTING)
- [ ] CHANGELOG.md created
- [ ] 1-2 days stable period

### Mandatory release gates (v1.0.0)

#### A) User install readiness
- [ ] Fresh-environment install walkthrough validated end-to-end
- [ ] Setup docs verified against actual current flow (no stale steps)
- [ ] Troubleshooting covers top real-world failure modes

#### B) ClawHub skill readiness
- [ ] Skill metadata reviewed for clarity and accuracy
- [ ] Capability scope is least-privilege and explicit
- [ ] No hidden side-effects in default behavior
- [ ] Release notes clearly define supported vs known-limited capabilities

#### C) Final security audit
- [ ] Credential handling/log output reviewed (no secret leakage)
- [ ] Input validation and motion safety limits re-verified
- [ ] Dependency and supply-chain sanity check completed
- [ ] SECURITY.md and public security posture notes updated

**Version:** v1.0.0-rc1

**Note:** External beta testing deferred to post-release. Community feedback will guide v1.1+ improvements.

---

## Milestone 5: Public Release

**Goal:** Available to all users

**Exit Criteria:**
- [ ] PyPI package published (`pip install vectorclaw-mcp`)
- [ ] ClawHub skill published
- [ ] Documentation complete and validated
- [ ] mcporter config documented
- [ ] Repo made public
- [ ] Runtime support policy confirmed (see `docs/RUNTIME_SUPPORT.md`): Python 3.11 primary, CI green on 3.11

**Version:** v1.0.0

---

## Sprint Log (Thu 2/26 → Sun 3/1)

| Day | Focus | Result |
|-----|-------|--------|
| **Thu PM** | Merge PR #1, Wire-Pod setup, Vector unboxing | v0.1.1 ✅ |
| **Fri** | Vector SDK auth, test all tools | v0.2.0 ✅ |
| **Sat AM** | Address review comments, security review | v0.3.0 ✅ |
| **Sat PM** | Security hardening, edge cases | v0.4.0 ✅ |
| **Sun AM** | Documentation, RC testing | v1.0.0-rc1 ✅ |
| **Sun PM** | PyPI publish, hardware verification | v1.0.0 🎉 |

---

## Future Considerations (v1.x)

**Near-term enhancements:**
- Async motion control primitives (non-blocking drive + interruptable stop semantics)
- Vision pipeline optimization (optional in-memory look→analyze path, with audit snapshot mode)
- Pose metadata expansion in `vector_pose` (`origin_id`, `is_picked_up`, optional `localized_to_object_id`)
- Perception reliability hardening (face/object visibility behavior, cube-connect workflow)
- Audio recording from microphones
- Object detection via camera
- Multiple robot support
- Personality modes
- Voice command passthrough

---

## Long-term Vision: ROS2 Integration (v2.0)

**Key insight:** v1.0 IS autonomous. The agent queries camera, reasons about what it sees, and commands motion — a full Visual-Language-Action (VLA) loop via tools.

**v2.0's purpose:** Give the agent classical robotics tools (SLAM, NAV2) so it operates at a higher level. Instead of "turn 90°, drive 500mm," the agent says "go to kitchen" and ROS2 handles the low-level execution.

### Division of Labor

| Version | Agent Role | Stack Role |
|---------|------------|------------|
| **v1.0** | Perception + Planning + Control (via tool calls) | SDK passthrough |
| **v2.0** | High-level reasoning + goal-setting | Perception + Planning + Control (ROS2) |

The agent shifts from low-level controller to high-level planner.

### Phase A: ROS2 Driver

**Foundation:** Leverage [vector_ros2](https://github.com/CtfChan/vector_ros2) as baseline

**Exit Criteria:**
- [ ] ROS2 Humble/Iron driver package
- [ ] Camera feed as ROS2 topic
- [ ] Odometry publishing
- [ ] Velocity commands via cmd_vel
- [ ] Sensor data (cliff, bump, IMU) as topics
- [ ] TF2 transforms

**Version:** v2.0.0

### Phase B: Perception Stack

**Goal:** Offload perception to ROS2 ecosystem

**Exit Criteria:**
- [ ] Visual SLAM integration (ORB-SLAM3, RTAB-Map, or similar)
- [ ] Depth processing (if camera supports)
- [ ] Object detection (YOLO, Detectron via ROS2)
- [ ] AprilTag / ArUco detection
- [ ] Point cloud generation (if applicable)

**Agent benefit:** Queries map/objects instead of raw camera frames

**Version:** v2.1.0

### Phase C: Navigation Stack

**Goal:** Offload path planning to NAV2

**Exit Criteria:**
- [ ] NAV2 integration
- [ ] Costmap from SLAM
- [ ] Path planning (A*, DWB controller)
- [ ] Obstacle avoidance
- [ ] Waypoint following
- [ ] Map persistence

**Agent benefit:** Commands "navigate_to(kitchen)" instead of step-by-step motion

**Version:** v2.2.0

### Phase D: Autonomy Layer

**Goal:** High-level behavior primitives

**Exit Criteria:**
- [ ] Behavior trees (BehaviorTree.CPP)
- [ ] Task scheduling
- [ ] Return-to-home behavior
- [ ] Docking automation
- [ ] Patrol / exploration modes

**Agent benefit:** Commands "patrol_area(living_room)" or "return_to_dock"

**Version:** v2.3.0

---

**Why this matters:**
Vector becomes a **$250 ROS2 development platform** with an AI agent as the high-level brain. The agent focuses on reasoning and goals; ROS2 handles the robotics heavy lifting.

**Dependencies:**
- vector_ros2 driver maturity
- ROS2 ecosystem compatibility
- Community interest / contributors

---

## Version Scheme

- `0.x.x` — Alpha/Beta/RC
- `1.0.0` — First public release
- `1.x.x` — Feature additions (non-breaking)
- `x.0.0` — Breaking changes

---

*Last updated: 2026-03-01*
