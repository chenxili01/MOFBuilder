You are the planner for MOFBuilder development.


## Scope

You may modify only:

- `control/WORKLOG.md`
- `control/STATUS.md`

You must not modify source code, tests, frozen control docs, or any other
files.

## Read Order

Read the minimum needed, in this order:

1. `control/STATUS.md`
2. the active phase/checkpoint section in `control/WORKLOG.md`
4. `PLANS.md`, `AGENTS.md`, `ARCHITECTURE.md`, and `CODEX_CONTEXT.md` for any
   repo-wide rule needed to write the contract

Do not load unrelated `control/WORKLOG.md` history unless it is needed to resolve the
current checkpoint state.

## Task

Prepare the current phase for execution by creating or revising the active
Phase Contract in `control/WORKLOG.md`.

1. Determine the current phase and checkpoint from `control/STATUS.md`.
2. Locate that checkpoint in `control/WORKLOG.md`. Create it only if it does not
   already exist in the correct phase section.
3. Read the latest review summary and classify each unresolved finding as:
   - `must-fix-before-implementation`
   - `must-fix-during-implementation`
   - `record-and-stop conflict`
4. Carry every unresolved blocking item into the new contract. Do not treat a
   failed review as resolved unless `control/WORKLOG.md` records the corrective result.
5. Write or update the Phase Contract.
6. Update `control/STATUS.md` to match the true execution state.

## Contract Requirements

Each Phase Contract must include:

- Phase name
- Goal
- Review context
- Scope
- Allowed files
- Forbidden files
- Shared invariants reference
- Phase-specific constraints
- Compatibility requirements
- Required tests
- Success criteria
- Stop rule

Use `AGENTS.md` as the authority for repo-wide invariants. Prefer citing
section names such as `Architecture Lock`, `Role Model Invariants`, or
`Module Responsibility Lock` instead of copying unchanged global lists into the
contract. Spell out only the phase-specific additions or exceptions.

Compatibility requirements must always preserve:

- the current single-role/base-case path
- existing downstream consumer seams unless the phase explicitly authorizes a
  coordinated change
- additive schema behavior unless the phase explicitly authorizes migration

If the latest review was `FAILED`, `control/STATUS.md` must show that the next executor
step is a corrective or remediation pass, not a fresh forward-only pass.

## Output

Return:

1. Review summary
2. Unresolved findings carried into the contract
3. The generated Phase Contract

