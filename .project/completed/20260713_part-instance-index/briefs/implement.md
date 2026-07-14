# Brief: Item 4 implement — Part-Instance Index

You are the implement stage for Item 4 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents or schedule check-backs.
- You ARE allowed to commit in this repo — you are the only session writing to this tree. Commit at each completed plan phase; check off plan.md checkboxes with implementation notes. End commit messages with: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Do NOT touch `.project/` outside `.project/active/part-instance-index/`. Do NOT run the snapshot-capture script.

## Input — execute the plan
`.project/active/part-instance-index/plan.md` (3 phases) is authoritative; the design (`design.md`, rev 2) holds the node-type-dispatch gate, walker, dedup, and identity rules; `b1-probe-evidence.md` holds the live API table your classifier must match.

## Environment
- Phase 1 (classifier truth table) is license-free: plain `uv run pytest` here.
- Phases 2–3 live tests run via the licensed sibling env exactly as the plan states (`uv run --directory /home/reid/1cfe/agentic-mbse python ...` / pytest form; pytest 9.0.2 confirmed present there). Note: another implement session is committing in agentic-mbse right now — you only READ that repo's env, never write to it.
- Item 6 landed since your plan was written: `PipelineModule` now carries `module_kind` (enum) instead of Boolean flags. Item 4 is additive and shouldn't touch those files, but if a fixture or helper you promote references the old flags, adapt to `module_kind` (the suite will tell you).

## Quality bar
- Match `analysis/` module idiom. No TODOs, no commented-out code.
- The byte-identity/additive gate is proven, not asserted: `git status` after generation runs shows only your additions; record evidence in plan notes.
- Final gates: all 8 design validation tests green, full suite green (2142+new expected), mypy no new errors vs baseline 77, ruff clean.
- If a gate fails and the fix is outside plan scope, STOP and report precisely.
