---
date: 2026-02-13T15:28:45+00:00
researcher: Claude
topic: "Why Bug 2 (EXPOSE->CalcUsage wiring) persists after fix: root cause tracing through code fixes, tests, and customer validation"
tags: [research, bug-analysis, backtracker, expose-pure, wiring, regression]
status: in-progress
last_updated: 2026-02-13T16:45:00+00:00
---

# Research: Why Bug 2 (EXPOSE->CalcUsage Wiring) Still Fails for the Customer

**Date**: 2026-02-13T15:28:45+00:00
**Researcher**: Claude
**Research Type**: Codebase / Bug Analysis / Cross-Repository Trace

## Research Question

The customer (fusion-tea validation plan, Phase 2.3) reports that **Bug 2 — EXPOSE->CalcUsage wiring** — still shows `total_capex` wired to `ENTRY_POINT` (design_params) instead of `MODULE_OUTPUT` (component_cost.total_cost) in the e2e_attr_expr_v3 codegen output. This is identical to V2 behavior. We believed this was fixed. Three specific questions:

1. Which specific parts of our code fixes were supposed to address this bug?
2. How did we test that bug fix?
3. Why does it still not seem to be working for the end user?

## Summary (Updated)

The initial research hypothesized a "second-hop resolution" failure where `component_cost.total_cost` couldn't be found in the CalcUsage output catalog. **Deeper investigation has significantly refined the picture:**

- **The first hop (Strategy 5 → design attr index) works on paper.** `parameter_groups.py:_extract_default_value()` correctly extracts `"component_cost.total_cost"` from the FeatureChainExpression, and `get_parent_part_name()` correctly returns `"e2e_plant"`, so the index key `"e2e_plant.total_capex"` is built correctly. Strategy 5's `::` normalization produces the matching dotted key.

- **The second hop's success depends on whether CalcUsages are concrete or template-expanded.** This is the critical fork:
  - **Concrete CalcUsages** (`instance_name = "component_cost"`): The output catalog has simple key `"component_cost.total_cost"` and `_usage_by_name["component_cost"]` exists. Resolution via Strategy 1 or 2a succeeds cleanly.
  - **Virtual/template CalcUsages** (`instance_name = "E2EAttrExprDesign__e2e_plant__component_cost"`): The output catalog simple key becomes `"E2EAttrExprDesign__e2e_plant__component_cost.total_cost"`, and `_usage_by_name` has no `"component_cost"` key. Strategy 1 and 2a both miss. Only Strategy 2b (suffix match) might find it.

- **The unit test passes by coincidence.** `test_colon_colon_binding_to_expose_pure_resolves_transitively` uses synthetic CalcUsageData with `instance_name = "component_cost"` (concrete format) and default `source_file = Path("unknown")`. This doesn't replicate the real model's behavior if template expansion is active.

- **The e2e_attr_expr model structure is ambiguous for template detection.** The SysML uses `part e2e_plant` (untyped PartUsage in a Package), which may or may not trigger template expansion depending on how syside reports `owning_type` for CalcUsages inside untyped PartUsages.

## Detailed Findings

### 1. What Code Fixes Were Supposed to Address Bug 2?

**Design document:** `.project/active/codegen-bug-fixes/design.md` — "Bug 2: FORMULA/EXPOSE Backtracker Wiring"

Three changes were designed and implemented:

**Change A: Extend `_computed_attr_index` keys** (`dependency_backtracker.py`)
- Added SysML qualified name key (`owning_part_qualified_name::name`) to the FORMULA computed attribute index
- Purpose: Allow bindings in `Package::Part::attr` format to find FORMULA attributes
- **This works correctly for FORMULA lookups** — tested and passing

**Change B: Normalize lookup path for `::` separator** (`dependency_backtracker.py`)
- Extended fallback in `_trace_dependencies()` to handle `::` separator when looking up computed attributes
- Purpose: When a binding's `source_path` is `E2EAttrExprDesign::e2e_plant::power_mw`, extract `power_mw` and find the FORMULA
- **This works correctly for FORMULA bindings** — tested and passing

