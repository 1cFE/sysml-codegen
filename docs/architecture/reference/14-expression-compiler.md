# 14 — Expression Compiler

`extraction/expression_compiler.py` compiles calculation-definition outputs using exact declaration identity. Agentic owns neutral expression IR; codegen owns dependency classification, Python rendering, and compilability. This leaf imports neither resolution nor generation.

## Exact compilation

`compile_calc_def_exact(calc_def, dependencies_by_member)` requires UUID-bearing input/output attributes and the definition's UUID-keyed expression/member/name sidecars. The caller supplies exact per-member dependency UUIDs from semantic evidence. A missing identity or dependency fact refuses; names are not a second way to resolve it.

The compiler discovers intermediate members by UUID, builds their dependency graph, and topologically orders them. Cycles mark outputs manual-required. `ExactCalcDefCompilationResult` records definition ID, declared output IDs, execution order, and per-output `ExactCompilationResult` values with expression, input/dependency IDs, and unsupported reason.

## IR and Python rendering

Agentic's `extract_expression_ir()` yields `ExpressionIR` nodes, including feature references, operators, literals, and unit annotations. The mapped metatype and referent evidence distinguish feature chains from operators. See [19-ast-dispatch-invariant](19-ast-dispatch-invariant.md).

`calc_compat_renderer.py` renders a validated IR into a Python expression. UUID-based attachment and dependency discovery happen before names are supplied for Python variable rendering. Rendered expressions pass `ast.parse(..., mode="eval")`; unsupported forms raise `CompilationError` rather than silently emit another interpretation.

- N-ary arithmetic folds operands in source order.
- Unit annotations render the value operand; codegen performs no automatic unit conversion.
- Compilability rolls up from fully compilable through partial/manual requirements. The enumeration is defined in `expression_compiler.py`; generation uses the explicit result rather than guessing from expression text.

## Occurrence aggregation

Occurrence-based sums are compiled by the exact elaborator, using modeled plural occurrences and the same expression evidence boundary. The deleted hierarchy aggregation walker is not an alternate compiler. See [the pipeline overview](00-pipeline-overview.md).

## Evidence and traceability

`tests/conformance/test_exact_compiler_core.py` checks UUID-based attachment, intermediates, and cycles. `tests/conformance/test_expression_evidence_integrity.py` checks the upstream evidence boundary. `tests/conformance/test_expression_compiler.py` covers retained rendering behavior. The [verification matrix](../verification-matrix.md#ec) records the current scope of REQ-EC obligations and retired dispatch claims.
