# SDK Fork Patch Notes (wirepod_vector_sdk)

These are the local unblock patches applied during hardware validation.

## Why
Current SDK behavior required compatibility and runtime adjustments to unblock real robot testing on modern Python.

## Patches to carry into fork

### 1) asyncio compatibility (Python 3.10+)

**File:** `anki_vector/connection.py`

Replace:
- `asyncio.Event(loop=loop)` (3 occurrences)

With:
- `asyncio.Event()`

**File:** `anki_vector/events.py`

Replace:
- `asyncio.Event(loop=self._loop)`

With:
- `asyncio.Event()`

### 2) Animation-list timeout mitigation

**File:** `anki_vector/robot.py`

Change Robot constructor default:
- `cache_animation_lists: bool = True`

To:
- `cache_animation_lists: bool = False`

Rationale: avoids startup timeout path while validating core motion/sensing.

## Follow-up recommendation for fork
- Add explicit config/env toggle for animation caching instead of hard default swap.
- Add regression tests for Python 3.11/3.12 event-loop compatibility.