**Change C: Generalize `::` normalization in `_resolve_binding_to_usage()`** (`dependency_backtracker.py`)
- Added Strategy 5 at the bottom of `_resolve_binding_to_usage()` that converts `::` paths to dotted format and checks only `_design_attr_binding_index` (not full resolution — to avoid self-referential loops)
- Strategy 5 is deliberately restricted: it ONLY checks the design attr binding index, not all strategies. This prevents `Package::Part::CalcUsage::Param` from incorrectly matching via Strategy 2a (instance name match).
- **This correctly finds `e2e_plant.total_capex` in the design attr binding index for the first hop.**

### 2. How Did We Test Bug 2?

**Unit test:** `test_colon_colon_binding_to_expose_pure_resolves_transitively` (test_backtracker_computed_attrs.py:486-547)

This test creates:
- Producer CalcUsage: `instance_name="component_cost"`, `qualified_name="Pkg__Part__component_cost"`, `source_file=Path("unknown")` (default)
- Consumer CalcUsage: binding with `source_path="E2EDesign::e2e_plant::total_capex"`
- DesignAttributeData: `name="total_capex"`, `parent_part="e2e_plant"`, `default_value="component_cost.total_cost"`, `source_file=Path("design.sysml")`

**Critical test gap 1 — `_resolve_target_to_qualified` cross-file behavior:**

`_resolve_target_to_qualified("component_cost.total_cost", Path("design.sysml"))` at line 937-970 iterates all_usages checking `usage.instance_name == "component_cost" AND usage.source_file == Path("design.sysml")`. In the test, `usage.source_file = Path("unknown")` (CalcUsageData default), so the file check FAILS (`Path("unknown") != Path("design.sysml")`). This means `_resolve_target_to_qualified` returns None, and the index stores the SIMPLE target `"component_cost.total_cost"` (not a qualified key).

However, **the test still passes** because the second hop's `_resolve_binding_to_usage("component_cost.total_cost")` finds the target via Strategy 1: the output catalog has simple key `"component_cost.total_cost"` (built from `instance_name="component_cost"` + `attr.name="total_cost"`).

**Critical test gap 2 — concrete vs virtual CalcUsage:**

The test uses `_make_calc_usage("component_cost", ...)` which creates a CalcUsageData with `instance_name="component_cost"` — a simple concrete instance name. In the real model, if template expansion is active, the CalcUsage would have `instance_name="E2EAttrExprDesign__e2e_plant__component_cost"` (the full qualified name, per `_create_virtual_calc_usage` at usage_extractor.py:255).

With the virtual instance name:
- Output catalog simple key = `"E2EAttrExprDesign__e2e_plant__component_cost.total_cost"` (NOT `"component_cost.total_cost"`)
- `_usage_by_name` key = `"E2EAttrExprDesign__e2e_plant__component_cost"` (NOT `"component_cost"`)

So Strategy 1 (exact match on `"component_cost.total_cost"`) and Strategy 2a (instance name match on `"component_cost"`) would both fail.

### 3. The Resolution Chain — Traced Through Code

**Binding extraction** (usage_extractor.py:534-544):
The SysML `in total_capex = total_capex` creates a `FeatureReferenceExpression`. `_parse_reference_expression()` extracts `referent.qualified_name`, which produces `source_path = "E2EAttrExprDesign::e2e_plant::total_capex"` (SysML `::` qualified name format).

**Design attribute extraction** (parameter_groups.py:130-152, 158-199):
`_extract_single_attribute()` calls `_extract_default_value(feature_value_expression)`. **IMPORTANT**: `parameter_groups.py:_extract_default_value()` is a DIFFERENT function from `extractor.py:_extract_default_value()`. The parameter_groups version handles `FeatureChainExpression` (line 181-183) via `_extract_chain_path()` (line 215-232), which extracts the dotted path `"component_cost.total_cost"`.

So `DesignAttributeData.default_value = "component_cost.total_cost"` — the attribute IS captured with the correct target.

**Design attr binding index** (dependency_backtracker.py:873-909):
- `attr.parent_part = "e2e_plant"` (confirmed via `get_parent_part_name()` at agentic-mbse/helpers.py:117-122, which returns the owning PartUsage name)
- Key: `"e2e_plant.total_capex"`
- Target: `_resolve_target_to_qualified("component_cost.total_cost", design_file)` or simple `"component_cost.total_cost"`

