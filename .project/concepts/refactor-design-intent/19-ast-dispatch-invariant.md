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

---

## Where This Matters: All 9 Dispatch Sites

The codebase has 9 files with `is_instance()` dispatch on expression types.
Each site must check FCE before OE when both are tested.

### extraction/expression_utils.py (lines 48-54)

```python
if SysideAdapter.is_instance(expr_node, "FeatureChainExpression"):     # 1st
    return extracted_feature_chain_name(expr_node)
elif SysideAdapter.is_instance(expr_node, "OperatorExpression"):       # 2nd
    return reconstruct_operator_expression(expr_node)
elif SysideAdapter.is_instance(expr_node, "FeatureReferenceExpression"):
    return extracted_feature_reference_name(expr_node)
```

Status: **CORRECT**. FCE first, OE second.

### extraction/expression_compiler.py (lines 316-381)

```python
# Line 313: "MUST be before OperatorExpression"
if SysideAdapter.is_instance(syside_node, "FeatureChainExpression"):   # 1st
    ...  # unsupported classification
elif SysideAdapter.is_instance(syside_node, "OperatorExpression"):     # 2nd
    ...  # operator handling with unit stripping
elif SysideAdapter.is_instance(syside_node, "FeatureReferenceExpression"):
    ...  # input_ref or intermediate_ref
```

Status: **CORRECT**. Explicit comment documents the invariant.

### extraction/hierarchy_resolver.py (lines 331-361)

```python
# Line 328: "MUST be before OperatorExpression"
if SysideAdapter.is_instance(node, "FeatureChainExpression"):          # 1st
    ...  # SingletonTerm classification
elif SysideAdapter.is_instance(node, "OperatorExpression"):            # 2nd
    ...  # operator recursion in aggregation
elif SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
    ...  # LocalTerm classification
```

Status: **CORRECT**. Explicit comment documents the invariant.

### extraction/extractor.py (lines 276-295)

FCE checked before FRE in `_parse_expression_to_path()`. OE not checked
in this context (only path extraction, not operator handling).

Status: **CORRECT**.

### extraction/usage_extractor.py (lines 521-557)

```python
if SysideAdapter.is_instance(expr, "FeatureChainExpression"):          # 1st
    ...  # CHAIN binding
elif SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):    # 2nd
    ...  # REFERENCE binding
elif SysideAdapter.is_instance(expr, "OperatorExpression"):            # 3rd
    ...  # EXPRESSION binding
```

Status: **CORRECT**. FCE checked well before OE.

### extraction/computed_attribute_extractor.py (line 104)

Only checks FCE (for EXPOSE_PURE classification). OE not checked.

Status: **CORRECT** (no dual-match risk).

### extraction/constraint_extractor.py (lines 156-174)

Checks CalculationDefinition, PartDefinition, PartUsage, RequirementDefinition.
No expression type dispatch. No FCE/OE overlap.

Status: **N/A** (no expression dispatch).

### analysis/parameter_groups.py (lines 176-186)

```python
elif SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):    # 1st
    ...
elif SysideAdapter.is_instance(expr, "FeatureChainExpression"):        # 2nd
    ...
elif SysideAdapter.is_instance(expr, "OperatorExpression"):            # 3rd
    ...
```

Status: **NEEDS REVIEW**. FCE checked after FRE. Since FRE is independent
of both FCE and OE (no subtype relationship), this doesn't cause misclassification
today. However, it violates the canonical ordering convention.

### generation/initialization.py (line 195)

Only checks `CalculationUsage`. No expression dispatch.

Status: **N/A**.

---

## Summary Table

| File | FCE First? | OE After? | Status |
|------|:---:|:---:|--------|
| expression_utils.py | yes | yes | CORRECT |
| expression_compiler.py | yes | yes | CORRECT |
| hierarchy_resolver.py | yes | yes | CORRECT |
| extractor.py | yes | n/a | CORRECT |
| usage_extractor.py | yes | yes | CORRECT |
| computed_attribute_extractor.py | yes | n/a | CORRECT |
| constraint_extractor.py | n/a | n/a | N/A |
| parameter_groups.py | no* | yes | REVIEW |
| initialization.py | n/a | n/a | N/A |

*FCE after FRE (not OE), so no misclassification -- but inconsistent ordering.

---

## Why This Is a System Invariant

Bug A (commit `20b720e`) proved that violating this ordering causes
37 aggregation inputs to be misclassified. The hierarchy_resolver site
was the critical one: FCE nodes (`pv_module.capital_cost`) were being
handled as OE nodes, producing wrong term types in aggregation expressions.

The rule applies everywhere `is_instance()` dispatches on expression types,
not just in one file. Any new dispatch site must follow: **FCE, then OE,
then FRE, then literals**.

---

## Data Models

| Type | File | Role |
|------|------|------|
| `FeatureChainExpression` | SysIDE (agentic-mbse) | `a.b` dotted access |
| `OperatorExpression` | SysIDE (agentic-mbse) | `a + b`, `a * b` operators |
| `FeatureReferenceExpression` | SysIDE (agentic-mbse) | `param_name` bare reference |
| `SysideAdapter.is_instance()` | `agentic_mbse.sysml.syside_adapter` | Type check function |
