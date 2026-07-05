# Spike Report: SysIDE AST Discovery for Hierarchy Patterns

**Status:** Complete
**Date:** 2026-02-10
**Branch:** cost-pattern
**Epic:** COST-PATTERN (Item 1)
**Script:** `scripts/spike_hierarchy_ast.py`

## Related Artifacts

- **Spec:** `.project/active/hierarchy-spike/spec.md`
- **Design:** `.project/active/hierarchy-spike/design.md`
- **Plan:** `.project/active/hierarchy-spike/plan.md`
- **Model fixture:** `tests/fixtures/solar_battery_model/`

---

## Q1: Template CalcUsage Ownership

**Status: PASS**

`owning_type` cleanly distinguishes template (PartDefinition) from concrete (PartUsage).

| Target | owning_type | Expected | Match |
|--------|-------------|----------|-------|
| PV Module.cost_model | PartDefinition | PartDefinition | YES |
| Solar Array.allocation_model | PartDefinition | PartDefinition | YES |
| solar_battery_plant.energy_production | PartUsage | PartUsage | YES |

**Owner chain traversal:** CalcUsage → Part → Package → Namespace (consistent at all levels).

**Code example:**
```python
calc_usage = <find 'cost_model' in PV Module.owned_members>
type(calc_usage.owning_type).__name__  # => 'PartDefinition'
calc_usage.owning_type.name             # => 'PV Module'
```

---

## Q2: :>> Redefinition AST Representation

**Status: PASS**

All 4 `:>>` patterns produce `ReferenceUsage` (NOT AttributeUsage) with `owned_redefinitions[0].redefined_feature` pointing to `Costed Component` abstract attributes.

| Pattern | Target | Element Type | Redefined Feature | RHS Expression |
|---------|--------|-------------|-------------------|----------------|
| Enum literal | PV Module :>> cas_category | ReferenceUsage | Costed Component.cas_category | FeatureReferenceExpression |
| EXPOSE | PV Module :>> capital_cost | ReferenceUsage | Costed Component.capital_cost | FeatureChainExpression |
| Aggregation | Solar Array :>> capital_cost | ReferenceUsage | Costed Component.capital_cost | OperatorExpression (with InvocationExpression children) |
| FORMULA | PV Module :>> idiot_index | ReferenceUsage | Costed Component.idiot_index | FeatureChainExpression |

**CRITICAL FINDING:** `:>>` creates `ReferenceUsage`, not `AttributeUsage`. All code processing `:>>` must check ReferenceUsage.

**Code example:**
```python
attr = <find ':>> capital_cost' ReferenceUsage on PV Module>
redef = attr.owned_redefinitions[0]
redef.redefined_feature.name                # => 'capital_cost'
redef.redefined_feature.owning_type.name    # => 'Costed Component'
type(attr.feature_value_expression).__name__ # => 'FeatureChainExpression'
```

---

## Q3: part redefines vs Plain part

**Status: PASS**

`part redefines` produces an explicit `Redefinition` in `owned_redefinitions` and `owned_specializations`. Plain `part` has `FeatureTyping + Subsetting` instead.

| Variant | owned_redefinitions | owned_specializations |
|---------|--------------------|-----------------------|
| design: `part redefines solar_array` | 1 (Redefinition → Solar Battery Plant.solar_array) | Redefinition + FeatureTyping |
| library: `part solar_array` | 0 (empty) | FeatureTyping + Subsetting |

**Code example:**
```python
len(design_elem.owned_redefinitions)  # => 1
len(library_elem.owned_redefinitions) # => 0
```

---

## Q4: Deep-Path :>> Resolution

**Status: PASS (with caveats)**

Deep-path overrides (`:>> pv_module.wattage = 400.0`) are unnamed `ReferenceUsage` elements with `name=None`. The `owned_feature_chainings` list is empty (0 found) on the redefining element, and `chaining_features` also returns 0 items when consumed.

Design's `solar_array` contains 5 unnamed ReferenceUsage members (the deep-path overrides):

