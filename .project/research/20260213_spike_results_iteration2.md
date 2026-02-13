# Research: Iteration 2 Spike Results

**Date:** 2026-02-13
**Models tested:** solar_battery, chain_spike, e2e_attr_expr, catf_mfe
**Scripts:** `scripts/spikes/spike_reference_resolution.py`, `spike_chain_redef_rhs.py`, `spike_design_attr_defaults.py`
**Purpose:** Empirically answer 3 questions blocking OutputRegistry design finalization (Issues 9, 11, 12 from `design_revision_comments_v2.md`)

---

## Spike 5 Findings: REFERENCE Binding Resolution Outcomes

**Question:** Do REFERENCE bindings ever resolve to MODULE_OUTPUT, or always to ENTRY_POINT?
**Addresses:** Issue 11 (SYSML_QN normalization in resolve() -- dead code or broken?)

### Data

Grand cross-tabulation across all 4 models (215 total binding resolutions):

| BindingType | ENTRY_POINT | MODULE_OUTPUT | Total |
|-------------|-------------|---------------|-------|
| CHAIN       | 5           | 39            | 44    |
| LITERAL     | 5           | 0             | 5     |
| REFERENCE   | **119**     | **4**         | 123   |
| UNBOUND     | 43          | 0             | 43    |
| **Total**   | **172**     | **43**        | **215** |

Per-model REFERENCE breakdown:

| Model | REF -> ENTRY_POINT | REF -> MODULE_OUTPUT |
|-------|-------------------|---------------------|
| solar_battery | 23 | **2** |
| chain_spike | 3 | 0 |
| e2e_attr_expr | 6 | **2** |
| catf_mfe | 87 | 0 |

### The 4 REFERENCE -> MODULE_OUTPUT Cases

All 4 cases resolve through the **computed attribute index** in the backtracker, NOT through OutputRegistry key matching:

| source_path | Resolved channel | `replace("::", "__")` matches? |
|---|---|---|
| `SolarBatteryDesign::solar_battery_plant::annualized_om::p_net_kw` | `...p_net_kw__p_net_kw` | **NO** |
| `SolarBatteryLibrary::'Solar Battery Plant'::capital_cost` | `...capital_cost__capital_cost` | **NO** |
| `E2EAttrExprDesign::e2e_plant::energy::power_mw` | `...power_mw__power_mw` | **NO** |
| `E2EAttrExprDesign::e2e_plant::lcoe::annual_om` | `...annual_om__annual_om` | **NO** |

The naive `replace("::", "__")` normalization fails in all 4 cases because:
- The source_path contains the **consuming** usage's path (e.g., `...annualized_om::p_net_kw`)
- The resolved channel uses the **producing** computed attribute's EQN (e.g., `...p_net_kw__p_net_kw`)
- The intermediate path segments differ

### All REFERENCE source_paths are SYSML_QN

100% of REFERENCE bindings (123/123) use SYSML_QN format (`Namespace::Part::param`). Zero use DOTTED or BARE.

### Design Implication

**SYSML_QN normalization in `resolve()` is exercised but broken.**

The OutputRegistry's `::` -> `__` replacement would produce keys like
`SolarBatteryDesign__solar_battery_plant__annualized_om__p_net_kw` which don't match
any registered channel. The current backtracker resolves these 4 cases through the
computed attribute index (a parallel lookup mechanism), not the OutputRegistry.

**Resolution options for Issue 11:**

1. **Remove SYSML_QN normalization from resolve()** and instead handle REFERENCE -> MODULE_OUTPUT
   through computed attribute EXPOSE_PURE aliases (Phase 3). The 4 cases are all computed
   attributes (`p_net_kw`, `capital_cost`, `power_mw`, `annual_om`) that would be registered
   as Phase 3 aliases if EXPOSE_PURE alias registration uses the source_path as an alias key.

2. **Fix the normalization** to handle the path segment mismatch. This requires understanding
   which segment of the SYSML_QN path maps to which computed attribute, which is complex and
   fragile.

**Recommendation:** Option 1. Let Phase 3 EXPOSE_PURE aliases handle these 4 cases. The
resolve() method should handle DOTTED keys (exact match) and alias lookups only.

---

## Spike 6 Findings: `:>>` CHAIN Redefinition RHS Content

