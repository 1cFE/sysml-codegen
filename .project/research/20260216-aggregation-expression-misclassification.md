# Research: Aggregation Expression Term Misclassification

**Date:** 2026-02-16
**Context:** COST-PATTERN epic, post-aggregation-wiring-fix validation
**Scope:** 58 of 70 aggregation inputs in solar_battery model remain unwired as ENTRY_POINTs

---

## Executive Summary

Two distinct bugs cause 46 of 58 unwired aggregation inputs. The remaining 12
(multiplicity counts) are correct by design.

**Bug A (37 inputs):** `_walk_aggregation_ast()` check ordering — `OperatorExpression`
fires before `FeatureChainExpression`, causing `array_bos.capital_cost` to be
classified as `LocalTerm("array_bos")` instead of
`SingletonTerm("array_bos.capital_cost")`.

**Bug B (9 inputs):** Graph builder unconditionally creates entry points for
LocalTerms without attempting sibling aggregation output resolution —
`capital_cost` in `idiot_index = capital_cost / raw_material_cost` should wire
to the sibling `capital_cost` aggregation module's output.

---

## Bug A: FeatureChainExpression Misclassified as Unary OperatorExpression

### Root Cause

In `_walk_aggregation_ast()` (`hierarchy_resolver.py:305-433`), the
`OperatorExpression` check at **line 328** fires before the
`FeatureChainExpression` check at **line 350**.

Syside's AST for `array_bos.capital_cost` (a FeatureChainExpression) matches
**both** `is_instance("OperatorExpression")` and
`is_instance("FeatureChainExpression")`:

```
FeatureChainExpression
  is_instance("OperatorExpression") = True    ← fires first (line 328)
  is_instance("FeatureChainExpression") = True ← never reached (line 350)
  operator = "."
  operands = [FeatureReferenceExpression(referent="array_bos")]
  target_feature.name = "capital_cost"
```

### Execution Trace (Current — WRONG)

```
_walk_aggregation_ast(node=FCE[array_bos.capital_cost])
  line 328: is_instance("OperatorExpression") → True → ENTERS
  operator = ".", num_operands = 1 → unary path (line 336)
  inner = _walk_aggregation_ast(operands[0])  # recurse
    → operands[0] is FeatureReferenceExpression(referent="array_bos")
    → line 358: is_instance("FeatureReferenceExpression") → True
    → extract_feature_reference_name() → "array_bos"
    → ctx.local_terms.append(LocalTerm("array_bos"))     ← WRONG
    → returns "array_bos"
  line 340: f"{operator}({inner})" → ".(array_bos)"
```

### Execution Trace (Fixed — CORRECT)

```
_walk_aggregation_ast(node=FCE[array_bos.capital_cost])
  line 350: is_instance("FeatureChainExpression") → True → ENTERS
  chain_name = extract_feature_chain_name(node) → "array_bos.capital_cost"
  ctx.singleton_terms.append(SingletonTerm("array_bos.capital_cost"))  ← CORRECT
  returns "array_bos.capital_cost"
```

### Why sum() Works But Standalone Doesn't

`sum(pv_module.capital_cost)` wraps the FeatureChainExpression in an
`InvocationExpression(func="sum")`. The InvocationExpression does NOT match
`is_instance("OperatorExpression")`, so it enters the sum handler at line 364.
The sum handler calls `_unwrap_invocation()` which has explicit FCE/FRE guards
(lines 294-297) and returns the FeatureChainExpression unchanged. Then
`extract_feature_chain_name()` correctly produces `"pv_module.capital_cost"`.

The standalone `.(array_bos)` has no InvocationExpression wrapper — the
FeatureChainExpression IS the top-level node, and it enters the
OperatorExpression handler first.

### Proof (AST Dump)

```
# sum(.(pv_module))
InvocationExpression  OE=False  func=sum
  └─ FeatureChainExpression  FCE=True  OE=True  func=.  target=capital_cost
       └─ FeatureReferenceExpression  FRE=True  referent=pv_module
→ SumTerm("pv_module", "capital_cost")  ✓

# .(array_bos)  [standalone, not inside sum()]
FeatureChainExpression  FCE=True  OE=True  func=.  target=capital_cost
  └─ FeatureReferenceExpression  FRE=True  referent=array_bos
→ LocalTerm("array_bos")  ✗  (should be SingletonTerm("array_bos.capital_cost"))
```

