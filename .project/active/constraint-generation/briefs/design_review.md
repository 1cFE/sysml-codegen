# Brief: Item 7 design review — Constraint Generation

You are a fresh review session in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`. You did not write this design; review it skeptically.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `design-review.md` in `.project/active/constraint-generation/`.

## Review target
`.project/active/constraint-generation/design.md` (spec, spec-review, briefs, [OWNER] gate evidence beside it).

## Ground truth
S4's `s4_lib.py` + findings; S2 probes (Kleene oracle); Item 5's `constraint_lowering.py` (esp. the `if eligible:` gate at ~761 that D11 touches, and `extend_graph_with_constraints`); Item 6's seams; the generation templates (`generation/`); the sealed-package fixture in teax as the reference output.

## What to probe hardest
1. **D1 exit-ancestry under a USER-narrowed exit.** Explicit membership = report channel unioned into the exit set. Walk how exits are actually selected/emitted today (cli/YAML): if a user narrows exits (targets list, exit config), does the union genuinely survive every path, or only the default capture-everything path? The falsifying test's control leg must be constructible — check it is.
2. **D3 shared predicates module.** The compile-once/N-classes bridge: verify the same-IR generation guard still binds per-class (each class's predicate_ir serialization-equal to catalog) when the compiled function is shared — what exactly is asserted for instance 2..N? The two-instance case the author flagged: walk it concretely.
3. **D11 (the Item 5 touch).** Is relaxing the eligible gate actually required for the zero-assertion aggregator (vs. calling extend_graph unconditionally when facts exist), and does the relaxation risk unassessed records producing modules? The constraint-free corpus byte-identity claim under D11: verify the guard logic keeps constraint-free models on the untouched path.
4. **D7/D8 skip decisions.** test-gen/stencil/backlog-report skip for constraint kinds: check each skip against what those emitters do for other kinds — does skipping test-gen leave the generated constraint modules untested by the package's own test scaffolding (is that consistent with how aggregation modules are treated)?
5. **Kleene compilation fidelity.** The compiled-Python shape vs S2's oracle: three-valued leaf/propagation, negated polarity status, margin sign, boundary-zero — is each rendered semantic tested at the compiler level (not just end-to-end)?
6. **D10 execution lane.** In-process execute_pipeline in the agentic-mbse venv: reconcile with how Items 10-12 run simkit (teax venv) — will the lane actually work in this repo's test environment (imports, license)?

Verdict format: must-fix list (each with why), nice-to-haves, overall verdict (Approved / Approved-with-must-fixes / Rework). Verify against code — do not take the design's word.
