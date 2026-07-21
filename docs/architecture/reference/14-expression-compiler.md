# 14 — Expression Compiler

## What This Module Does

`extraction/expression_compiler.py` converts raw SysIDE AST nodes from
[`CalculationDefinitionData`](09-data-models.md#extraction-models) output attributes into
Python expression strings. It is a **leaf module** in the extraction layer — no imports from
analysis/, resolution/, or generation/. The compiler answers two questions per CalcDef output:
(1) what Python code computes it, and (2) can the pipeline auto-generate that code or must a
human write it?

It does this in two delegated steps. It does **not** build its own syntax tree anymore.
For each output it obtains an [`ExpressionIR`](#expressionir-intermediate-representation)
tree from agentic-mbse's `extract_expression_ir()`, then renders that tree to a Python string
via `extraction/calc_compat_renderer.py` (`render_calc_expression()`). `compile_calc_def()`
orchestrates the two steps across a CalcDef's outputs in dependency order and rolls up the
compilability verdict. (This replaced the retired in-repo `build_expression_ast()` /
`compile_expression()` / `ExpressionAST` path in CONSTRAINT-EXEC Item 13, which had its own
private syntax tree.)

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-EC-01 | A feature chain in a CalcDef output SHALL NOT be misread as an operator | The IR represents a feature chain as a `FeatureReferenceNode` carrying `chain_segments` (never an `OperatorNode`), so `_render_reference()` rejects it as unsupported. FCE/OE subtype ordering is enforced upstream during IR extraction (agentic-mbse `extract_expression_ir`); see [19-ast-dispatch-invariant](19-ast-dispatch-invariant.md) |
| REQ-EC-02 | N-ary operands SHALL be left-folded into nested binary operations | Left-fold loop over `node.operands` in `_render_operator()` (`calc_compat_renderer.py`) |
| REQ-EC-03 | Unit annotations (`[` operator) SHALL be stripped; only the value operand is retained | `UnitAnnotationNode` is rendered by recursing on `node.value` in `_render()` — the unit is dropped structurally |
| REQ-EC-04 | Every compiled expression SHALL be validated via `python_ast.parse(result, mode="eval")` | Validation at the end of `render_calc_expression()` raises `CompilationError` on `SyntaxError` |
| REQ-EC-05 | Cycle detection in dependency graph SHALL mark ALL outputs as `MANUAL_REQUIRED` | `if execution_order is None` block in `compile_calc_def()` |
| REQ-EC-06 | `classify_compilability()` SHALL use worst-case roll-up semantics | `classify_compilability()`: MANUAL > PARTIALLY > FULLY |
| REQ-EC-07 | Undeclared intermediates SHALL be discovered iteratively from `member_expressions` | Iterative discovery loop (`while to_process`) in `compile_calc_def()` |

---

## The 3-Step Pipeline

### Step 1: `extract_expression_ir()` -- SysIDE AST to ExpressionIR

A raw syside AST node is converted to an [`ExpressionIR`](#expressionir-intermediate-representation)
tree by agentic-mbse's `extract_expression_ir()` (`agentic_mbse.sysml.constraint_extraction`).
This is where the SysIDE type dispatch lives, including the FCE-before-OE subtype ordering
(see [19-ast-dispatch-invariant](19-ast-dispatch-invariant.md)): a feature chain comes back as
a `FeatureReferenceNode` carrying `chain_segments`, an operator as an `OperatorNode`, a unit
annotation as a `UnitAnnotationNode`, and so on. The IR is agentic-mbse-owned and carries
feature references **unclassified** — a reference is just a `source_name`, not yet resolved to
input vs intermediate.

### Step 2: `render_calc_expression()` -- ExpressionIR to Python string

Pure recursive descent in `extraction/calc_compat_renderer.py`. Each IR node kind maps to a
Python fragment. Because the IR leaves references unclassified, classifying one as an input or
an intermediate is **calc-specific policy applied here at render time**, from the caller's name
sets — not baked into the tree:

| IR node kind | Output pattern |
|-----------|---------------|
| `OperatorNode` (n-ary) | left-folded `(left op right)` -- fully parenthesized (`^` → `**`) |
| `OperatorNode` (unary) | `(-operand)` |
| `LiteralNode` | `str(value)` -- e.g. `3.14` (keyed on the syside literal kind) |
| `FeatureReferenceNode`, name in `input_names` | `inputs.param_name` |
| `FeatureReferenceNode`, name in `member_names` | bare name -- e.g. `subtotal` |
| `FeatureReferenceNode` with `chain_segments`, or an unresolved name | raises `CompilationError` |
| `UnitAnnotationNode` | recurses on `node.value` (unit dropped) |
| `InvocationNode` / `UnsupportedNode` | raises `CompilationError` |

The final string is validated via `python_ast.parse(result, mode="eval")`. `render_calc_expression`
reproduces the retired compiler's dialect byte-for-byte (frozen in
`tests/fixtures/golden/calc_compat_parity_golden.json`).

### Step 3: Compilability verdict assignment

`classify_compilability()` rolls up per-output verdicts into an overall
CalcDef verdict using worst-case semantics.

---

## ExpressionIR Intermediate Representation

`ExpressionIR` (`agentic_mbse.sysml.expression_ir`) is a `kind`-tagged union of one dataclass
per algebra kind — the same production predicate tree the constraint machinery uses. The
renderer dispatches on the node class via `isinstance`, not on a discriminant string:

```
ExpressionIR = (
    LiteralNode          # a literal leaf: LiteralFact + OperandTypeFact
  | FeatureReferenceNode # a reference leaf: FeatureReferenceFact (carries chain_segments)
  | OperatorNode         # n-ary: operator: str, operands: list[ExpressionIR]
  | UnitAnnotationNode   # a `[` unit annotation: value + unit_text
  | InvocationNode       # a resolved function call: function_qn + arguments
  | UnsupportedNode      # explicit fallback: node_kind, diagnostic, source_text
)
```

Every node also carries `kind` (the union tag) and `schema_version`. References are
**unclassified** in the tree — `FeatureReferenceNode.reference.source_name` is a bare name;
the renderer decides `inputs.x` vs bare `x` from the caller's name sets (this is the key
difference from the retired build-time-classified `ExpressionAST`).

`collect_calc_refs(ir, input_names, member_names)` (`calc_compat_renderer.py`) walks the tree
(pre-order, first-occurrence deduplicated) and returns `(input_refs, intermediate_refs)` lists.

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
5. **Compile in order**: `extract_expression_ir()` (agentic-mbse) then
   `render_calc_expression()` per name. Result stored as `CompilationResult`.
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

**Step 1 input** -- the `expression_asts` dict contains:

```
{"total_cost": <OperatorExpression operator="*" operands=[
    <FeatureReferenceExpression referent.name="capacity">,
    <FeatureReferenceExpression referent.name="cost_per_kwh">
]>}
```

**Step 1 output** -- `extract_expression_ir()` produces (references still unclassified):

```
OperatorNode(operator="*", operands=[
  FeatureReferenceNode(source_name="capacity"),
  FeatureReferenceNode(source_name="cost_per_kwh"),
])
```

**Step 2 output** -- `render_calc_expression(ir, input_names={"capacity", "cost_per_kwh"}, member_names=set())`
classifies each reference at render time. Both names are in `input_names`, so both become
`inputs.<name>`:

```
capacity      -> "inputs.capacity"
cost_per_kwh  -> "inputs.cost_per_kwh"
root          -> "(inputs.capacity * inputs.cost_per_kwh)"
```

**Step 3** -- single output, no unsupported nodes.
Verdict: `FULLY_COMPILABLE`.

---

## Reference Handling

### Input references -> `inputs.param_name`

A `FeatureReferenceNode` whose `_sanitize_name()`-d `source_name` is in `input_names` is
rendered by `_render_reference()` as `inputs.<name>`, mapping to the Pydantic
[input schema](22-output-schema-rules.md) at runtime. `_sanitize_name()` strips quotes,
replaces special chars with underscores, and collapses runs to match names in
[`CalculationDefinitionData`](09-data-models.md#extraction-models).

### Intermediate references -> bare name or undeclared discovery

Two cases for intermediates:

1. **Output-to-output**: Output `subtotal` referenced by output `total` is in
   `member_names`, so `_render_reference()` renders it as bare `subtotal`.
   Topological sort ensures correct evaluation order.

2. **Undeclared intermediate**: A member in `all_member_names` not in
   input or output sets. The orchestrator discovers it during dep-graph
   construction, marks `is_undeclared_intermediate=True`, and compiles
   its expression from `member_expressions`.

A name in neither `input_names` nor `member_names` raises `CompilationError`
(`"unresolved reference: <name>"`), which `compile_calc_def()` catches and records as
`MANUAL_REQUIRED` for that output. A `FeatureReferenceNode` carrying `chain_segments` (a
feature chain like `part.attr`) is likewise rejected — chains are not compilable in a CalcDef
output.

## Two AST Processing Pipelines

This system has TWO separate expression-to-Python paths:

| Aspect | Expression Compiler (this doc) | Aggregation Walker ([13](13-aggregation-scoping.md), [25](25-hierarchy-resolver.md)) |
|--------|------|------|
| **Scope** | CalcDef outputs, FORMULA attributes | Aggregation expressions (sum/count) |
| **Input** | SysIDE AST nodes | SysIDE AST nodes |
| **Output** | `ExpressionIR` → Python string | Text string (direct transform) |
| **Operators** | 7 arithmetic (+, -, *, /, **, ^, [) | 12+ (arithmetic + comparison + logical) |
| **FCE handling** | → UNSUPPORTED (not compilable) | → SingletonTerm (wired to upstream) |
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
- **Data models**: [09-data-models](09-data-models.md) — `CalcDefCompilationResult`, `Compilability`; `ExpressionIR` is agentic-mbse-owned (`agentic_mbse.sysml.expression_ir`)
