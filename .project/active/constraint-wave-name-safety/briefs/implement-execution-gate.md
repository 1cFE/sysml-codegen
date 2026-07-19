# Stage brief: implement — close Item 2's execution gate

**Epic**: `.project/backlog/epic_constraint_pr_wave_remediation.md`, Item 2 (Generated Constraint
Name-Safety Boundary, R-3). Orchestrated run, 2026-07-19.

## Scope (owner-aligned today)

- [OWNER, 2026-07-19] Close **only** the open execution criterion. No re-run of spec/design/
  implementation stages — the item is certified for the license-free scope
  (`.project/active/constraint-wave-name-safety/audit.md`).
- [OWNER, 2026-07-19] Licensed live/snapshot parity (design I11) stays with Item 8. Do not claim it.
- [OWNER, via epic] No commit, push, PR comment, or merge action. All artifacts land in the
  working tree uncommitted.

## What is open, precisely

1. `plan.md:572-573` — run `evidence/run_collision_free_control.py` in fresh subprocesses against
   both generated trees; save the exact satisfied and violated evidence tuples.
2. `plan.md:609-611` (Execution Gate) — the pinned node:
   `pytest -q -m execution tests/execution/test_constraint_execution.py -k name_safety_collision_free`
   (node `test_name_safety_collision_free_exact_evidence`). It must run in the real configured
   environment, not mocked.
3. Spec SC-9 and the epic Item 2 third success criterion (rejection policy: collision-free controls
   import and preserve correct verdict/status/margin for both truth values).

The prior audit left these open solely because `pandas` was unavailable. It now is.

## Environment facts ([AGENT], verified today + project memory)

- The codegen venv lacks `pandas`; the working recipe is: host the run in the agentic-mbse venv
  (`/home/reid/1cfe/agentic-mbse/.venv/bin/python`, pandas 2.3.3 confirmed) with
  `/home/reid/1cfe/sysml-codegen/src` importable and teax-simkit on `sys.path`.
- `tests/execution/conftest.py` already inserts `src` and discovers teax-simkit via
  `tests/helpers/teax_discovery.discover_teax_simkit` (env `TEAX_SIMKIT_PATH` or sibling
  discovery; teax lives at `/home/reid/1cfe/teax`, a sibling — packages path
  `/home/reid/1cfe/teax/packages/teax-simkit`).
- Do not use teax's own `.venv` or `uv run` inside teax — known broken.
- The syside license is NOT needed for this leg; do not pull licensed work in.

## Notes on the "both generated trees" box

The Phase's baseline/candidate temporary worktrees were removed after the byte-identity evidence
(27-file identical manifests, recorded in `evidence/evidence.md` and the sha256 files). Re-read the
plan phase and reproduce the minimum faithful equivalent: regenerate the collision-free package
from the current tree (which the byte-identity evidence ties to the candidate), and either
recreate the detached-candidate worktree if the plan's wording requires two trees, or record a
one-tree deviation with the byte-identity evidence as the bridge. Record whichever you do,
honestly, in the plan's implementation notes.

## Deliverables

1. Exact satisfied and violated evidence tuples saved under
   `.project/active/constraint-wave-name-safety/evidence/` (durable files, exact values).
2. The execution-gate pytest node run green in the real environment; command + output recorded.
3. `plan.md`: check the two open boxes with dated notes naming the environment used and any
   deviation.
4. `evidence/evidence.md`: append the execution-gate section (commands, environment, tuples).
5. `spec.md` SC-9 and status line updated honestly (execution evidence now claimed; licensed live
   parity still open → Item 8).
6. `audit.md`: append a dated post-audit addendum recording that the previously-unavailable
   execution leg was executed and its result. Do not rewrite the audit's own verdict text.
7. Epic Item 2: flip the third success criterion checkbox and update the item's status note
   (`.project/backlog/epic_constraint_pr_wave_remediation.md`). Mark the item heading complete only
   if every Item 2 criterion is now genuinely closed.
8. `.project/CURRENT_WORK.md`: update the Item 2 entry.
9. No commit, push, or PR action.

## Quality bar

- If the execution run produces a wrong verdict, wrong status, or wrong margin, that is a real
  R-3 defect: stop the closure claims, record the failing evidence exactly, and report back —
  do not patch production code in this stage without reporting first.
- Fresh subprocesses for evidence runs; no in-process reuse that could mask import-time failures.
- Record exact numbers; no "passed" without the tuple values.
