## Workflow Status

- Phase: Phase 5
- Checkpoint: phase-5-complete
- Status: COMPLETE
- Next step: planner
- Last update: 2026-03-16

## Branch

svd-anchor-shape-stabilization

## Objective

Stabilize role-aware rotation initialization by correcting the geometry used
during SVD anchor alignment and by preventing downstream optimizer stages from
degrading already-valid semantic seed rotations in covered cases.

## Current Focus

Phase 5 is complete.
`src/mofbuilder/core/optimizer.py` now keeps a covered Phase 4
`role-aware seed rotation` when the downstream geometry-only refinement drifts
away from a shape-preserving semantic seed backed by builder-compiled anchor
inputs, while uncovered cases and explicit compatibility fallback cases remain
on the downstream refinement path.
The covered guard is narrow: it applies only when the rigid seed carries
`shape-preserving pseudo anchor` support and does not depend on the
`legacy uniform-scale orientation proxy`.
Role-aware debug records now state whether the selected pose came from the
`rigid_seed` or `downstream_refinement`, whether the node was a covered
shape-preserving case, and the bounded guard reason when the seed was
preserved.
`tests/test_core_optimizer.py` now includes a bounded regression that forces a
covered downstream refinement drift and proves the semantic seed is preserved.
The next workflow step is Phase 6 planning only: compatibility-layer and
rollout work must remain bounded, explicit, and separate from this completed
Phase 5 guard.

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

1. Planner must prepare Phase 6 only.
2. Keep Phase 6 bounded to compatibility-layer and rollout behavior in the
   allowed modules named by `PLAN.md` / `PHASE_SPEC.md`.
3. Preserve the ownership seam unchanged:
   graph/topology is the source of truth, builder owns semantics, optimizer
   consumes compiled semantics, framework remains role-agnostic.
4. Preserve the semantic/geometry contract:
   semantics still precede geometry, null edge remains distinct from
   zero-length real edge, and backward compatibility remains required but is
   not the semantic source of truth.
5. Do not reopen Phase 5 implementation work unless a bounded defect is found.

## Invariants

1. Graph/topology remains the source of truth.
2. Builder owns semantic interpretation.
3. Optimizer consumes compiled semantics.
4. Framework remains role-agnostic.
5. Backward compatibility must be preserved.
6. Semantics must precede geometry.
7. Null edge remains distinct from zero-length real edge.
8. No broad redesign is allowed.
