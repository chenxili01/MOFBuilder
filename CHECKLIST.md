# CHECKLIST.md

Confirm:
- Phase scope stayed bounded to `mofbuilder/core/optimizer.py`, `mofbuilder/core/builder.py`,
  `tests/`, and workflow markdown files.
- Regression coverage includes the bounded seam:
  legacy literal-`X` compatibility,
  typed `XA`,
  and one supported mixed-source case such as `XA` + `Al`.
- Guard-enabled optimizer placement without an
  `OptimizationSemanticSnapshot` fails explicitly.
- Missing or unresolved resolved-anchor metadata still fails explicitly and
  explainably rather than through geometry-first behavior.
- Builder remains the only owner of slot/path legality and
  `source_atom_type` resolution; optimizer consumes compiled anchors only.
- Workflow docs state covered support honestly and do not imply broader typed-family
  rollout than the current seam actually implements.
