# Tool Docking / Charger Prerequisites Matrix

Purpose: quick operator reference for which tool behaviors require undocked state vs can run while on charger.

> This matrix is **observed behavior + implementation intent** for current VectorClaw tools. Re-validate when SDK/runtime changes.

| Tool | Requires undocked? | Behavior if docked | Source of truth |
|---|---|---|---|
| `vector_drive` | **Yes** | Returns actionable error (`on_charger`, `action_required`) or attempts auto-undock if `VECTOR_AUTO_DRIVE_OFF_CHARGER` enabled | `tools_motion.vector_drive` + `_motion_precheck` |
| `vector_drive_off_charger` | No | Intended command to undock; should succeed when docked | `tools_motion.vector_drive_off_charger` |
| `vector_drive_on_charger` | **Yes** (must be undocked) | Returns `{status: ok, already_on_charger: true}` immediately; SDK call skipped to avoid undefined behaviour (cube activation) | `tools_motion.vector_drive_on_charger` |
| `vector_say` | No | Works while docked | hardware smoke 2026-02-27 |
| `vector_status` | No | Works while docked | hardware smoke 2026-02-27 |
| `vector_pose` | No | Works while docked | implementation (no motion precheck) |
| `vector_look` | No | Works while docked | hardware smoke 2026-02-27 |
| `vector_face` | No | Works while docked (fixed in v1.0.0) | hardware smoke 2026-02-28 |
| `vector_head` | No | Works while docked | hardware smoke 2026-02-27 |
| `vector_lift` | No | Works while docked | hardware smoke 2026-02-27 |
| `vector_cube` | Depends on action/cube availability | Requires connected cube for dock/pickup/roll actions; no charger gate today | `tools_perception.vector_cube` |
| `vector_animate` | No | Should run while docked, but subject to animation/runtime caveats | implementation + playbook caveats |

## Notes

- Docking gate currently exists only for explicit drive motion path (`vector_drive`).
- Lack of docking gate does **not** imply behavior will always be physically smooth (idle behavior can overlap commands).
- Keep this matrix aligned with `HARDWARE_SMOKE_LOG.md` and `HARDWARE_TEST_PLAYBOOK.md`.
