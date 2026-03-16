## Workflow Status

- Phase: Phase 1
- Checkpoint: phase-1-entry
- Status: READY
- Next step: planner
- Last update: TBD

## Branch

svd-anchor-shape-stabilization

## Objective

Stabilize role-aware rotation initialization by correcting the geometry used
during SVD anchor alignment and by preventing downstream optimizer stages from
degrading already-valid semantic seed rotations in covered cases.

## Current Focus

Phase 1 is not implementation work.
This phase defines the anchor-geometry contract, the ownership seam, the
forbidden uniform-radius flattening behavior, and the phase-bounded workflow
rules for the rest of the branch.

## Executor Handoff

1. Phase 1 is documentation-only.
2. Planner must generate a bounded Phase 1 plan only.
3. Executor must update control docs only.
4. No production code, tests, runtime payloads, or workflow automation code
   may change in Phase 1.

## Invariants

1. Graph/topology remains the source of truth.
2. Builder owns semantic interpretation.
3. Optimizer consumes compiled semantics.
4. Framework remains role-agnostic.
5. Backward compatibility must be preserved.
6. Semantics must precede geometry.
7. Null edge remains distinct from zero-length real edge.
8. No broad redesign is allowed.
