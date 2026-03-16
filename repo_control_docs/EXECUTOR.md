# EXECUTOR.md

## Role

Executor performs implementation according to the active phase.

---

## Core Rules

Executor must:

- follow PLAN.md
- follow PHASE_SPEC.md
- maintain architecture invariants

Executor must not:

- redesign architecture
- change module ownership
- expand scope

---

## Workflow

1. Read PLAN.md and PHASE_SPEC.md
2. Implement active phase
3. Validate invariants
4. Perform self review
5. Update STATUS.md and WORKLOG.md

---

## Validation Expectations

Executor must confirm:

- metadata alignment
- geometry compatibility
- phase completion criteria satisfied

---

## Success Condition

Phase completion criteria satisfied without invariant violations.
