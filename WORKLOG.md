# WORKLOG.md

Use this file as the execution log for the multi-role topology effort.
Keep it aligned with `PLANS.md`. Do not use it to redefine phase scope.

## Rules

- One Codex thread should usually touch one phase only.
- Append facts; do not rewrite completed entries except to add a clearly marked
  correction.
- Log only concrete execution details: files changed, tests added/run, result,
  blockers, and handoff notes.
- If implementation reveals a conflict with `PLANS.md`, graph invariants, or
  the canonical role model, stop and record the conflict before changing the
  plan.
- Keep single-role behavior as the default/base case in every phase entry.

## Reusable Checkpoint Template

Copy this subsection shape when adding a new checkpoint under a phase.

### Checkpoint PX.Y — title

- Date:
- Thread / branch:
- Goal:
- Files changed:
- Tests added:
- Tests run:
- Result:
  - passed / partial / blocked
- Decisions:
- Risks / blockers:
- Handoff:

## Phase 1 — Role-Safe Topology Parsing

- Scope anchor: `src/mofbuilder/io/cif_reader.py`, `src/mofbuilder/core/net.py`,
  matching tests
- Must preserve: current single-role scalar outputs and graph-state semantics
- Must not yet: change builder/runtime behavior or infer chemistry from role
  labels

### Checkpoint P1.0 — before coding

- Date:
- Thread / branch:
- Goal: add stable graph role annotations without changing higher layers
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

### Checkpoint P1.1 — implementation

- Date:
- Thread / branch:
- Goal:
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

### Checkpoint P1.2 — handoff

- Date:
- Thread / branch:
- Goal: confirm Phase 1 exit criteria and next-phase handoff
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

## Phase 2 — Additive Family/Template Role Metadata

- Scope anchor: `src/mofbuilder/core/moftoplibrary.py`, matching tests, optional
  metadata fixture
- Must preserve: current `MOF_topology_dict` behavior for single-role families
- Must not yet: refactor builder/runtime or support multiple metadata schemas

### Checkpoint P2.0 — before coding

- Date:
- Thread / branch:
- Goal: define one additive metadata path and passive normalized accessors
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

### Checkpoint P2.1 — implementation

- Date:
- Thread / branch:
- Goal:
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

### Checkpoint P2.2 — handoff

- Date:
- Thread / branch:
- Goal: confirm metadata schema is stable enough for builder normalization
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

## Phase 3 — Builder Input Normalization and Role Registries

- Scope anchor: `src/mofbuilder/core/builder.py`, matching tests
- Must preserve: current scalar builder inputs as the single-role shorthand
- Must not yet: redesign Phase 2 metadata or modify optimizer/supercell/writer

### Checkpoint P3.0 — before coding

- Date:
- Thread / branch:
- Goal: normalize scalar inputs into one-entry role registries
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

### Checkpoint P3.1 — implementation

- Date:
- Thread / branch:
- Goal:
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

### Checkpoint P3.2 — handoff

- Date:
- Thread / branch:
- Goal: confirm builder-owned registries are ready for optimizer consumption
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

## Phase 4 — Role-Aware Optimizer Inputs

- Scope anchor: `src/mofbuilder/core/optimizer.py`,
  `src/mofbuilder/utils/geometry.py`, matching tests
- Must preserve: current single-role numerical path
- Must not yet: refactor supercell, writer, defects, or MD layers

### Checkpoint P4.0 — before coding

- Date:
- Thread / branch:
- Goal: consume graph role ids plus builder registries in optimizer logic
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

### Checkpoint P4.1 — implementation

- Date:
- Thread / branch:
- Goal:
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

### Checkpoint P4.2 — handoff

- Date:
- Thread / branch:
- Goal: confirm optimizer supports minimal heterogeneous runtime behavior
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

## Phase 5 — Role Propagation Through Supercell and Edge Graph

- Scope anchor: `src/mofbuilder/core/supercell.py`, matching tests
- Must preserve: current `superG` / `eG` behavior for single-role builds
- Must not yet: redesign writer outputs, defects APIs, or MD handling

### Checkpoint P5.0 — before coding

- Date:
- Thread / branch:
- Goal: preserve role ids through `superG`, `eG`, and `cleaved_eG`
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

### Checkpoint P5.1 — implementation

- Date:
- Thread / branch:
- Goal:
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

### Checkpoint P5.2 — handoff

- Date:
- Thread / branch:
- Goal: confirm downstream phases can consume propagated role metadata
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

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
- Goal: generalize merged-data and defect paths to consume role-specific node
  metadata
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

### Checkpoint P6.1 — implementation

- Date:
- Thread / branch:
- Goal:
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

### Checkpoint P6.2 — handoff

- Date:
- Thread / branch:
- Goal: confirm writer/defect paths are stable before MD generalization
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

## Phase 7 — Multi-Edge Force-Field and Simulation-Prep Support

- Scope anchor: `src/mofbuilder/md/linkerforcefield.py`,
  `src/mofbuilder/md/gmxfilemerge.py`, `src/mofbuilder/core/framework.py`,
  matching tests
- Must preserve: current one-linker MD-prep path
- Must not yet: broaden scope into general heterogeneous force-field research

### Checkpoint P7.0 — before coding

- Date:
- Thread / branch:
- Goal: support multiple edge-role force-field paths at the currently supported
  level
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

### Checkpoint P7.1 — implementation

- Date:
- Thread / branch:
- Goal:
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

### Checkpoint P7.2 — handoff

- Date:
- Thread / branch:
- Goal: confirm minimal heterogeneous multi-edge MD-prep support only
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

## Phase 8 — Documentation and Example Sync

- Scope anchor: `README.md`, `docs/source/manual/*.md`,
  `ARCHITECTURE.md`, `CODEX_CONTEXT.md`, `AGENTS.md`
- Must preserve: implemented behavior, not aspirational behavior
- Must not yet: mix documentation updates with new algorithmic refactors

### Checkpoint P8.0 — before coding

- Date:
- Thread / branch:
- Goal: sync docs to the implemented multi-role model and verified limits
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

### Checkpoint P8.1 — implementation

- Date:
- Thread / branch:
- Goal:
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:

### Checkpoint P8.2 — handoff

- Date:
- Thread / branch:
- Goal: confirm docs match code and known limitations
- Files changed:
- Tests added:
- Tests run:
- Result:
  - pending
- Decisions:
- Risks / blockers:
- Handoff:
