# AGENTS.md

## Purpose

Define the governance model for repository development using a two-agent workflow.

This document establishes:
- authority boundaries
- execution rules
- architectural invariants
- workflow constraints

All agents must comply with this contract.

---

## Governance Model

Development is controlled by a **two-agent system**.

```
Planner → Executor
```

Rules:
- Planner defines the implementation plan.
- Executor implements exactly one phase at a time.
- No reviewer role exists.
- Executor performs mandatory self-review.
- Architecture remains stable unless explicitly changed by the plan.

---

## Agent Roles

### Planner

Responsibilities:
- Define the branch objective.
- Produce an implementation-ready plan.
- Define sequential phases.
- Preserve architecture and ownership boundaries.

Planner must not modify code.

Planner output:
```
PLAN.md
PHASE_SPEC.md
```

---

### Executor

Responsibilities:
- Implement the active phase.
- Respect module boundaries.
- Perform validation and self-review.
- Update status and worklog.

Executor must not:
- invent new phases
- modify architecture without plan authorization
- expand scope

Executor output:
```
code changes
STATUS.md updates
WORKLOG.md entries
```

---

## Architectural Invariants

The following rules must remain true:

- Graph topology is the source of truth.
- Builder owns semantics.
- Optimizer performs geometry alignment.
- Framework construction remains role-agnostic.
- Backward compatibility must be preserved.
- Semantic ordering must not be replaced by geometry ordering.

---

## Execution Safety Rules

Executor must confirm before changes:

- architecture boundaries remain intact
- semantic ownership is preserved
- backward compatibility remains intact

Executor must stop if:
- plan ambiguity exists
- architecture changes are required but not authorized

---

## Development Phases

Development is phase-gated.

Rules:
- only one phase active at a time
- phases must complete sequentially
- phase completion must be verified

Executor must not skip phases.
