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

- Date:
- Thread / branch:
- Status: pending
- Goal: add stable graph role annotations without changing higher layers
- Phase gate checked against `PLANS.md`:
- Files changed:
- Tests added:
- Tests run:
- Decisions:
- Conflicts / blockers:
- Handoff / next checkpoint:

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
