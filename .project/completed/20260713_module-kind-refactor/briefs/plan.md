# Brief: Item 6 plan — module_kind Refactor

You are the plan stage for Item 6 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `plan.md` in `.project/active/module-kind-refactor/`.

## Input
- Design (committed, review-revised, orchestrator-accepted): `.project/active/module-kind-refactor/design.md` — its migration order (model → construction → dispatch → tests/baselines lockstep, tree red between steps 1–4, step 4 atomic) and per-site dispatch notes are authoritative.
- Spec: `spec.md`; reviews: `spec-review.md`, `design-review.md` (context on what was contested).

## Planning guidance (orchestrator, agent-grade)
- The implement stage will run on a smaller model (sonnet): phases must be mechanical, each with exact files, the design's per-site before/after reference, the verification command to run, and expected outcome. No judgment calls left open.
- Since the tree is deliberately red between steps 1–4, define per-phase checkpoints that ARE checkable (e.g. mypy on touched files, targeted test subsets) and say explicitly which full-suite/byte-identity gates only pass at the end.
- Include the byte-identity protocol as its own phase with exact commands: regenerate fixture corpus, timestamp-only diff check, revert (memory discipline: a full re-capture rewrites captured_at; only accept timestamp-only churn).
- Final phase: repo-wide zero-hit grep gate for both flags, full suite, mypy, ruff.
- Keep phases small enough that a budget-killed session can resume from checkboxes.
