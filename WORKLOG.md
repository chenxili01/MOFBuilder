# WORKLOG.md

Use this file as the execution log for the multi-role topology effort.
Keep it aligned with `PLANS.md`. Use `STATUS.md` as the live dashboard and this
file as the append-only history.

## Rules

- `PLANS.md` is the frozen roadmap. Do not use this file to redefine phase
  scope.
- One Codex thread should usually touch one phase only.
- Append facts; do not rewrite completed entries except to add a clearly marked
  correction.
- Update the matching checkpoint before starting work and again at handoff.
- Record only execution details: files changed, tests added/run, decisions,
  blockers, and the next checkpoint.
- If implementation reveals a conflict with `PLANS.md`, graph invariants, or
  the canonical role model, stop and record the conflict here and in
  `STATUS.md` before changing the plan.
- Keep single-role behavior as the default/base case in every phase entry.

## Exact Checkpoint Template

Use this exact field set for every checkpoint subsection.

### Checkpoint PX.Y — title

- Date:
- Thread / branch:
- Status: pending / in progress / complete / blocked
- Goal:
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

## Phase 1 — Role-Safe Topology Parsing

- Scope anchor: `src/mofbuilder/io/cif_reader.py`, `src/mofbuilder/core/net.py`,
  matching tests
- Must preserve: current single-role scalar outputs and graph-state semantics
- Must not yet: change builder/runtime behavior or infer chemistry from role
  labels

### Checkpoint P1.0 — before coding

- Date: 2026-03-12
- Thread / branch: `codex_record`
- Status: complete
- Goal: add stable graph role annotations without changing higher layers
- Phase gate checked against `PLANS.md`: yes; Phase 1 remains limited to topology parsing in `src/mofbuilder/io/cif_reader.py`, `src/mofbuilder/core/net.py`, and matching tests only.
- Files changed: `WORKLOG.md`, `STATUS.md`
- Tests added: none
- Tests run: none
- Decisions: recorded the Phase Contract under `P1.0`; preserved the locked architecture, role-model invariants, and the Phase 1 execution boundary from `PLANS.md`.
- Conflicts / blockers: none
- Handoff / next checkpoint: `P1.1` — implementation

**Phase Contract**

- Phase name: `Phase 1 — Role-Safe Topology Parsing`

**Goal**
- Add internal role annotations at the topology/CIF parsing layer without changing the locked MOFBuilder pipeline or current single-role behavior.

**Scope**
- Preserve raw site-label detail needed to distinguish topology node and edge roles during CIF parsing.
- Prevent premature role-label collapse inside [cif_reader.py](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/src/mofbuilder/io/cif_reader.py).
- Attach deterministic `node_role_id` and `edge_role_id` metadata to `FrameNet.G` in [net.py](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/src/mofbuilder/core/net.py).
- Preserve existing single-role scalar outputs from `FrameNet`: `linker_connectivity`, `max_degree`, `sorted_nodes`, and `sorted_edges`.
- Keep the change topology-only; higher layers may ignore the new annotations in this phase.

**Allowed Files**
- [cif_reader.py](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/src/mofbuilder/io/cif_reader.py)
- [net.py](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/src/mofbuilder/core/net.py)
- [test_io_reader.py](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/tests/test_io_reader.py)
- [test_core_net.py](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/tests/test_core_net.py)
- [WORKLOG.md](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/WORKLOG.md) for required phase logging only
- [STATUS.md](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/STATUS.md) for phase/checkpoint/status updates only

**Forbidden Files**
- All files outside the allowed list are out of scope for Phase 1.
- Explicitly forbidden: [moftoplibrary.py](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/src/mofbuilder/core/moftoplibrary.py), [builder.py](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/src/mofbuilder/core/builder.py), [optimizer.py](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/src/mofbuilder/core/optimizer.py), [supercell.py](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/src/mofbuilder/core/supercell.py), [write.py](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/src/mofbuilder/core/write.py), [defects.py](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/src/mofbuilder/core/defects.py), [framework.py](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/src/mofbuilder/core/framework.py), [src/mofbuilder/md](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/src/mofbuilder/md), [database](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/database), [PLANS.md](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/PLANS.md) unless a real conflict is first recorded, [ARCHITECTURE.md](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/ARCHITECTURE.md), [AGENTS.md](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/AGENTS.md), [README.md](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/README.md), and [docs](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/docs)

