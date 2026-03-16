Generate a repository control-document set in a zip for a two-agent engineering workflow.

I want the files written in a strict, clean, concise, reproducible style with these characteristics:

GLOBAL STYLE
- Markdown only.
- Short, explicit sections with clear headings.
- Declarative engineering tone, not conversational.
- Dense, high-signal writing with minimal fluff.
- Strong use of “must”, “must not”, “do not”, “preserve”, “confirm”, “remains”.
- Bullet lists for constraints and responsibilities.
- Code blocks for canonical terms, statuses, APIs, invariants, and examples.
- Explicit ownership boundaries, invariants, non-goals, validation rules, and exit criteria.
- Narrow scope control: every file should reduce ambiguity and prevent scope drift.
- No marketing tone, no storytelling, no generic filler.

WORKFLOW MODEL
- Two agents only: Planner and Executor.
- Planner creates a single-phase, implementation-ready plan.
- Executor implements only the active phase, performs self-review, and updates status/worklog.
- No reviewer role.
- Plan-driven development with strict phase boundaries.
- Architecture and ownership must remain stable unless explicitly changed by plan.

WRITE THESE FILES WITH THESE PURPOSES AND STYLES:

1. AGENTS.md
- Style: governance contract / operating constitution.
- Include: purpose, governance model, agent roles, self-review requirement, architectural invariants, development phases, execution safety rules.
- Tone: strict, procedural, authoritative.

2. PLAN.md
- Style: roadmap + phase program spec.
- Include: branch objective, architectural invariants, ownership rules, design rules, sequential phases, stop rule.
- Each phase should explain the goal, scope, and what it is not doing.
- Tone: strategic but concrete.

3. PHASE_SPEC.md
- Style: hard boundary implementation spec.
- For each phase include: Allowed Modules, Required Work, Forbidden Changes, Completion Criteria.
- Tone: restrictive and execution-oriented.

4. ARCHITECTURE.md
- Style: high-level technical architecture narrative.
- Include: branch context, workflow, core principle, system layers, ownership boundaries, source-of-truth rules, compatibility requirements, future handoff.
- Tone: explanatory and stable.

5. ARCHITECTURE_DECISIONS.md
- Style: ADR log.
- Each ADR must use:
  - Context
  - Decision
  - Consequences
- Tone: formal and crisp.

6. CODEX_CONTEXT.md
- Style: quick repo/operator orientation brief.
- Include: repository map, branch context, pipeline, current problem context, immediate goal, invariants, ownership summary, stop rule.
- Tone: compressed and practical.

7. CHECKLIST.md
- Style: pre-flight and post-change safety checklist.
- Include: required reading, architecture safety checks, compatibility checks, scope checks, validation planning, self-review checks.
- Tone: procedural and auditable.

8. PLANNER.md
- Style: role prompt for the planner agent.
- Include: role definition, core rules, source-of-truth precedence, expected workflow, exact required output shape, success condition.
- Tone: deterministic and instruction-heavy.

9. EXECUTOR.md
- Style: role prompt for the executor agent.
- Include: role definition, core rules, source-of-truth precedence, required workflow, validation expectations, exact required output shape.
- Tone: deterministic and implementation-focused.

10. STATUS.md
- Style: compact workflow state snapshot.
- Keep short and structured.
- Start with fixed bullet fields such as:
  - Phase
  - Checkpoint
  - Status
  - Next step
  - Last update
- Then include branch, objective, current focus, invariants.
- Tone: minimal and stateful.

11. WORKLOG.md
- Style: append-only chronological engineering log.
- Include a fixed entry template with:
  - date / role / short title
  - branch
  - phase
  - checkpoint
  - summary
  - files touched
  - invariants checked
  - validation
  - notes
- Tone: factual, honest, operational.

12. HANDOFF DOC (example: SNAPSHOT_API_HANDOFF.md)
- Style: downstream handoff contract.
- Include: branch status at handoff, ownership summary, implemented surfaces, concrete available fields, expected future contract, intended future flow, non-goals, open decisions, readiness statement.
- Tone: descriptive, stable, documentation-only.

OUTPUT REQUIREMENTS
- Make every file consistent with the same governance model and vocabulary.
- Preserve explicit ownership boundaries.
- Preserve backward compatibility language.
- Use phase-gated execution language.
- Keep the documents clean, concise, and reusable as control docs for future GPT-driven coding workflows.