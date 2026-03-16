## Workflow

Agents:

Planner
Executor

No reviewer role.

Planner produces a single-phase implementation-ready plan.
Executor implements one phase only.

Executor must self-check with CHECKLIST.md.

Executor must update:

STATUS.md
WORKLOG.md

after every completed phase.

---

# Branch Objective

Branch:

svd-anchor-shape-stabilization

Goal:

Stabilize role-aware rotation initialization by correcting the geometry
representation used during SVD alignment and by preventing downstream optimizer
stages from degrading already-valid semantic seed rotations in covered cases.

Anchor-geometry failure class:

valid role-aware source-anchor geometry must not be flattened into a
uniform-radius orientation proxy before covered SVD initialization, and valid
semantic seed rotations must not be degraded afterward by geometry-only
refinement stages that do not preserve the same semantic objective.

Required terminology for this branch:

- `source_anchor_vector`
- `target_anchor_direction`
- `slot_radius`
- `shape-preserving pseudo anchor`
- `role-aware seed rotation`
- `legacy uniform-scale orientation proxy`

This branch must implement the agreed bounded flow:

source-anchor shape preservation
→ shape-preserving orientation-pair construction
→ stable local SVD initialization
→ guarded downstream refinement for covered semantic cases
→ bounded compatibility and regression hardening

This branch must not redesign builder ownership, graph semantics, framework
ownership, or the global optimizer pipeline.

---

# Upstream Branch Baseline

This branch reuses the same development routine that worked in the completed
prior branch workflow:

- Planner / Executor split only
- planner is planning-only
- executor is implementation-only
- executor implements one phase only
- explicit phase roadmap in PLAN.md
- hard module boundaries in PHASE_SPEC.md
- append-only WORKLOG.md
- explicit STATUS.md handoff after planner and executor steps
- conservative architectural invariants and stop rules

The new branch changes the problem target, not the workflow discipline.

---

# Architectural Invariants

Must not change:

graph/topology as source of truth
builder owns semantics
optimizer consumes compiled semantics
framework remains role-agnostic
backward compatibility preserved
semantics before geometry
null edge distinct from zero-length real edge
primitive-first optimization preserved
snapshots remain derived views, not new sources of truth

This branch is a semantic/geometry seam stabilization, not a pipeline redesign.

---

# Core Design Rules

## 1. Graph/topology remains the source of truth

Semantic legality and role/path meaning originate from graph/topology and the
builder-owned interpretation layer, not from downstream geometry heuristics.

## 2. Builder owns semantics

Builder remains the only owner of semantic interpretation and compiled anchor
meaning. Optimizer consumes compiled semantics only.

## 2a. Framework remains role-agnostic

Framework behavior remains role-agnostic and must not become a semantic source
of truth for anchor legality, role meaning, or compatibility interpretation.

## 3. Semantics before geometry

Geometry may refine already-legal semantic placements, but geometry must not
replace semantic legality or flatten valid semantic anchor structure prematurely.

## 4. Source-anchor shape must be preserved

When the covered seam requires local SVD alignment, the real source-anchor
radius/shape must remain available. Orientation-only alignment must not default
to a uniform-radius proxy when source-shape information exists.

Required compatibility rule:

backward compatibility remains required, but compatibility behavior is not the
semantic source of truth.

## 5. No broad redesign

The branch may harden the covered seam only. It must not widen into framework
redesign, graph grammar changes, supercell redesign, or a full optimizer rewrite.

---

# Phase Roadmap

Executor implements phases sequentially.

# Phase 1 — Anchor Geometry Contract

Define the anchor-geometry contract, required terminology, ownership seam, and
forbidden flattening behavior.

Primary goal:

name the failure class explicitly and freeze the semantic/geometry seam

This phase is documentation-only.

Execution plan for this phase only:

1. Update the control docs so the branch objective, anchor-geometry failure
   class, and builder/optimizer ownership seam are stated directly.