| Index | Value | Actual SysML (via redefined_feature.chaining_features) |
|-------|-------|-------------|
| [0] | 400.0 | :>> pv_module.wattage = 400.0 |
| [1] | 0.21 | :>> pv_module.efficiency = 0.21 |
| [2] | 2000.0 | :>> inverter.power_rating = 2000.0 |
| [3] | 4.0 | :>> array_bos.string_count = 4.0 |
| [4] | 20.0 | :>> array_bos.panel_count = 20.0 |

**UPDATE (audit follow-up):** The original report identified members [2]-[4] by heuristic value matching and got them wrong (was: `inverter.inverter_cost`, `inverter_count`, `module_count`). The corrected table above was obtained by consuming `owned_redefinitions[0].redefined_feature.chaining_features` -- the chaining information lives on the **redefined feature**, not the redefining element. This is the key discovery: deep-path resolution IS fully structured, just accessed through the redefinition chain.

**Resolution pattern (corrected):** The redefining element has empty `chaining_features` and empty `owned_feature_chainings`. However, `owned_redefinitions[0].redefined_feature.chaining_features` returns the full path components:
- Member [0]: `[PartUsage 'pv_module', AttributeUsage 'wattage']`
- Member [2]: `[PartUsage 'inverter', AttributeUsage 'power_rating']`
- Member [3]: `[PartUsage 'array_bos', AttributeUsage 'string_count']`

This means heuristic value-matching is NOT needed. Items 2-4 can resolve deep-path overrides programmatically.

**Code example:**
```python
elem = <deep-path element on design solar_array>
elem.name                              # => None
type(elem).__name__                    # => 'ReferenceUsage'
elem.feature_value_expression.value    # => 400.0

# Chaining is on the REDEFINED FEATURE, not the redefining element:
rf = elem.owned_redefinitions[0].redefined_feature
path = list(rf.chaining_features)      # => [PartUsage 'pv_module', AttributeUsage 'wattage']
path[0].name                           # => 'pv_module'
path[1].name                           # => 'wattage'
```

---

## Q5: Multiplicity Representation

**Status: PASS**

Multiplicity is on the PartUsage element as a `MultiplicityRange` with cached bounds.

| Attribute | Value |
|-----------|-------|
| `.multiplicity` | MultiplicityRange |
| `.cached_lower_bound` | 20 |
| `.cached_upper_bound` | 21 |
| `.upper_bound` | FeatureReferenceExpression → module_count |

The `upper_bound` is a `FeatureReferenceExpression` referencing the sibling attribute `module_count` (which has `default := 20`).

**UPDATE (audit follow-up):** `cached_upper_bound = N+1` is **systematic** across all 3 multiplicities in the model:

| PartUsage | SysML | module_count default | cached_lower | cached_upper |
|-----------|-------|---------------------|-------------|-------------|
| Solar Array.pv_module | [module_count] | 20 | 20 | **21** |
| Solar Array.inverter | [inverter_count] | 4 | 4 | **5** |
| Battery System.battery_pack | [pack_count] | 8 | 8 | **9** |

Per the KerML spec (MultiplicityRange.md): the range is defined as **(inclusive)**, and when only one bound expression is given (as in `[N]`), the default lower bound equals the upper bound. So both should be 20. The `cached_lower_bound` is correct (20), but `cached_upper_bound` is consistently N+1. This appears to be a syside convention where `cached_upper_bound` uses an **exclusive** representation despite the spec saying "inclusive."

Additional observations:
- `lower_bound` is `None` (no explicit lower bound expression in SysML `[N]` syntax)
- `bounds` list is `[None, FeatureReferenceExpression]` confirming single-expression multiplicity
- The `upper_bound` FeatureReferenceExpression correctly resolves: `upper_bound.referent.name = 'module_count'` → `feature_value_expression.value = 20`

