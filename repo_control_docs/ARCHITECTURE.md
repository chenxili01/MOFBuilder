# ARCHITECTURE.md

## Branch Context

This branch introduces typed attachment slot preservation for heterogeneous anchor nodes.

The existing system relied on flattened anchor arrays which lose semantic identity.

---

## Core Principle

Semantics must exist before geometry.

The optimizer must operate on geometry without redefining semantics.

---

## System Pipeline

```
Graph topology
      ↓
Builder (semantic compilation)
      ↓
Optimizer (geometry alignment)
      ↓
Framework construction
```

---

## System Layers

### Graph

Defines node connectivity.

### Builder

Produces semantic attachment definitions.

### Optimizer

Aligns node geometries.

### Framework

Constructs the final periodic structure.

---

## Source-of-Truth Rules

```
Topology → connectivity truth
Builder  → semantic truth
Optimizer → geometric alignment
```

No layer may override upstream ownership.

---

## Compatibility Requirements

The following must remain supported:

```
node_X_pos_dict (flat anchors)
```

Semantic structures must coexist with the legacy format.

---

## Future Handoff

Future systems may transition to semantic-first placement, but must maintain compatibility with existing geometry pipelines.
