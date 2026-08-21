# Phase 2 audit — targeted confirmation of the fix round

The implementer closed your findings at `stop-parser-evidence-r2` commit `68bca37` (phase record
updated at docs commit `719dce1`, "Audit-fix pass" note in plan.md's Phase 2 completion section).
Confirm the closures by execution, not by reading the diff. This is not a re-audit of the phase.

Scope, in priority order:

1. **M1.** Verify `extract_expression_ir` and `reconstruct_expression` now exhaust into
   `EXPRESSION_DEPTH_EXHAUSTED` on your original self-nesting reproduction (rerun it), that the
   budget is the same shared non-caller-selectable constant, and that the four kept tests would
   catch a de-wiring (kill one wiring in a throwaway copy if cheap).
2. **m3.** Verify the unit operand is no longer emitted at the inspection boundary and shape
   validation survives. Assess the implementer's flag: the project-scoped unit
   (`3.0 [MyUnits::widget]`) does not parse at SysIDE 0.8.4, so that case is proved through a
   double on the same path. Is the double faithful to the live structure, and is the closure
   adequate given the live case is unreachable? If you judge it inadequate, say what would make
   it adequate — do not fix it yourself.
3. **m2, m4, m6, m7, i10.** Spot-check each closure (AST-based scope with anti-vacuity intact;
   load-failure asserts; helper + hasattr test gone with absence pinned; getattr mutants; `or ""`
   removed).
4. **m5.** Verify the record corrections: the 14-passed count and the named artifact-isolated
   set replacing "221 passed" — reproduce the named set's figure.
5. Confirm no regression: focused suites, scoped strict zero, fast-suite baseline still exactly
   the 18 known nodes, Codegen worktree untouched at `d257ef1`, user checkouts clean.

Append an addendum to
`.project/active/stop-reinventing-the-parser/run-records/phase2-audit.md` (do not commit) stating
per-finding confirmed/not-confirmed with your evidence, and whether Phase 2 is now fit for
Phase 3 without carried findings (i11 remains carried to close by design). Final message: prose
summary ending with
`ARTIFACT: .project/active/stop-reinventing-the-parser/run-records/phase2-audit.md`.
