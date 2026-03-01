# Investigation Report: `ListAnimations request timed out`

## A) Code-Path Trace

**Call chain:**

1. **`Robot.__enter__`** — `robot.py:754`: calls `self.connect(self.behavior_activation_timeout)` (default 10s)

2. **`Robot.connect`** — `robot.py:628`: connects gRPC, initializes all components, then:

3. **Animation preload check** — `robot.py:663-669`:
   ```python
   if self.cache_animation_lists:
       anim_request = self._anim.load_animation_list()
       if isinstance(anim_request, concurrent.futures.Future):
           anim_request.result()               # <-- BLOCKS here
       anim_trigger_request = self._anim.load_animation_trigger_list()
       if isinstance(anim_trigger_request, concurrent.futures.Future):
           anim_trigger_request.result()        # <-- or here
   ```

4. **`AnimationComponent.load_animation_list`** — `animation.py:147-170`: decorated with `@on_connection_thread`, has a bare `except` that retries once:
   ```python
   try:
       return await self._load_animation_list()
   except:
       return await self._load_animation_list()
   ```

5. **`_load_animation_list`** — `animation.py:133-137`:
   ```python
   result = await self.grpc_interface.ListAnimations(req, timeout=10)
   ```

6. **gRPC timeout** → `grpc.RpcError` with `StatusCode.DEADLINE_EXCEEDED` → caught in `log_handler` at `connection.py:775-776` → converted via `connection_error()` at `exceptions.py:115-124` → `VectorTimeoutException`

---

## B) Timeout Mechanics

| Aspect | Detail |
|--------|--------|
| **Where set** | Hardcoded `timeout=10` in `animation.py:134` and `animation.py:140` |
| **Type** | Per-call gRPC deadline — each `ListAnimations` / `ListAnimationTriggers` RPC gets 10 seconds |
| **Retry logic** | Bare `except` retries **once** — so worst case is 2 × 10s = **20 seconds** of blocking before failure |
| **Exception path** | `grpc.RpcError` → `log_handler` catches → `connection_error(rpc_error)` → `VectorTimeoutException` |
| **Not configurable** | The 10s deadline is a literal in the source, not parameterized |
| **After timeout** | The gRPC channel itself remains alive — connection is fine. Only the animation dicts stay empty. `Robot.connect()` aborts entirely because `.result()` propagates the exception. |

---

## C) Wire-Pod Compatibility Analysis

**Confirmed from source:**

- `play_animation_trigger(name)` and `play_animation(name)` call `_ensure_loaded()` internally (`animation.py:225` and `animation.py:266`), which lazy-loads the lists if empty. This means **direct playback also needs the list to resolve names** — it validates the name against the cached dict before sending the `Play*` RPC.

- The `ListAnimations` and `ListAnimationTriggers` RPCs enumerate potentially hundreds of entries. Under Wire-Pod firmware, this enumeration can be slow/unimplemented, while the simpler `PlayAnimation`/`PlayAnimationTrigger` RPCs (which take a single name and execute) work fine.

- **Listing is empirically less reliable than direct playback** under Wire-Pod. The play RPCs are simple unary calls; the list RPCs must serialize a large response payload.

**Key architectural observation:** Even `play_animation_trigger('GreetAfterLongTime')` will internally try to load the full animation list via `_ensure_loaded()` if the cache is empty. So the timeout can also hit on *first play*, not just at startup. However, the lazy-load path has the same retry-once logic and the same 10s per-attempt deadline.

---

## D) Mitigation Options (Ranked)

| # | Strategy | Startup Impact | Runtime Impact | Complexity |
|---|----------|---------------|----------------|------------|
| **1** | **`cache_animation_lists=False`** (our fix) | Startup succeeds immediately | First anim menu access may be slow | Trivial — one flag change |
| **2** | **Guard lazy-load with try/except in harness** | None | Warns user, falls through gracefully | Small wrapper function |
| **3** | Add retry/backoff in SDK `_load_animation_list` | Slower startup if failing | Same | SDK-level change, risky |
| **4** | Feature-degrade mode: empty list = "list unavailable" | None | Some menu items show warnings | Moderate |
| **5** | Bypass list entirely — pass raw string to `PlayAnimationTrigger` without validation | None | Removes safety check, any typo hits robot | Requires SDK change |

**Recommended: Options 1 + 2 combined** — which is what the patch implements.

---

## E) Applied Patch

Three changes to `sdk_test_harness.py`:

1. **Changed `cache_animation_lists=True` → `False`** — startup no longer blocks on `ListAnimations`. (line ~650)

2. **Added `_ensure_anim_cache(robot)` helper** — a best-effort lazy loader that:
   - Runs only once (guarded by `_anim_cache_attempted` flag)
   - Calls `load_animation_list` then `load_animation_trigger_list`
   - Catches any exception per-call and prints a warning instead of crashing
   - (lines 25-52)

3. **Animation menu items call `_ensure_anim_cache(robot)`** before accessing `anim_list` / `anim_trigger_list`, and handle empty lists gracefully. (lines 200-230)

**Net effect:** Connection always succeeds. Animation listing is attempted once when the user first picks an animation menu item. If it times out, they see a warning but can still use `play_animation_trigger('GreetAfterLongTime')` directly (since *that* call will internally retry `_ensure_loaded` via the SDK's own lazy path). All other SDK functions are completely unaffected.