**Architecture Invariants**
- Preserve the locked pipeline: `MofTopLibrary.fetch(...)` -> `FrameNet.create_net(...)` -> `MetalOrganicFrameworkBuilder.load_framework()` -> `MetalOrganicFrameworkBuilder.optimize_framework()` -> `MetalOrganicFrameworkBuilder.make_supercell()` -> `MetalOrganicFrameworkBuilder.build()`.
- Preserve graph states `G`, `sG`, `superG`, `eG`, and `cleaved_eG`.
- Do not rename, reorder, merge, or add pipeline stages.
- Keep responsibilities fixed: `FrameNet` owns topology graph construction and topology role annotation; downstream modules remain unchanged in this phase.
- Preserve graph-centered architecture, existing geometry and coordinate conventions, and the single-role template path as the base case.
- Do not change public builder/framework/package/CLI APIs or bundled database formats.

**Role Model Invariants**
- Topology role identifiers are the only topology classification mechanism.
- `node_role_id` must live on `FrameNet.G.nodes[n]["node_role_id"]`.
- `edge_role_id` must live on `FrameNet.G.edges[e]["edge_role_id"]`.
- Role ids must be stable and deterministic for the same template input.
- Role ids must not be inferred from chemistry, recomputed downstream, or replaced by local role maps.
- Fragment registries remain `node_role_registry` and `edge_role_registry`; Phase 1 must not introduce alternate role stores or fragment-assignment paths.
- Single-role templates must remain compatible with the canonical default-role base case rather than inventing a new single-role convention.

**Required Tests**
- Update and pass the relevant CIF-reader coverage in [test_io_reader.py](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/tests/test_io_reader.py).
- Update and pass the relevant topology parsing coverage in [test_core_net.py](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/tests/test_core_net.py).
- Add explicit single-role regression coverage proving current single-role CIF parsing still yields the same `linker_connectivity`, `max_degree`, `sorted_nodes`, and `sorted_edges`.
- Add one minimal topology-only heterogeneous-role test proving distinct role labels survive parsing and appear on `FrameNet.G` as `node_role_id` and `edge_role_id`.

**Success Criteria**
- Single-role templates behave exactly as before at the current public and scalar topology outputs.
- [cif_reader.py](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/src/mofbuilder/io/cif_reader.py) preserves enough raw topology label detail to support role-safe parsing.
- [net.py](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/src/mofbuilder/core/net.py) emits stable per-node and per-edge role annotations on `G`.
- Repeated parsing of the same topology produces the same role ids.
- Higher layers continue to function without consuming the new role annotations.
- No architecture lock, role-model invariant, or database schema is changed.

**Stop Rule**
- Stop immediately if Phase 1 work requires editing any forbidden file or changing module responsibilities.
- Stop immediately if satisfying the phase requires changes to `MofTopLibrary`, builder inputs or runtime behavior, optimizer, supercell, writer, defects, framework, CLI, MD code, or bundled database schema.
- Stop immediately if the implementation would infer chemistry from role labels, add fragment-assignment logic, or redesign graph APIs beyond attaching stable role annotations.
- Stop immediately if the locked pipeline, graph-state names, or public APIs would need to change.
- If any schema, runtime, or invariant conflict is discovered, record it first in [WORKLOG.md](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/WORKLOG.md) and [STATUS.md](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/STATUS.md), then stop before revising [PLANS.md](/Users/chenxili/GitHub/Cursor_repo/mof_cursor/MOFbuilder/PLANS.md).

### Checkpoint P1.1 — implementation

- Date:
- Thread / branch:
- Status: pending
- Goal:
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

### Checkpoint P1.2 — handoff

- Date:
- Thread / branch:
- Status: pending
- Goal: confirm Phase 1 exit criteria and next-phase handoff
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

## Phase 2 — Additive Family/Template Role Metadata

- Scope anchor: `src/mofbuilder/core/moftoplibrary.py`, matching tests, optional
  metadata fixture
- Must preserve: current `MOF_topology_dict` behavior for single-role families
- Must not yet: refactor builder/runtime or support multiple metadata schemas

### Checkpoint P2.0 — before coding

- Date:
- Thread / branch:
- Status: pending
- Goal: define one additive metadata path and passive normalized accessors
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

### Checkpoint P2.1 — implementation

- Date:
- Thread / branch:
- Status: pending
- Goal:
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

### Checkpoint P2.2 — handoff

- Date:
- Thread / branch:
- Status: pending
- Goal: confirm metadata schema is stable enough for builder normalization
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

## Phase 3 — Builder Input Normalization and Role Registries

- Scope anchor: `src/mofbuilder/core/builder.py`, matching tests
- Must preserve: current scalar builder inputs as the single-role shorthand
- Must not yet: redesign Phase 2 metadata or modify optimizer/supercell/writer

