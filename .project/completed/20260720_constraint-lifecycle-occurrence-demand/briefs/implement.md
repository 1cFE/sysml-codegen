# Implement Brief — Lifecycle Item 1: Occurrence and Demand Integrity

**Stage:** implement (phases run in groups; orchestrator reviews between groups)
**Work item:** `.project/active/constraint-lifecycle-occurrence-demand/plan.md` (Phases 1–6;
Phase 0 is complete with recorded hashes — do not redo or modify its overlay bytes)
**Authority chain:** approved `spec.md` and `design.md` in the same directory; epic Item 1 in
`.project/backlog/epic_constraint_execution_lifecycle_remediation.md`.

## Intent (from the epic — provenance: [INHERITED: ratified lifecycle contract])

Close R-4/R-5/R-7: occurrence-stable usage identity instead of nullable-QN membership; loud
atomic failure on recursive containment (no partial index); one deterministic demand identity
per normalized target (no duplicate demand, no last-write-wins synthesis). Unsupported owners
never reach a package fallback. Valid replay is never mislabeled corrupt.

**[OWNER-VERBATIM]:** "Remember to mention in the epic document the importance of
SIMPLIFICATION and REDUCING code wherever possible." This is an execution gate: Phase 4 must
DELETE `RecordingOccurrenceIndex`, `collect_bare_actual_demand`, `materialize_supplied_values`,
the duplicate route blocks, and last-write-wins synthesis — no wrapper, feature flag, or
compatibility alias may remain. Executable-LOC hard gate ≤ 3,524 across the automatic union
(design target ≤ 3,504), measured by the frozen `evidence/production_metrics.py`.

## Execution rules

1. Follow the plan phase by phase. Tests first per each phase's stencil. Check boxes and fill
   Implementation Notes from recorded facts as you complete each phase.
2. Do only the phase group named in the stage message, then stop and report: what changed,
   test results, any challenged design bet, LOC trajectory.
3. The plan's Stop conditions are binding. If a design bet is contradicted (plan §Stop #2) or
   scope wants to absorb Item 2/4/5 work (§Stop #1), stop and report — do not improvise.
4. Phase 3 is not a releasable state; Phases 3+4 must both land before any green claim.

## Environment gotchas (orchestrator-verified, from prior sessions)

- Syside license: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` before any
  licensed pytest run. Without it the suite silently reads as a fake 23F/96E baseline.
- Never ruff-format `tests/fixtures/` or `baseline_outputs/` — generator-owned bytes;
  byte-identity gates depend on them.
- `.claude/projects/` is user-owned: never stage, clean, reset, or touch it.
- Preserve unrelated dirty files (`.project/CURRENT_WORK.md` is modified; leave it).
- The wired agentic-mbse checkout is `/home/reid/1cfe/agentic-mbse` (not `~/agentic-mbse`).
- TEAx execution tests: `TEAX_SIMKIT_PATH=../teax/packages/teax-simkit` as in the plan's
  Phase 5 commands; teax's own .venv is broken — don't use it.

## Quality bar

Clean, well-factored code matching the design's exact APIs and record shapes. No test-only
production parameters. No defensive guards layered where deletion is specified. Comments state
constraints, not narration. The reviewer will diff against the design's Appendix A caps.
