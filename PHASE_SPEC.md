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

- `src/mofbuilder/core/optimizer.py`
- optimizer input preparation helpers
- vector extraction and position-dictionary utilities
- `tests/test_core_optimizer.py`

### Phase Goal

Keep the optimizer's geometry pipeline on the legacy flat-anchor interface while
accepting builder-produced typed attachment tables as a compatibility-preserving
input source.

### Inputs Assumed Complete

- builder now emits `node_attachment_metadata`
- builder now emits `node_attachment_lookup`
- builder preserves flattened attachment row ordering for each role payload

### Required Work

- ensure fragment payload compilation continues to produce flat `x_coords`
  arrays for every optimizer node/edge path, even when the upstream source is
  heterogeneous typed attachment tables
- preserve row-order alignment between typed attachment metadata and any
  optimizer-generated attachment position dictionaries or rotated attachment
  lookups
- maintain fallback behavior for legacy `X`-only payloads so pre-existing
  optimizer flows still run without typed metadata requirements
- verify that rotation, cell optimization, target-edge-length calculation, and
  related vector extraction paths do not introduce shape or count mismatches
  when heterogeneous attachment inputs are present

### Expected Touchpoints

- `_fragment_payload_from_arrays()`
- `_resolve_attachment_coords_by_type()`
- `_flatten_attachment_coords()`
- `_generate_pos_dict()`
- `_generate_attachment_position_dict()`
- `_build_attachment_lookup_from_positions()`
- targeted optimizer tests covering heterogeneous typed attachments and legacy
  flat-anchor fallback

### Forbidden Changes

- semantic decision logic inside optimizer
- slot-resolution or placement-policy changes
- builder or topology schema changes
- topology changes
- removal or renaming of `node_X_pos_dict`
- moving semantic ownership from builder into optimizer

### Completion Criteria

- optimizer preparation accepts heterogeneous typed attachments without vector
  count or shape mismatches
- flattened optimizer anchor rows remain aligned with builder-defined metadata
  ordering
- legacy flat-anchor inputs still produce the same optimizer-facing interface
- metadata remains passive compatibility context; optimizer geometry ownership is
  unchanged

### Validation Requirements

- targeted tests cover typed attachment flattening order
- targeted tests cover legacy `X` fallback compatibility
- targeted tests cover rotated attachment lookup row alignment without requiring
  Phase 3 placement changes

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
