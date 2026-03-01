## Summary
`vector_pose` is not fully functional for localization/delocalization diagnostics. It appears to work in happy-path driving flows (dock -> drive off -> move around), but does not expose enough state to validate pose-frame resets after pickup/delocalization.

## What we observed (hardware empirical run)
- Baseline docked pose was near `(0,0,0)`.
- After `vector_drive_off_charger`, pose changed as expected (e.g. x ~128mm).
- After pickup/setdown cycles, pose changed, but did **not** clearly reset to `(0,0,0)` as expected for a new origin frame.
- We currently cannot confirm whether true delocalization occurred because tool output omits key fields.

## Why this matters
Agent consumers can misinterpret pose continuity across handling events. If origin frame changes are hidden, downstream planning can compare poses that may not be comparable.

## Current tool gap
`vector_pose` currently returns only:
- `x`, `y`, `z`, `angle_deg`

Missing state needed for correct interpretation:
- `origin_id`
- `is_picked_up`
- (optional) `localized_to_object_id`

## Scope decision
For release safety, we are **not changing tool behavior in this cycle**. We are documenting this as a known limitation.

## Recommended follow-up
1. Add optional extended pose output fields (`origin_id`, `is_picked_up`, `localized_to_object_id`).
2. Document comparability rule (`origin_id` must match, or use `is_comparable`).
3. Add an empirical regression test protocol for pickup/delocalization transitions.

## Release note impact
Known limitation: `vector_pose` should be treated as reliable for happy-path driving from base, but not as a full delocalization diagnostic until origin metadata is surfaced.
