# Brief: Item 13 design — Calc-Seam Cutover

You are the design stage for Item 13 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- An Item 8 implement session may be committing to this tree — write ONLY design.md (+ CURRENT_WORK entry); touch no code.
- Artifact: `design.md` in `.project/active/expression-ast-cutover/`.

## Input
- Spec (committed): `.project/active/expression-ast-cutover/spec.md` — Option A scope (three real consumers; shared_aggregation is a Non-Goal), comparand discipline, post-Item-8 baseline, staged per-consumer gates are fixed.
- S2's proven compat rendering: `.project/reference/s2-spike/` (probe4_calc_compat + probe5_committed_fixtures — byte-identical reproduction of today's compiler output over the corpus).
- The three consumers' real code: `extraction/expression_compiler.py` (build_expression_ast + compile_expression + the ExpressionAST types), `extraction/computed_attribute_extractor.py:300-306`, snapshot `compilation_results` (loader/serializer — result carriage, shape held constant).
- Item 7's predicate_compiler.py (the IR-consuming precedent in this repo).

## Design guidance (orchestrator, agent-grade)
- Design the compat renderer's production home (S2's probe4 logic productionized — where does it live relative to predicate_compiler? One IR→Python module with calc-compat and predicate modes, or two siblings? Decide with rejected alternative).
- Stage plan per the spec: seam first (keep S2's byte-identity proof as a committed test until deletion), then computed attributes, then the snapshot-replay verification, then deletion + grep gate. Each stage's parity comparand = the exact replaced function's output (the F4 rule) — name the comparand per stage.
- Byte-identity is the whole game: the corpus gate runs per stage; the design must say exactly how each stage's parity test captures before/after (function-level golden comparison, not package-level only).
- Extraction happens where the license lives — note the license env incantation for the plan.
- A skeptical design_review follows; this item retires load-bearing code — make the deletion order and rollback story explicit.
