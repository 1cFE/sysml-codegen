# Brief: implement stage, named-subset-members

Run as a subagent by the orchestrating session on 2026-10-26.

## Task

Implement the plan at the end of `.project/active/named-subset-members/design.md` (round 2, commit `8f118cbd`), following `~/.claude/commands/_my_implement.md` (if absent, `/home/reid/src/agentic-mbse/.claude/commands/_my_implement.md`). Work in `/home/reid/src/sysml-codegen` on branch `named-subset-members`. Commit each phase on this branch with explicit paths (never `git add -A`), a subject leading with what changed, and the trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Tick plan checkboxes with short notes. Don't push. Don't touch agentic-mbse or dc3 (dc3 is read-only; regenerate from its committed tree as the design says).

## Intent

[AGENT recommended, ratified by owner 2026-10-26] option A: named subsets count as members of the collection they subset; `sum()` includes them; the generator builds the declared number of parts. The owner's priority: no silent wrong numbers. Read spec, design, `design-review.md` and `product-lens.md`.

## Orchestrator decision [AGENT, owner informed 2026-10-26]

The design's "refuse every non-sibling named member" rule stands, including its cost: `candidate-es-009__typed_subsetting__part_usage` and `..._nested_untyped_subsetting__part_usage` (compose by subsetting a package-level part, `part facility :> ac_facility`) change from built to refused. The refusal message should name the working alternative (compose with a part def: `part facility : Fac`). If the owner reverses this, it will come as a separate instruction.

## Quality bar

- Production code, not the prototype patch: write it cleanly where the design puts it, matching surrounding style. Each refusal reason raised from one place.
- Values before stored answers: check every spec value and every review probe value in real TEAx (`PYTHONPATH=src:/home/reid/src/teax/packages/teax-simkit /home/reid/src/dc3/.venv/bin/python`) before re-capturing any stored answer.
- Whole-corpus byte check: only the design's listed roots may differ; record it in an evidence receipt like `.project/active/repeated-rollup-collision/evidence/corpus-receipt.md`.
- dc3 byte-identical from its committed tree.
- Default suite: `uv run --env-file /home/reid/src/agentic-mbse/.env --extra dev pytest tests/`; 9 known failures (`test_check_ledger_4a.py` ×8, one `test_study_cli.py`); any other failure is yours. The manifest test needs reviewed rows for the new parser reads.
- `ruff check src/` and `mypy src/` clean.
- Backlog: close `[NAMED-SUBSET-DOUBLE-COUNT]` and `[REDEFINITION-DROPS-COUNT]`; file the rows the design plans; document the new refusals as limits in `docs/architecture/modeling-assumptions.md`.

If you hit evidence against a premise of the design, stop and report. Final report: phases with SHAs, test results, corpus receipt, dc3 result, values, backlog changes, deviations, what you didn't check. End with `ARTIFACT: <path>`.
