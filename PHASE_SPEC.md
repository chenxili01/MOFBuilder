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

- `src/mofbuilder/core/optimizer_contract.py`
- `src/mofbuilder/core/optimizer.py`
- `tests/test_core_optimizer.py`

### Phase Goal

Resolve node-edge placement correspondences by slot identity using the semantic
snapshot produced upstream, while keeping the optimizer's flat-anchor geometry
contract unchanged.

### Inputs Assumed Complete

- builder snapshot records already carry resolved `slot_rules`
- graph edge records already carry stable `slot_index` maps
- optimizer payload preparation already preserves flattened attachment row order
  and rotated attachment lookup alignment
- legacy flat-anchor interfaces remain available through `node_X_pos_dict`

### Required Work

- compile node placement contracts directly from semantic snapshot node and edge
  records without redefining builder semantics inside optimizer
- match incident edges to node slots using builder-defined slot identity and
  graph-owned `slot_index` data, while respecting endpoint side, resolve mode,
  null-edge policy, and bundle ordering hints
- enumerate legal node correspondences deterministically and preserve stable
  ambiguity tie-breaking for multi-slot heterogeneous nodes
- build local rigid initialization and constrained refinement from the selected
  slot mapping using explicit source/target anchor or direction metadata
- keep guarded role-aware local placement opt-in and preserve clean fallback
  behavior for unsupported roles, missing semantic snapshots, legacy literal
  `X` compatibility, and other non-slot-aware cases
- expose debug records that explain whether slot-aware placement selected a
  semantic pose or fell back to legacy behavior

### Expected Touchpoints

- `compile_node_placement_contract()`
- `compile_legal_node_correspondences()`
- `compile_local_rigid_initialization()`
- `compile_discrete_ambiguity_resolution()`
- `compile_local_constrained_refinement()`
- `_compile_role_aware_initial_rotations()`
- `_select_guarded_role_aware_local_placement()`
- `_build_guarded_debug_record()`

### Forbidden Changes

- builder metadata schema changes
- optimizer fragment flattening or `node_X_pos_dict` contract changes
- topology ordering or graph slot-index generation changes
- framework assembly or write-path changes
- moving semantic ownership from builder into optimizer
- moving topology ownership away from graph

### Completion Criteria

- role-aware placement selects slot-consistent correspondences for supported
  heterogeneous nodes using builder-provided semantics
- ambiguous slot mappings resolve deterministically without count or shape
  mismatches in the guarded placement path
- guarded fallback preserves legacy behavior when slot-aware placement is
  disabled, unsupported, or semantically incomplete
- Phase 2 flat-anchor compatibility and row-order guarantees remain unchanged

### Validation Requirements

- targeted tests cover contract compilation from `slot_rules`, `slot_index`,
  and edge metadata target-anchor payloads
- targeted tests cover legal correspondence enumeration for heterogeneous slot
  types, endpoint-side constraints, and bundle-ordered cases
- targeted tests cover rigid initialization and constrained refinement using the
  selected slot mapping
- targeted tests cover guarded fallback reasons for disabled placement, missing
  semantic snapshot, unsupported role classes, and legacy literal `X`
  compatibility