2. Record the required terminology:
   `source_anchor_vector`,
   `target_anchor_direction`,
   `slot_radius`,
   `shape-preserving pseudo anchor`,
   `role-aware seed rotation`,
   `legacy uniform-scale orientation proxy`.
3. Document the forbidden behavior directly:
   valid source-anchor geometry must not be flattened into a uniform-radius
   orientation proxy before covered SVD initialization.
4. Freeze the ownership seam:
   graph/topology remains source of truth, builder owns semantics, optimizer
   consumes compiled semantics, framework remains role-agnostic.
5. Keep Phase 1 documentation-only:
   no production code, tests, runtime payloads, or workflow automation changes.

Executor handoff constraints:

- Allowed files: workflow markdown files only.
- Required outcome: control docs explicitly state the anchor-geometry failure class.
- Required seam statement: graph/topology is source of truth, builder owns semantics,
  optimizer consumes compiled semantics, framework remains role-agnostic.
- Required compatibility statement: backward compatibility remains required, but
  compatibility behavior is not the semantic source of truth.
- Stop rule: stop immediately if Phase 1 would require production code, tests,
  runtime payloads, or workflow automation changes.

Implementation-ready execution checklist for this phase only:

1. Audit the current control docs only:
   `ARCHITECTURE.md`, `PLAN.md`, `PHASE_SPEC.md`, and `STATUS.md`.
2. Update those docs so the same Phase 1 contract appears consistently:
   the branch objective, the anchor-geometry failure class, the required
   terminology list, the forbidden uniform-radius flattening behavior, and the
   ownership seam.
3. State the Phase 1 compatibility rule explicitly in the docs:
   backward compatibility remains required, but compatibility behavior is not
   the semantic source of truth.
4. Confirm the docs state, without ambiguity, that semantics precede geometry
   and that null edge remains distinct from zero-length real edge.
5. Stop after the documentation contract is consistent and future phases are
   still described as pending work rather than implemented behavior.
6. Then run the Phase 1 checklist review, update `STATUS.md` for Phase 1
   completion and Phase 2 readiness, and append `WORKLOG.md` with the bounded
   documentation-only changes.

# Phase 2 — Source Anchor Shape Preservation

Preserve real source-anchor radial shape in the covered seam before local SVD inputs
are constructed.

Primary goal:

stop losing physically distinct slot-radius shape before local alignment

Execution plan for this phase only:

1. Audit the covered builder-owned and optimizer-consumed source-anchor surfaces
   in `src/mofbuilder/core/builder.py` and `src/mofbuilder/core/optimizer.py`
   to identify where real source-anchor vectors already exist and where
   per-slot radius/shape data is dropped before the local alignment seam.
2. Preserve the real `source_anchor_vector` and derived `slot_radius` on the
   covered builder-compiled slot-rule and edge-metadata payloads so
   heterogeneous per-slot radii survive into optimizer-consumable semantics.
3. Keep existing compatibility fields and fallbacks explicit and bounded when
   shape data is absent, including current `anchor_vector` behavior and legacy
   literal-`X` compatibility.
4. Add bounded tests for one heterogeneous-radius shape-preserved case and one
   compatibility case that confirm the preserved source-shape data survives into
   the covered local SVD input seam without changing later-phase behavior.
5. Do not yet replace target-side orientation pseudo-anchor construction, do
   not modify `src/mofbuilder/core/optimizer_contract.py`, and do not add
   downstream optimizer guarding in this phase.

Executor handoff constraints:

- Allowed files: `src/mofbuilder/core/builder.py`,
  `src/mofbuilder/core/optimizer.py`, `tests/`, and workflow markdown files
  only.
- Required audit targets:
  `MetalOrganicFrameworkBuilder._compile_resolved_slot_rules`,
  `MetalOrganicFrameworkBuilder._build_target_anchor_payload`,
  `MetalOrganicFrameworkBuilder._build_graph_edge_records`,
  `NetOptimizer._resolve_semantic_node_anchor_position`, and
  `NetOptimizer._resolve_semantic_edge_anchor_coords`.
