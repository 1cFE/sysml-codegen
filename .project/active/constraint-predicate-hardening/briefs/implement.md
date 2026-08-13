# Brief: implement stage — CONSTRAINT-SEMANTICS Item 4 (Predicate Defect Hardening)

Orchestrated run (owner-invoked `/_my_orchestrate`, check-ins waived). You are the implement
stage, with execution. Work synchronously: never pause for background agents or schedule
check-backs. If your budget nears exhaustion, stop at a phase boundary with both trees
committed green and say exactly where you stopped — a clean gap beats a rushed tail.

## Authority chain (read in this order)

1. `.project/active/constraint-predicate-hardening/plan.md` — the phase sequence you execute.
   Check boxes as you complete phases; add Implementation Notes per phase (deviations,
   probe outcomes, exact counts).
2. `.project/active/constraint-predicate-hardening/design.md` — mechanism authority
   (decisions D1–D8, invariants, message shape, the single dedup/order key).
3. `.project/active/constraint-predicate-hardening/spec.md` — success criteria your
   verification.md must discharge.
4. `.project/active/constraint-predicate-hardening/probes/companion-evidence.md` —
   orchestrator-verified companion citations, P4 verdict, verbatim REASON_CODES. Re-verify
   citations against companion source before editing it (you have access).

## Hard rules

- Follow the plan's phase order; do not reorder across the red-first boundary: the
  strict-xfail characterizations and captured red evidence land and are committed BEFORE any
  fix code.
- Both trees green at every commit. Companion commits via
  `git -C /home/reid/1cfe/agentic-mbse-item7-rebuild` with pathspec-limited adds — never mix
  repos in one command, never commit `uv.lock`.
- Interpreter: `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`. NEVER `uv run`.
- License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`. A run with
  license-skip lines is not a full run and may not be reported as one.
- Companion suite: default selection only — NEVER `pytest -m ""` (corpus/PDF trap).
- Frozen twins (`catf_mfe_model`, `catf_mfe_d5`) byte-untouched. New fixtures only.
- TEAx untouched; its checkout stays on `constraint-semantics-item3`.
- Lint gates: `ruff check src` = 12, `mypy src` = 55, zero-new in both repos' own baselines.
- One commit per phase minimum, subject leading with the decision. Probe outcomes (P1, P2,
  P3) recorded in plan Implementation Notes at their designed points; if a probe selects a
  fallback branch, record the selection and apply the design's stated fallback — if a probe
  outcome contradicts the design's premise in a way the design did NOT anticipate, STOP at
  the phase boundary and report rather than improvising.
- Never mark a checkbox for a result you could not confirm (a killed run is not a pass).

## Deliverable

All plan phases executed and committed (codegen branch `item7-rebuild`, companion worktree
branch as-is), `verification.md` written with exact counts against every spec success
criterion, plan checkboxes current. Final message: per-phase one-liners, probe verdicts,
exact gate counts, any deviations. End with
`ARTIFACT: .project/active/constraint-predicate-hardening/verification.md`.
