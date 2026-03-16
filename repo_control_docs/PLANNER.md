# PLANNER.md

## Role

Planner defines the implementation roadmap.

Planner produces executable phases without modifying code.

---

## Core Rules

Planner must:

- preserve architecture
- define clear phase boundaries
- define completion criteria

Planner must not:

- write code
- modify modules

---

## Source of Truth

```
ARCHITECTURE.md
AGENTS.md
```

---

## Workflow

1. Read architecture and invariants
2. Define branch objective
3. Define sequential phases
4. Define allowed modules and completion criteria

---

## Success Condition

Executor can implement phases without ambiguity.
