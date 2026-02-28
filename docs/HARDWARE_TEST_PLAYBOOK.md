# VectorClaw Hardware Test Playbook

Repeatable, low-ambiguity on-robot validation protocol for VectorClaw.

> **Quick reference:** See [API Reference](API_REFERENCE.md) for tool parameters and [Wire-Pod SDK Implementation Guide](WIREPOD_SDK_IMPLEMENTATION_GUIDE.md) for implementation details.
>
> **Running records:** [Hardware Smoke Log](HARDWARE_SMOKE_LOG.md) and [Tool Docking Prerequisites](TOOL_DOCKING_PREREQUISITES.md).
>
> **Post-integration add-on:** Issue #67 (tool registration integration) is merged. Run the expanded matrix in `HARDWARE_SMOKE_LOG.md` for the newly registered tools before release cut.

---

## Pre-flight Checklist

Before starting any hardware validation session:

- [ ] Wire-Pod server running and reachable
- [ ] Robot powered on, Wi-Fi connected, shows stable status (no blinking/error eyes)
- [ ] `VECTOR_SERIAL` environment variable set
- [ ] `VECTOR_HOST` set or auto-discovery confirmed working
- [ ] VectorClaw MCP server starts cleanly (`vectorclaw-mcp` — no connection errors in stderr)
- [ ] Robot placed on charger (many tests begin by explicitly driving off charger)
- [ ] Clear flat surface (≥ 60 cm × 60 cm) available for motion tests
- [ ] Operator note-taking method ready (timestamp, outcome, observations)

---

## Known Ambiguity Sources

### Idle Behavior Noise
Vector runs autonomous idle behaviors (head/eye movements, small adjustments, reactions to sound/light) independently of MCP commands. These can be mistaken for commanded motion.

**Mitigations:**
1. **One command at a time** — send a single command, then pause and observe before sending the next.
2. **Use large, discrete movements** — prefer ≥ 100 mm drives and ≥ 45° turns so commanded behavior is visually distinct from idle.
3. **Human confirmation gate** — do not issue the next command until the operator explicitly confirms the outcome of the previous one.
4. **Silence the environment** — loud sounds can trigger unexpected idle reactions; test in a quiet room.
5. **Minimize session length** — the longer the robot is on, the more idle behaviors accumulate; run tests in focused bursts.

### Charger State
`vector_drive` and other motion tools will return `{"status":"error","message": ...}` when the robot is on the charger, with an error message indicating that driving is not allowed while docked (some SDKs may include `SHOULDNT_DRIVE_ON_CHARGER` in this message). Always call `vector_drive_off_charger` as the first motion step and verify the robot physically moved off before continuing.

### Animation / Idle Overlap
`vector_animate` responses can overlap with autonomous eye/head animations. Validate animation output only when the robot has been idle and stationary for at least 3 seconds prior.

---

## Command-by-Command Validation Protocol

Each step follows the pattern:

```
1. Issue exactly ONE command.
2. Observe robot behavior.
3. Operator records outcome (PASS / FAIL / AMBIGUOUS + notes).
4. Wait for explicit human confirmation before next command.
```

### Phase 0 — Connectivity

| # | Command / Action | Expected result | Confirmation |
|---|---|---|---|
| 0.1 | Start MCP server | No errors in stderr, server ready | Operator confirms |
| 0.2 | `vector_status` | JSON with `battery_level`, `is_charging: true`, `is_carrying_block` | Operator reads payload |
| 0.3 | `vector_pose` | JSON with `x`, `y`, `z`, `angle_deg` | Operator reads payload |

### Phase 1 — Motion (requires charger start)

| # | Command | Parameters | Expected result | Confirmation |
|---|---|---|---|---|
| 1.1 | `vector_drive_off_charger` | — | Robot drives off charger ramp; charger LED extinguishes | Visual |
| 1.2 | `vector_status` | — | `is_charging: false` | Operator reads payload |
| 1.3 | `vector_drive` | `distance_mm: 150, speed: 50` | Robot moves ~15 cm forward | Visual |
| 1.4 | `vector_drive` | `distance_mm: -150, speed: 50` | Robot moves ~15 cm backward | Visual |
| 1.5 | `vector_drive` | `angle_deg: 90` | Robot turns ~90° left in place | Visual |
| 1.6 | `vector_drive` | `angle_deg: -90` | Robot turns ~90° right in place | Visual |
| 1.7 | `vector_pose` | — | Pose values differ from 0.3 values | Operator reads payload |

### Phase 2 — Speech

| # | Command | Parameters | Expected result | Confirmation |
|---|---|---|---|---|
| 2.1 | `vector_say` | `text: "VectorClaw test one"` | Audible TTS speech | Auditory |
| 2.2 | `vector_say` | `text: "Hardware validation complete"` | Audible TTS speech | Auditory |

### Phase 3 — Camera

| # | Command | Parameters | Expected result | Confirmation |
|---|---|---|---|---|
| 3.1 | `vector_look` | — | Non-empty `image_base64` JPEG payload | Operator decodes sample / checks length > 0 |

### Phase 4 — Environment-Dependent (run only when prerequisites met)