### Affected Inputs (37 total)

| Assembly | Expression | Misclassified Terms |
|----------|-----------|---------------------|
| solar_array :: capital_cost | `.(array_bos) + misc_hardware_cost` | `array_bos` (1) |
| solar_array :: raw_material_cost | `.(array_bos) + .(allocation_model)` | `array_bos`, `allocation_model` (2) |
| solar_array :: fabrication_cost | `.(array_bos)` | `array_bos` (1) |
| solar_array :: installation_cost | `.(array_bos)` | `array_bos` (1) |
| battery_system :: capital_cost | `.(hybrid_inverter) + .(battery_bos)` | `hybrid_inverter`, `battery_bos` (2) |
| battery_system :: raw_material_cost | same pattern | 2 |
| battery_system :: fabrication_cost | same pattern | 2 |
| battery_system :: installation_cost | same pattern | 2 |
| site_infra :: capital_cost | `.(racking) + .(electrical_panel) + .(permitting)` | 3 |
| site_infra :: raw_material_cost | same pattern | 3 |
| site_infra :: fabrication_cost | same pattern | 3 |
| site_infra :: installation_cost | same pattern | 3 |
| plant :: capital_cost | `.(solar_array) + .(battery_system) + .(site_infra)` | 3 |
| plant :: raw_material_cost | same pattern | 3 |
| plant :: fabrication_cost | same pattern | 3 |
| plant :: installation_cost | same pattern | 3 |

**Total: 37 inputs across 16 aggregation expressions.**

### Fix

**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py`

Move the `FeatureChainExpression` check (line 350) **before** the
`OperatorExpression` check (line 328) in `_walk_aggregation_ast()`. Since FCE
nodes are a subtype of OE in syside's type hierarchy, the more specific check
must come first.

```python
def _walk_aggregation_ast(node, mult_lookup, ctx):
    if node is None:
        return ""

    # FeatureChainExpression: child.attr → SingletonTerm
    # MUST be before OperatorExpression (FCE is a subtype of OE in syside)
    if SysideAdapter.is_instance(node, "FeatureChainExpression"):
        chain_name = extract_feature_chain_name(node)
        ctx.singleton_terms.append(SingletonTerm(source_path=chain_name))
        ctx.input_channels.append(chain_name)
        return chain_name

    # OperatorExpression: recurse into operands
    if SysideAdapter.is_instance(node, "OperatorExpression"):
        ...  # existing code unchanged
```

**Impact:** 37 LocalTerms become SingletonTerms with dotted paths (e.g.,
`SingletonTerm("array_bos.capital_cost")`). These then go through the existing
SingletonTerm resolution path in the graph builder, which (after Phase 1-2
fixes) uses `_resolve_aggregation_input_channel()` with scoped registry lookup.

**Downstream requirement:** After Bug A is fixed, the graph builder must
resolve these new SingletonTerms. The Phase 1-2 scoped registry lookup should
handle most cases. Some may need additional registry key formats (e.g., for
`allocation_model.material_portion` which is a CalcUsage output, not an
aggregation output).

---

## Bug B: No LocalTerm Resolution for Sibling Aggregation Outputs

### Root Cause

`_build_aggregation_module()` (`graph_builder.py:1015-1036`) unconditionally
creates entry points for all LocalTerms without attempting resolution.
Additionally, `_resolve_aggregation_input_channel()` has an early return for
non-dotted refs (line 773): `if "." not in symbolic_ref: return None`.

### Example: idiot_index

```sysml
:>> idiot_index = capital_cost / raw_material_cost;
```

AST:
```
OperatorExpression (operator="/")
  ├─ FeatureReferenceExpression (referent="capital_cost")
  └─ FeatureReferenceExpression (referent="raw_material_cost")
