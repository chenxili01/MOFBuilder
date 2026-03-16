# SNAPSHOT_API_HANDOFF.md

## Branch Status

Typed attachment slot preservation branch.

Phase 1 implementation planned.

---

## Ownership Summary

```
Graph → connectivity
Builder → semantic slot metadata
Optimizer → geometry alignment
Framework → structure construction
```

---

## Implemented Surfaces

Expected metadata structure:

```
slot_type
slot_ordinal
row_index
```

---

## Future Contract

Placement systems will use metadata lookup to resolve attachment slots.

---

## Non-Goals

This branch does not:

- redesign the optimizer
- remove flat anchor arrays
- alter topology schema

---

## Open Decisions

Future semantic-first placement strategy.

---

## Readiness Statement

Repository prepared for phased implementation of typed attachment slot preservation.