**Question:** What does the RHS of `:>>` CHAIN redefinitions contain?
**Addresses:** Issue 9 (CHAIN alias canonical_name is bare -- can't resolve in OutputRegistry)

### Data

| Model | CHAIN redefs | CHAIN overrides | BARE | DOTTED |
|-------|-------------|----------------|------|--------|
| solar_battery | 54 | 0 | 13 | 41 |
| e2e_attr_expr | 0 | 0 | 0 | 0 |
| **Total** | **54** | **0** | **13** | **41** |

No SYSML_QN, AST_TEXT, or NONE formats observed. e2e_attr_expr has no hierarchy data
(no PartDefs with `:>>` redefinitions).

### The 13 BARE cases are NOT channel references

All 13 BARE source_paths are **CAS category codes** assigned to `cas_category` attributes:

| owning_part | attribute_name | source_path | Nature |
|---|---|---|---|
| PV_Module | cas_category | `CAS220101` | String literal |
| String_Inverter | cas_category | `CAS220107` | String literal |
| Array_BOS | cas_category | `CAS24` | String literal |
| Battery_Pack | cas_category | `CAS27` | String literal |
| ... (9 more) | cas_category | `CAS*` | String literal |

These are **enum-like string literal values**, not channel references. They are misclassified
as CHAIN by the hierarchy resolver because they lack a numeric literal value. The ChannelAlias
builder should **filter these out** (e.g., skip CHAIN redefs where `source_path` has no `.`
and doesn't match any known part usage or CalcUsage instance name).

### The 41 DOTTED cases follow a uniform pattern

All 41 DOTTED source_paths follow the pattern `cost_model.{output_name}`:

| Attribute | source_path | Semantic |
|---|---|---|
| capital_cost | `cost_model.total_cost` | CalcUsage output |
| raw_material_cost | `cost_model.material_cost` | CalcUsage output |
| fabrication_cost | `cost_model.fab_cost` | CalcUsage output |
| installation_cost | `cost_model.install_cost` | CalcUsage output |
| idiot_index | `cost_model.idiot_index` | CalcUsage output |

These are **PartDef-local dotted paths** referencing sibling CalcUsage outputs.
`cost_model` is a child CalcUsage on the same PartDef. The path is relative to the
PartDef, not design-scoped.

### Additional facts

- `expression_text` is **empty** for all CHAIN redefinitions (source_path is the reliable field)
- `expression_ast` is **None** for all CHAIN redefinitions
- All 13 design_overrides are LITERAL type (no CHAIN overrides exist)

### Design Implication

**Confirms Issue 9 and provides the fix.**

All DOTTED CHAIN source_paths need design instance scoping at alias construction time:

```python
# At Step 3.5(D), for each CHAIN redef with "." in source_path:
ChannelAlias(
    alias_name=f"{instance_path}.{redef.attribute_name}",
    canonical_name=f"{instance_path}.{redef.source_path}",
    owning_part_qn=redef.owning_part_qn,
    source="redefinition",
)
```

BARE CAS-code redefs should be **filtered out** before alias construction:

```python
# Skip non-reference CHAIN redefs
if redef.source_path and "." not in redef.source_path:
    continue  # CAS codes, enum values, etc.
```

---

## Spike 7 Findings: DesignAttributeData.default_value Format

**Question:** For design attributes with path-like default_value, what format is it in?
**Addresses:** Issue 12 (Phase 4 transitive alias registration)

### Data

| Model | Total attrs | NUMERIC | NONE | DOTTED_PATH | Other |
|-------|------------|---------|------|-------------|-------|
| solar_battery | 100 | 46 | 53 | **1** | 0 |
| e2e_attr_expr | 28 | 12 | 15 | **1** | 0 |
| **Total** | **128** | **58** | **68** | **2** | **0** |

No BOOLEAN, SYSML_QN, AST_TEXT, or STRING_LITERAL defaults observed.

### The 2 Transitive Defaults

| Attribute | default_value | Catalog lookup | Resolves? |
|---|---|---|---|
| `e2e_plant.total_capex` | `component_cost.total_cost` | `component_cost__total_cost` | **YES** |
| `solar_battery_plant.misc_hardware_cost` | `allocation_model.total_allocation` | `...allocation_model__total_allocation` | **YES** |

Both resolve via **direct catalog lookup** -- no normalization needed.

### Design Implication

**Phase 4 transitive alias registration WORKS with actual data.**

- `default_value` is always a **clean dotted path** (not raw AST text like EXPOSE_PURE's `expression_text`)
- The proposed filter correctly identifies transitive defaults:
  ```python
  def _is_transitive_default(attr: DesignAttributeData) -> bool:
      if attr.default_value is None:
          return False
      val = str(attr.default_value)
      if "." not in val:
          return False
      try:
          float(val)
          return False
      except ValueError:
          return True
  ```
- No SYSML_QN defaults exist, so the `::` normalization branch in Phase 4 is dead code for default_value resolution (can be removed or left as defensive code)

---

## Design Comment Resolutions

| Issue | Finding | Resolution |
|---|---|---|
| **Issue 9** (CHAIN alias bare name) | CHAIN source_paths are DOTTED (76%) or BARE CAS codes (24%). BARE cases are string literals, not references. | **Scope DOTTED canonical_names with instance_path prefix at construction time. Filter out BARE non-reference CAS codes.** |
| **Issue 11** (REFERENCE -> MODULE_OUTPUT?) | **4 cases exist** (solar_battery: 2, e2e_attr_expr: 2). All are computed attributes. Naive `::` -> `__` normalization fails in all 4 cases. | **Remove SYSML_QN normalization from resolve(). Handle these 4 cases through Phase 3 EXPOSE_PURE aliases instead.** |
| **Issue 12** (design attr default_value) | 2 transitive defaults found, both clean DOTTED_PATH, both resolve. | **Phase 4 works as designed. Use proposed filter. No SYSML_QN normalization needed for default_value.** |

## Informed Resolutions (no spike needed, informed by spike data)

| Issue | Informed by | Resolution |
|---|---|---|
| **Issue 10** (`_resolve_to_design_attribute()` unspecified) | Spike 5: 119 REFERENCE -> ENTRY_POINT cases all use SYSML_QN source_path | **Implement as proposed in Issue 10 comments: extract leaf name from SYSML_QN source_path (last segment after `::`), search design_attrs by (parent_path, leaf_name). Transitive cases handled by Phase 4 aliases and never reach this method.** |
| **Issue 13** (FORMULA input wiring) | Spike 7: design attributes are simple (NUMERIC or NONE). Spike 5: all binding types route correctly through backtracker. | **Preserve synthetic CalcUsage approach from expression-aware-codegen.md. FORMULA computed attributes produce synthetic CalcUsageData that flow through normal backtracking. No special input wiring needed.** |
| **Issue 14** (aggregation input resolution) | Spike 6: aggregation expressions are extracted with full scoped data from Step 3.5. ScopedAggregationData already has instance paths. | **Aggregation module builder constructs input channels directly from ScopedAggregationData, NOT through OutputRegistry. Clarify in design: OutputRegistry is the single mechanism for *binding* resolution (Step 6), not for all channel construction. Aggregation modules are built in Step 7 using pre-scoped data.** |
| **Issue 6** (AggregationDecomposer Protocol) | N/A (carried from v1) | **CLOSED: Drop the Protocol. Keep direct sum() code per project guidelines.** |

---

## Summary of OutputRegistry Simplifications

Based on iteration 2 findings, the OutputRegistry can be simplified:

1. **Remove SYSML_QN normalization from `resolve()`** -- the 4 REFERENCE -> MODULE_OUTPUT cases will be handled by Phase 3 EXPOSE_PURE aliases
2. **Remove SYSML_QN normalization from Phase 4** -- no SYSML_QN default_values exist
3. **Add CHAIN redef filtering** -- skip CAS-code BARE redefs (no `.` in source_path)
4. **Add instance_path scoping** for CHAIN redef canonical_names at construction time
5. **Clarify OutputRegistry scope** -- it handles *binding* resolution only; aggregation modules use ScopedAggregationData directly

The OutputRegistry's `resolve()` method becomes simpler:
1. Exact match on dotted key (CHAIN bindings, Phase 1 primary keys)
2. Alias lookup (Phase 2 CHAIN redefs, Phase 3 EXPOSE_PURE, Phase 4 transitive)
3. No bare-name handling, no SYSML_QN normalization

---

**Next step:** Update `08_algorithm_revised.md` with these empirically grounded decisions.
