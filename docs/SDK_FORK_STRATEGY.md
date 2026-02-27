# SDK Fork Strategy (Hybrid: Temporary Fork + Upstream Convergence)

## Goal
Ship VectorClaw v1 on time while avoiding a long-term SDK maintenance burden.

## Chosen approach
Hybrid:
1. **Temporary fork pin** for hard compatibility blockers
2. **Upstream PRs** opened immediately for each patch
3. **VectorClaw-side shims** for behavior-level resilience
4. **De-fork checkpoint** after upstream release or explicit timeout review

## Ownership split

### In VectorClaw repo
- `SDK_FORK_PATCH_NOTES.md` (what we depend on + why)
- Release-note transparency for users
- Dependency pin policy and rollback plan
- De-fork tracking issue/state

### In SDK fork repo
- Actual patch commits
- Fork tags/releases
- SDK-level tests validating patched behavior
- Upstream PR references in commit messages

## Patch admission policy
A patch is allowed in the temporary fork only if all are true:
- Blocks release or core hardware reliability
- Cannot be safely solved in VectorClaw wrapper layer
- Is minimal/surgical (no unrelated refactor)
- Has an upstream PR plan
- Has a removal path documented

## De-fork exit criteria
We switch back to official SDK when:
- Required patches are merged upstream and released, **or**
- Equivalent behavior is available via wrapper-layer compatibility with no user-facing regressions

## Release messaging requirements
When fork pin is active, release notes must include:
- Why fork is used
- Exact patch categories
- Upstream PR links/status
- Intended convergence plan

## Immediate execution checklist
- [ ] Freeze patch set in `SDK_FORK_PATCH_NOTES.md`
- [ ] Add dependency pin to temporary fork release/tag
- [ ] Open upstream PR(s) for each patch
- [ ] Open de-fork tracking issue in VectorClaw
- [ ] Validate via CI + hardware smoke before release cut
