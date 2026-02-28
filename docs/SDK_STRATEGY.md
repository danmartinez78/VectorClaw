# SDK Strategy

## Current strategy (2026-02-27)
Use upstream Wire-Pod SDK directly.

- No maintained fork in active use
- No fork pin required for baseline functionality
- Keep compatibility focused on stable upstream versions

## Fallback strategy (only if needed)
If a future blocker appears (runtime breakage, hard incompatibility), use a **temporary patch path**:
1. Apply minimal patch
2. Track in `SDK_PATCH_NOTES.md`
3. Upstream the fix when possible
4. Remove local delta quickly

## Decision rule
Default to upstream unless a blocker is demonstrated by reproducible failure.