- Required outcome: covered source-anchor inputs retain the real
  `source_anchor_vector` and `slot_radius` so the local alignment seam can read
  preserved per-slot shape instead of only a flattened compatibility proxy.
- Required compatibility statement: compatibility fallback remains explicit and
  bounded; backward compatibility remains required, but compatibility behavior
  is not the semantic source of truth.
- Stop rule: stop immediately if the work widens into target pseudo-anchor
  redesign, `optimizer_contract.py` changes, downstream stage guarding,
  framework changes, graph grammar changes, or broad optimizer-flow rollout.

Implementation-ready execution checklist for this phase only:

1. Trace the current covered seam in
   `src/mofbuilder/core/builder.py`,
   `src/mofbuilder/core/optimizer.py`,
   `tests/test_core_builder.py`, and
   `tests/test_core_optimizer.py`.
2. Add only the bounded source-shape fields needed for Phase 2 so builder-owned
   resolved slot rules and edge metadata preserve `source_anchor_vector` and
   `slot_radius` alongside existing compatibility payloads.
3. Keep optimizer ownership unchanged: optimizer consumes the builder-compiled
   shape fields but does not invent new semantic meaning or redesign the local
   orientation-pair construction in this phase.
4. Extend tests with:
   one shape-preservation regression proving heterogeneous slot radii survive
   from builder snapshot compilation into optimizer-consumable semantics, and
   one compatibility regression proving legacy literal-`X` or absent-shape
   fallback remains explicit and unchanged.
5. Validate with targeted Phase 2 coverage only, then stop after the preserved
   source-shape seam is in place and later-phase work is still pending.
6. Then run the checklist review, update `STATUS.md` for Phase 2 completion and
   Phase 3 readiness, and append `WORKLOG.md` with the bounded Phase 2 changes.

# Phase 3 — Orientation Pair Construction Fix

Replace uniform-radius orientation-only pseudo-anchor construction with
shape-preserving pseudo-anchor construction in the covered seam.

Primary goal:

construct target-side pseudo anchors from source-side radius/shape rather than one shared scale

Execution plan for this phase only:

1. Audit covered orientation-pair construction paths.
2. Replace uniform-radius pseudo-anchor construction with source-shape-preserving construction.
3. Keep explicit fallback only when source-shape data is unavailable.
4. Add bounded tests for one per-slot-radius case and one fallback case.
5. Do not yet redesign full SVD candidate ranking or downstream optimizer guarding.

Executor handoff constraints:

- Allowed files: optimizer.py, optimizer_contract.py, builder.py, tests/, workflow markdown files only.
- Required outcome: covered orientation pairs preserve per-slot radius/shape.
- Required compatibility statement: fallback remains explicit and bounded, not universal.
- Stop rule: stop immediately if the work widens into global optimizer redesign,
  framework changes, or later-phase guarding logic.

# Phase 4 — SVD Initialization Stabilization

Update covered local rigid/SVD initialization so it consumes shape-preserving anchors
and produces stable role-aware seed rotations.

Primary goal:

make local SVD consume direction plus source-shape geometry in the covered seam

Execution plan for this phase only:

1. Audit the covered local rigid/SVD initialization path.
2. Ensure the covered SVD input cloud uses shape-preserving anchors.
3. Keep candidate selection and ambiguity resolution bounded to the covered seam.
4. Add bounded tests for one stable typed/shape-aware seed case.
5. Do not yet guard downstream optimizer stages in this phase.

Executor handoff constraints:

- Allowed files: optimizer.py, optimizer_contract.py, tests/, workflow markdown files only.
- Required outcome: covered SVD initialization consumes direction plus source-shape geometry.
- Required compatibility statement: compatibility behavior remains explicit and bounded.
- Stop rule: stop immediately if the work widens into downstream optimizer-stage guarding,
  framework redesign, or global optimizer-objective redesign.

