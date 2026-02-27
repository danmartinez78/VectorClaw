# Last-Night Fixes Ledger (Forensic Backfill)

Date range reconstructed: 2026-02-26 → 2026-02-27 (CST)

Purpose: preserve **what changed, where it changed, and where the source of truth lives** so we don’t lose momentum after high-tempo sessions.

## Executive summary

- Many edits were performed in temporary local clones (`/tmp/VectorClaw`, `~/.openclaw/workspace/vectorclaw-repo`) and then pushed.
- Temporary clones were deleted multiple times after push.
- Durable source of truth is now GitHub history + current `VectorClaw` local clone.
- Animation-timeout workaround context lives in SDK patch notes/docs (not as a `wire-pod` repo patch).

## Recovered local working paths

- `/tmp/VectorClaw` (temporary)
- `~/.openclaw/workspace/vectorclaw-repo` (temporary, repeatedly recreated/deleted)
- `~/.openclaw/workspace/VectorClaw` (current persistent local clone)

## Confirmed fix areas

### A) SDK/runtime compatibility + reliability

Primary reference:
- `docs/SDK_FORK_PATCH_NOTES.md`

Key patch set tracked:
- `asyncio.Event(loop=...)` → `asyncio.Event()` (SDK compatibility)
- `cache_animation_lists=False` default recommendation (animation-list timeout mitigation path)

### B) Runtime guardrails / support policy

Related docs/code:
- `docs/RUNTIME_SUPPORT.md`
- `src/vectorclaw_mcp/compat.py`

### C) Hardware/docs feature stream

Representative commits in repo history include:
- `a507dff` docs: comprehensive setup guide (Wire-Pod heavy)
- `6e34db9`, `3bc43b9`, `58a1421`, `a575eeb` roadmap iterations
- `5d28eec`, `ba1cc1e`, `5143c69` SDK quick-reference + follow-ups
- `777f204`, `0e18659`, `9b4caf0`, `5507cb7` docs + features + motion precheck stream

## What is NOT currently stashed

Audit result at time of writing:
- `~/wire-pod`: no stash, clean working tree
- `~/.../workspace/VectorClaw`: no stash; has local uncommitted docs taxonomy changes (now being captured)

## Open local WIP captured now

Docs taxonomy normalization:
- `VECTOR_SDK_REFERENCE.md` → `WIREPOD_SDK_REFERENCE.md`
- `FUNCTIONALITY_MATRIX.md` → `SDK_TO_MCP_COVERAGE_MATRIX.md`

## Process guardrails (agreed going forward)

1. **One canonical local path per repo** (no ad-hoc temp clone unless explicitly noted).
2. Before edits, record in session:
   - `pwd`
   - `git remote -v`
   - `git branch --show-current`
   - `git status -sb`
3. If using temp clone, create explicit note: "TEMP CLONE" + reason.
4. No repo cleanup (`rm -rf`) without explicit confirmation.
5. End-of-session checkpoint: commit or stash + ledger note.

This file exists so frantic progress still remains principled and recoverable.
