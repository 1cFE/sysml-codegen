# Brief: audit stage, named-subset-members

Run as a fresh subagent by the orchestrating session on 2026-10-26. You did not write any of this; check it skeptically.

## Task

Audit branch `named-subset-members` in `/home/reid/src/sysml-codegen` (implementation commits `55c22152`, `1ba181d0`, `153d09e2`; it stacks on `repeated-rollup-collision`, so compare against that branch's tip `26dbcc5e` plus the backlog commit `63819eab`) against `.project/active/named-subset-members/spec.md` and `design.md`, following `~/.claude/commands/_my_audit.md` (if absent, `/home/reid/src/agentic-mbse/.claude/commands/_my_audit.md`). Write `audit.md` beside the design. Don't fix anything, don't commit. For comparison builds use a git worktree under `/tmp/claude-1000/nsm-audit/`; never switch the main checkout's branch. dc3 is read-only.

## Intent

[AGENT recommended, ratified by owner 2026-10-26] option A: named subsets count as members of the collection they subset. The owner's priority: no silent wrong numbers.

## What matters most

- **Try to get a wrong count or wrong sum that builds.** New shapes, not only the design's and review's probes: a collection read from inside one of its own named members (the implementer did not check this), named members whose type is a subtype of the collection's type, a named member with a nested collection that also has named members, named members combined with repeated rolled-up sub-assemblies (the previous item's fix), mixed literal and expression overrides, named members under `nonunique`. Run values in real TEAx (`PYTHONPATH=src:/home/reid/src/teax/packages/teax-simkit /home/reid/src/dc3/.venv/bin/python`).
- **Claims hold.** Re-run the default suite (9 known failures), regenerate a sample of the corpus receipt's roots on both sides, and dc3 from its committed tree at `8a98af8`.
- **Code quality.** One rule in one place; refusal reasons raised once; matches surrounding style; the deviations the implementer lists are sound.
- **Docs and backlog** say what the code does, including the `[MEMBERSHIP-LIST-IGNORED]` note that s7 now sums 35 (check it: is that right per SysML, and on base too?).

Rank findings must-fix / should-fix / note. End with `ARTIFACT: <path>`.