**`_trace_dependencies()` processing** (dependency_backtracker.py:447-500):
1. `_computed_attr_index.get(source_path)` → None (EXPOSE_PURE not indexed, only FORMULA at line 146)
2. Bare name fallback with `::` split → `_computed_attr_index.get("total_capex")` → None
3. `_aggregation_output_index.get(source_path)` → None (e2e_attr_expr has no aggregation)
4. Falls through to `_resolve_binding_to_usage("E2EAttrExprDesign::e2e_plant::total_capex")`

**`_resolve_binding_to_usage()` resolution** (dependency_backtracker.py:776-871):
- Strategy 1 (exact match): `"E2EAttrExprDesign::e2e_plant::total_capex"` not in output catalog → miss
- Strategy 2 (parse instance): no "." in source → skip
- Strategy 4 (transitive design attr): `"E2EAttrExprDesign::e2e_plant::total_capex"` not in index (uses `::` not dotted) → miss
- Strategy 2b (cross-file): no "." → skip
- Strategy 3 (bare instance): `"E2EAttrExprDesign::e2e_plant::total_capex"` not in usage_by_name → miss
- **Strategy 5 (`::` normalization)**: `parts = ["E2EAttrExprDesign", "e2e_plant", "total_capex"]`, `dotted = "e2e_plant.total_capex"` → **FOUND in `_design_attr_binding_index`!**
  - target = index value (qualified or simple, see below)
  - Recurse: `_resolve_binding_to_usage(target, visited)`

**The second hop — the critical fork:**

If `_resolve_target_to_qualified` succeeded (same-file CalcUsage), target = `"E2EAttrExprDesign__e2e_plant__component_cost__total_cost"` (qualified key):
- Strategy 1: exact match in output catalog → **YES** (this is the qualified key format) → resolves correctly

If `_resolve_target_to_qualified` returned None (cross-file or virtual CalcUsage), target = `"component_cost.total_cost"` (simple):
- **IF CalcUsage is concrete** (`instance_name = "component_cost"`):
  - Strategy 1: `_output_catalog["component_cost.total_cost"]` → **YES** (simple key matches)
  - OR Strategy 2a: `_usage_by_name["component_cost"]` → **YES**
  - → resolves correctly
- **IF CalcUsage is virtual/template** (`instance_name = "E2EAttrExprDesign__e2e_plant__component_cost"`):
  - Strategy 1: `_output_catalog["component_cost.total_cost"]` → **NO** (simple key is `"E2EAttrExprDesign__e2e_plant__component_cost.total_cost"`)
  - Strategy 2a: `_usage_by_name["component_cost"]` → **NO** (key is `"E2EAttrExprDesign__e2e_plant__component_cost"`)
  - Strategy 4: `_design_attr_binding_index["component_cost.total_cost"]` → probably not
  - Strategy 2b: suffix match on `.total_cost` → **MAYBE** (fragile, could be ambiguous)
  - Strategy 3: bare name `"component_cost.total_cost"` → no
  - → **likely resolves to None → ENTRY_POINT!**

### 4. The e2e_attr_expr Model Structure

**SysML source** (`fusion-tea/models/tests/e2e_attr_expr/design.sysml`):
```sysml
package E2EAttrExprDesign {
    part e2e_plant {                                          // Untyped PartUsage in Package
        attribute quantity : Real = 100.0;
        attribute unit_cost : Real = 50.0;
        // ... more literals ...
        calc component_cost : ComponentCostCalc {             // CalcUsage inside PartUsage
            in quantity = quantity;
            in unit_cost = unit_cost;
        }
        attribute total_capex : Real = component_cost.total_cost;  // EXPOSE_PURE
        calc financial : AnnualizedCostCalc {                 // Consumer CalcUsage
            in total_capex = total_capex;                     // The failing binding
            in discount_rate = discount_rate;
            in lifetime = lifetime;
        }
    }
}
```

Key structural observations:
- `e2e_plant` is an **untyped** PartUsage (`part e2e_plant` — no `: SomePartDef`)
- Owned by a **Package** (not a PartDef)
- All CalcUsages (`component_cost`, `financial`, `energy`, `lcoe`) are inside this untyped PartUsage
- `total_capex = component_cost.total_cost` is the EXPOSE_PURE pattern binding `financial.total_capex` to `component_cost.total_cost`

