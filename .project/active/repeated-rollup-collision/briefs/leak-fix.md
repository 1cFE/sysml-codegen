# Brief: fix the sibling-override leak, repeated-rollup-collision

Run as a subagent by the orchestrating session on 2026-10-26.

## Intent

[OWNER-VERBATIM] 2026-10-26: "ok fix the leak and investigate the double counting". The leak is backlog `[NESTED-OVERRIDE-LEAKS-TO-SIBLING]`. This item's collision fix turned one refused shape into a silent wrong number because of it, so it ships on this branch.

## Task

Work in `/home/reid/src/sysml-codegen` on branch `repeated-rollup-collision`. Read `evidence/leak-investigation/report.md` and `fix.patch` beside it first; they give the cause (`elaboration/occurrence.py:503-511`, `occurrences_for_declaration` selects by redefinition family, not by each occurrence's effective declaration), the shapes, native SysIDE values and the expected test fallout.

1. Apply the fix cleanly: make `FeatureSlotIndex._redefines` public (or add a well-named public method) rather than calling a private one; match the surrounding style. Add a short note to `design.md` (new decision D9) and tick a plan line for it.
2. Regression tests: one case per shape group from the report, at least the nested override in a usage, the same in a specializing def, the one-level part redefinition in a specialized definition (crosses roots), the deep chain owned by a redefining usage, and a new attribute or constraint declared inside the redefinition. Assert per-copy values in `inputs/` and node presence; add the `leak_rollup` model to the real-TEAx execution test (a = 30, b = 60, total 90).
3. The three `candidate-es-008` refusal cases flip to building. A separate investigation into named-subset double counting is running and may change how they should behave. For now follow the repo's practice for pinning today's output: re-capture their stored answers as building, and file backlog row `[NAMED-SUBSET-DOUBLE-COUNT]` (owner Reid Westwood, `[AGENT]`) stating that a named subset (`server_1 :> servers`) is built as an extra copy beside the indexed ones, that these three cases now build with that double count, and that the stored answers pin today's output so a fix shows as a changed answer. Fix the `_require_one_writer` mutation witness (the report names the remaining refusal, s17, as a candidate witness).
4. Close `[NESTED-OVERRIDE-LEAKS-TO-SIBLING]` in the backlog.
5. Prove nothing else changed: re-run the whole-corpus byte check (`evidence/corpus-receipt.md` method); only the three flipped cases and new fixtures may differ. Default suite: 9 known failures only. `ruff check src/` and `mypy src/` clean.

Commit each step on the branch with explicit paths and the trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Don't push. If you find evidence against the report's cause or fix, stop and report. Report SHAs, results and anything you didn't check. End with `ARTIFACT: <path>`.
