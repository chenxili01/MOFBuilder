## Workflow Status

- Phase: Phase 6
- Checkpoint: phase-6-complete
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

Phase 6 is complete.
`src/mofbuilder/core/optimizer_contract.py` now evaluates bounded
shape-preserving rollout eligibility before covered role-aware initialization:
the rollout remains limited to the already-supported `ROLE-AWARE` family seam,
and it requires builder-compiled `source_anchor_vector`,
`target_anchor_direction`, and `slot_radius` semantics on covered
orientation-only assignments.
`src/mofbuilder/core/optimizer.py` now keeps legacy literal-`X`,
missing-shape, missing-target-direction, and unsupported-family cases on an
explicit compatibility fallback path instead of letting them silently enter the
covered shape-preserving rollout, and the Phase 5 seed-preservation guard no
longer treats unsupported rollout seeds as covered.
`tests/test_core_optimizer.py` now locks down one supported covered rollout
case and one explicit legacy literal-`X` fallback case.
Phase 7 remains pending for broader regression/debug expansion only.

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

1. Planner must prepare Phase 7 only.
2. Keep Phase 7 bounded to `tests/`, workflow markdown files, and
   `src/mofbuilder/core/optimizer.py` only if a narrow explicit debug or
   failure surface is required.
3. Preserve the ownership seam unchanged:
   graph/topology is the source of truth, builder owns semantics, optimizer
   consumes compiled semantics, framework remains role-agnostic.
4. Preserve the semantic/geometry contract:
   semantics still precede geometry, null edge remains distinct from
   zero-length real edge, and backward compatibility remains required but is
   not the semantic source of truth.
5. Keep supported versus unsupported rollout coverage documented honestly:
   covered rollout remains limited to the bounded `ROLE-AWARE` seam, while
   legacy literal-`X`, missing-shape, missing-target-direction, and
   unsupported-family cases remain explicit compatibility fallbacks.
6. Add only bounded Phase 7 regression coverage, inspectable debug/failure
   surfaces, and handoff notes; do not widen rollout scope or introduce new
   family support.

## Invariants

1. Graph/topology remains the source of truth.
2. Builder owns semantic interpretation.
3. Optimizer consumes compiled semantics.
4. Framework remains role-agnostic.
5. Backward compatibility must be preserved.
6. Semantics must precede geometry.
7. Null edge remains distinct from zero-length real edge.
8. No broad redesign is allowed.