**Items 2-4 guidance:** DO NOT use `cached_upper_bound` directly as multiplicity count. Instead use one of:
1. **`cached_lower_bound`** -- correct for exact multiplicity `[N]` syntax (lower = upper per spec)
2. **`upper_bound.referent.feature_value_expression.value`** -- resolves through the expression to the default literal (most robust)

**Code example:**
```python
pv_module = <find 'pv_module' PartUsage on Solar Array>
mult = pv_module.multiplicity               # => MultiplicityRange
mult.cached_lower_bound                      # => 20 (CORRECT -- use this)
mult.cached_upper_bound                      # => 21 (WRONG for count -- exclusive convention)
mult.upper_bound.referent.name               # => 'module_count'
mult.upper_bound.referent.feature_value_expression.value  # => 20 (CORRECT -- most robust)
```

---

## Q6: sum() InvocationExpression Structure

**Status: PASS**

`InvocationExpression` nodes are accessible in the expression tree. `sum()` has `.function.name='sum'` and 1 operand (FeatureChainExpression for the collection path).

**Expression tree for Solar Array :>> capital_cost:**
```
OperatorExpression (+)
├── OperatorExpression (+)
│   ├── OperatorExpression (+)
│   │   ├── InvocationExpression (sum)  ← pv_module.capital_cost
│   │   └── InvocationExpression (sum)  ← inverter.capital_cost
│   └── FeatureChainExpression          ← allocation_model.total_allocation
└── FeatureReferenceExpression          ← misc_hardware_cost
```

Both `walk_expression_tree()` (our custom) and `traverse_expression()` (agentic-mbse) successfully visit `InvocationExpression` nodes.

**Code example:**
```python
expr = solar_array_capital_cost.feature_value_expression
# Walk tree, find InvocationExpression nodes
invocation.function.name  # => 'sum'
len(invocation.operands)  # => 1 (the collection FeatureChainExpression)
```

---

## Q7: Specialization Chain Traversal

**Status: PASS**

Full 8-step chain traversal works via alternating `.types` and `owned_members`:

| Step | Element | Type | Method |
|------|---------|------|--------|
| 1 | solar_battery_plant | PartUsage | find_element_by_name |
| 2 | Solar Battery Plant | PartDefinition | .types |
| 3 | solar_array | PartUsage | owned_members lookup |
| 4 | Solar Array | PartDefinition | .types |
| 5 | pv_module | PartUsage | owned_members lookup |
| 6 | PV Module | PartDefinition | .types |
| 7 | cost_model | CalculationUsage | owned_members lookup |
| 8 | PVModuleCostCalc | CalculationDefinition | .types |

**Code example:**
```python
plant = find('PartUsage', 'solar_battery_plant')
plant_def = next(iter(plant.types))          # => PartDefinition
sa = find_member(plant_def, 'PartUsage', 'solar_array')
sa_def = next(iter(sa.types))                # => PartDefinition
pv = find_member(sa_def, 'PartUsage', 'pv_module')
pv_def = next(iter(pv.types))                # => PartDefinition
cm = find_member(pv_def, 'CalcUsage', 'cost_model')
calc_def = next(iter(cm.types))              # => CalcDefinition
```

---

## Q8: New Attribute vs Redefined Attribute Distinction

**Status: PASS**

`owned_redefinitions` is the clean distinguisher:

| Attribute | Element Type | owned_redefinitions | Purpose |
|-----------|-------------|--------------------|---------|
| misc_hardware_cost | AttributeUsage | empty (0) | NEW attribute |
| capital_cost (:>>) | ReferenceUsage | 1 (→ Costed Component) | REDEFINED attribute |

**Additional differentiator:** New attributes are `AttributeUsage`; redefined `:>>` attributes are `ReferenceUsage`.

**Code example:**
```python
len(new_attr.owned_redefinitions)    # => 0
len(redef_attr.owned_redefinitions)  # => >0
type(new_attr).__name__              # => 'AttributeUsage'
type(redef_attr).__name__            # => 'ReferenceUsage'
```

---

## Q9: default := Representation

**Status: PASS**

`feature_value.is_default=True` uniformly marks `default :=` in both contexts:

