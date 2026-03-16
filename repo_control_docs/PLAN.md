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
- maintain vector extraction compatibility

Not doing:
- semantic placement

---

### Phase 3 — Slot-Aware Placement

Goal:
Resolve attachment slots using metadata.

Scope:
- placement lookup logic

Not doing:
- topology redesign

---

## Stop Rule

Execution must stop if:

- architecture boundaries would change
- semantic ownership moves into optimizer
- flat anchor interface would be removed
