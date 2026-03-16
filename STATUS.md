# STATUS.md

- Phase: Phase 3
- Checkpoint: mixed-attachment-hotfix-applied
- Status: COMPLETED
- Next step: done
- Last update: 2026-03-16

---

Branch: typed-attachment-slots

Objective:
Preserve heterogeneous attachment slot identity.

Current focus:
Phase 3 remains complete. A follow-up hotfix now preserves mixed typed
attachment slots in source fragment order through builder and optimizer payload
preparation so `node_X_pos_dict` keeps the full attachment-slot count for
heterogeneous nodes while legacy `X`-only compatibility remains available.

Invariants:
- topology source of truth
- builder owns semantics
- optimizer consumes geometry
- backward compatibility preserved
