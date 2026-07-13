# Brief: Item 7 implement — Constraint Generation

You are the implement stage for Item 7 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents or schedule check-backs.
- You ARE allowed to commit in this repo — you are the only session writing to this tree. Commit at each completed plan phase; check off plan.md checkboxes with implementation notes. End commit messages with: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Do NOT touch `.project/` outside `.project/active/constraint-generation/`. Never run the snapshot-capture script. Do NOT modify teax or agentic-mbse (read-only; the teax venv on its epic branch is your execution environment for Phase 4).

## Input — execute the plan
`.project/active/constraint-generation/plan.md` (Phases 1–5) is authoritative; the teax-state pin at its end pre-discharges Phase 4's first checkbox (persist-and-assert in force). `design.md` rev 2 holds D1–D11, template specs, and both guards (same-IR INV-2, B5 leaf-name).

## Quality bar
- Phase 1's Kleene unit suite is the item's semantic core — every truth-table cell asserted on the emitted function directly, including -0.0→0.0.
- Phase 2's exit test must have a genuinely falsifying control leg (report ABSENT when narrowed without the pin).
- Phase 3's D11 touch to constraint_lowering.py is exactly one condition — anything more, STOP and report.
- Phase 4 runs the generated package under real simkit; record exact incantations in plan notes. Violated verdicts complete with ordinary outputs intact — the epic's core semantics — assert it explicitly.
- Final gates: constraint-free corpus byte-identity, full suite green, mypy 76 baseline, ruff clean.
- If a gate fails and the fix is outside plan scope, STOP and report precisely.
