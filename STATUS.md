## Workflow Status

- Phase: Phase 7
- Checkpoint: workflow-complete
- Status: COMPLETED
- Next step: done
- Last update: 2026-03-16

## Branch

svd-anchor-shape-stabilization

## Objective

Stabilize role-aware rotation initialization by correcting the geometry used
during SVD anchor alignment and by preventing downstream optimizer stages from
degrading already-valid semantic seed rotations in covered cases.

## Current Focus

All planned branch phases are complete.
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
Phase 7 closed the bounded regression/debug seam only:
the executor stayed inside `tests/test_core_optimizer.py`, workflow markdown
files, and `src/mofbuilder/core/optimizer.py` only where the already-covered
`ROLE-AWARE` seam exposed bounded inspectable debug/failure behavior.
The audited Phase 7 targets were
`NetOptimizer._compile_role_aware_initial_rotations`,
`NetOptimizer._build_guarded_debug_record`,
`NetOptimizer._build_guarded_fallback_debug_records`, and
`NetOptimizer.place_edge_in_net`, with final hardening limited to covered
typed rollout coverage, explicit legacy literal-`X` fallback coverage, mixed
typed resolved-anchor source coverage, and honest unsupported-case handoff
notes.
The bounded Phase 7 seam is now closed without widening rollout scope:
`tests/test_core_optimizer.py` already covers one covered typed
shape-preserving rollout case, one explicit legacy literal-`X` compatibility
fallback case, one mixed typed resolved-anchor source placement case, and the
bounded missing-input error paths for role-aware placement.
`src/mofbuilder/core/optimizer.py` already exposes the bounded inspectable
status, fallback-reason, guard-reason, pair-count, and missing-input failure
surfaces allowed for this phase, so no additional optimizer rollout changes
were required.
Unsupported cases remain documented honestly and unchanged:
legacy literal-`X`, missing-shape, missing-target-direction,
unsupported-family, and missing resolved-anchor metadata cases stay on their
explicit fallback or error paths.

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

1. Phase 7 executor work is complete.
2. The covered rollout remains limited to the bounded `ROLE-AWARE` seam.
3. Ownership boundaries remain unchanged:
   graph/topology is the source of truth, builder owns semantics, optimizer
   consumes compiled semantics, and framework remains role-agnostic.
4. The semantic/geometry contract remains unchanged:
   semantics precede geometry, null edge remains distinct from zero-length real
   edge, and backward compatibility remains required but is not the semantic
   source of truth.
5. Unsupported or compatibility cases remain explicit and bounded:
   legacy literal-`X`, missing-shape, missing-target-direction,
   unsupported-family, and missing resolved-anchor metadata cases stay on their
   existing fallback or error paths.
6. No further executor phase remains on this branch workflow.

## Invariants

1. Graph/topology remains the source of truth.
2. Builder owns semantic interpretation.
3. Optimizer consumes compiled semantics.
4. Framework remains role-agnostic.
5. Backward compatibility must be preserved.
6. Semantics must precede geometry.
7. Null edge remains distinct from zero-length real edge.
8. No broad redesign is allowed.
