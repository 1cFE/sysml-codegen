# Brief: audit stage, repeated-rollup-collision

Run as a fresh subagent by the orchestrating session on 2026-10-26. You did not write any of this; check it skeptically.

## Task

Audit branch `repeated-rollup-collision` in `/home/reid/src/sysml-codegen` (implementation commits `44d4ed5e`..`7063db16`, base `e6c20bca`) against `.project/active/repeated-rollup-collision/spec.md` and `design.md`, following `~/.claude/commands/_my_audit.md` (if absent, `/home/reid/src/agentic-mbse/.claude/commands/_my_audit.md`). Write `audit.md` beside the design. Don't fix anything and don't commit.

## Intent

[OWNER-VERBATIM] "yes file it and orchestrate a fix in sysml-codegen": several identical sub-assemblies, each rolling up its own children, generate and compute the right numbers.

## What matters most

- **No silent wrong number.** Try to break the shape comparison: write models where two copies differ in something that changes the computed value (expression via a redefinition, an input bound to a different source, a different multiplicity deeper down, a unit, a default) and check, in real TEAx, that each copy computes its own value. Use `PYTHONPATH=src:/home/reid/src/teax/packages/teax-simkit /home/reid/src/dc3/.venv/bin/python` (see the design's Validation section). `[NESTED-OVERRIDE-LEAKS-TO-SIBLING]` is a known pre-existing defect; don't count it, but say if the change makes it worse.
- **Claims in the report hold.** Re-run the default suite (`uv run --env-file /home/reid/src/agentic-mbse/.env --extra dev pytest tests/`, 9 known failures), spot-check the corpus byte-identity receipt (`evidence/corpus-receipt.md`) by regenerating a few fixtures on `e6c20bca` and on the branch, and confirm the real collision case still refuses.
- **Code quality.** Is it one clear rule in the right places, matching the code around it? Look at the implementer's listed deviations (registry entry fields, the fourth path copy in `generation/stencils.py`, intermediate commits with failing tests, `PROJECTOR_SEMANTICS` not bumped) and judge each.
- **Docs and backlog** say what the code now does.

Rank findings must-fix / should-fix / note. End with `ARTIFACT: <path>`.
