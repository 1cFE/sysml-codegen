# 19 -- AST Dispatch Invariant: FCE Before OE

## The Problem

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

**Root cause of Bug A** (commit `20b720e`): Three dispatch sites checked OE
before FCE, causing 37 aggregation inputs to be misclassified as LocalTerms
instead of SingletonTerms. This broke aggregation wiring in the
[hierarchy resolver](13-aggregation-scoping.md).

---

## Requirements

| ID | Requirement | Traces to | Verified by |
|----|-------------|-----------|-------------|
| REQ-AST-01 | Every `is_instance()` dispatch that checks both FCE and OE SHALL check FCE first | Bug A (20b720e) | `grep -n` ordering audit across all dispatch sites |
| REQ-AST-02 | Every dispatch site checking both FCE and OE SHALL include a comment: "MUST be before OperatorExpression" | Bug A prevention | `grep` for comment at each dual-check site |
| REQ-AST-03 | The canonical dispatch ordering SHALL be: FCE, OE, FRE, Literal | Bug A prevention | All dispatch sites follow this order |
| REQ-AST-04 | New dispatch sites SHALL follow REQ-AST-03 ordering | Bug A prevention | Code review checklist |
| REQ-AST-05 | `hierarchy_resolver._walk_aggregation_ast()` SHALL classify FCE nodes as `SingletonTerm` (not `LocalTerm`) | Bug A root cause | `SingletonTerm` count matches FCE node count in aggregation AST |
| REQ-AST-06 | `expression_compiler.build_expression_ast()` SHALL return `unsupported` for FCE (not "unsupported operator: .") | Bug A symptom | No "unsupported operator: ." in diagnostics |
| REQ-AST-07 | `expression_utils.reconstruct_expression()` SHALL return `"name.attr"` for FCE (not `".(name)"`) | Bug A symptom | Reconstructed expressions match `name.attr` format |

---

## The Canonical Dispatch Ordering

```
1. FeatureChainExpression   -- most specific (subtype of OE)
2. OperatorExpression       -- generic operator (+, *, -)
3. FeatureReferenceExpression  -- bare name reference
4. InvocationExpression     -- function call (e.g., sum())
5. Literal*                 -- concrete values
```

Why this order: FCE must precede OE due to the subtype relationship. FRE is
independent (no overlap with FCE or OE) but placed after both by convention.
Literals have no subtype overlaps and go last.

---

## Dispatch Site Audit

The codebase has **8 files** with `is_instance()` dispatch on expression types.
Three were the Bug A sites fixed in commit `20b720e`.

### Bug A Sites (Fixed)

| File | Function | Lines | Invariant comment? | Status |
|------|----------|-------|--------------------|--------|
| `expression_utils.py` | `reconstruct_expression` | 48, 51, 54 | Yes | **FIXED** |
| `expression_compiler.py` | `build_expression_ast` | 316, 323, 381 | Yes | **FIXED** |
| `hierarchy_resolver.py` | `_walk_aggregation_ast` | 331, 338, 361 | Yes | **FIXED** |

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

### Other Sites (Correct)

| File | Function | Lines | Checks both FCE+OE? | Status |
|------|----------|-------|----------------------|--------|
| `usage_extractor.py` | `extract_binding_info` | 521-557 | Yes (elif) | CORRECT |
| `parameter_groups.py` | `_extract_default_value` | 163-191 | Yes (elif) | CORRECT |
| `hierarchy_resolver.py` | `extract_redefinition_value` | 105-116 | No (FCE+FRE only) | N/A |
| `hierarchy_resolver.py` | `_unwrap_invocation` | 294-296 | No (FCE+FRE only) | N/A |
| `extractor.py` | `_parse_expression_to_path` | 276-295 | No (FCE+FRE only) | N/A |

Sites using `elif` chains (parameter_groups.py, usage_extractor.py) are safe
because first-match-wins prevents misclassification. However, they should still
follow canonical ordering for consistency (REQ-AST-03).

---

## Concrete Example: Before and After Bug A Fix

**SysML aggregation expression**: `pv_module.capital_cost + inverter.capital_cost`

**Before fix** (OE checked first):
```
Node: FCE "pv_module.capital_cost"
  is_instance("OperatorExpression") → True (FCE is subtype!)
  → enters OE handler → recurses on operands
  → finds FRE "capital_cost" → classifies as LocalTerm
  Result: LocalTerm(attribute_name="capital_cost")  ← WRONG
```

**After fix** (FCE checked first):
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
