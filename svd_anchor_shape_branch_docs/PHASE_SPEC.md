# Phase Specifications

Each phase defines:
- allowed modules
- required work
- forbidden changes
- completion criteria

---

# Phase 1 — Anchor Geometry Contract

Allowed modules:
workflow markdown files

Required work:
define anchor geometry terminology:
source_anchor_vector
target_anchor_direction
slot_radius
shape-preserving pseudo anchors

Forbidden:
production code edits

Completion:
docs clearly define geometry model and seam.

---

# Phase 2 — Source Anchor Shape Preservation

Allowed modules:
optimizer.py
builder.py
tests/

Required:
ensure source anchor vectors preserve slot radius shape.

Forbidden:
framework edits
graph grammar changes

Completion:
source anchors retain original radial geometry.

---

# Phase 3 — Orientation Pair Construction Fix

Allowed modules:
optimizer.py
builder.py
tests/

Required:
replace uniform-scale pseudo anchors with source-radius anchors.

Completion:
orientation pairs preserve per-slot radius.

---

# Phase 4 — SVD Initialization Stabilization

Allowed modules:
optimizer.py
tests/

Required:
update SVD initialization to use shape-preserving anchors.

Completion:
SVD alignment uses direction + radius geometry.

---

# Phase 5 — Optimizer Stage Guarding

Allowed modules:
optimizer.py
tests/

Required:
prevent optimizer stages from overriding role-aware initialization.

Completion:
rotation seed preserved when semantic anchors present.

---

# Phase 6 — Compatibility and Guarded Rollout

Allowed modules:
optimizer.py
builder.py
tests/

Required:
ensure legacy literal-X families still function.

Completion:
legacy behavior preserved.

---

# Phase 7 — Regression Coverage

Allowed modules:
tests/
workflow docs

Required:
add regression coverage for:
legacy X
typed anchors
mixed cases

Completion:
coverage exists and seam documented.
