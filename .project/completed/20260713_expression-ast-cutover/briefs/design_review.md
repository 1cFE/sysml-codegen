# Brief: Item 13 design review — Calc-Seam Cutover

You are a fresh review session in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`. You did not write this design; review it skeptically.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- An Item 8 implement session may be committing to this tree — write ONLY design-review.md; touch no code.
- Artifact: `design-review.md` in `.project/active/expression-ast-cutover/`.

## Review target
`.project/active/expression-ast-cutover/design.md` (spec + briefs beside it). Note: the design's plan-task-0 question is RESOLVED — agentic-mbse now exposes `extract_expression_ir` (landed with a serialization-equality test, commit 3ad890e in agentic-mbse); review the design as if that entry exists, because it does.

## Ground truth
S2's proofs: `.project/reference/s2-spike/` (probe4_calc_compat — the exact rendering rules: str-literals, inputs./bare classification, `**`→`^` handling, unary minus); the three consumers' code (`extraction/expression_compiler.py`, `computed_attribute_extractor.py:300-306`, snapshot compilation_results carriage); Item 7's `generation/predicate_compiler.py` (the sibling).

## What to probe hardest
1. **The Stage-0 parity harness.** B1 says the landed extractor must re-prove byte-identity (S2 used its own extractor). Is the harness defined precisely: for every corpus calc expression, render via (landed extract_expression_ir → calc-compat renderer) and compare against the EXACT output of today's build_expression_ast+compile_expression — same inputs, same name-set classification? Where do the "supplied name sets" come from at Stage 0 (the same call sites?)?
2. **Dialect completeness.** Diff the compat rules the design specifies against expression_compiler.py's actual behavior: literal formatting (int vs float repr), operator spellings (`^`→`**`), unary minus, the `[`-unit strip, parenthesization, feature-ref classification edge cases (aliases? computed attributes' own dialect at :300-306 — is it the SAME dialect or subtly different?). A missed rule = byte-identity failure mid-implement.
3. **Snapshot replay (Stage 3).** "Verify, don't change": compilation_results carry compiled STRINGS — after the seam flips, newly-captured snapshots carry compat-rendered strings while old snapshots carry old-compiler strings (byte-identical by the gate, so no divergence) — is that reasoning stated and correct? What test proves --from-snapshot byte-identity across the flip?
4. **Deletion completeness (Stage 4).** The grep gate's symbol list: ExpressionAST + build_expression_ast + compile_expression — check for other ExpressionAST-family types/helpers (AST node classes, type imports in data models, snapshot serializer references) the design's deletion list might miss.
5. **Rollback story**: revert-per-stage claimed — check no stage couples with Item 8/9's concurrent landings in a way that makes a clean revert false.

Verdict format: must-fix list (each with why), nice-to-haves, overall verdict (Approved / Approved-with-must-fixes / Rework). Verify against code — do not take the design's word.
