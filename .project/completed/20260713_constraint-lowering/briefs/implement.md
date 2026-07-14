# Brief: Item 5 implement — Concrete Lowering

You are the implement stage for Item 5 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents or schedule check-backs.
- You ARE allowed to commit in this repo — you are the only session writing to this tree. Commit at each completed plan phase; check off plan.md checkboxes with implementation notes. End commit messages with: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Do NOT touch `.project/` outside `.project/active/constraint-lowering/`. Never run the snapshot-capture script.

## Input — execute the plan
`.project/active/constraint-lowering/plan.md` (Phases 1–5) is authoritative; `design.md` rev 2 (probe-settled) holds the models, ladder, four-kind dispatch, D5-IR carriage; `b1-probe-evidence.md` holds the fixture model skeleton (package-level design instance required — a def-only model drops template calcs).

## Environment
- This repo's venv is licensed (verified this run); live tests via `uv run pytest`.
- agentic-mbse is consumed via the editable install — read-only; if an agentic-mbse change seems needed, STOP and report (coordinated-pair discipline).

## Quality bar
- Phase 2's mini byte-identity check the moment the backtracker switch lands is non-negotiable (the F4 lesson) — record its evidence in plan notes before proceeding.
- The recorded-shared-binding semantics from the B1 adjudication must be asserted in the multi-instance fixture test (3 IDs / 3 entries / 3 modules' channels + recorded shared producer binding), not just implemented.
- Final gates: all new fixture tests green, full suite green, corpus byte-identity (regenerate + timestamp-only diff check + revert), mypy no new errors vs 77 baseline, ruff clean.
- If a gate fails and the fix is outside plan scope, STOP and report precisely.