| Context | Element | is_default | is_initial | Expression Type | Value |
|---------|---------|-----------|-----------|----------------|-------|
| CalcDef param | cost_per_watt | True | True | LiteralRational | 1.07 |
| Part attribute | module_count | True | True | LiteralInteger | 20 |

**Code example:**
```python
attr = <find attribute with default>
fv = attr.feature_value                # => FeatureValue object
fv.is_default                          # => True for 'default :='
attr.feature_value_expression           # => the default value expression
```

---

## Q10: Binding to Inherited/Redefined Attribute

**Status: PASS**

`in total_capex = capital_cost` resolves to the **redefined** attribute on `Solar Battery Plant` PartDef, NOT the abstract `Costed Component`.

| Attribute | Value |
|-----------|-------|
| Binding expression type | FeatureReferenceExpression |
| Referent | ReferenceUsage name='capital_cost' |
| Referent owning_type | PartDefinition name='Solar Battery Plant' |
| Referent has owned_redefinitions | Yes → Costed Component.capital_cost |

The binding resolves through the redefinition chain: `total_capex` → `capital_cost` on `Solar Battery Plant` (which is itself a `:>>` of `Costed Component.capital_cost`).

**Code example:**
```python
binding_expr = total_capex.feature_value_expression
type(binding_expr).__name__                    # => 'FeatureReferenceExpression'
binding_expr.referent.owning_type.name         # => 'Solar Battery Plant'
```

---

## agentic-mbse Reuse Assessment (FR-11)

### Module: syside_adapter.py
- **Type map present (7):** PartDefinition, PartUsage, FeatureTyping, ReferenceUsage, CalculationDefinition, CalculationUsage, AttributeUsage (plus expressions, literals)
- **Type map missing (5):** Redefinition, Specialization, Multiplicity, MultiplicityRange, InvocationExpression
- **Assessment:** Missing types are all accessible via element attributes (`elem.owned_redefinitions`, `elem.owned_specializations`, `elem.multiplicity`). Type map entries NOT needed for attribute-based access. Items 2-4 MAY benefit from adding InvocationExpression for `elements_of_type()` queries.

### Module: binding.py
- **classify_binding() BindingTypes:** UNBOUND, CHAIN, REFERENCE, LITERAL, EXPRESSION
- **Redefinition awareness:** None
- **InvocationExpression handling:** Falls to EXPRESSION via `hasattr(expr, 'operands')`
- **Assessment:** Can reuse as-is for parameter bindings on CalcUsages. `:>>` redefinition bindings are structurally different (not calc params) and don't need `classify_binding()`. No changes needed.

### Module: expression.py
- **traverse_expression():** Visits InvocationExpression (via operands fallback)
- **extract_feature_refs():** Extracts refs from InvocationExpression operands but does NOT extract function name (e.g., 'sum')
- **Assessment:** `traverse_expression()` works for InvocationExpression. Items 2-4 need: (1) function name extraction from InvocationExpression, (2) recognition of `sum()` as aggregation pattern. Recommend adding `extract_invocation_info()`.

### Module: helpers.py
- **get_parent_part_name():** Immediate parent PartUsage only
- **Full chain traversal:** Not available
- **Assessment:** Insufficient for hierarchy traversal. Q7 confirmed full chain requires alternating `.types` and `owned_members` across 8 steps. Items 2-4 need a `traverse_hierarchy()` function. Recommend placing in sysml-codegen (not agentic-mbse) since it's codegen-specific logic.

### Module: types.py
- **Existing models:** BindingInfo, ExpressionRef, CalcUsageInfo, ValidationIssue
- **Hierarchy/redefinition models:** None
- **Assessment:** Items 2-4 may need RedefinitionInfo or HierarchyNode models for the hierarchy traversal pipeline. These should be sysml-codegen-local unless shared utility is needed.

