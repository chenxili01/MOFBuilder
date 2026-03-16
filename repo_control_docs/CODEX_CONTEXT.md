# CODEX_CONTEXT.md

## Repository Map

```
graph/
builder/
optimizer/
framework/
```

---

## Branch Context

Branch introduces typed attachment slots while preserving flat anchors.

---

## Pipeline

```
graph → builder → optimizer → framework
```

---

## Current Problem

Hungarian alignment assumed equal vector counts.

Heterogeneous anchors violate this assumption.

---

## Immediate Goal

Preserve slot identity across the pipeline.

---

## Invariants

- graph defines connectivity
- builder defines semantics
- optimizer aligns geometry
- flat anchors remain supported

---

## Stop Rule

Stop if architecture changes are required without plan authorization.
