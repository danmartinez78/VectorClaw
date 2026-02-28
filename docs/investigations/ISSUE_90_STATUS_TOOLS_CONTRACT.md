# Issue #90: Status Tools SDK Contract Alignment

**Status:** Investigation complete
**Created:** 2026-02-28
**Issue:** https://github.com/danmartinez78/VectorClaw/issues/90

---

## Problem

VectorClaw status tools assume status attributes that are not guaranteed in the SDK's `RobotStatus` class:

- `is_carrying_object` → NOT a valid property
- `is_on_charger_platform` → NOT a valid property
- `is_cliff_detected` → NOT a valid property

These were accessed via `getattr()` with fallback to `None`, which masks the contract mismatch instead of addressing it.

---

## Authoritative SDK Contract

**Source:** `anki_vector.status.RobotStatus` class

| Property | Type | Description |
|----------|------|-------------|
| `are_motors_moving` | bool | Any motor (head, lift, wheels) active |
| `is_carrying_block` | bool | Robot carrying cube/block |
| `is_docking_to_marker` | bool | Heading toward marker (charger/cube) |
| `is_picked_up` | bool | Robot in air (not on stable surface) |
| `is_button_pressed` | bool | Button pressed |
| `is_falling` | bool | Robot falling |
| `is_animating` | bool | Animation playing |
| `is_pathing` | bool | Path planning active |
| `is_lift_in_pos` | bool | Lift at target position |
| `is_head_in_pos` | bool | Head at target position |
| `is_in_calm_power_mode` | bool | Low power mode |
| `is_on_charger` | bool | On charger platform |
| `is_charging` | bool | Actively charging |

**NOT in RobotStatus:**
- ~~`is_carrying_object`~~ → Use `is_carrying_block`
- ~~`is_on_charger_platform`~~ → Use `is_on_charger`
- ~~`is_cliff_detected`~~ → Not available via RobotStatus

---

## Current Implementation Issues

### `vector_status()` (tools_perception.py)

```python
def vector_status() -> dict:
    robot = _robot()
    battery = robot.get_battery_state()
    st = robot.status
    return {
        "status": "ok",
        "battery_level": battery.battery_level,
        "is_charging": st.is_charging,                              # ✅ Valid
        "is_carrying_block": st.is_carrying_block,                  # ✅ Valid
        "is_carrying_object": getattr(st, "is_carrying_object", None),   # ❌ Invalid
        "is_on_charger_platform": getattr(st, "is_on_charger_platform", None),  # ❌ Invalid
        "is_cliff_detected": getattr(st, "is_cliff_detected", None),  # ❌ Invalid
        "is_picked_up": getattr(st, "is_picked_up", None),           # ⚠️ Valid but using getattr
    }
```

### `vector_charger_status()` (tools_perception.py)

```python
def vector_charger_status() -> dict:
    ...
    return {
        ...
        "is_on_charger_platform": robot.status.is_on_charger_platform,  # ❌ Will raise AttributeError
    }
```

**Note:** The hardware smoke test showed `vector_charger_status` FAIL with attribute error, confirming this issue.

---

## Recommended Fix

### Option A: Strict Contract (Recommended)

Remove invalid fields, use only authoritative SDK properties:

```python
def vector_status() -> dict:
    robot = _robot()
    battery = robot.get_battery_state()
    st = robot.status
    return {
        "status": "ok",
        "battery_level": battery.battery_level,
        "is_charging": st.is_charging,
        "is_carrying_block": st.is_carrying_block,
        "is_on_charger": st.is_on_charger,
        "is_picked_up": st.is_picked_up,
    }
```

**Pros:**
- Clean contract, no assumptions
- Fails fast on SDK changes (good for detection)
- Matches hardware reality

**Cons:**
- Breaking change if external tools depend on old field names
- `is_cliff_detected` not available (but wasn't working anyway)

### Option B: Defensive with Warnings

Keep `getattr()` but log warnings for missing fields:

```python
import logging
logger = logging.getLogger(__name__)

def vector_status() -> dict:
    ...
    is_cliff = getattr(st, "is_cliff_detected", None)
    if is_cliff is None:
        logger.warning("is_cliff_detected not available in RobotStatus")
    ...
```

**Pros:**
- Non-breaking for consumers
- Visibility into contract drift

**Cons:**
- Masks the real problem
- Log noise

---

## Implementation Plan

1. **Update `vector_status()`**:
   - Remove `is_carrying_object` (use `is_carrying_block`)
   - Remove `is_on_charger_platform` (use `is_on_charger`)
   - Remove `is_cliff_detected` (not available)
   - Remove `getattr()` for valid properties

2. **Update `vector_charger_status()`**:
   - Change `is_on_charger_platform` → `is_on_charger`

3. **Update API docs**:
   - Document authoritative field names
   - Note breaking change if applicable

4. **Add tests**:
   - Mock RobotStatus with valid properties only
   - Assert no AttributeError on status tool calls

---

## Test Evidence

**Hardware smoke (2026-02-27):**
- `vector_status`: FAIL → PASS after hotfix (bcee0db)
- `vector_charger_status`: FAIL (not fixed yet)

The hotfix added `getattr()` fallbacks, but this is a bandage. The real fix is using correct property names.

---

## References

- SDK source: `anki_vector/status.py`
- Hardware smoke log: `docs/HARDWARE_SMOKE_LOG.md`
- Issue: https://github.com/danmartinez78/VectorClaw/issues/90
