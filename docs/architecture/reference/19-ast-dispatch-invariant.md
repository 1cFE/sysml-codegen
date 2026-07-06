# 19 -- AST Dispatch Invariant: FCE Before OE

## Design Constraint

SysIDE's type hierarchy has a subtype relationship: `FeatureChainExpression`
(FCE) is a subtype of `OperatorExpression` (OE). When Python code calls
`SysideAdapter.is_instance(node, "OperatorExpression")`, it returns `True`
for both OE nodes AND FCE nodes. If OE is checked before FCE, feature chains
like `instance.attribute` are misclassified as generic operators.

```
Type Hierarchy (SysIDE):
  Expression
  +-- OperatorExpression
  |   +-- FeatureChainExpression   <-- subtype! both is_instance() checks True
  +-- FeatureReferenceExpression   <-- independent, no overlap
  +-- InvocationExpression
  +-- Literal* (Integer, Rational, Real, Boolean, String)
```

**The invariant**: Always check FCE before OE. No exceptions.

**Consequence of violation**: Dispatch sites that check OE before FCE cause
aggregation inputs to be misclassified as LocalTerms instead of SingletonTerms,
breaking aggregation wiring in the
[hierarchy resolver](13-aggregation-scoping.md).

---

## Requirements

| ID | Requirement | Traces to | Verified by |
|----|-------------|-----------|-------------|
| REQ-AST-01 | Every `is_instance()` dispatch that checks both FCE and OE SHALL check FCE first | Subtype misclassification | `grep -n` ordering audit across all dispatch sites |
| REQ-AST-02 | Every dispatch site checking both FCE and OE SHALL include a comment: "MUST be before OperatorExpression" | Prevent regressions | `grep` for comment at each dual-check site |
| REQ-AST-03 | Among the reference/operator branches the ordering SHALL be FCE, OE, FRE; and in `reconstruct_expression` all literal/null branches SHALL dispatch **before** the invocation catch-all | Consistent dispatch; literals must not hit the `.function` catch-all | `test_canonical_ordering_fce_oe_fre` (FCE<OE<FRE); real-AST + totality guard (literal-before-invocation) |
| REQ-AST-04 | New dispatch sites SHALL follow REQ-AST-03 ordering | Consistent dispatch | Code review checklist |
| REQ-AST-08 | `reconstruct_expression` SHALL dispatch all literal and `NullExpression` branches (via `is_instance`) before the invocation catch-all | Every node carries a derived `.function`, so the catch-all must not precede literals | License-gated real-AST test + offline literal-totality guard |
| REQ-AST-09 | `reconstruct_operator_expression` SHALL parenthesize a child operand (binary or unary) iff it binds looser than its parent, or equal and on the associativity-unfavored side (precedence-aware) | Preserve meaning-changing grouping in displayed math | Real-AST repro + branch fixture; offline hand-trace unit tests |
| REQ-AST-05 | `hierarchy_resolver._walk_aggregation_ast()` SHALL classify FCE nodes as `SingletonTerm` (not `LocalTerm`) | Correct aggregation wiring | `SingletonTerm` count matches FCE node count in aggregation AST |
| REQ-AST-06 | `expression_compiler.build_expression_ast()` SHALL return `unsupported` for FCE (not "unsupported operator: .") | Correct diagnostics | No "unsupported operator: ." in diagnostics |
| REQ-AST-07 | `expression_utils.reconstruct_expression()` SHALL return `"name.attr"` for FCE (not `".(name)"`) | Correct reconstruction | Reconstructed expressions match `name.attr` format |

---

## The Canonical Dispatch Ordering

```
1. FeatureChainExpression   -- most specific (subtype of OE)
2. OperatorExpression       -- generic operator (+, *, -)
3. FeatureReferenceExpression  -- bare name reference
4. Literal* / NullExpression -- concrete values (via is_instance)
5. InvocationExpression     -- function call (e.g., sum()) -- catch-all, LAST
```

Why this order: FCE must precede OE due to the subtype relationship. FRE is
independent (no overlap with FCE or OE) but placed after both by convention.
The literal/null branches MUST dispatch **before** the invocation catch-all
(REQ-AST-08): every SysIDE node carries a derived KerML `.function`, so the
catch-all (`hasattr(expr_node, "function")`) matches every literal. Placed after
it, the literal branches are dead code and each literal stringifies to
`LiteralRationalEvaluation()`. The catch-all is therefore the last branch.

**Known deviation — `_walk_aggregation_ast`.** `_walk_aggregation_ast` in
`extraction/hierarchy_resolver.py` keeps the old literal-after-invocation ordering
and carries the same latent bug: an aggregation literal is mis-dispatched to the
invocation catch-all and marked unsupported, so its trailing `reconstruct_expression`
delegation (the `is_literal_expression` branch) is dead. It is **not** fixed here — that touches an executable
aggregation path (out of the display-only scope of REQ-AST-08/-09). Filed to
BACKLOG.

