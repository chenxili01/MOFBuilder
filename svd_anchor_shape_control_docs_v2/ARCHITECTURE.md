# SVD Anchor Shape Stabilization Architecture

This branch stabilizes role-aware local rotation initialization by correcting the
geometry representation used during SVD alignment and by preventing downstream
optimizer stages from degrading already-valid semantic placements.

## Branch Contract

The failure class for this branch is explicit:

valid role-aware source-anchor geometry must not be flattened into a uniform-radius
orientation proxy before SVD initialization, and valid semantic seed rotations must
not be degraded afterward by geometry-only refinement stages that do not preserve the
same semantic objective.

The required terminology for this branch is:

- `source_anchor_vector`: the fragment-local anchor vector derived from the real source anchor
- `target_anchor_direction`: the target-side semantic direction compiled from graph/builder semantics
- `slot_radius`: the source-anchor radial distance from the local COM or equivalent local origin
- `shape-preserving pseudo anchor`: a target-side pseudo anchor constructed from target direction
  using the corresponding source-side radius/shape rather than a uniform global scale
- `role-aware seed rotation`: the local rotation produced from builder-compiled semantic anchor inputs
- `legacy uniform-scale orientation proxy`: the prior flattened orientation-only construction where
  source/target directions are normalized and assigned one shared scale

## Ownership Seam

Raw fragment geometry and graph/topology semantics are upstream inputs only.

Builder-owned runtime and snapshot compilation must:

- preserve semantic legality from graph and slot/path rules
- compile optimizer-consumable anchor semantics
- remain the owner of semantic interpretation

Optimizer must:

- consume compiled anchor semantics
- use geometry only after semantic legality is established
- not reinterpret graph legality or builder ownership
- not flatten valid source-anchor geometry when constructing local SVD inputs

## Architectural Invariants

Must remain unchanged:

1. Graph/topology remains the source of truth.
2. Builder owns semantics.
3. Optimizer consumes compiled semantics.
4. Framework remains role-agnostic.
5. Backward compatibility is preserved.
6. Semantics must precede geometry.
7. Null edge remains distinct from zero-length real edge.
8. Primitive-first optimization order remains intact.
9. Snapshots remain derived views, not new sources of truth.
10. No broad redesign is allowed in this branch.

## Branch Scope

This branch is a bounded semantic/geometry seam stabilization only.

It must not redesign:

- framework ownership
- graph grammar
- supercell behavior
- builder ownership
- pipeline order
- global optimizer architecture

Covered concern:

builder-compiled semantic anchors
→ local shape-preserving SVD inputs
→ guarded downstream refinement in covered cases

Not covered here:

- broad optimizer rewrite
- framework redesign
- unbounded rollout to unrelated families
- new sources of truth outside graph/builder ownership
