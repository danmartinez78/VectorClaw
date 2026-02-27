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
