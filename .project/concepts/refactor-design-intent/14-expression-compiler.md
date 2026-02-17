# 14 — Expression Compiler

## What This Module Does

`extraction/expression_compiler.py` converts raw SysIDE AST nodes from
[`CalculationDefinitionData`](09-data-models.md#extraction-models) output attributes into
Python expression strings. It is a **leaf module** in the extraction layer — no imports from
analysis/, resolution/, or generation/. The compiler answers two questions per CalcDef output:
(1) what Python code computes it, and (2) can the pipeline auto-generate that code or must a
human write it?

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-EC-01 | `FeatureChainExpression` SHALL be checked BEFORE `OperatorExpression` (FCE is OE subtype in SysIDE) | Line 312 checks FCE before line 323 checks OE; see also [19-ast-dispatch-invariant](19-ast-dispatch-invariant.md) |
| REQ-EC-02 | N-ary operands SHALL be left-folded into binary `BINARY_OP` nodes | Left-fold loop at lines 364-374 |
| REQ-EC-03 | Unit annotations (`[` operator) SHALL be stripped; only the value operand is retained | `[` handler at lines 333-340 discards unit, recurses on value |
| REQ-EC-04 | Every compiled expression SHALL be validated via `python_ast.parse(result, mode="eval")` | Validation at lines 217-223 raises `CompilationError` on `SyntaxError` |
| REQ-EC-05 | Cycle detection in dependency graph SHALL mark ALL outputs as `MANUAL_REQUIRED` | `if execution_order is None` block at lines 532-547 |
| REQ-EC-06 | `classify_compilability()` SHALL use worst-case roll-up semantics | Function at lines 263-282: MANUAL > PARTIALLY > FULLY |
| REQ-EC-07 | Undeclared intermediates SHALL be discovered iteratively from `member_expressions` | Iterative discovery loop at lines 520-527 |

---

## The 3-Phase Pipeline

### Phase 1: `build_expression_ast()` -- SysIDE AST to ExpressionAST IR

Accepts a raw syside AST node (duck-typed, from the SysIDE Java bridge)
and produces a clean `ExpressionAST` binary tree. Key transformations:

- **N-ary left-fold**: SysIDE `OperatorExpression` nodes can have 2+
  operands. The builder left-folds: `a + b + c` becomes
  `BinaryOp(+, BinaryOp(+, a, b), c)`.
- **Unit stripping**: The `[` operator (unit annotation like `[kW]`) is
  discarded; recursion continues on the value operand only.
- **Reference classification**: `FeatureReferenceExpression` nodes are
  resolved against three name sets (`input_names`, `output_names`,
  `all_member_names`) to produce `INPUT_REF`, `INTERMEDIATE_REF`, or
  `UNSUPPORTED` nodes.
- **Subtype ordering**: `FeatureChainExpression` is checked *before*
  `OperatorExpression` because FCE is an OE subtype in SysIDE (see
  [19-ast-dispatch-invariant](19-ast-dispatch-invariant.md)). FCE always
  produces UNSUPPORTED (chained paths like `part.attr` are not compilable).

### Phase 2: `compile_expression()` -- ExpressionAST IR to Python string

Pure recursive descent. Each node type maps to a Python fragment:

| Node type | Output pattern |
|-----------|---------------|
| `BINARY_OP` | `(left op right)` -- fully parenthesized |
| `UNARY_OP` | `(-operand)` |
| `LITERAL` | `str(value)` -- e.g. `3.14` |
| `INPUT_REF` | `inputs.param_name` |
| `INTERMEDIATE_REF` | bare name -- e.g. `subtotal` |
| `UNSUPPORTED` | raises `CompilationError` |

Every fragment is validated via `python_ast.parse(result, mode="eval")`.

### Phase 3: Compilability verdict assignment

`classify_compilability()` rolls up per-output verdicts into an overall
CalcDef verdict using worst-case semantics.

---

## ExpressionAST Intermediate Representation

[`ExpressionAST`](09-data-models.md#extraction-models) is a `@dataclass` with tagged-union
design. The `node_type: ExpressionNodeType` discriminant selects which fields apply:

```
ExpressionAST
  node_type: ExpressionNodeType   # discriminant
  operator:  str | None           # BINARY_OP, UNARY_OP
  left:      ExpressionAST | None # BINARY_OP (left), UNARY_OP (operand)
  right:     ExpressionAST | None # BINARY_OP only
  value:     float | int | None   # LITERAL
  input_name: str | None          # INPUT_REF
  intermediate_name: str | None   # INTERMEDIATE_REF
  raw_text:  str | None           # UNSUPPORTED
  reason:    str | None           # UNSUPPORTED
```

Six named constructors: `.binary()`, `.unary()`, `.literal()`,
`.input_ref()`, `.intermediate_ref()`, `.unsupported()`.

`_collect_refs()` walks the tree (pre-order) and returns deduplicated
`(input_refs, intermediate_refs)` lists.

---

## Compilability Verdicts

| Verdict | Enum value | When it applies |
|---------|-----------|-----------------|
| `FULLY_COMPILABLE` | `"fully_compilable"` | All outputs compiled to valid Python. No human edits needed. |
| `PARTIALLY_COMPILABLE` | `"partially_compilable"` | Some outputs compiled, others not. Mix of auto-filled and TODO. |
| `MANUAL_REQUIRED` | `"manual_required"` | UNSUPPORTED node, circular dep, or missing AST. Human must write it. |
| `UNKNOWN` | `"unknown"` | Sentinel for PipelineModules not yet compiled. Never a valid result. |

Roll-up: all FULLY -> overall FULLY. Any MANUAL -> overall MANUAL.
Otherwise PARTIALLY.

---

## The `compile_calc_def()` Orchestrator

Compiles all outputs of a CalcDef in dependency order:

1. **Collect name sets** from `calc_def.input_attributes` / `.output_attributes`.
2. **Build dependency graph**: For each output, extract feature refs from
   its syside AST. Refs to other outputs/members become edges; refs to
   inputs are skipped.
3. **Discover undeclared intermediates**: Members not in input or output
   sets but referenced by an output. Added iteratively -- a discovered
   intermediate may reference further undeclared intermediates.
4. **Topological sort** (Kahn's algorithm, deterministic via `sorted()`).
   Cycle detected -> all outputs get `MANUAL_REQUIRED`.
5. **Compile in order**: `build_expression_ast()` then `compile_expression()`
   per name. Result stored as `CompilationResult`.
6. **Roll up** via `classify_compilability()`.

Returns [`CalcDefCompilationResult`](09-data-models.md#extraction-models) with `calc_def_name`,
`overall_compilability`, `output_results: list[CompilationResult]`,
and `execution_order: list[str]`.

---

## Concrete Example

SysML input:

```sysml
calc def CostCalc {
    in capacity : Real;
    in cost_per_kwh : Real;
    return total_cost : Real = capacity * cost_per_kwh;
}
```

**Phase 1 input** -- the `expression_asts` dict contains:

```
{"total_cost": <OperatorExpression operator="*" operands=[
    <FeatureReferenceExpression referent.name="capacity">,
    <FeatureReferenceExpression referent.name="cost_per_kwh">
]>}
```

**Phase 1 output** -- `build_expression_ast()` produces:

```
ExpressionAST(BINARY_OP, operator="*",
  left  = ExpressionAST(INPUT_REF, input_name="capacity"),
  right = ExpressionAST(INPUT_REF, input_name="cost_per_kwh"))
```

Both operands resolve as `INPUT_REF` because their names are in `input_names`.

**Phase 2 output** -- `compile_expression()` recurses:

```
left  -> "inputs.capacity"
right -> "inputs.cost_per_kwh"
root  -> "(inputs.capacity * inputs.cost_per_kwh)"
```

**Phase 3** -- single output, no UNSUPPORTED nodes.
Verdict: `FULLY_COMPILABLE`.

---

## Reference Handling

### Input references -> `inputs.param_name`

A `FeatureReferenceExpression` whose `_sanitize_name()`-d name is in
`input_names` becomes `INPUT_REF`. `compile_expression()` renders it as
`inputs.<name>`, mapping to the Pydantic [input schema](22-output-schema-rules.md) at runtime.
`_sanitize_name()` strips quotes, replaces special chars with underscores,
and collapses runs to match names in [`CalculationDefinitionData`](09-data-models.md#extraction-models).

### Intermediate references -> bare name or undeclared discovery

Two cases for intermediates:

1. **Output-to-output**: Output `subtotal` referenced by output `total`
   becomes `INTERMEDIATE_REF("subtotal")`, compiled to bare `subtotal`.
   Topological sort ensures correct evaluation order.

2. **Undeclared intermediate**: A member in `all_member_names` not in
   input or output sets. The orchestrator discovers it during dep-graph
   construction, marks `is_undeclared_intermediate=True`, and compiles
   its expression from `member_expressions`.

Unresolved names (not in any name set) become `UNSUPPORTED` with reason
`"unresolved reference: <name>"`.

## Two AST Processing Pipelines

This system has TWO separate expression-to-Python paths:

| Aspect | Expression Compiler (this doc) | Aggregation Walker ([13](13-aggregation-scoping.md), [25](25-hierarchy-resolver.md)) |
|--------|------|------|
| **Scope** | CalcDef outputs, FORMULA attributes | Aggregation expressions (sum/count) |
| **Input** | SysIDE AST nodes | SysIDE AST nodes |
| **Output** | `ExpressionAST` IR → Python string | Text string (direct transform) |
| **Operators** | 7 arithmetic (+, -, *, /, **, ^, [) | 12+ (arithmetic + comparison + logical) |
| **FCE handling** | → INPUT_REF (compilable) | → SingletonTerm (wired to upstream) |
| **OE handling** | → BinaryOp (recursive) | → text concatenation |
| **Shared invariant** | [FCE before OE](19-ast-dispatch-invariant.md) | [FCE before OE](19-ast-dispatch-invariant.md) |

These pipelines exist separately because they serve different purposes: the compiler
produces executable Python expressions; the walker decomposes aggregation math into
typed terms (SumTerm, SingletonTerm, LocalTerm) for module wiring.

## Related Documents

- **Upstream**: [01-extraction](01-extraction.md) — provides `CalculationDefinitionData` with AST nodes and member expressions
- **Invariant**: [19-ast-dispatch-invariant](19-ast-dispatch-invariant.md) — FCE-before-OE subtype ordering rule (REQ-EC-01)
- **Downstream**: [08-generation](08-generation.md) — uses `CalcDefCompilationResult` to decide auto-fill vs TODO stubs, [23-smart-regen-preservation](23-smart-regen-preservation.md) — preserves handwritten code when compilability is MANUAL_REQUIRED
- **Cross-cutting**: [16-computed-attributes](16-computed-attributes.md) — FORMULA modules also use compilability verdicts, [05-module-factory](05-module-factory.md) — reads `compilability` from `AggregationExpressionData`
- **Data models**: [09-data-models](09-data-models.md) — `ExpressionAST`, `CalcDefCompilationResult`, `Compilability`
