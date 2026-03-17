# STATUS.md

- Phase: Phase 3
- Checkpoint: linker-shared-center-order-rule-applied
- Status: COMPLETED
- Next step: done
- Last update: 2026-03-16

---

Branch: typed-attachment-slots

Objective:
Preserve heterogeneous attachment slot identity.

Current focus:
Phase 3 remains complete. A follow-up linker hotfix now canonicalizes
center-fragment cyclic attachment order from `cyclic_order_rules` metadata
before `X1..Xn` emission, while builder injects the active center alias set,
a pre-resolved shared `center_order_rule`, and canonical metadata into
`FrameLinker`. Mixed C* role families now reuse a shared cyclic rule only when
their rules are identical and fail loudly when current linker preprocessing
cannot represent conflicting center-role ordering safely. Optimizer ownership
and legacy no-rule extraction order remain unchanged.

Invariants:
- topology source of truth
- builder owns semantics
- optimizer consumes geometry
- backward compatibility preserved
