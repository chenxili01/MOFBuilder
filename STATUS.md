# STATUS.md

## Workflow Status

- Phase: Phase 4
- Checkpoint: phase-4-executor-implemented
- Status: COMPLETED_PENDING_PLANNER
- Next step: Planner reviews completion and decides whether to advance
- Last update: 2026-03-14

## Branch

optimizer-reconstruction

## Objective

Reconstruct the optimizer / rotation logic so local placement is driven by the completed snapshot contract from the `role-runtime-contract` branch, using semantics-first legality, node-local contract compilation, SVD/Kabsch initialization, and constrained refinement while preserving the legacy optimizer path initially.

## Current Focus

Phase 4 executor work is complete and pending planner review. The implemented scope adds a passive optimizer-owned ambiguity layer that enumerates only legal correspondence candidates, runs SVD/Kabsch for each legal candidate, scores candidates by post-legality rigid-fit signals with deterministic tie breaking, and selects the best legal result for representative ambiguity and single-candidate cases. Scope remained limited to optimizer-owned modules and tests; no builder changes, framework changes, broad optimizer-loop changes, local refinement, guarded integration wiring, or legacy-path replacement were introduced.

## Invariants

1. Topology graph remains the source of truth.
2. Builder owns role interpretation and snapshot compilation.
3. Optimizer consumes the narrowed snapshot seam rather than arbitrary builder internals.
4. Framework remains role-agnostic in this branch.
5. Backward compatibility must be preserved.
6. Primitive-first optimization must be preserved.
7. Null-edge semantics must remain consistent with the checkpoints.
8. Bundle ownership and resolver boundaries must remain consistent with the checkpoints.
9. Snapshots remain derived API views, not new sources of truth.
10. Semantics must determine legality before geometry.
