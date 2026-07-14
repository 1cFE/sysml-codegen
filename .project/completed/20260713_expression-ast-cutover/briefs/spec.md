# Brief: Item 13 spec — Calc-Seam Cutover: Retire ExpressionAST

You are the spec stage for Item 13 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- An Item 8 implement session is committing to this tree concurrently — write ONLY spec.md (+ CURRENT_WORK entry); touch no code.
- Artifact: `spec.md` in `.project/active/expression-ast-cutover/`.

## Provenance
- Concept (owner-ratified): Architectural Bets (predicate/IR bullet — extract-and-migrate, staged, S2's decision) + S2 result and carry-forward (1): the ~zero convergence cost was measured at the expression-compiler seam ONLY; aggregation walking, computed attributes, and snapshot compilation_results replay are separate consumers migrating in their own gated steps.
- Epic Item 13: `.project/backlog/epic_constraint_execution.md`.
- Memory-grade lesson (epic risk table): the F4-cutover comparand discipline — each step's parity gate compares against the EXACT function it replaces, not a downstream proxy.
- **Certified upstream**: Item 2 (the shared IR + S2's compat-rendering proof: `.project/reference/s2-spike/` probe4/probe5 reproduce today's calc compiler output byte-identically); Item 7 (predicates already compile from IR — the staged-decision ordering is satisfied).
- Current calc representation: `extraction/expression_compiler.py` (`build_expression_ast` + `compile_expression`, ExpressionAST), aggregation walking (`extraction/hierarchy_resolver.py` agg AST walk), computed attributes, snapshot `compilation_results` replay.

## Scope (epic Item 13 §1–4)
1. **Seam cutover**: compat renderer (input/intermediate classification at render time from supplied name sets) replaces build_expression_ast + compile_expression; byte-identical output for the entire corpus is the gate; keep S2's proof as a test until deletion.
2. **Remaining consumers, staged**: aggregation walking, computed attributes, snapshot compilation_results replay — each its own gated step.
3. **Comparand discipline**: each step's parity gate compares against the exact replaced function.
4. Delete ExpressionAST when the last consumer moves; no silent third representation remains (grep gate); re-capture baselines byte-identically or as a reviewed capture-script diff.

## Out of scope
New expression capability (operators, invocation) — representation migration, not semantics change; predicate compilation (already on IR).

## Success criteria (from the epic)
- Every corpus calc expression renders byte-identically through the IR path before each consumer flips; generated packages byte-identical after each step.
- ExpressionAST deleted; no silent third representation (grep gate).
- Full suite + mypy green; baselines byte-identical or reviewed.
