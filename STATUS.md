## Workflow Status

- Phase: Phase 2
- Checkpoint: phase-2-ready-for-executor
- Status: READY_FOR_EXECUTION
- Next step: executor
- Last update: 2026-03-16

## Branch

svd-anchor-shape-stabilization

## Objective

Stabilize role-aware rotation initialization by correcting the geometry used
during SVD anchor alignment and by preventing downstream optimizer stages from
degrading already-valid semantic seed rotations in covered cases.

## Current Focus

Phase 1 is complete as documentation-only work.
The active handoff is now Phase 2, which preserves real source-anchor radial
shape in the covered seam before local SVD inputs are constructed.

## Phase 1 Contract

Anchor-geometry failure class:

valid role-aware source-anchor geometry must not be flattened into a
uniform-radius orientation proxy before covered SVD initialization, and valid
semantic seed rotations must not be degraded afterward by geometry-only
refinement stages that do not preserve the same semantic objective.

Required terminology:

- `source_anchor_vector`
- `target_anchor_direction`
- `slot_radius`
- `shape-preserving pseudo anchor`
- `role-aware seed rotation`
- `legacy uniform-scale orientation proxy`

## Executor Handoff

1. Stay within Phase 2 only. Allowed files are `builder.py`, `optimizer.py`,
   `tests/`, and workflow markdown files only.
2. Preserve real source-anchor radial shape in the covered seam before local
   SVD inputs are constructed.
3. Keep the ownership seam unchanged: graph/topology is the source of truth,
   builder owns semantics, optimizer consumes compiled semantics, framework
   remains role-agnostic.
4. Keep the compatibility statement explicit: backward compatibility remains
   required, but compatibility behavior is not the semantic source of truth.
5. Confirm semantics still precede geometry and null edge remains distinct from
   zero-length real edge.
6. Stop immediately if the work widens into target pseudo-anchor redesign,
   downstream stage guarding, framework changes, graph grammar changes, or
   broad optimizer-flow redesign.
7. After Phase 2 implementation is complete, run the checklist review, update
   `STATUS.md` for the next phase handoff, and append `WORKLOG.md`.

## Invariants

1. Graph/topology remains the source of truth.
2. Builder owns semantic interpretation.
3. Optimizer consumes compiled semantics.
4. Framework remains role-agnostic.
5. Backward compatibility must be preserved.
6. Semantics must precede geometry.
7. Null edge remains distinct from zero-length real edge.
8. No broad redesign is allowed.
