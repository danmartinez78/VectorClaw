## Summary
- adopt clearer documentation naming boundaries:
  - `API_REFERENCE.md` -> `MCP_API_REFERENCE.md`
  - `API_REFERENCE_COPILOT_GENERATED.md` -> `VECTOR_SDK_REFERENCE.md`
- update README/docs links to align with MCP contract vs SDK capability boundaries
- add release decision planning artifact:
  - `docs/research/RELEASE_DECISION_MATRIX_2026-02-28.md`
- update roadmap with mandatory release gates for:
  - user install readiness
  - ClawHub skill readiness
  - final security audit
- add additive boundary/context sections to `VECTOR_SDK_REFERENCE.md`
- mark legacy SDK surface doc as temporary during consolidation

## Why
Reduce user confusion between "what exists in SDK" vs "what is exposed in MCP", and align release planning with current validated state.

## Scope
Documentation/roadmap/planning only. No runtime code changes.
