# VectorClaw Hardware Smoke Log

Purpose: running record of real-world hardware smoke tests (fast confidence checks).

Use alongside:
- `HARDWARE_TEST_PLAYBOOK.md` (full protocol)
- `API_REFERENCE.md` (tool contract)

---

## Run Template

- **Date/Time (local):**
- **Operator:**
- **Robot serial:**
- **Branch / Commit:**
- **Wire-Pod status:**
- **SDK env:**
- **Result:** PASS / PARTIAL / FAIL

### Commands + Outcomes

| Command | Tool result | Physical verification | Notes |
|---|---|---|---|
| `vector_status` |  |  |  |
| `vector_say` |  |  |  |
| `vector_drive_off_charger` |  |  |  |
| `vector_drive` |  |  |  |
| `vector_look` |  |  |  |
| `vector_face` |  |  |  |
| `vector_head` |  |  |  |
| `vector_lift` |  |  |  |
| `vector_scan` |  |  | Pending MCP registration (#67) — skip until integrated |
| `vector_find_faces` |  |  | Pending MCP registration (#67) — skip until integrated |
| `vector_list_visible_faces` |  |  | Pending MCP registration (#67) — skip until integrated |
| `vector_list_visible_objects` |  |  | Pending MCP registration (#67) — skip until integrated |
| `vector_drive_on_charger` |  |  | Pending MCP registration (#67) — skip until integrated |
| `vector_emergency_stop` |  |  | Pending MCP registration (#67) — skip until integrated |
| `vector_capture_image` |  |  | Pending MCP registration (#67) — skip until integrated |
| `vector_face_detection` |  |  | Pending MCP registration (#67) — skip until integrated |
| `vector_vision_reset` |  |  | Pending MCP registration (#67) — skip until integrated |
| `vector_charger_status` |  |  | Pending MCP registration (#67) — skip until integrated |
| `vector_touch_status` |  |  | Pending MCP registration (#67) — skip until integrated |
| `vector_proximity_status` |  |  | Pending MCP registration (#67) — skip until integrated |

### Anomalies / Follow-ups
- 

---

## 2026-02-27 — PR #38 refactor smoke

- **Date/Time (local):** 2026-02-27 09:12–09:29 CST
- **Operator:** Dan + Tachi (single-command, human-verification loop)
- **Robot serial:** `00a1546c`
- **Branch / Commit:** `chore/split-tools-server-for-parallel-dev` / `fb1787c`
- **Wire-Pod status:** active/running
- **SDK env:** `PYTHONPATH=src`, `VECTOR_SERIAL=00a1546c`, python from `/home/daniel/.venv/vectorclaw-test/bin/python`
- **Result:** **PARTIAL** (all tested paths passed except known `vector_face` bug)

### Commands + Outcomes

| Command | Tool result | Physical verification | Notes |
|---|---|---|---|
| `vector_status` | `ok` | N/A | Robot woke up; battery/status payload valid |
| `vector_say("Smoke test from Tachi.")` | `ok` | PASS | Speech audible; pronunciation quirk on “Tachi” noted |
| `vector_drive_off_charger` | `ok` | PASS | Robot drove off charger |
| `vector_drive(distance_mm=120,speed=80)` | `ok` | PASS | Clear forward movement observed |
| `vector_look` | `ok` | PASS | Image decoded + manually verified (desk/face/monitor alignment) |
| `vector_face` | **FAIL** | FAIL | SDK expects 35328-byte face payload; current code sends JPEG bytes |
| `vector_head(-15)` | `ok` | PASS | Clear head-down actuation |
| `vector_lift(0.9)` | `ok` | PASS | Clear lift-up actuation |

### Anomalies / Follow-ups
- Repeated non-fatal SDK warning: `events.EventHandler WARNING Unknown Event type` (tracked in issue #39)
- `vector_face` hardware bug tracked in issue #41
- Behavioral note: occasional aggressive post-command lift settle (“slammed arm down”) observed once; not blocking but worth tracking in behavior tuning.
- Camera optics note: slight possible barrel/radial distortion observed; ROS2 calibration follow-up tracked in issue #40.

---

## 2026-02-27 — Post-integration MCP-path expanded smoke (#67 integrated)

- **Date/Time (local):** 2026-02-27 evening CST (session recovered from reset artifact)
- **Operator:** Dan + Tachi (MCP command-by-command + human physical verification)
- **Robot serial:** `00a1546c`
- **Branch / Commit:** `dev` (included hotfix commit `bcee0db` during run)
- **Wire-Pod status:** active/running
- **SDK env:** `PYTHONPATH=src`, `VECTOR_SERIAL=00a1546c`, python from `/home/daniel/.venv/vectorclaw-test/bin/python`
- **Result:** **PARTIAL** (majority pass; status-schema and charger-path issues identified)

### Commands + Outcomes

| Command | Tool result | Physical verification | Notes |
|---|---|---|---|
| `vector_status` | FAIL → PASS | N/A | Initial runtime attr error (`is_carrying_object` missing); hotfixed during run to avoid crash |
| `vector_say` | `ok` | PASS | Audible speech confirmed |
| `vector_drive_off_charger` | `ok` | PASS | Undock behavior confirmed |
| `vector_drive` | `ok` | PASS | Forward motion confirmed |
| `vector_look` | `ok` | PASS | Valid non-empty JPEG payload; saved and reviewed |
| `vector_head` | `ok` | PASS | Head actuation confirmed |
| `vector_lift` | `ok` | PASS | Lift actuation confirmed |
| `vector_scan` | `ok` | PASS | Head/yaw scan behavior observed |
| `vector_find_faces` | `ok` | PASS-ish | Behavior similar to scan, with larger one-direction yaw sweep |
| `vector_list_visible_faces` | `ok` | PARTIAL | Functional path; often empty results |
| `vector_list_visible_objects` | `ok` | PARTIAL | Functional path; empty list despite nearby cube in some trials |
| `vector_drive_on_charger` | `ok` tool-side | FAIL/PARTIAL | Cube-light behavior observed; no clear charger-approach on command |
| `vector_emergency_stop` | `ok` | PASS | Stop path responded correctly |
| `vector_capture_image` | `ok` | PASS | Valid non-empty JPEG payload |
| `vector_face_detection` | `ok` | PARTIAL | Often `faces: []` even in favorable conditions |
| `vector_vision_reset` | `ok` | PASS | Returned `All vision modes disabled` |
| `vector_charger_status` | FAIL | N/A | Runtime attr error (`is_on_charger_platform` missing) |
| `vector_touch_status` | `ok` | PASS | Touch state toggled false→true with contact |
| `vector_proximity_status` | `ok` | PASS (with note) | Distance changed clearly (e.g., ~279→45mm); `found_object` remained false |

### Anomalies / Follow-ups
- Runtime schema variance in status tools:
  - `vector_status` attr mismatch observed and patched during smoke (`bcee0db`)
  - `vector_charger_status` still fails on assumed `is_on_charger_platform`
- Perception semantics/reliability investigations opened:
  - #87 (`vector_list_visible_objects` semantics)
  - #89 (broader perception visibility reliability)
  - #91 (SDK object-detection semantics: proximity vs classification)
- Charger return path investigation opened:
  - #88 (`vector_drive_on_charger` behavior mismatch)
  - Additional observation: robot later autonomously returned to charger on low battery (capability exists; tool-path semantics likely mismatched)
- Event-noise observability issue tracked in #86 (`Unknown Event type` warnings)

---

## 2026-02-28 — Proximity empirical deep dive (release validation)

- **Date/Time (local):** 2026-02-28 14:25–14:40 CST
- **Operator:** Dan + Tachi (MCP command execution + physical verification)
- **Robot serial:** `00a1546c`
- **Branch / Commit:** `dev` (post-doc merge state)
- **Wire-Pod status:** active/running
- **SDK env:** `VECTOR_SERIAL=00a1546c`, Python `.venv/bin/python`
- **Result:** **PARTIAL** (distance/unobstructed usable; `found_object` not reliable)

### Commands + Outcomes

| Command | Tool result | Physical verification | Notes |
|---|---|---|---|
| `vector_status` | `ok` | PASS | Connected cleanly; on charger reported true |
| `vector_pose` | `ok` | PASS | Near-zero pose while stationary on charger |
| `vector_proximity_status` (far) | `ok` | PASS | `distance_mm=180`, `signal_quality=0.0317`, `found_object=false`, `unobstructed=false` |
| `vector_proximity_status` (mid) | `ok` | PASS | `distance_mm=92`, `signal_quality=0.4383`, `found_object=false`, `unobstructed=false` |
| `vector_proximity_status` (close) | `ok` | PASS | `distance_mm=42`, `signal_quality=6.1456`, `found_object=false` |
| `vector_proximity_status` (mid, larger cardboard) | `ok` | PASS | `distance_mm=97`, `signal_quality=1.4551`, `found_object=false` |
| `vector_proximity_status` (close, cardboard touching) | `ok` | PASS | `distance_mm=48`, `signal_quality=11.6966`, `found_object=false` |
| `vector_proximity_status` (no object) | `ok` | PASS | `distance_mm=244`, `signal_quality=0.0060`, `unobstructed=true`, `found_object=false` |

### Anomalies / Follow-ups
- `found_object` never flipped true despite near-field and high signal-quality returns.
- `signal_quality` exceeded 1.0 by large margin (up to ~11.7); prior 0.0–1.0 assumption is incorrect for this setup.
- `unobstructed` did behave as expected in clear-path test.
- Operator observation: LightCube lit during some proximity trials (possible state interaction worth separate check, but not required for raw ToF reading path).

---

## 2026-02-28 — Final smoke wrap (single-step reruns)

- **Date/Time (local):** 2026-02-28 15:10–15:25 CST
- **Operator:** Dan + Tachi (strict one-command-at-a-time with explicit human confirmation)
- **Robot serial:** `00a1546c`
- **Branch / Commit:** `dev`
- **Wire-Pod status:** active/running
- **SDK env:** `VECTOR_SERIAL=00a1546c`, Python `.venv/bin/python`
- **Result:** **PARTIAL** (core basics work; head/perception/charger-return limitations remain)

### Commands + Outcomes

| Command | Tool result | Physical verification | Notes |
|---|---|---|---|
| `vector_say` | `ok` | PASS | Speech confirmed by operator |
| `vector_lift` | `ok` | PASS | Lift motion confirmed |
| `vector_touch_status` (no touch) | `ok` | PASS | `is_being_touched=false`, raw value stable |
| `vector_touch_status` (touching) | `ok` | PASS | `is_being_touched=true`, raw value increased |
| `vector_charger_status` (off charger) | `ok` | PASS | Negative case validated (`is_on_charger=false`) |
| `vector_head` | **FAIL** | N/A | Runtime type error: `Unsupported type for comparison expected Angle` |
| `vector_drive_on_charger` | **FAIL** | FAIL/PARTIAL | Timed out (`timed_out=true`, `motors_stopped=true`) |
| `vector_emergency_stop` | `ok` | PARTIAL | Stop command returns `ok`; physical interruption validation is limited by sync motion call path |

### Anomalies / Follow-ups
- `vector_head` currently non-functional due to Angle comparison bug.
- `vector_drive_on_charger` remains unreliable/timeout-prone in this run.
- Perception tools still return empty detections under favorable human/cube conditions.
- **Emergency-stop usability caveat:** current tool path is synchronous for motion, which weakens true mid-command interrupt semantics. Async motion/control path should be added to roadmap before treating emergency stop as robust operational control.