# Phase 5 — Optimizer Stage Guarding

Guard downstream covered refinement stages so they do not degrade already-valid
semantic seed rotations in covered semantic-anchor cases.

Primary goal:

preserve valid semantic seeds during bounded downstream refinement

Execution plan for this phase only:

1. Audit covered downstream refinement stages that can degrade valid semantic seeds.
2. Add narrow guarding, skip, or freeze behavior for covered semantic-anchor cases only.
3. Preserve backward compatibility and bounded rollout.
4. Add bounded tests for one valid-seed-preservation case.
5. Do not redesign the full optimizer objective or widen architecture scope.

Executor handoff constraints:

- Allowed files: optimizer.py, tests/, workflow markdown files only.
- Required outcome: covered valid semantic seeds are not degraded by downstream refinement.
- Required compatibility statement: any guard behavior is explicit, narrow, and documented honestly.
- Stop rule: stop immediately if the work widens into global optimizer-objective redesign,
  framework changes, pipeline reorder, or broad rollout changes.

# Phase 6 — Compatibility Layer and Guarded Rollout

Keep legacy literal-X and already-supported families working while enabling the
shape-preserving SVD path in a bounded, explicit way.

Primary goal:

stabilize rollout without widening scope

Execution plan for this phase only:

1. Keep legacy and already-supported compatibility behavior working.
2. Add any necessary bounded rollout guards for the new shape-preserving path.
3. Document supported versus unsupported coverage honestly.
4. Add bounded compatibility tests.
5. Do not remove broad legacy paths or widen scope beyond the covered seam.

Executor handoff constraints:

- Allowed files: optimizer.py, optimizer_contract.py, builder.py, tests/, workflow markdown files only.
- Required outcome: compatibility remains preserved and rollout is bounded.
- Required compatibility statement: supported versus unsupported cases are documented honestly.
- Stop rule: stop immediately if the work widens into framework redesign, broad legacy-path removal,
  or unbounded rollout expansion.

# Phase 7 — Regression Coverage, Debug Surfaces, and Handoff

Add regression coverage, explicit debug/failure surfaces, and final handoff notes
for the bounded seam.

Primary goal:

finish with inspectable behavior and honest scope docs

Execution plan for this phase only:

1. Add regression coverage for covered legacy, typed, and mixed-source cases.
2. Add explicit bounded debug/failure surfaces where useful.
3. Document unresolved risks and unsupported cases honestly.
4. Finalize handoff notes.
5. Do not widen scope beyond the covered seam.

Executor handoff constraints:

- Allowed files: tests/, workflow markdown files, optimizer.py only if a bounded explicit debug/error surface is required.
- Required outcome: covered seam has regression coverage and inspectable failure behavior.
- Required compatibility statement: remaining unsupported cases are documented honestly.
- Stop rule: stop immediately if the work widens architecture scope, ownership boundaries,
  or rollout scope.

---

# Executor Rules

Executor must:

read PLAN.md
detect current phase from STATUS.md
implement only that phase
self-check with CHECKLIST.md
update STATUS.md
update WORKLOG.md

Executor must not modify architecture outside the active phase.

---

# Stop Rule

Stop immediately if a task requires:

builder semantic ownership redesign
framework semantic redesign
new graph grammar
supercell semantic redesign
deleting compatibility surfaces before covered behavior is proven
changing snapshot ownership ad hoc
broad optimizer rewrite beyond the active phase

Those require explicit replanning.

---

# End of Plan

This branch is successful when:

- valid source-anchor shape is preserved in the covered seam
- orientation pairs stop defaulting to uniform-radius flattening
- covered local SVD initialization becomes more stable and inspectable
- downstream covered refinement preserves already-valid semantic seeds
- compatibility remains preserved
- regression coverage and handoff docs are honest and bounded