| # | Command | Prerequisite | Parameters | Expected result |
|---|---|---|---|---|
| 4.1 | `vector_animate` | Robot stationary ≥ 3 s | `animation_name: "anim_greeting_happy_01"` | Visible animation plays |
| 4.2 | `vector_face` | Valid Pillow-supported image (auto-resized to 144×108) | `image_base64: <test>`, `duration_sec: 2` | Face image displayed for 2 s |
| 4.3 | `vector_cube` | Cube paired and visible to robot | `action: "dock"` | Robot docks with cube |

### Phase 5 — Error Handling

| # | Scenario | How to trigger | Expected result |
|---|---|---|---|
| 5.1 | Drive while on charger | Skip Phase 1 and call `vector_drive` | `{"status":"error","message": ...}` indicating driving not allowed while docked |
| 5.2 | Cube unavailable | Call `vector_cube` with `action: "dock"` while no cube is paired/visible | Error response with actionable message |

---

## Pass/Fail Checklist Template

Copy the block below into a PR description or issue comment for hardware validation evidence.

```markdown
## Hardware Validation Checklist

**Date:** YYYY-MM-DD  
**Operator:** @username  
**Robot serial:** XXXXXXXX  
**Network:** Wire-Pod / direct  
**VectorClaw version:** x.y.z  

### Phase 0 — Connectivity
- [ ] 0.1 MCP server starts clean
- [ ] 0.2 `vector_status` — valid payload
- [ ] 0.3 `vector_pose` — valid payload

### Phase 1 — Motion
- [ ] 1.1 `vector_drive_off_charger` — visual confirm
- [ ] 1.2 `vector_status` — `is_charging: false`
- [ ] 1.3 `vector_drive` forward 150 mm — visual confirm
- [ ] 1.4 `vector_drive` reverse 150 mm — visual confirm
- [ ] 1.5 `vector_drive` turn +90° — visual confirm
- [ ] 1.6 `vector_drive` turn −90° — visual confirm
- [ ] 1.7 `vector_pose` — values changed from baseline

### Phase 2 — Speech
- [ ] 2.1 `vector_say` — audible TTS
- [ ] 2.2 `vector_say` — audible TTS

### Phase 3 — Camera
- [ ] 3.1 `vector_look` — non-empty image payload

### Phase 4 — Environment-Dependent (mark N/A if prerequisites not met)
- [ ] 4.1 `vector_animate` — N/A / PASS / FAIL
- [ ] 4.2 `vector_face` — N/A / PASS / FAIL
- [ ] 4.3 `vector_cube` dock — N/A / PASS / FAIL

### Phase 5 — Error Handling
- [ ] 5.1 Drive-on-charger error — correct error returned
- [ ] 5.2 Cube-unavailable error — actionable message returned

### Overall Result
- [ ] **PASS** (all required phases pass)
- [ ] **FAIL** (one or more required phases fail — see notes)
- [ ] **PARTIAL** (environment-dependent phases not tested)

### Operator Notes
<!-- timestamps, anomalies, ambient conditions, software versions -->
```

---

## Minimum Required Evidence Format

Every hardware validation run must capture:

| Field | Required | Example |
|---|---|---|
| Date + time (local + UTC offset) | Yes | `2026-02-26 14:32 PST (UTC-8)` |
| Operator | Yes | `@section9-tachi` |
| Robot serial | Yes | `00a1546c` |
| VectorClaw version / commit SHA | Yes | `v0.3.1` / `5143c69` |
| Wire-Pod / SDK version | Yes | `wirepod_vector_sdk 0.8.1` |
| Network topology | Yes | `Wire-Pod on 192.168.1.x` |
| Phase 0–3 outcome per step | Yes | `PASS`, `FAIL`, or `AMBIGUOUS` |
| Phase 4–5 outcome per step | If run | `PASS`, `FAIL`, `N/A` |
| Ambient condition notes | Recommended | `quiet room, flat table, no cube present` |
| Anomalies observed | Yes | `idle head-bob on step 1.3 — movement still visually distinct` |

### Example Operator Note Entry

```
2026-02-26 14:35 PST — Step 1.3: issued vector_drive forward 150mm.
Robot moved clearly forward ~15 cm. Small head tilt occurred simultaneously
(idle behavior) but drive motion unambiguous. PASS.
```

---

## Release Gate Criteria

A release or PR merge that includes motion/control changes **must** include:

1. A completed hardware validation checklist (Phases 0–3 minimum) attached to the PR.
2. At least one operator note entry per phase.
3. No unresolved FAIL outcomes in Phases 0–3.
4. AMBIGUOUS outcomes must include a written explanation and mitigation.

Docs-only PRs are exempt from hardware validation but must not change or remove playbook criteria without a corresponding issue discussion.

---

## Quick-Reference Command Sequence

Minimal smoke-test sequence (≈ 5 minutes). Send each command as a JSON argument object to the MCP tool:

```json
{"tool": "vector_status"}
{"tool": "vector_pose"}
{"tool": "vector_drive_off_charger"}
{"tool": "vector_status"}
{"tool": "vector_drive",   "args": {"distance_mm": 150,  "speed": 50}}
{"tool": "vector_drive",   "args": {"distance_mm": -150, "speed": 50}}
{"tool": "vector_drive",   "args": {"angle_deg": 90}}
{"tool": "vector_say",     "args": {"text": "VectorClaw smoke test complete"}}
{"tool": "vector_look"}
```
