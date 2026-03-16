# PHASE_SPEC.md

## Phase 1 — Metadata Preservation

### Allowed Modules

- builder
- attachment metadata structures

### Required Work

- implement slot metadata structure
- map metadata rows to flattened anchor indices
- preserve slot ordering

### Forbidden Changes

- optimizer modification
- topology schema changes
- removal of flat anchors

### Completion Criteria

- metadata exists for every attachment slot
- metadata row indices align with flat anchors
- existing builds remain functional

---

## Phase 2 — Optimizer Compatibility

### Allowed Modules

- optimizer input preparation
- vector extraction utilities

### Required Work

- ensure optimizer receives flat anchors
- preserve compatibility with metadata

### Forbidden Changes

- semantic decision logic inside optimizer
- topology changes

### Completion Criteria

- optimizer runs without shape mismatches
- metadata structures remain intact

---

## Phase 3 — Slot-Aware Placement

### Allowed Modules

- placement logic

### Required Work

- resolve anchors using slot metadata
- map placement edges to slot identity

### Forbidden Changes

- altering builder semantics
- modifying optimizer geometry pipeline

### Completion Criteria

- heterogeneous anchor nodes place correctly
- slot identity preserved during placement
