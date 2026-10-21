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

## Milestones 1–5 (Completed Archive)

These were completed during the v1.0.0 release push and are retained as historical checkpoints.

### Milestone 1: Hardware Validation (v0.2.0) ✅
- [x] Wire-Pod running
- [x] Vector configured (firmware/WiFi/SDK auth)
- [x] Core tooling validated on real hardware
- [x] Happy-path stability confirmed

### Milestone 2: Code Quality (v0.3.0) ✅
- [x] Review feedback addressed
- [x] Connection/threading reliability improved
- [x] Input validation and graceful error handling added
- [x] CI-backed test coverage in place

### Milestone 3: Security Hardening (v0.4.0) ✅
- [x] Threat model and security docs published
- [x] Credential/log handling reviewed
- [x] Input/motion safety constraints added

### Milestone 4: Release Candidate (v1.0.0-rc1) ✅
- [x] Docs finalized for release path
- [x] Release gates executed (install, skill, security)
- [x] Stable RC validation pass completed

### Milestone 5: Public Release (v1.0.0) ✅
- [x] PyPI published
- [x] ClawHub published
- [x] Public docs and setup flow validated
- [x] Runtime support policy documented

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

## Embodied AI MVP API Roadmap (Canonical)

This roadmap is the canonical post-v1.0 direction.

### Cross-cutting acceptance criteria (all tracks)

- Deterministic success/failure payloads
- No silent “empty means anything” outcomes
- Explicit precondition reporting
- Tests cover success + failure + disabled-mode paths
- Docs reflect actual observed semantics (not optimistic assumptions)

---

## MUST-HAVE (v1.1)

### 1) Embodied state core
**Goal:** Expand `vector_status` + `vector_pose` for embodied planning

**Add:**
- Charging/on-charger, motors moving, pathing, carrying block, picked up, cliff flags
- Pose origin/localization fields (`origin_id`, `localized_to_object_id` when available)
- Timestamps for state freshness

**DoD:** Agent can decide “can I move?” and “am I localized?” from one call.

### 2) Perception mode control + semantics
**Goal:** Add explicit vision mode tools and unify perception contracts

**Add:**
- `vector_enable_face_detection`
- `vector_enable_motion_detection`
- `vector_vision_status`

**DoD:** Face/object tools never fail ambiguously; they report disabled/empty/stale clearly.

### 3) Object/face visibility semantics split
**Goal:** Split “currently visible” vs “known world” entity views

**Add:**
- Clear payload fields: `visible_now`, `last_seen_ts`, `origin_id`
- Dedupe for repeated face/object IDs

**DoD:** No more confusion from empty visible list when known entities exist.

### 4) Charger workflow hardening
**Goal:** Harden `vector_drive_on_charger` with explicit state-machine responses

**Add:**
- Return states: searching, approaching, docked, timeout, failed
- Actionable failure reasons + next-step hints

**DoD:** Operator can tell if failure is perception/timing vs impossible state.

---

## SHOULD-HAVE (v1.2)

### 5) Attention primitives
**Add:**
- `vector_look_around_in_place` (if not already exposed cleanly)
- One-shot wait helpers: `vector_wait_for_face`, `vector_wait_for_object` (bounded)

**DoD:** Agent can intentionally gather perception before acting.

### 6) Social/expressive layer
**Add:**
- `vector_play_animation_trigger`
- `vector_set_eye_color`
- Optional screen text/image polish

**DoD:** Embodied assistant can communicate internal state socially.

### 7) Motion goal helpers
**Add:**
- `vector_turn_towards_face`
- `vector_go_to_pose` (guardrailed)

**DoD:** Fewer brittle low-level movement scripts for common goals.

---

## EXPERIMENTAL LATER

### 8) Audio expansion
- Guarded `vector_play_wav`
- Volume profiles
- Mic/audio-stream integrations (if policy allows)

### 9) Persistent world memory
- Optional local map of known entities with confidence decay

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
