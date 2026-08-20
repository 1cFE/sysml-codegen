# Phase 2 fix round — audit findings

The independent Phase 2 audit returned **Pass with findings**
(`run-records/phase2-audit.md`). Close the following in your worktree
(`/tmp/stop-parser-rev2/worktrees/agentic-mbse`, branch `stop-parser-evidence-r2`), tests first
where a finding lacks one. Same hard constraints as your original brief: no PDF/paid suites, no
other checkout, scoped strict stays zero, baselines stay non-regressed.

**M1 (Major — must close).** The design's shared depth budget covers
`inspect_reference_uses`, `extract_expression_ir`, and expression reconstruction; only the first
(plus `traverse_expression`) got it. `extract_expression_ir`
(`constraint_extraction.py:663`) and `reconstruct_expression` (`expression.py:298`) raise bare
`RecursionError` on self-nesting expressions — reproduced by the auditor. Wire the same
non-caller-selectable `MAX_EXPRESSION_DEPTH` into both so exhaustion raises the named
`EXPRESSION_DEPTH_EXHAUSTED` failure, and add kept tests for both entries.

**m3 (design conformance — close at the boundary, not by tier filtering).** The design says a
structural unit annotation "visits its value operand and validates its shape but never emits the
unit operand as a data reference." `inspect_reference_uses` emits it, and the downstream tier
filter would pass a **project-scoped** unit (`3.0 [MyUnits::widget]`) through as a design
dependency. Stop emitting the unit operand at the inspection boundary; keep validating its shape;
add a project-scoped-unit test proving it.

**m2.** The ownership gate decides scope by substring (`ADAPTER_IMPORT in path.read_text()`).
Make it structural: parse imports (AST) instead of text matching. Keep both anti-vacuity tests
firing.

**m4.** Narrow the `except Exception: pytest.skip` around `SysideAdapter.load_model` in
`test_reference_use.py` (two sites) to the specific load failure, or assert the model loaded.

**m6.** `level2_structure.py:280` `_has_defined_value` is dead production code kept alive by a
`hasattr` test. Delete both, or record in the phase record exactly why it stays.

**m7.** Add the `getattr(node, "...")` spelling to the scanner's anti-vacuity mutant set so that
detection branch is tested.

**m5 (record corrections).** In plan.md's Phase 2 completion section: ownership file is **14
passed** not 12; the "221 passed" artifact-isolated figure must name its exact file set or be
replaced with a reproducible figure.

**i10 (cheap, take it).** Drop the `or ""` in `_document_tier_name` (`reference_use.py:263`) so a
tier-less target propagates as the named adapter failure its docstring promises.

Leave i8 as-is; i11 is carried to close per the audit. Do not re-litigate what the audit
confirmed sound.

When done: rerun the focused suites, scoped strict, fast suite (expect the 18-node baseline), and
the wheel check if any public surface moved. Append an "Audit-fix pass" note to the Phase 2
completion section (commits, what closed, test results) and commit it in the docs checkout. Final
message: prose summary of each finding's closure ending with
`ARTIFACT: .project/active/stop-reinventing-the-parser/plan.md`.