### 5. Why It Works for solar_battery but Not e2e_attr_expr

In the solar_battery model, `annualized_financial.total_capex` was fixed by **BF-7** (hierarchy bugfix design), which:
1. Added EXPOSE_PURE aliases to the **aggregation output index** (e.g., `solar_battery_plant.total_capex` → aggregation channel)
2. Sanitized PartDef names in the `::` fallback

BF-7 was specifically designed for the **aggregation** resolution path, which is unique to models with hierarchy/aggregation. The e2e_attr_expr model has no aggregation — its `total_capex` resolves through the **CalcUsage output** path instead. BF-7's fixes don't apply to this path.

The solar_battery E2E test at `test_costed_component_e2e.py:309-327` explicitly validates `annualized_financial.total_capex` wiring — this passes because the aggregation output index (with BF-7 aliases) resolves it before the backtracker reaches `_resolve_binding_to_usage`.

## Code References

- `src/sysml_codegen/analysis/dependency_backtracker.py`:
  - `__init__` lines 117-261: Index construction (output_catalog, usage_by_name, design_attr_binding_index)
  - `_trace_dependencies` lines 379-621: Main binding resolution loop
  - `_resolve_binding_to_usage` lines 776-871: 5-strategy resolution
  - `_build_design_attr_binding_index` lines 873-909: Constructs `parent.attr` → `target` mapping
  - `_resolve_target_to_qualified` lines 937-970: File-context matching for target qualification
  - `_build_channel_name_for_binding` lines 710-774: Channel name construction from resolved usage
- `src/sysml_codegen/analysis/parameter_groups.py`:
  - `_extract_default_value` lines 158-199: Handles FeatureChainExpression (returns dotted path)
  - `_extract_chain_path` lines 215-232: Extracts `instance.attribute` path from FeatureChainExpression
  - `extract_design_attributes` lines 87-127: Iterates AttributeUsage elements
- `src/sysml_codegen/extraction/usage_extractor.py`:
  - `_parse_reference_expression` lines 600-616: Extracts `referent.qualified_name` → `::` format source_path
  - `_create_virtual_calc_usage` lines 232-268: Sets `instance_name = qualified_name` for virtual instances
  - Template detection lines 440-448: Checks `owning_type` for PartDefinition
- `agentic_mbse/sysml/helpers.py`:
  - `get_parent_part_name` lines 105-130: Returns owning PartUsage name
- `tests/unit/test_backtracker_computed_attrs.py`:
  - `test_colon_colon_binding_to_expose_pure_resolves_transitively` lines 486-547
- `.project/active/codegen-bug-fixes/design.md` — Bug 2 design (Changes A, B, C)
- `.project/active/hierarchy-bugfix/design.md` — BF-7 (aggregation alias fix, solar_battery specific)
- `~/1cfe/fusion-tea/.project/active/e2e-post-codegen-validation/plan.md` — Phase 2.3 customer failure evidence
- `~/1cfe/fusion-tea/models/tests/e2e_attr_expr/design.sysml` — The failing model's SysML source

## Root Cause Hypotheses (Ranked)

### Hypothesis 1: Template expansion creates virtual CalcUsages with qualified instance_names (HIGH confidence)

If `component_cost` inside the untyped `part e2e_plant` triggers template detection (because `owning_type` returns an implicit PartDefinition), then:
- `instance_name` becomes `"E2EAttrExprDesign__e2e_plant__component_cost"`
- Output catalog simple keys and `_usage_by_name` both use this qualified form
- The second hop in the transitive resolution chain receives `"component_cost.total_cost"` as the target, which doesn't match any qualified-form keys
- Resolution fails → ENTRY_POINT

**Evidence for:** The customer error matches this exactly — the wiring falls through to ENTRY_POINT with no partial resolution. The unit test avoids this by using concrete CalcUsageData.

**Evidence against:** Untyped PartUsages in Packages may not trigger template detection — depends on syside's `owning_type` behavior.

### Hypothesis 2: `_resolve_target_to_qualified` cross-file mismatch (MEDIUM confidence)

