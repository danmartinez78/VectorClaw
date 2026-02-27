# OpenClaw Skill Plan (Issue #70)

## Objective
Deliver a foolproof OpenClaw skill that guides users from zero setup to a validated, working VectorClaw MCP integration.

## User Experience Goals
- Minimal manual steps
- Clear prompts and defaults
- Deterministic pass/fail end-state
- Actionable remediation for every failure mode

## Proposed Skill Flow

1. **Preflight**
   - Verify Python version
   - Verify network reachability assumptions
   - Verify OpenClaw runtime context

2. **Configuration Prompting**
   - Prompt for `VECTOR_SERIAL` (required)
   - Prompt for `VECTOR_HOST` (optional)
   - Confirm values before write

3. **SDK Setup**
   - Install `wirepod_vector_sdk` from upstream
   - Verify `import anki_vector` succeeds
   - Print installed version for traceability

4. **Connectivity Validation**
   - Run lightweight status check
   - Detect and classify failures:
     - serial missing/invalid
     - host unreachable
     - SDK not importable

5. **Self-Test**
   - Execute safe smoke checks:
     - status
     - speech (optional)
     - non-destructive command
   - Output clear summary and next steps

## Failure Taxonomy + Remediation

| Failure | Detection | User Action |
|---|---|---|
| Missing serial | empty `VECTOR_SERIAL` | provide serial from Vector settings/cert |
| SDK import fails | `ImportError` | run provided install command |
| Robot unreachable | connection timeout | verify Wire-Pod, IP/network, cert context |
| MCP misconfiguration | startup error | print exact env/config path and fix snippet |

## Implementation Boundaries
- Skill handles setup/orchestration/validation
- Core tool behavior remains in VectorClaw codebase
- No ROS2 scope in this skill

## Acceptance Criteria
- New user can complete setup in one guided run
- Skill output includes deterministic PASS/FAIL
- Each FAIL has a concrete remediation message
- Docs include copy/paste setup + troubleshoot snippets