### Checkpoint P3.0 — before coding

- Date:
- Thread / branch:
- Status: pending
- Goal: normalize scalar inputs into one-entry role registries
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

### Checkpoint P3.1 — implementation

- Date:
- Thread / branch:
- Status: pending
- Goal:
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

### Checkpoint P3.2 — handoff

- Date:
- Thread / branch:
- Status: pending
- Goal: confirm builder-owned registries are ready for optimizer consumption
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

## Phase 4 — Role-Aware Optimizer Inputs

- Scope anchor: `src/mofbuilder/core/optimizer.py`,
  `src/mofbuilder/utils/geometry.py`, matching tests
- Must preserve: current single-role numerical path
- Must not yet: refactor supercell, writer, defects, or MD layers

### Checkpoint P4.0 — before coding

- Date:
- Thread / branch:
- Status: pending
- Goal: consume graph role ids plus builder registries in optimizer logic
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

### Checkpoint P4.1 — implementation

- Date:
- Thread / branch:
- Status: pending
- Goal:
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

### Checkpoint P4.2 — handoff

- Date:
- Thread / branch:
- Status: pending
- Goal: confirm optimizer supports minimal heterogeneous runtime behavior
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

## Phase 5 — Role Propagation Through Supercell and Edge Graph

- Scope anchor: `src/mofbuilder/core/supercell.py`, matching tests
- Must preserve: current `superG` / `eG` behavior for single-role builds
- Must not yet: redesign writer outputs, defects APIs, or MD handling

### Checkpoint P5.0 — before coding

- Date:
- Thread / branch:
- Status: pending
- Goal: preserve role ids through `superG`, `eG`, and `cleaved_eG`
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

### Checkpoint P5.1 — implementation

- Date:
- Thread / branch:
- Status: pending
- Goal:
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

### Checkpoint P5.2 — handoff

- Date:
- Thread / branch:
- Status: pending
- Goal: confirm downstream phases can consume propagated role metadata
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

## Phase 6 — Role-Aware Writer and Defect Metadata

- Scope anchor: `src/mofbuilder/core/write.py`,
  `src/mofbuilder/core/defects.py`, `src/mofbuilder/core/framework.py`,
  matching tests
- Must preserve: `Framework.get_merged_data()` as the sync point and current
  `remove()` / `replace()` semantics
- Must not yet: change MD contracts or invent local role identifiers

### Checkpoint P6.0 — before coding

- Date:
- Thread / branch:
- Status: pending
- Goal: generalize merged-data and defect paths to consume role-specific node
  metadata
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

### Checkpoint P6.1 — implementation

- Date:
- Thread / branch:
- Status: pending
- Goal:
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

### Checkpoint P6.2 — handoff

- Date:
- Thread / branch:
- Status: pending
- Goal: confirm writer/defect paths are stable before MD generalization
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

## Phase 7 — Multi-Edge Force-Field and Simulation-Prep Support

- Scope anchor: `src/mofbuilder/md/linkerforcefield.py`,
  `src/mofbuilder/md/gmxfilemerge.py`, `src/mofbuilder/core/framework.py`,
  matching tests
- Must preserve: current one-linker MD-prep path
- Must not yet: broaden scope into general heterogeneous force-field research

### Checkpoint P7.0 — before coding

- Date:
- Thread / branch:
- Status: pending
- Goal: support multiple edge-role force-field paths at the currently supported
  level
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

### Checkpoint P7.1 — implementation

- Date:
- Thread / branch:
- Status: pending
- Goal:
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

### Checkpoint P7.2 — handoff

- Date:
- Thread / branch:
- Status: pending
- Goal: confirm minimal heterogeneous multi-edge MD-prep support only
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

## Phase 8 — Documentation and Example Sync

- Scope anchor: `README.md`, `docs/source/manual/*.md`, `ARCHITECTURE.md`,
  `CODEX_CONTEXT.md`, `AGENTS.md`
- Must preserve: implemented behavior, not aspirational behavior
- Must not yet: mix documentation updates with new algorithmic refactors

### Checkpoint P8.0 — before coding

- Date:
- Thread / branch:
- Status: pending
- Goal: sync docs to the implemented multi-role model and verified limits
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

### Checkpoint P8.1 — implementation

- Date:
- Thread / branch:
- Status: pending
- Goal:
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

### Checkpoint P8.2 — handoff

- Date:
- Thread / branch:
- Status: pending
- Goal: confirm docs match code and known limitations
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:
