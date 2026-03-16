## Workflow Status

- Phase: Phase 4
- Checkpoint: phase-4-ready
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

Phase 3 is complete.
Covered orientation-only pair construction in
`src/mofbuilder/core/optimizer_contract.py` now preserves the real
`source_anchor_vector` and matching `slot_radius` when building each
`shape-preserving pseudo anchor`, while keeping the
`legacy uniform-scale orientation proxy` as an explicit fallback only when
source-shape data is unavailable.
Phase 4 is now planned and ready for execution.
The active handoff is limited to the covered local rigid/SVD initialization
path in `src/mofbuilder/core/optimizer_contract.py` and
`src/mofbuilder/core/optimizer.py`, where the new shape-preserving orientation
pairs must be consumed directly to stabilize the bounded `role-aware seed rotation`
path without widening into downstream guarding.

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

1. Stay within Phase 4 only. Allowed files are
   `src/mofbuilder/core/optimizer.py`,
   `src/mofbuilder/core/optimizer_contract.py`,
   `tests/`, and workflow markdown files only.
2. Audit the covered local rigid/SVD initialization path first:
   `compile_local_rigid_initialization`,
   `_fit_rotation_from_point_pairs`, and the immediate local-seed consumer path
   in `src/mofbuilder/core/optimizer.py`.
   Do not widen into builder changes, framework changes, global candidate
   ranking, or downstream refinement guarding.
3. Ensure the covered SVD input cloud consumes the Phase 3
   `shape-preserving pseudo anchor` pairs together with the preserved real
   source-anchor geometry so the bounded local initialization uses direction
   plus source-shape geometry directly.
4. Keep compatibility behavior explicit and bounded.
   Backward compatibility remains required, but compatibility behavior is not
   the semantic source of truth.
5. Extend only the bounded regression coverage for this phase.
   Update `tests/test_core_optimizer.py` with one stable typed/shape-aware
   initialization case that proves the covered local SVD path consumes the
   shape-preserving orientation inputs.
6. Keep the ownership seam unchanged throughout:
   graph/topology is the source of truth, builder owns semantics, optimizer
   consumes compiled semantics, framework remains role-agnostic.
   Semantics still precede geometry, and null edge remains distinct from
   zero-length real edge.
7. Stop immediately once covered local rigid/SVD initialization consumes
   direction plus source-shape geometry in the bounded seam and the regression
   coverage is updated.
   Do not widen into Phase 5 downstream guarding, framework changes, graph
   grammar changes, or broad optimizer-pipeline redesign.

## Invariants

1. Graph/topology remains the source of truth.
2. Builder owns semantic interpretation.
3. Optimizer consumes compiled semantics.
4. Framework remains role-agnostic.
5. Backward compatibility must be preserved.
6. Semantics must precede geometry.
7. Null edge remains distinct from zero-length real edge.
8. No broad redesign is allowed.
