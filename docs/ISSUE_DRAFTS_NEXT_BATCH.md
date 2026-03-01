# Issue Drafts — Next Batch (Post-v1.0 Evidence)

Use these as ready-to-open GitHub issues.

---

## 1) MCP: Face detection enablement semantics

**Title**
`Clarify and enforce face-detection preconditions in MCP face tools`

**Problem**
Face features work in direct SDK harness testing, but require explicit vision mode enablement. Current MCP behavior can appear inconsistent without clear precondition handling.

**Scope**
- Face-related MCP tools only.
- No new perception models.

**Tasks**
- [ ] Decide policy: fail-fast guidance vs auto-enable mode.
- [ ] Return explicit states: disabled / enabled-no-face / face-detected.
- [ ] Add actionable tool errors and hints.
- [ ] Update docs with exact contract.

**Acceptance Criteria**
- Face tools never fail ambiguously when detection mode is off.
- Response payload clearly indicates mode state and visibility state.
- Unit tests cover success + disabled + empty-result paths.

**Labels**
`enhancement`, `mcp-semantics`, `perception`, `v1.1`

---

## 2) MCP: Visible vs known object semantics

**Title**
`Align object tools with SDK semantics: visible-now vs known-world`

**Problem**
SDK world model tracks known objects and currently visible objects differently. Empty visible lists have been misinterpreted as failures.

**Scope**
- Object listing/status tools.
- Payload semantics and docs.

**Tasks**
- [ ] Separate or annotate visible-now vs known-world results.
- [ ] Include observation timing metadata where available.
- [ ] Deduplicate repeated object entries where needed.
- [ ] Document visibility timing expectations.

**Acceptance Criteria**
- Tool output distinguishes `visible_now` from known objects.
- Operators can explain empty visible results without guessing.
- Tests validate visibility transitions and semantics.

**Labels**
`enhancement`, `mcp-semantics`, `perception`, `v1.1`

---

## 3) Charger workflow contract hardening

**Title**
`Harden vector_drive_on_charger result semantics and operator feedback`

**Problem**
Direct SDK path shows docking works but can require search time. Current MCP messaging needs clearer states and failure context.

**Scope**
- `vector_drive_on_charger` behavior and response schema.
- No robotics algorithm rewrite.

**Tasks**
- [ ] Define explicit result states (searching/attempting/success/timeout/failure).
- [ ] Improve timeout and failure messaging with next-step hints.
- [ ] Align known-limited docs with observed behavior.

**Acceptance Criteria**
- Operator can distinguish perception/search delay from true failure.
- Timeout path is explicit and actionable.
- Behavior remains best-effort and clearly documented.

**Labels**
`enhancement`, `mcp-semantics`, `charger`, `v1.1`

---

## 4) SDK harness parity tests for MCP

**Title**
`Add parity tests: MCP behavior vs validated SDK harness behavior`

**Problem**
SDK harness is now validated as baseline. MCP should match semantics for key flows.

**Scope**
- Test-only change (mocked SDK patterns as used in repo).
- Key flows: faces, objects, charger.

**Tasks**
- [ ] Add parity-style tests for face detection mode + results.
- [ ] Add parity-style tests for object visibility semantics.
- [ ] Add parity-style tests for charger call result mapping.

**Acceptance Criteria**
- Tests pass in CI and capture previously observed mismatch classes.
- Failure messages are specific and diagnostic.

**Labels**
`tests`, `quality`, `mcp-semantics`, `v1.1`

---

## 5) Docs and release messaging refresh

**Title**
`Refresh known-issues language using post-v1.0 empirical evidence`

**Problem**
Some current phrasing implies fundamental failures where evidence now shows precondition/timing semantics.

**Scope**
- README / troubleshooting / release notes / skill docs.
- No runtime code changes required.

**Tasks**
- [ ] Replace outdated “broken” phrasing with evidence-backed constraints.
- [ ] Add explicit precondition sections for perception and docking workflows.
- [ ] Ensure docs match real observed behavior from harness runs.

**Acceptance Criteria**
- Documentation reflects current empirical status.
- Known limitations are precise and actionable.
- No contradictory claims across docs.

**Labels**
`documentation`, `release-readiness`, `v1.1`

---

## Suggested execution order

1. Issue 5 (docs wording baseline)
2. Issue 1 (face semantics)
3. Issue 2 (object semantics)
4. Issue 3 (charger semantics)
5. Issue 4 (parity test lock-in)

This order reduces confusion first, then hardens behavior, then locks it with tests.
