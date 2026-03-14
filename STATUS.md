# STATUS.md

## Workflow Status

- Phase: Phase 7
- Checkpoint: workflow-complete
- Status: COMPLETED
- Next step: done
- Last update: 2026-03-15

## Branch

typed-attachment-hardening

## Objective

Systematically remove hard-coded universal attachment-atom assumptions so fragment loading,
builder/runtime compilation, and optimizer-local placement use typed attachment sources and
resolved anchors rather than a universal literal `X` bucket.

## Current Focus

Phase 7 is complete. The bounded optimizer-local placement seam now has
regression coverage for legacy literal-`X`, typed `XA`, and one supported
mixed-source `XA` + `Al` case, plus explicit failure coverage for missing
semantic snapshot and missing edge-anchor source metadata.

## Executor Handoff

1. Executor completed Phase 7 within the allowed scope:
   tests and workflow markdown files only.
2. The covered seam remains bounded:
   guard-off placement stays legacy literal-`X`,
   guard-enabled placement consumes builder-compiled resolved anchors only,
   and explicit `anchor_source_type == "X"` compatibility remains valid.
3. Added regression coverage for:
   one legacy literal-`X` case,
   one typed `XA` case,
   one mixed-source `XA` + `Al` case,
   one missing-semantic-snapshot failure,
   and one missing edge-anchor source metadata failure.
4. No framework behavior, graph grammar, snapshot ownership, or rollout scope
   was widened in Phase 7.

## Invariants

1. Topology graph remains the source of truth.
2. Builder owns role interpretation and runtime/snapshot compilation.
3. Optimizer consumes compiled attachment semantics rather than inferring role meaning from raw fragment atoms.
4. Framework remains role-agnostic.
5. Backward compatibility must be preserved.
6. Primitive-first optimization must be preserved.
7. Null-edge semantics must remain explicit.
8. Snapshots remain derived API views, not new sources of truth.
9. Slot/path semantics determine legality before geometry.
10. Attachment-source typing must not be collapsed to a universal literal `X` assumption.
