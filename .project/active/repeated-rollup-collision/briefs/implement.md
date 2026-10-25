# Brief: implement stage, repeated-rollup-collision

Run as a subagent by the orchestrating session on 2026-10-25.

## Task

Implement the plan at the end of `.project/active/repeated-rollup-collision/design.md` (design at `79e80d3a`), following `~/.claude/commands/_my_implement.md` (if absent, `/home/reid/src/agentic-mbse/.claude/commands/_my_implement.md`). Work in `/home/reid/src/sysml-codegen` on branch `repeated-rollup-collision`. Commit each phase yourself on this branch, with explicit paths (never `git add -A`), a subject that leads with what changed, and the trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Tick the plan's checkboxes and add short implementation notes as you go. Do not push. Do not touch agentic-mbse or dc3.

## Intent

[OWNER-VERBATIM] "yes file it and orchestrate a fix in sysml-codegen": several identical sub-assemblies, each rolling up its own children, generate and compute the right numbers. The spec is the contract; the design and `design-review.md` explain the choices. Read all three.

## Quality bar

- Production code, not the prototype. The design's prototype monkeypatches; write the real change cleanly where the design puts it, matching the surrounding code's style and comment density. Remove nothing the design doesn't say to remove.
- Single-copy output must be byte-identical: run the whole-corpus diff the plan describes and record its result.
- Values before baselines: check every hand-worked value in the two flipping fixtures in real TEAx before re-capturing any stored answer.
- Real TEAx runs: `PYTHONPATH=src:/home/reid/src/teax/packages/teax-simkit /home/reid/src/dc3/.venv/bin/python` (see the design's Validation section for the execution lane and `lane.sh` notes).
- Licensed runs need `--env-file /home/reid/src/agentic-mbse/.env`. Default suite: `uv run --env-file /home/reid/src/agentic-mbse/.env --extra dev pytest tests/`. 9 failures predate this branch (`test_check_ledger_4a.py` ×8, one `test_study_cli.py`); any other failure is yours to fix or explain.
- `uv run --extra dev mypy src/` and `uv run --extra dev ruff check src/` stay clean on the files you touch.
- `[NESTED-OVERRIDE-LEAKS-TO-SIBLING]` is out of scope; no test may depend on it.

If you hit evidence against a premise of the design, stop and report rather than improvising a different design.

Final report: phases done with commit SHAs, test results against the baseline, the corpus diff result, the flipped-fixture values, backlog rows filed, deviations from the design, and what you didn't check. End with `ARTIFACT: <path of design.md>`.
