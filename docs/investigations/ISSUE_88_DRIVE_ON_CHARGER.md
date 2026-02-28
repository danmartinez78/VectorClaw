# Issue #88: vector_drive_on_charger Behavior Investigation

**Status:** Investigation in progress
**Created:** 2026-02-28
**Issue:** https://github.com/danmartinez78/VectorClaw/issues/88

---

## Observation

During MCP hardware smoke testing (2026-02-27), `vector_drive_on_charger` did not produce visible charger approach behavior. Instead:
- The light cube illuminated
- No clear charger drive attempt was observed
- Tool returned `ok` status (no error)

**Key context:** The robot later autonomously returned to charger on low battery, confirming the hardware capability exists and the charger is recognizable.

---

## SDK Contract

From `anki_vector.behavior.BehaviorComponent.drive_on_charger()`:

> Vector will attempt to find the charger and, if successful, he will back onto it and start charging.
>
> Vector's charger has a visual marker so that the robot can locate it for self-docking.

**Expected behavior:**
1. Vector searches for charger visual marker
2. If found, navigates to charger
3. Backs onto charger platform
4. Begins charging

---

## Implementation Analysis

Current VectorClaw implementation (`src/vectorclaw_mcp/tools_motion.py`):

```python
def vector_drive_on_charger(timeout_sec: float = 10.0) -> dict:
    """Experimental: drive Vector onto its charger with a timeout and motor-stop fallback."""
    robot = _robot()
    result: list = []

    def _attempt() -> None:
        try:
            robot.behavior.drive_on_charger()
            result.append({"status": "ok"})
        except Exception as exc:
            result.append({"status": "error", "message": str(exc)})

    t = threading.Thread(target=_attempt, daemon=True)
    t.start()
    t.join(timeout=timeout_sec)

    if t.is_alive():
        # Timeout handling with motor stop fallback
        ...
```

**Key observations:**
- Direct passthrough to SDK `robot.behavior.drive_on_charger()`
- No preconditions checked (e.g., is charger visible?)
- Timeout + motor stop fallback added for safety
- Tool returns `ok` even if behavior doesn't complete successfully

---

## Hypotheses

### H1: Charger Marker Not Visible
- **Symptom:** Cube lights up (Vector looking for objects), no charger approach
- **Cause:** Charger marker obstructed, dirty, or at bad angle
- **Test:** Verify charger marker visibility; try different charger placement

### H2: Cube Interference
- **Symptom:** Cube activates during command
- **Cause:** SDK behavior may trigger cube interaction as part of search pattern
- **Test:** Run command with cube powered off / in different room

### H3: SDK Behavior Timing
- **Symptom:** Tool returns `ok` before behavior completes
- **Cause:** `drive_on_charger()` is async; thread completes on call, not on result
- **Test:** Check if behavior is async and needs await/callback handling

### H4: Robot State Precondition
- **Symptom:** Behavior silently fails if robot not in correct state
- **Cause:** SDK may require robot to be off charger, batteries above threshold, etc.
- **Test:** Check SDK source for preconditions

---

## Reproduction Steps

**Environment:**
- Robot serial: `00a1546c`
- Wire-Pod: active/running
- Branch: `dev`

**Steps:**
1. Place Vector near charger (but not on it)
2. Ensure cube is visible but not on charger
3. Call `vector_drive_on_charger` via MCP
4. Observe physical behavior

**Variables to test:**
- [ ] With cube powered off
- [ ] With cube in different room
- [ ] With charger marker cleaned
- [ ] With charger at different angle
- [ ] With different lighting conditions
- [ ] With robot at different distances from charger

---

## Operator Guidance (Interim)

Until root cause is identified:

1. **Do not rely on `vector_drive_on_charger` for autonomous docking**
   - Tool may return `ok` without completing behavior
   - Manual verification required

2. **Preconditions to check:**
   - Charger marker clean and visible
   - Robot has clear line of sight to charger
   - Cube not interfering (try powering off)

3. **Alternative:**
   - Use manual driving commands to position near charger
   - Let robot's autonomous low-battery behavior handle final docking

---

## Proposed Fixes

### Option A: Add Precondition Checks
Check charger visibility before calling SDK:
- Query robot state for charger visibility
- Return error if charger not detected
- Requires SDK investigation for available state attributes

### Option B: Re-scope Tool
If behavior cannot be made deterministic:
- Rename to `vector_attempt_charger_dock`
- Document as "best effort" with no completion guarantee
- Add `observation_required: true` flag in tool metadata

### Option C: Hybrid Approach
- Add optional `require_visual_confirm` parameter
- If true, wait for `is_on_charger_platform` state change
- If false, return immediately (current behavior)

---

## Next Steps

- [ ] Test with cube powered off
- [ ] Check SDK source for preconditions/async behavior
- [ ] Test with cleaned charger marker
- [ ] Document findings in HARDWARE_SMOKE_LOG.md
- [ ] Update tool docs with interim guidance
- [ ] Decide on fix approach (A, B, or C)

---

## References

- SDK docs: `anki_vector.behavior.BehaviorComponent.drive_on_charger`
- Hardware smoke log: `docs/HARDWARE_SMOKE_LOG.md`
- Issue: https://github.com/danmartinez78/VectorClaw/issues/88
