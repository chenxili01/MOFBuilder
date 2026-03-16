## Purpose

Defines implementation boundaries for each phase described in PLAN.md.

Each phase specifies:

Allowed modules
Required work
Forbidden changes
Completion criteria

Executor must stop immediately when the active phase completion criteria are satisfied.

---

# Global Rules

Default allowed production modules:

optimizer.py
optimizer_contract.py
builder.py
tests/
workflow markdown files

Do not modify unless the phase explicitly allows it:

framework behavior
FrameNet graph stamping
graph grammar
supercell expansion behavior
writer/export behavior
run_auto.py

Do not change:

existing ownership boundaries
primitive-first optimization order
snapshot ownership boundaries
role-agnostic framework contract

---

# Phase 1 — Anchor Geometry Contract

## Allowed Modules

workflow markdown files

## Required Work

- Define the branch objective and anchor-geometry failure class.
- Record required terminology:
  `source_anchor_vector`,
  `target_anchor_direction`,
  `slot_radius`,
  `shape-preserving pseudo anchor`,
  `role-aware seed rotation`,
  `legacy uniform-scale orientation proxy`.
- Document the ownership seam:
  graph/topology as source of truth,
  builder owns semantics,
  optimizer consumes compiled semantics.
- State directly that semantics precede geometry.
- State directly that null edge remains distinct from zero-length real edge.

## Forbidden Changes

Do not modify production code, tests, runtime payloads, or workflow automation code.

## Completion Criteria

control docs are initialized
ownership boundaries are explicit
failure class is named directly
future-phase work is not implied as already implemented

---

# Phase 2 — Source Anchor Shape Preservation

## Allowed Modules

builder.py
optimizer.py
tests/
workflow markdown files

## Required Work

- Audit the covered source-anchor surfaces used for local SVD inputs.
- Preserve real source-anchor radial shape instead of flattening slot radii too early.
- Ensure source-anchor shape remains available to the local alignment path.
- Add bounded tests for one shape-preserved case and one compatibility case.

## Forbidden Changes

Do not modify framework, graph grammar, supercell behavior, or broad optimizer flow.

## Completion Criteria

source-anchor shape survives into the covered local alignment seam
compatibility behavior remains explicit and preserved

---

# Phase 3 — Orientation Pair Construction Fix

## Allowed Modules

optimizer.py
optimizer_contract.py
builder.py
tests/
workflow markdown files

## Required Work

- Replace uniform-radius orientation-only pseudo-anchor construction in the covered seam.
- Construct target-side pseudo anchors from target direction using the corresponding source-side radius/shape.
- Preserve compatibility fallback only where source-shape data is unavailable.
- Add bounded tests covering one per-slot-radius case and one fallback case.

## Forbidden Changes

Do not redesign builder ownership, framework behavior, or global optimizer architecture.

## Completion Criteria

orientation-pair construction preserves per-slot radius/shape
uniform-scale flattening is no longer the covered default path

---

# Phase 4 — SVD Initialization Stabilization

## Allowed Modules

optimizer.py
optimizer_contract.py
tests/
workflow markdown files

## Required Work

- Update local rigid/SVD initialization to consume shape-preserving anchors.
- Keep ambiguity resolution and candidate selection bounded to the covered seam.
- Add bounded tests for one stable typed/shape-aware initialization case.
- Keep compatibility behavior explicit.

## Forbidden Changes

Do not redesign the full optimizer pipeline or widen into later-stage guarding.

## Completion Criteria

covered SVD initialization consumes direction plus source-shape geometry
role-aware seed generation is more stable and inspectable in the covered seam

---

# Phase 5 — Optimizer Stage Guarding

## Allowed Modules

optimizer.py
tests/
workflow markdown files

## Required Work

- Audit covered downstream refinement stages that can degrade valid semantic seed rotations.
- Add narrow guarding or skip/freeze behavior for covered semantic-anchor cases only.
- Preserve backward compatibility and bounded rollout.
- Add bounded tests for one valid-seed-preservation case.

## Forbidden Changes

Do not redesign the global optimizer objective, framework, or pipeline order.

## Completion Criteria

covered valid semantic seeds are not degraded by downstream refinement in the bounded seam
guard behavior is explicit, narrow, and documented honestly

---

# Phase 6 — Compatibility Layer and Guarded Rollout

## Allowed Modules

optimizer.py
optimizer_contract.py
builder.py
tests/
workflow markdown files

## Required Work

- Keep legacy literal-X and already-supported families working.
- Add any necessary bounded rollout guards for the new shape-preserving path.
- Document supported versus unsupported families honestly.
- Add bounded compatibility tests.

## Forbidden Changes

Do not remove legacy paths broadly or widen rollout beyond the covered seam.

## Completion Criteria

compatibility remains preserved
rollout is explicit, bounded, and documented honestly

---

# Phase 7 — Regression Coverage, Debug Surfaces, and Handoff

## Allowed Modules

tests/
workflow markdown files
optimizer.py only if a bounded explicit debug/error surface is required

## Required Work

- Add regression coverage for covered legacy, typed, and mixed-source cases.
- Add explicit debug/failure surfaces where helpful and bounded.
- Document remaining unsupported cases honestly.
- Finalize handoff state.

## Forbidden Changes

Do not widen architecture scope, ownership boundaries, or rollout scope.

## Completion Criteria

regression coverage exists for the covered seam
remaining gaps are documented honestly
handoff state is clear
