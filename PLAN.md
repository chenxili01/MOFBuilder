# PLAN.md

## Branch Objective

Introduce typed attachment-slot preservation while maintaining the legacy flat anchor interface.

Goal:
- preserve slot identity across builder → optimizer → placement
- maintain backward compatibility

---

## Architectural Invariants

The following must remain unchanged:

- graph topology remains the connectivity authority
- builder produces semantic structures
- optimizer consumes geometry
- placement resolves semantics

Flat anchor representation must remain available.

---

## Ownership Rules

Ownership is strict:

```
Graph      → topology structure
Builder    → semantic compilation
Optimizer  → geometric alignment
Framework  → final assembly
```

Modules must not assume responsibilities outside their ownership.

---

## Design Rules

Required structures:

```
node_X_pos_dict           (legacy flat anchors)
node_attachment_metadata  (typed slot metadata)
node_attachment_lookup    (semantic lookup)
```

Semantic metadata must map directly to flattened geometry rows.

---

## Phases

### Phase 1 — Metadata Preservation

Goal:
Preserve slot identity during builder processing.

Scope:
- create metadata structures
- attach slot metadata to nodes

Not doing:
- optimizer changes

---

### Phase 2 — Optimizer Compatibility

Goal:
Ensure optimizer consumes flat anchors while metadata persists.

Scope:
- normalize optimizer fragment payload preparation so heterogeneous typed attachment
  tables still compile into the legacy flat anchor arrays consumed by rotation,
  cell, and target-length optimization
- preserve flattened row ordering between builder-owned attachment metadata and
  optimizer-generated attachment position dictionaries
- keep optimizer geometry operations role-agnostic while allowing passive
  metadata-derived lookup construction to survive scaling and rotation

Not doing:
- semantic placement changes
- builder metadata schema changes
- topology redesign

Execution notes:
- `node_X_pos_dict` remains the optimizer compatibility contract
- typed attachment tables are only an upstream source for compiling stable flat
  anchor rows
- legacy `X`-only inputs must keep their current fallback behavior

---

### Phase 3 — Slot-Aware Placement

Goal:
Resolve attachment slots during role-aware local placement using builder-defined
semantic records while preserving the legacy flat-anchor optimizer pipeline.

Scope:
- compile node-local placement contracts from semantic snapshot records
- derive deterministic edge-to-slot correspondences for heterogeneous nodes
- feed selected correspondences into guarded local rigid initialization and
  constrained refinement for supported placement paths
- preserve explicit fallback behavior when slot-aware placement is unavailable

Not doing:
- builder metadata schema changes
- optimizer flat-anchor preparation changes
- topology redesign
- framework assembly redesign

Execution notes:
- placement must consume builder-owned `slot_rules`, `node_attachment_lookup`,
  and graph `slot_index` metadata without reassigning semantic ownership
- graph `slot_index` remains the attachment-incidence authority
- `node_X_pos_dict` and the legacy non-role-aware optimizer path must remain
  available

---

## Stop Rule

Execution must stop if:

- architecture boundaries would change
- semantic ownership moves into optimizer
- flat anchor interface would be removed
