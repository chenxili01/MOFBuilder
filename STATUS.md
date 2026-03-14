# STATUS.md

## Workflow Status

- Phase: Phase 2
- Checkpoint: phase-2-reader-preservation-complete
- Status: COMPLETED
- Next step: planner
- Last update: 2026-03-15

## Branch

typed-attachment-hardening

## Objective

Systematically remove hard-coded universal attachment-atom assumptions so fragment loading,
builder/runtime compilation, and optimizer-local placement use typed attachment sources and
resolved anchors rather than a universal literal `X` bucket.

## Current Focus

Phase 2 implementation is complete. Reader/parser surfaces now preserve typed
attachment candidates by source atom type while keeping the legacy literal-`X`
compatibility outputs available for existing builder and optimizer code.

## Executor Handoff

1. Phase 2 completed without widening scope beyond reader/parser preservation.
2. `PdbReader` now preserves attachment rows grouped by source atom type, while
   still exposing legacy `X_data` for literal-`X` compatibility.
3. `FrameNode` and `FrameLinker` now retain typed attachment tables alongside
   existing `*_X_data` outputs so later builder phases can resolve `source_atom_type`
   without re-reading fragment atoms.
4. Phase 2 tests were added for:
   typed attachment preservation and recentering in `PdbReader`
   and legacy literal-`X` compatibility in node/linker public outputs.
5. Validation was limited in this shell:
   `python -m compileall` passed for the changed production modules, but
   `python -m pytest` could not run because `pytest` is not installed and direct
   runtime checks could not execute because `numpy` is unavailable in the active
   interpreter.
6. Next step is planner handoff for Phase 3 only.

## Invariants

1. Topology graph remains the source of truth.
2. Builder owns role interpretation and runtime/snapshot compilation.
3. Optimizer consumes compiled attachment semantics rather than inferring role meaning from raw fragment atoms.
4. Framework remains role-agnostic.
5. Backward compatibility must be preserved.
6. Primitive-first optimization must be preserved.
7. Null-edge semantics must remain explicit.
8. Snapshots remain derived API views, not new sources of truth.
9. Slot/path semantics determine legality before geometry.
10. Attachment-source typing must not be collapsed to a universal literal `X` assumption.
