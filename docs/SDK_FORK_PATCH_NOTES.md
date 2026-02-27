# SDK Fork Patch Notes (wirepod_vector_sdk)

These are the temporary fork patches required to keep VectorClaw release-ready while upstream convergence is in progress.

Related policy: [SDK Fork Strategy](SDK_FORK_STRATEGY.md)

## Why
Current SDK behavior required compatibility and runtime adjustments to unblock real robot testing on modern Python.

## Patch tracking status

| Patch area | Fork status | Upstream PR | Planned removal trigger |
|---|---|---|---|
| asyncio Event loop compatibility | Pending fork commit | _TBD_ | Upstream release includes fix |
| animation cache default behavior | Pending fork commit | _TBD_ | Upstream release or wrapper-level toggle lands |

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
