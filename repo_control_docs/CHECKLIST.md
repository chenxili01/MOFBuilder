# CHECKLIST.md

## Pre-Change Checks

Required reading:

- AGENTS.md
- PLAN.md
- PHASE_SPEC.md
- ARCHITECTURE.md

Confirm:

- architecture invariants preserved
- module ownership respected
- backward compatibility preserved

---

## Scope Check

Confirm change belongs to the active phase.

Executor must not expand scope.

---

## Validation Plan

Confirm:

- optimizer input shape correctness
- metadata alignment with flat anchors

---

## Post-Change Self Review

Executor must confirm:

- invariants preserved
- phase scope respected
- compatibility maintained
