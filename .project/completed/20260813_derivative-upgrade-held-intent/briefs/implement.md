# Orchestrator brief — implement stage, CONSTRAINT-SEMANTICS Item 9

## Input

Plan: `.project/active/derivative-upgrade-held-intent/plan.md` (five phases C1–C5, committed).
Design rev 2 and spec sit beside it — the design's change list, expectation table, A9 predicate,
and PROVENANCE edit list are authoritative; do not re-derive or re-decide them. The held-intent
rows (`.project/completed/20260813_catf-constraint-policy-acceptance/owner-disposition.md`
A5/A6/A9) are owner payload — no re-disposition.

## Execution rules

- Walk the plan phase by phase, checking boxes as you complete each, with implementation notes
  at each phase (what changed, issues, deviations).
- **Commit at each plan commit point (C1–C5) yourself**, message subject leading with the
  decision/phase. Stage ONLY files this item touches (`git add` explicit paths; never `-A`).
  Another agent may write to `.project/` files — if `git status` shows a foreign edit in a file
  you must touch (BACKLOG.md guard in C4), follow the plan's defer path and record it.
- **C2's position in history is the SC-6 evidence**: every expectation (manifest JSON,
  population JSON, expected-coverage.md, test literals, all PROVENANCE edits incl. §3b SC-3
  side 1, §5 A9 subsection, D3 record, float-drift record) lands in C2 with NO confirmation run
  before it. Do not peek at a run to fill a value.
- **Stop-and-surface, never adapt**: if the edited fixture refuses at snapshot/re-seal (C1), if
  any ruled form refuses, or if a confirmation run contradicts a committed expectation, STOP,
  record exactly what happened, and return to the orchestrator. A committed expectation that
  proves wrong is corrected only with a named, value-free reasoned edit (Item 5's discipline),
  not silently retuned.
- Known pre-existing failure, not yours to chase:
  `tests/execution/...::test_the_lane_runs_the_real_simkit` fails on whole-set runs, passes in
  isolation. Record if hit.

## Environment

- Interpreter: `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest` (NOT `uv run`).
- License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`. Licensed proof = zero
  license-skip lines in the output, recorded.
- Baselines: ruff check src = 12, mypy = 52 errors; the gate is zero-NEW.
- Frozen surfaces (verify byte-untouched at C5, record the check): `tests/fixtures/catf_mfe_model/`,
  `tests/fixtures/catf_mfe_d5/`, `.project/completed/20260813_catf-constraint-policy-acceptance/`.

## Deliverable

All five phases executed and committed; plan checkboxes ticked with notes;
`verification.md` in the item folder with exact counts (suite numbers, license proof line,
ruff/mypy, byte-untouched checks, the SC-6 commit SHAs). Reply with what landed, any deviation,
and ARTIFACT: the verification file.
