## Workflow Status

- Phase: Phase 1
- Checkpoint: phase-1-entry
- Status: READY
- Next step: planner
- Last update: TBD

## Branch

svd-anchor-shape-stabilization

## Objective

Stabilize SVD rotation initialization by preserving anchor geometry shape
and preventing optimizer stages from degrading valid role-aware alignment.

## Invariants

Graph is source of truth.
Builder owns semantics.
Optimizer consumes compiled anchors.
Framework remains role-agnostic.
Null edges remain distinct from zero-length edges.
