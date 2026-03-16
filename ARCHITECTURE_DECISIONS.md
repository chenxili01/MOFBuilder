# ARCHITECTURE_DECISIONS.md

## ADR-001 Typed Attachment Metadata

### Context

Flat anchor arrays remove slot identity in heterogeneous nodes.

### Decision

Introduce metadata structures that preserve slot type and ordering.

### Consequences

Semantic slot identity remains accessible while flat geometry remains unchanged.

---

## ADR-002 Preserve Flat Anchor Interface

### Context

Optimizer currently consumes flat anchor arrays.

### Decision

Maintain flat anchors as optimizer input.

### Consequences

Backward compatibility remains intact.

---

## ADR-003 Slot-Aware Placement

### Context

Placement must respect slot identity.

### Decision

Placement will resolve anchors using semantic metadata.

### Consequences

Correct attachment alignment for heterogeneous nodes.