### Extension Recommendations
1. **syside_adapter:** Add InvocationExpression to type map (optional, for queries)
2. **expression.py:** Add `extract_invocation_info()` for function name + operand analysis
3. **helpers.py:** No changes -- hierarchy traversal belongs in sysml-codegen
4. **types.py:** Add RedefinitionInfo model in sysml-codegen (not agentic-mbse)
5. **binding.py:** No changes needed -- `:>>` is not a calc parameter binding
6. **CRITICAL:** `:>>` creates ReferenceUsage (not AttributeUsage). Any code processing `:>>` must check ReferenceUsage.

---

## Metamodel Type Population (NFR-3)

| Type | Available in API | Populated on Model Elements |
|------|-----------------|----------------------------|
| Redefinition | yes | yes (probed by Q2, Q3, Q8) |
| Specialization | yes | yes (probed by Q3, Q7) |
| Multiplicity | yes | yes (probed by Q5) |
| MultiplicityRange | yes | yes (probed by Q5) |
| InvocationExpression | yes | yes (probed by Q6) |
| FeatureChainExpression | yes | yes (probed by Q2) |
| FeatureValue | yes | yes (probed by Q9) |

Note: "Available in API" = attribute accessible on element without error. "Populated" = attribute returned non-empty/non-None value on at least one solar_battery model element during probing.

---

## Summary

| Q | Status | Finding |
|---|--------|---------|
| Q1 | PASS | owning_type distinguishes PartDefinition (template) from PartUsage (concrete) |
| Q2 | PASS | All 4 :>> patterns have owned_redefinitions linking to abstract interface |
| Q3 | PASS | redefines produces owned_redefinitions; plain part does not |
| Q4 | PASS | deep-path is ReferenceUsage name=None; path resolved via redefined_feature.chaining_features |
| Q5 | PASS | multiplicity is MultiplicityRange; use cached_lower_bound or resolve upper_bound (NOT cached_upper_bound) |
| Q6 | PASS | InvocationExpression found (2 nodes) |
| Q7 | PASS | Full chain traversable (8 steps) via alternating .types and owned_members |
| Q8 | PASS | owned_redefinitions empty for new, non-empty for :>> -- clean distinguisher |
| Q9 | PASS | feature_value.is_default distinguishes default := from regular assignment |
| Q10 | PASS | capital_cost resolves to redefined attribute on Solar Battery Plant |

---

## Go/No-Go Recommendation

**Probe results:** 10/10 passed, 0/10 warnings
**Type population:** 7/7 syside types available and populated

### RECOMMENDATION: GO

All critical patterns are probed and traversable. The SysIDE AST provides sufficient structure for Items 2-4 implementation.

**Key adaptations required for Items 2-4:**
- Code must handle `ReferenceUsage` (not just `AttributeUsage`) for `:>>` elements
- Deep-path resolution (Q4): use `owned_redefinitions[0].redefined_feature.chaining_features` to get path components (NOT heuristic value matching)
- `InvocationExpression` function name accessible via `.function.name`
- Full hierarchy traversal requires alternating `.types` and `owned_members` (8 steps for solar_battery)
- Multiplicity count: use `cached_lower_bound` or resolve `upper_bound.referent.feature_value_expression.value` (DO NOT use `cached_upper_bound` -- it is N+1 due to syside exclusive convention)

**Resolved anomalies (UPDATE from audit follow-up):**
- **Q5 `cached_upper_bound=21`:** Confirmed systematic across all 3 multiplicities (20→21, 4→5, 8→9). Syside uses exclusive upper bound convention despite KerML spec saying "inclusive." Workaround: use `cached_lower_bound` (correct for `[N]` syntax) or resolve via `upper_bound` expression chain. See Q5 section for details.
- **Q4 `owned_feature_chainings` empty:** The chaining information is on the `redefined_feature`, not the redefining element. `owned_redefinitions[0].redefined_feature.chaining_features` returns the full path (e.g., `[PartUsage 'pv_module', AttributeUsage 'wattage']`). Deep-path resolution is fully structured. See Q4 section for corrected code example.

Proceed to Item 2 spec.
