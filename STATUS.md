## Workflow Status

- Phase: Phase 5
- Checkpoint: phase-4-complete
- Status: READY_FOR_PLANNING
- Next step: planner
- Last update: 2026-03-16

## Branch

svd-anchor-shape-stabilization

## Objective

Stabilize role-aware rotation initialization by correcting the geometry used
during SVD anchor alignment and by preventing downstream optimizer stages from
degrading already-valid semantic seed rotations in covered cases.

## Current Focus

Phase 4 is complete.
Covered local rigid/SVD initialization in
`src/mofbuilder/core/optimizer_contract.py` now consumes the preserved
`shape-preserving pseudo anchor` inputs directly in the bounded SVD point-pair
cloud for covered semantic cases, including two-anchor cases where centroid-only
anchor fitting collapses the local rotation cue to a single line.
The covered seam now adds bounded shape-preserving orientation-support pairs
from real `source_anchor_vector` / `slot_radius` geometry when
`target_anchor_direction` data exists, keeps the
`legacy uniform-scale orientation proxy` explicit only for covered
orientation-only compatibility fallback, and exposes the local SVD composition
through rigid-init/debug metadata without widening into downstream guarding.
`tests/test_core_optimizer.py` now includes a stable typed/shape-aware local
seed regression for this bounded seam.
Phase 5 downstream refinement guarding remains pending and has not yet been
implemented.

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

## Next Step

1. Planner must prepare the Phase 5 handoff only.
2. The next bounded target is downstream optimizer-stage guarding for covered
   semantic seed rotations in `src/mofbuilder/core/optimizer.py`, `tests/`,
   and workflow markdown files only.
3. Do not reopen builder ownership, framework behavior, graph grammar, global
   candidate ranking, or broad optimizer-pipeline redesign while planning the
   next phase.
4. Keep the ownership seam unchanged:
   graph/topology is the source of truth, builder owns semantics, optimizer
   consumes compiled semantics, framework remains role-agnostic.
   Semantics still precede geometry, null edge remains distinct from
   zero-length real edge, and backward compatibility remains required but is
   not the semantic source of truth.

## Invariants

1. Graph/topology remains the source of truth.
2. Builder owns semantic interpretation.
3. Optimizer consumes compiled semantics.
4. Framework remains role-agnostic.
5. Backward compatibility must be preserved.
6. Semantics must precede geometry.
7. Null edge remains distinct from zero-length real edge.
8. No broad redesign is allowed.