---

## Dispatch Sites

The codebase has **8 multi-type dispatch functions across 6 files** that check
two or more of FCE / OE / FRE via `is_instance()`.

### Dual-Check Sites (FCE + OE)

These three sites check both FCE and OE and include the invariant comment:

| File | Function | Invariant comment? |
|------|----------|--------------------|
| `expression_utils.py` | `reconstruct_expression` | Yes |
| `expression_compiler.py` | `build_expression_ast` | Yes |
| `hierarchy_resolver.py` | `_walk_aggregation_ast` | Yes |

Example from `expression_utils.py` (the pattern all sites must follow):
```python
# FeatureChainExpression MUST be before OperatorExpression -- FCE is a
# subtype of OE in SysIDE's type system.
if SysideAdapter.is_instance(expr_node, "FeatureChainExpression"):     # 1st
    return extract_feature_chain_name(expr_node)
if SysideAdapter.is_instance(expr_node, "OperatorExpression"):         # 2nd
    return reconstruct_operator_expression(expr_node)
if SysideAdapter.is_instance(expr_node, "FeatureReferenceExpression"): # 3rd
    return extract_feature_reference_name(expr_node)
```

### Other Sites

| File | Function | Checks both FCE+OE? |
|------|----------|----------------------|
| `usage_extractor.py` | `_extract_single_binding` | Yes (elif) |
| `parameter_groups.py` | `_extract_default_value` | Yes (elif) |
| `hierarchy_resolver.py` | `_extract_single_redefinition` | No (FCE+FRE only) |
| `hierarchy_resolver.py` | `_unwrap_invocation` | No (FCE+FRE only) |
| `extractor.py` | `_parse_expression_to_path` | No (FCE+FRE only) |

Sites using `elif` chains (parameter_groups.py, usage_extractor.py) are safe
because first-match-wins prevents misclassification. However, they should still
follow canonical ordering for consistency (REQ-AST-03).

In addition to the 8 multi-type dispatch functions above, single-type helper
functions also call `is_instance()` on expression types (checking only FCE,
only FRE, or only OE — e.g. `extract_feature_chain_segments` and `binary_op_of`
in `expression_utils.py`). These are not dispatch sites -- they check a single
type and cannot misclassify. Item 6's literal branches added further
`is_instance()` calls, so this doc no longer tracks a total call-site count;
the audited dual-check inventory is `DUAL_CHECK_SITES` in
`tests/conformance/test_ast_dispatch_invariant.py`.

---

## Concrete Example: Why Ordering Matters

**SysML aggregation expression**: `pv_module.capital_cost + inverter.capital_cost`

**Wrong ordering** (OE checked first):
```
Node: FCE "pv_module.capital_cost"
  is_instance("OperatorExpression") → True (FCE is subtype!)
  → enters OE handler → recurses on operands
  → finds FRE "capital_cost" → classifies as LocalTerm
  Result: LocalTerm(attribute_name="capital_cost")  ← WRONG
```

**Correct ordering** (FCE checked first):
```
Node: FCE "pv_module.capital_cost"
  is_instance("FeatureChainExpression") → True
  → enters FCE handler → extracts chain name
  Result: SingletonTerm(source_path="pv_module.capital_cost")  ← CORRECT
```

The SingletonTerm feeds into [output registry](10-output-registry.md) lookup
(Key_C scoped chain), which wires the aggregation input to the upstream
module's output channel. The LocalTerm classification would attempt sibling
attribute lookup, which fails or produces wrong wiring.

---

## Data Models

| Type | File | Role |
|------|------|------|
| `FeatureChainExpression` | SysIDE (agentic-mbse) | `a.b` dotted access |
| `OperatorExpression` | SysIDE (agentic-mbse) | `a + b`, `a * b` operators |
| `FeatureReferenceExpression` | SysIDE (agentic-mbse) | `param_name` bare reference |
| `SingletonTerm` | `extraction/data_models.py` | Aggregation term from FCE |
| `LocalTerm` | `extraction/data_models.py` | Aggregation term from FRE |
| `SysideAdapter.is_instance()` | `agentic_mbse.sysml.syside_adapter` | Type check function |

---

## Related Documents

- **Upstream**: [13-aggregation-scoping](13-aggregation-scoping.md) -- where SingletonTerm/LocalTerm classification feeds aggregation wiring
- **Upstream**: [14-expression-compiler](14-expression-compiler.md) -- expression AST compilation uses same dispatch
- **Downstream**: [10-output-registry](10-output-registry.md) -- SingletonTerm source_path drives Key_C lookup
- **Downstream**: [05-module-factory](05-module-factory.md) -- term types determine module input construction
- **Pipeline context**: [00-pipeline-overview](00-pipeline-overview.md) -- where dispatch sits in the overall pipeline
- **Data models**: [09-data-models](09-data-models.md) -- SingletonTerm, LocalTerm, SumTerm field definitions
