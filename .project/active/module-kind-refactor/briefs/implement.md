# Brief: Item 6 implement — module_kind Refactor

You are the implement stage for Item 6 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents or schedule check-backs.
- You ARE allowed to commit in this repo — you are the only session writing to this tree. Commit at each completed plan phase (subject leads with the phase), and check off the plan.md checkboxes as you go, with implementation notes on deviations. End git commit messages with: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Do NOT touch `.project/` files outside `.project/active/module-kind-refactor/`, and never run the snapshot-capture script (the plan's guardrail — it churns captured_at timestamps for nothing; module_kind is not a snapshot field).

## Input — execute the plan
`.project/active/module-kind-refactor/plan.md` is authoritative and mechanical: model → construction sites → seam dispatch (per-site notes in design.md are authoritative, including Seam 1b two-arm aggregation-joins-calc) → tests/baselines lockstep → final gates.

- Design: `.project/active/module-kind-refactor/design.md` (per-seam before/after shapes).
- The tree is deliberately red between phases 1–4; use the plan's per-phase checkpoints (mypy on touched files, build probe, isolated fail-loud tests). Full suite + byte-identity only at the end.
- The two constructor-kwarg/positional-arg lookups the plan flags: mirror an existing conformance test, as instructed — no guessing.

## Quality bar
- Follow existing code idiom (naming, comment density). No commented-out code, no TODO placeholders.
- The byte-identity claims must be proven, not asserted: capture the regeneration diff evidence in the plan's implementation notes (exact commands + outcomes).
- Final gates before you finish: repo-wide zero-hit grep for both flags, full suite green, mypy clean, ruff clean, conformance byte-identity green, baseline JSON diff = exactly the two-out/two-in-plus-null swap.
- If a gate fails and the fix is outside the plan's scope, STOP and report precisely rather than improvising a workaround.