Even if CalcUsages are concrete, `_resolve_target_to_qualified` compares `usage.source_file == source_file`. If the design file's extracted Path doesn't match the CalcUsage's source_file Path (e.g., one is absolute, one is relative, or they point to different files), the qualified target lookup fails. The index stores simple target `"component_cost.total_cost"`, which then resolves via Strategy 1 (simple key in output catalog).

This would still work for concrete CalcUsages because `"component_cost.total_cost"` IS the simple key. But if there's a subtle mismatch in how `_build_channel_name_for_binding` constructs the channel name using the simple target, the wiring could be wrong even though the CalcUsage is found.

**Evidence for:** The unit test's `source_file` mismatch (`Path("unknown") != Path("design.sysml")`) proves this code path is exercised.

**Evidence against:** The unit test still passes — Strategy 1 finds the simple key correctly.

### Hypothesis 3: Binding source_path is bare name, not `::` format (LOW confidence)

If SysIDE produces `source_path = "total_capex"` (bare name) instead of `"E2EAttrExprDesign::e2e_plant::total_capex"`, then none of the strategies can resolve it — no "." for Strategy 2, not in the design attr index (which uses dotted keys), no `::` for Strategy 5.

**Evidence against:** `_parse_reference_expression` uses `referent.qualified_name`, which should produce the fully-qualified `::` format for any named element. SysML v2 requires qualified names for cross-scope references.

## Open Questions

### Critical (block spec/design)

1. **Is `component_cost` a concrete or virtual CalcUsage in e2e_attr_expr?**
   For `part e2e_plant` (untyped PartUsage in Package), does syside's `owning_type` attribute on the CalcUsage return a PartDefinition (triggering template expansion) or something else?
   - **How to verify:** Run `extract_calculation_usages()` on the e2e_attr_expr model and inspect `is_template` and `instance_name` for each returned CalcUsage. Or write a targeted unit test with a mock untyped PartUsage.

### Important (inform design approach)

2. **If concrete, does `_resolve_target_to_qualified` succeed for same-file CalcUsages in e2e_attr_expr?**
   Both `total_capex` (DesignAttributeData) and `component_cost` (CalcUsage) are in the same file (`design.sysml`). But do their `source_file` Path objects match exactly?

3. **If virtual, does Strategy 2b (suffix match `.total_cost`) actually find the right CalcUsage?**
   If there are multiple CalcUsages with `total_cost` output, Strategy 2b would produce ambiguous matches.

### Nice to have

4. **What is the exact `source_path` string that SysIDE produces for `in total_capex = total_capex` in e2e_attr_expr?**
   We assume `"E2EAttrExprDesign::e2e_plant::total_capex"` based on code reading, but confirming with debug logging would validate the full chain.

## Recommendations

### Regardless of Root Cause

The fundamental fragility is that the resolution chain depends on `instance_name` format matching `_output_catalog` and `_usage_by_name` key formats. Whether CalcUsages are concrete or virtual, the N-hop transitive resolution approach requested by the user would address this by iterating through all available resolution strategies at each hop until reaching a terminal (MODULE_OUTPUT or true ENTRY_POINT).

### Testing Gap to Close

1. Add an integration test that runs full codegen on e2e_attr_expr and asserts `financial.total_capex` wires to MODULE_OUTPUT (not ENTRY_POINT) — mirroring the customer's Phase 2.3 check
2. Add a unit test variant of `test_colon_colon_binding_to_expose_pure_resolves_transitively` that uses virtual CalcUsage instance names (qualified format) to test the template expansion scenario

### Why This Bug Was Missed

The Bug 2 design document correctly identified the `::` normalization issue and the EXPOSE_PURE transitive path. But:
1. The unit test used concrete instance names, not virtual/qualified ones
2. The unit test's `source_file` mismatch (defaulting to `Path("unknown")`) coincidentally doesn't matter for concrete CalcUsages
3. No E2E test for e2e_attr_expr checks specific pipeline wiring (only the solar_battery E2E test does, at `test_costed_component_e2e.py:309-327`)
4. The customer's fusion-tea validation plan is the only place that checks actual pipeline.yaml wiring for e2e_attr_expr — and that's where the failure surfaces
