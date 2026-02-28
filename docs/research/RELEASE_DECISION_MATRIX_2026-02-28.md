# Release Decision Matrix — 2026-02-28

## Purpose
Decide between:
1. **Ship now** (basic-functionality MVP)
2. **Fix/improve first** (address key gaps before public release)

---

## Current Evidence Snapshot (from latest smoke docs)

### Confirmed working (physically verified)
- `vector_drive_off_charger`
- `vector_say`
- `vector_lift`
- `vector_touch_status` (no-touch + touch)
- `vector_charger_status` (off-charger negative case)
- `vector_look` (feed/latest-image path)
- `vector_capture_image` (one-shot capture path)
- `vector_proximity_status` data path (with semantics caveats)

### Known limitations / failures
- `vector_head` fails (Angle type comparison bug)
- `vector_drive_on_charger` timeout/unreliable in smoke
- Perception detections currently non-functional in smoke:
  - `vector_list_visible_faces`
  - `vector_face_detection`
  - `vector_list_visible_objects`
- `vector_pose` lacks metadata for robust delocalization diagnostics
- Emergency stop practical interrupt semantics limited by synchronous motion call path

### Important architecture note
- Camera tools provide image bytes only; **look→reason→act requires a VLM/image-analysis model/tool in the runtime loop**.

---

## Roadmap Staleness Highlights (initial)

1. **Milestone wording implies broad “all tools tested and working”** as hardware-validation target.
   - Actual state now is mixed (clear MVP subset + known non-functional areas).

2. **v1 release criteria likely under-specify capability tiers**.
   - Need explicit “MVP guaranteed tools” vs “known-limited tools”.

3. **Emergency stop confidence is not represented with sync/async nuance**.
   - Current path is command-acknowledged but interrupt semantics are limited.

4. **Perception expectations appear ahead of validated reality**.
   - Raw camera loop works, but built-in face/object visibility tools are currently unreliable.

5. **Pose readiness criteria do not separate happy-flow from frame-validity diagnostics**.
   - Need explicit metadata requirement for delocalization-safe usage.

---

## Decision Criteria

Score each option 1–5 (5 best). Weight can be adjusted.

| Criterion | Weight | Ship Now (MVP) | Fix First |
|---|---:|---:|---:|
| User value this weekend | 5 |  |  |
| Safety / misuse risk | 5 |  |  |
| Functional honesty (docs match behavior) | 5 |  |  |
| Support burden post-release | 4 |  |  |
| Engineering focus / momentum | 4 |  |  |
| Confidence in critical tool paths | 5 |  |  |
| Time-to-release | 3 |  |  |
| Total (weighted) |  |  |  |

---

## Option A — Ship Now (MVP Scope)

### Publicly supported tool subset
- status/charger-status
- drive-off-charger + basic drive
- say
- lift
- touch-status
- look/capture-image
- proximity-status (with caveats)

### Required release notes language
- Explicit known limitations for head/perception/charger-return/pose metadata/stop semantics
- Explicit requirement: VLM/image-analysis runtime for look→reason→act autonomy

### Pros
- Momentum and real user feedback
- Delivers tangible value now

### Cons
- Higher support/expectation management load
- Risk users interpret non-functional tools as regressions

---

## Option B — Fix First, Then Release

### Suggested pre-release fixes
- `vector_head` type bug
- `vector_drive_on_charger` reliability
- minimum viable perception reliability or clear de-scope
- pose metadata fields (`origin_id`, `is_picked_up`, optional `localized_to_object_id`)
- async motion/control path for meaningful interrupt semantics

### Pros
- Cleaner first impression
- Lower near-term confusion/support burden

### Cons
- Delayed release
- Potential scope creep before first public milestone

---

## Open Questions to Resolve Before Final Decision

1. Do we want first release to be **capability-complete** or **honest MVP subset**?
2. Is “look→reason→act via external VLM” acceptable as core autonomy story for v1?
3. Should non-functional tools be hidden/de-scoped from README until fixed?
4. What minimum bar do we require for charger return and stop semantics before public launch?

---

## Next Step
Populate matrix scores with Dan, choose Option A or B, then align ROADMAP.md + README + release notes with that decision.
