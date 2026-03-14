# STATUS.md

## Workflow Status

- Phase: Phase 5
- Checkpoint: phase-5-complete
- Status: READY FOR PLANNER
- Next step: planner
- Last update: 2026-03-15

## Branch

typed-attachment-hardening

## Objective

Systematically remove hard-coded universal attachment-atom assumptions so fragment loading,
builder/runtime compilation, and optimizer-local placement use typed attachment sources and
resolved anchors rather than a universal literal `X` bucket.

## Current Focus

Phase 5 execution is complete. The next step is planner handoff for the next
bounded phase after optimizer-local placement now consumes builder-compiled
resolved anchors for covered role-aware paths.

## Planner Handoff

1. Phase 5 is complete: optimizer-local placement now resolves node and linker
   anchors from builder-compiled semantic snapshot records instead of treating
   raw literal-`X` payloads as the universal semantic source.
2. The implemented scope stayed bounded to `mofbuilder/core/optimizer.py`,
   `tests/test_core_optimizer.py`, and workflow markdown files.
3. Typed role-aware placement now consumes compiled `anchor_source_type` and
   `anchor_source_ordinal` metadata plus typed attachment coordinate tables to
   place edges from resolved anchors.
4. Legacy literal-`X` families remain valid only through resolved-anchor
   compatibility metadata; the optimizer still permits literal `X` placement
   when the compiled anchor source explicitly resolves to `X`.
5. Missing or incomplete resolved-anchor inputs now fail with explicit semantic
   `ValueError`s that identify missing builder-compiled anchor semantics.
6. Required bounded tests were added for:
   one typed optimizer-consumption case,
   one legacy literal-`X` compatibility-through-resolved-anchor case, and
   one explicit missing-anchor semantic failure case.
7. Planner should bound the next phase without reopening Phase 5 or widening
   into framework, graph-grammar, or pipeline-order changes.

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
