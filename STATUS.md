# STATUS.md

## Workflow Status

- Phase: Phase 4
- Checkpoint: phase-4-validation-implemented
- Status: COMPLETED_PENDING_PLANNER
- Next step: Planner reviews completion and decides whether to advance
- Last update: 2026-03-14

## Branch

role-runtime-contract

## Objective

Establish a clean, builder-owned snapshot API that future optimizer/rotation reconstruction can consume safely, without exposing arbitrary mutable builder internals.

## Current Focus

Harden snapshot compilation with focused validation and compatibility tests covering missing role registry data, graph/snapshot consistency, bundle ordering consistency, null-edge rule consistency, legacy/default fallback stability, and allowed empty/partial optional data, without changing optimizer behavior, framework behavior, FrameNet graph stamping, or the build pipeline.

## Invariants

1. Topology graph remains the source of truth.
2. Builder owns role interpretation.
3. Framework remains role-agnostic in this branch.
4. Backward compatibility must be preserved.
5. Primitive-first optimization must be preserved.
6. Null-edge semantics must remain consistent with the checkpoints.
7. Bundle ownership and resolver boundaries must remain consistent with the checkpoints.
8. Snapshots are derived API views, not new sources of truth.
