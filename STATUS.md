## Workflow Status

- Phase: Phase 3
- Checkpoint: phase-3-ready-for-execution
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

Phase 2 is complete.
Builder-owned semantics now preserve the real `source_anchor_vector` and
derived `slot_radius` on resolved slot rules, incident edge constraints, and
edge metadata while keeping existing `anchor_vector` payloads and legacy
literal-`X` compatibility explicit.
The active handoff is now Phase 3, which replaces the covered legacy
uniform-scale orientation proxy with shape-preserving pseudo-anchor
construction when source-shape data is available.

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

1. Stay within Phase 3 only. Allowed files are
   `src/mofbuilder/core/optimizer.py`,
   `src/mofbuilder/core/optimizer_contract.py`,
   `src/mofbuilder/core/builder.py`,
   `tests/`, and workflow markdown files only.
2. Audit the covered orientation-pair construction paths and replace the
   covered `legacy uniform-scale orientation proxy` with shape-preserving
   pseudo-anchor construction.
3. Use the preserved `source_anchor_vector` and `slot_radius` from Phase 2 to
   construct target-side pseudo anchors from `target_anchor_direction` without
   flattening all covered slots to one shared scale.
4. Keep fallback explicit and bounded when source-shape data is absent;
   backward compatibility remains required, but compatibility behavior is not
   the semantic source of truth.
5. Keep the ownership seam unchanged: graph/topology is the source of truth,
   builder owns semantics, optimizer consumes compiled semantics, framework
   remains role-agnostic.
6. Confirm semantics still precede geometry and null edge remains distinct from
   zero-length real edge.
7. Stop immediately if the work widens into downstream optimizer guarding,
   framework changes, graph grammar changes, or broad optimizer redesign.

## Invariants

1. Graph/topology remains the source of truth.
2. Builder owns semantic interpretation.
3. Optimizer consumes compiled semantics.
4. Framework remains role-agnostic.
5. Backward compatibility must be preserved.
6. Semantics must precede geometry.
7. Null edge remains distinct from zero-length real edge.
8. No broad redesign is allowed.
