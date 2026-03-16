# Workflow

Agents:

Planner
Executor

Planner produces phase plan only.
Executor performs implementation.

Executor must:

- implement ONE phase only
- self-check with CHECKLIST.md
- update STATUS.md
- append WORKLOG.md entry

No reviewer role.

---

# Branch

svd-anchor-shape-stabilization

---

# Branch Objective

Stabilize role-aware rotation initialization by correcting anchor geometry
used during SVD alignment and ensuring optimizer stages do not degrade
valid semantic placements.

semantic anchors
→ shape-preserving SVD initialization
→ guarded optimizer refinement
→ stable role-aware alignment

The branch must NOT redesign:

- builder ownership
- graph semantics
- framework assembly
- global optimizer structure.

---

# Architectural Invariants

Graph topology is source of truth.
Builder owns semantic interpretation.
Optimizer consumes compiled semantics.
Framework remains role-agnostic.
Backward compatibility preserved.
Primitive-first optimization preserved.
Slot/path legality precedes geometry.
Null edge distinct from zero-length edge.

---

# Phase Roadmap

Phase 1 — Anchor Geometry Contract
Phase 2 — Source Anchor Shape Preservation
Phase 3 — Orientation Pair Construction Fix
Phase 4 — SVD Initialization Stabilization
Phase 5 — Optimizer Stage Guarding
Phase 6 — Compatibility and Guarded Rollout
Phase 7 — Regression Coverage and Handoff
