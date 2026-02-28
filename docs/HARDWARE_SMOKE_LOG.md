# VectorClaw Hardware Smoke Log

Purpose: running record of real-world hardware smoke tests (fast confidence checks).

Use alongside:
- `HARDWARE_TEST_PLAYBOOK.md` (full protocol)
- `MCP_API_REFERENCE.md` (tool contract)

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

> Log only commands executed in this run. Do not mirror a fixed tool catalog here.
> Source of truth for currently exposed tools: `docs/MCP_API_REFERENCE.md`.

| Command | Tool result | Physical verification | Notes |
|---|---|---|---|
| `vector_example(arg=value)` | `ok` / `error` | PASS / PARTIAL / FAIL / N/A | Key observation |
| `...` |  |  |  |

### Anomalies / Follow-ups
Use this section for anything that needs action, caution, or later validation.

Suggested format:
- **Observed:** What happened (exact symptom/error)
- **Impact:** Why it matters (safety, reliability, usability)
- **Follow-up:** Issue/PR link or explicit next step

Example:
- **Observed:** `vector_head` returned `Unsupported type for comparison expected Angle`
- **Impact:** Head actuation unavailable in current build
- **Follow-up:** Track in issue #<id> and retest after fix

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

## 2026-02-28 — Comprehensive hardware smoke + empirical validation

- **Date/Time (local):** 2026-02-28 14:25–15:44 CST
- **Operator:** Dan + Tachi (MCP command execution + physical verification)
- **Robot serial:** `00a1546c`
- **Branch / Commit:** `dev` (post-doc merge state)
- **Wire-Pod status:** active/running
- **SDK env:** `VECTOR_SERIAL=00a1546c`, Python `.venv/bin/python`
- **Result:** **PARTIAL** (distance/unobstructed usable; `found_object` not reliable)

### Commands + Outcomes

| Command | Tool result | Physical verification | Notes |
|---|---|---|---|
| `vector_status` | `ok` | PASS | Connected cleanly; on/off-charger states observed across run |
| `vector_pose` | `ok` | PASS/PARTIAL | Happy-flow pose usable; delocalization diagnostics limited by current output fields |
| `vector_drive_off_charger` | `ok` | PASS | Repeatedly confirmed |
| `vector_say` | `ok` | PASS | Speech confirmed by operator |
| `vector_lift` | `ok` | PASS | Lift motion confirmed |
| `vector_touch_status` (no touch) | `ok` | PASS | `is_being_touched=false`, raw value stable |
| `vector_touch_status` (touching) | `ok` | PASS | `is_being_touched=true`, raw value increased |
| `vector_charger_status` (off charger) | `ok` | PASS | Negative case validated (`is_on_charger=false`) |
| `vector_look` | `ok` | PASS | Image verified; feed/latest-image path confirmed |
| `vector_capture_image` | `ok` | PASS | Image verified; one-shot capture path confirmed |
| `vector_scan` | `ok` | PARTIAL | Executes; physical behavior context-dependent on charger/motion state |
| `vector_find_faces` | `ok` | PARTIAL | Behavior executes; no face detections surfaced |
| `vector_list_visible_faces` | `ok` | FAIL | Empty list under favorable conditions |
| `vector_face_detection` | `ok` | FAIL | `face_count=0` under favorable conditions |
| `vector_list_visible_objects` | `ok` | FAIL | Empty list with nearby cube |
| `vector_vision_reset` | `ok` | PASS | Returned cleanly |
| `vector_proximity_status` (far) | `ok` | PASS | `distance_mm=180`, `signal_quality=0.0317`, `found_object=false`, `unobstructed=false` |
| `vector_proximity_status` (mid) | `ok` | PASS | `distance_mm=92`, `signal_quality=0.4383`, `found_object=false`, `unobstructed=false` |
| `vector_proximity_status` (close) | `ok` | PASS | `distance_mm=42`, `signal_quality=6.1456`, `found_object=false` |
| `vector_proximity_status` (mid, larger cardboard) | `ok` | PASS | `distance_mm=97`, `signal_quality=1.4551`, `found_object=false` |
| `vector_proximity_status` (close, cardboard touching) | `ok` | PASS | `distance_mm=48`, `signal_quality=11.6966`, `found_object=false` |
| `vector_proximity_status` (no object) | `ok` | PASS | `distance_mm=244`, `signal_quality=0.0060`, `unobstructed=true`, `found_object=false` |
| `vector_head` | **FAIL** | N/A | Runtime type error: `Unsupported type for comparison expected Angle` |
| `vector_drive_on_charger` | **FAIL** | FAIL/PARTIAL | Timed out (`timed_out=true`, `motors_stopped=true`) |
| `vector_emergency_stop` | `ok` | PARTIAL | Stop returns `ok`; practical interrupt validation limited by sync motion call path |

### Anomalies / Follow-ups
- `found_object` never flipped true despite near-field and high signal-quality returns.
- `signal_quality` exceeded 1.0 by large margin (up to ~11.7); prior 0.0–1.0 assumption is incorrect for this setup.
- `unobstructed` behaved as expected in clear-path test.
- Operator observation: LightCube lit during some proximity trials.
- `vector_head` currently non-functional due to Angle comparison bug.
- `vector_drive_on_charger` remains unreliable/timeout-prone in this run.
- Perception tools still return empty detections under favorable human/cube conditions.
- Runtime observation seen during perception attempts: `Event callback exception: object_id`.
- **Emergency-stop usability caveat:** current tool path is synchronous for motion, weakening true mid-command interrupt semantics; async motion/control path should be roadmap follow-up.