```

Both are bare `FeatureReferenceExpression` nodes — correctly classified as
LocalTerms. They are NOT FeatureChainExpressions. The extraction is correct.

But `capital_cost` and `raw_material_cost` are **outputs of sibling aggregation
modules** at the same scope:
- `capital_cost` → channel `{instance_path}__capital_cost__capital_cost`
- `raw_material_cost` → channel `{instance_path}__raw_material_cost__raw_material_cost`

The graph builder should check the OutputRegistry before creating entry points.

### Affected Inputs (9 total)

| Assembly | Expression | LocalTerms |
|----------|-----------|------------|
| solar_array :: idiot_index | `capital_cost / raw_material_cost` | 2 |
| battery_system :: idiot_index | `capital_cost / raw_material_cost` | 2 |
| site_infra :: idiot_index | `capital_cost / raw_material_cost` | 2 |
| plant :: idiot_index | `capital_cost / raw_material_cost` | 2 |
| solar_array :: capital_cost | `misc_hardware_cost` | 1 |

**Note:** `misc_hardware_cost` (1 input) is a genuinely local PartDef attribute
with no upstream producer. It correctly remains an entry point.

### Fix

**File:** `src/sysml_codegen/resolution/graph_builder.py`

In the LocalTerm processing loop, attempt resolution before creating entry
points:

```python
for l_term in agg.expression.local_terms:
    l_source: InputSource | None = None

    # Try 1: Direct aggregation output at same scope (double-attr format)
    agg_channel = get_channel_name(
        f"{agg.instance_path}__{l_term.attribute_name}",
        l_term.attribute_name,
    )
    if agg_channel in canonical_channels:
        l_source = InputSource(
            source_type="module_output",
            producer_channel=agg_channel,
        )

    # Try 2: Registry lookup (bare key)
    if l_source is None:
        resolved = output_registry.resolve(l_term.attribute_name)
        if resolved is not None:
            l_source = InputSource(
                source_type="module_output",
                producer_channel=resolved,
            )

    if l_source is None:
        # Genuinely unresolvable → entry point
        compilability = Compilability.MANUAL_REQUIRED
        ...  # existing entry point creation
```

---

## Not A Bug: Multiplicity Counts (12 inputs)

Multiplicity entry points (`module_count`, `inverter_count`, `pack_count`, etc.)
are **correct by design**. They parameterize array sizes and must be user-provided
in the JSON input. The SumTerm handler correctly creates these as entry points
with default values from the model.

---

## Summary

| Category | Count | Bug | Fix Location | Fix Type |
|----------|-------|-----|-------------|----------|
| FCE-as-LocalTerm (singleton children) | 37 | A | hierarchy_resolver.py:328/350 | Check reorder |
| Sibling agg refs (idiot_index) | 8 | B | graph_builder.py:1015-1036 | Add resolution |
| Genuine local (misc_hardware_cost) | 1 | None | N/A | Correct entry point |
| Multiplicity counts | 12 | None | N/A | Correct entry point |
| SumTerms (already wired by scoped fix) | 12 | Fixed | Already done | Already done |
| **Total** | **70** | | | |

**After fixing Bug A + B: 57 of 70 inputs wire to MODULE_OUTPUT.**
**Remaining 13 correct ENTRY_POINTs: 12 multiplicity + 1 misc_hardware_cost.**

---

## Method

1. Dumped all aggregation expressions with term classifications from production pipeline
2. Probed syside AST node types with `is_instance()` and attribute inspection
3. Traced `_walk_aggregation_ast()` execution for both working (sum) and broken (standalone) paths
4. Verified `extract_feature_chain_name()` produces correct output when called
5. Counted affected inputs by matching `.(name)` pattern in raw expression text
6. Confirmed idiot_index AST uses FeatureReferenceExpression (not FeatureChainExpression)

## Files Analyzed

| File | Lines | Finding |
|------|-------|---------|
| `extraction/hierarchy_resolver.py` | 305-434 | `_walk_aggregation_ast` check ordering bug |
| `extraction/hierarchy_resolver.py` | 278-302 | `_unwrap_invocation` has correct FCE guards |
| `extraction/expression_utils.py` | 133-161 | `extract_feature_chain_name` works correctly |
| `extraction/data_models.py` | 273-295 | SumTerm/SingletonTerm/LocalTerm definitions |
| `resolution/graph_builder.py` | 1015-1036 | LocalTerm unconditional entry point creation |
| `tests/fixtures/solar_battery_model/library.sysml` | 615-764 | Source SysML aggregation expressions |
