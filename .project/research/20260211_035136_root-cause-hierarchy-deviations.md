---
date: 2026-02-11T03:51:36-06:00
researcher: Claude
topic: "Root cause analysis of Phase 1 discovery deviations"
tags: [research, hierarchy, aggregation, bug-analysis, cost-pattern]
status: complete
last_updated: 2026-02-11
---

# Research: Root Cause Analysis of Phase 1 Hierarchy E2E Deviations

**Date**: 2026-02-11T03:51:36-06:00
**Researcher**: Claude
**Research Type**: Codebase / Bug Analysis

## Research Question

Root cause analysis of 4 Phase 1 discovery deviations found during E2E validation:
1. Aggregation modules have no impl files / unresolved `Evaluation()` expressions
2. `site_infra` missing from aggregation scoping
3. No multiplicity entry points (`module_count`, `inverter_count`, `pack_count`)
4. `annualized_financial.total_capex` wires to `ENTRY_POINT` not aggregation output

Cross-reference with original spike research and Item 1-4 designs to understand whether we're going in circles.

## Summary

- **Deviation 1**: Missing expression compilation step for aggregation. The `transformed_expression` is symbolic text, not compilable Python. No compiler exists to map symbolic refs to `inputs.X` form. **New bug introduced in Item 4** -- the architecture never included this step.
- **Deviation 2**: Name mismatch in `_scope_aggregation_expressions()` Strategy 2. Sanitized PartDef name `site_infrastructure` doesn't match PartUsage QN segment `site_infra`. **New bug introduced in Item 4** -- the other 3 assemblies match by coincidence.
- **Deviation 3**: Multiplicity entry points ARE created in `_build_aggregation_module()` and added to `entry_points` dict, but `ParameterGroupDeriver.derive_groups()` never produces `ParameterSource` entries for them (they're library PartDef attributes not in any deriver index). The Step 6.6 filter drops them. **Semi-new bug** -- architecture correct, filtering gap.
- **Deviation 4**: Composition failure between EXPOSE_PURE alias resolution (Bug 2 fix) and aggregation output index (Item 4). The index keys use `capital_cost` (attribute name) but CalcUsage bindings reference `total_capex` (EXPOSE_PURE alias). **Regression of Bug 2** -- two independently correct systems don't compose.
- **Circular fix assessment**: We are NOT going in circles. Only deviation 4 is a partial regression. Deviations 1-3 are genuinely new Item 4 gaps.

## Detailed Findings

### Deviation 1: No Aggregation Impl Files

**Symptom**: 15 aggregation module wrappers exist in `modules/` but 0 impl files exist in `handwritten/`. Backlog reports "0 functions to implement".

**Root Cause**: Missing expression compilation step.

The expression pipeline for CalcDefs has two phases:
1. **Extraction**: Raw SysML expressions → AST-based extraction (produces symbolic text)
2. **Compilation**: Symbolic text → `inputs.X`-form Python code (via `compile_calc_def()` in Step 6.5)

Aggregation expressions only go through phase 1. `hierarchy_resolver.build_aggregation_expression()` produces a symbolic `transformed_expression` like:
```
module_count * pv_module.capital_cost + inverter_count * inverter.capital_cost + ...
```

But `_generate_aggregation_stencils()` (cli/__init__.py:510-589) writes this symbolic text directly into the auto-impl template. The template expects `inputs.X`-form Python (e.g., `inputs.pv_module_capital_cost * inputs.module_count`). The symbolic refs don't match any `ModuleInput.param_name` entries.

Furthermore, there's a guard at cli/__init__.py:527-531:
```python
if agg.expression.has_unsupported_nodes:
    continue
if not agg.expression.transformed_expression:
    continue
```

This skips aggregation expressions that have unsupported nodes or empty expressions. But even when the guard passes, the expression is symbolic, not executable.

**The data needed exists**: `_build_aggregation_module()` (graph_builder.py:900-1086) already maps symbolic refs to `ModuleInput.param_name` entries. It creates the correct `param_name` for each term:
- SumTerm: `param_name = f"{term.part_usage_name}_{term.attribute_name}"` (line 935)
- Multiplicity: `param_name = term.multiplicity_attr` (line 988)
- SingletonTerm: `param_name = s_term.source_path.replace(".", "_")` (line 999)
- LocalTerm: `param_name = l_term.attribute_name` (line 1045)

The fix needs a compilation step that rewrites the symbolic expression using these mappings to produce `inputs.X`-form Python.

**Evidence this is new**: The original spike (report.md) didn't address expression compilation for aggregation. Item 4 design focused on module building but not impl generation. The `_generate_aggregation_stencils()` function was written in Item 4 but never tested against real output.

**Code References**:
- `src/sysml_codegen/cli/__init__.py:510-589` - Stencil generation with symbolic expression
- `src/sysml_codegen/extraction/hierarchy_resolver.py:400-448` - `build_aggregation_expression()` produces symbolic text
- `src/sysml_codegen/resolution/graph_builder.py:900-1086` - `_build_aggregation_module()` has param_name mappings
- `src/sysml_codegen/generation/initialization.py:440-480` - Step 6.5 only compiles CalcDef expressions

---

### Deviation 2: Site Infrastructure Missing from Aggregation

**Symptom**: Only 3 of 4 expected assembly aggregation modules appear. `site_infra` (Site Infrastructure) is missing entirely. Expected: `pv_array`, `energy_storage`, `site_infra`, `bos`. Got: `pv_array`, `energy_storage`, `bos`.

**Root Cause**: Name mismatch in `_scope_aggregation_expressions()` Strategy 2.

The scoping function (initialization.py:296-347) tries two strategies:
1. **Strategy 1** (lines 322-326): Direct match on owning PartDef QN in virtual CalcUsages
2. **Strategy 2** (lines 330-338): Child match -- scan virtual CalcUsage QN segments for a segment matching `sanitize_name(agg_expr.owning_part_name).lower()`

For Site Infrastructure:
- `agg_expr.owning_part_name` = `"Site Infrastructure"` (raw SysML name with space)
- `sanitize_name("Site Infrastructure").lower()` = `"site_infrastructure"` (snake_case)
- Virtual CalcUsage QN segments contain `"site_infra"` (the PartUsage name, NOT the PartDef name)

The comparison at line 336 is:
```python
if seg.lower() == owning_name and i < len(segments) - 1:
```

`"site_infra"` != `"site_infrastructure"` → no match → no instance_paths → no ScopedAggregationData.

The other 3 assemblies match by coincidence:
- PV Array: PartDef name `"PV Array"` → `"pv_array"`, PartUsage QN segment `"pv_array"` ✓
- Energy Storage: PartDef name `"Energy Storage"` → `"energy_storage"`, PartUsage QN segment `"energy_storage"` ✓
- BOS: PartDef name `"BOS"` → `"bos"`, PartUsage QN segment `"bos"` ✓

**Fix**: Strategy 2 needs fuzzy matching or a PartDef→PartUsage name lookup. Options:
1. Compare using `startswith()` or substring containment instead of exact equality
2. Build a PartDef QN → PartUsage name mapping from the hierarchy data and match on that
3. Normalize both names the same way (e.g., abbreviation expansion)

Option 2 is the most robust -- use the actual PartUsage element names from the hierarchy tree.

**Evidence this is new**: Item 4 implemented `_scope_aggregation_expressions()` as a new function. The spike identified aggregation structure but didn't design the scoping step. Strategy 2 was a heuristic that happens to fail on abbreviated names.

**Code References**:
- `src/sysml_codegen/generation/initialization.py:296-347` - `_scope_aggregation_expressions()` Strategy 2
- `src/sysml_codegen/generation/initialization.py:330-338` - Exact name comparison fails for abbreviated PartUsage names

---

### Deviation 3: No Multiplicity Entry Points

**Symptom**: No `module_count`, `inverter_count`, or `pack_count` entry points appear in generated JSON input files or parameter groups.

**Root Cause**: Entry points are created but not surfaced in parameter groups.

The flow:
1. `hierarchy_resolver._walk_aggregation_ast()` (lines 337-342) correctly populates `SumTerm.multiplicity_attr` from `mult_data.count_attribute_name` ✓
2. `_build_aggregation_module()` (graph_builder.py:970-995) creates `ModuleInput` entries for multiplicity and adds entry points to the `entry_points` dict ✓
3. Step 6.6 (graph_builder.py:190-203) rebuilds `param_groups` by:
   - Calling `group_deriver.derive_groups()` which returns `DerivedParameterGroup`s with `ParameterSource` entries
   - Filtering: `group.parameters = [p for p in group.parameters if p.name in all_ep_names]`

The problem: `group_deriver.derive_groups()` (parameter_groups.py:445-465) only produces `ParameterSource` entries from 4 indices:
- `_attr_index` - design file attributes
- `_binding_index` - bound parameters
- `_unbound_index` - unbound calc parameters
- `_literal_index` - literal values

Multiplicity attributes (e.g., `module_count`) are PartDef-level attributes from **library** files, not design files. They aren't CalcUsage parameters either. So they appear in NONE of these 4 indices. The deriver never creates `ParameterSource` entries for them, so the Step 6.6 intersection (`if p.name in all_ep_names`) has nothing to match against.

The entry points ARE in `entry_points` dict (added at line 975), but there's no corresponding `ParameterSource` in any group, so they fall through.

**Fix**: After Step 6.6 filtering, collect "orphan" entry points (those in `entry_points` dict but not covered by any `ParameterGroup`) and place them in a catch-all group or synthesize `ParameterSource` entries for them.

**Evidence this is semi-circular**: Bug 1 fix (Item 3) added `_build_aggregation_module()` which correctly creates multiplicity entry points. But the deriver was never extended to know about library-scoped multiplicity attributes. This is a new gap, not a regression -- the entry points didn't exist before Item 4.

**Code References**:
- `src/sysml_codegen/extraction/hierarchy_resolver.py:337-342` - SumTerm.multiplicity_attr populated ✓
- `src/sysml_codegen/resolution/graph_builder.py:970-995` - Multiplicity entry points created ✓
- `src/sysml_codegen/resolution/graph_builder.py:190-203` - Step 6.6 rebuild drops orphans
- `src/sysml_codegen/analysis/parameter_groups.py:445-465` - `derive_groups()` only uses 4 indices

---

### Deviation 4: total_capex Wires to ENTRY_POINT

**Symptom**: `annualized_financial.total_capex` input resolves to `ENTRY_POINT` instead of wiring to the `solar_battery_plant.capital_cost` aggregation module output. Meanwhile, `annualized_om.p_net_kw` correctly wires to `MODULE_OUTPUT` (to the PV Array aggregation).

**Root Cause**: Composition failure between EXPOSE_PURE alias resolution and aggregation output indexing.

The aggregation output index (dependency_backtracker.py:153-183) builds lookup keys from `ScopedAggregationData`:
```python
# Key 1: "part_usage_name.attribute_name"
f"{part_usage_name}.{agg.expression.attribute_name}"
# Example: "solar_battery_plant.capital_cost"
```

But the CalcUsage binding for `total_capex` in `annualized_financial` references:
- `binding.source_path` = something like `Solar Battery Plant::total_capex` (the EXPOSE_PURE alias, NOT the bare attribute name `capital_cost`)

The EXPOSE_PURE pattern (`:>> total_capex = sum(...)`) creates an alias. The aggregation expression has `attribute_name = "capital_cost"` (the underlying attribute being summed), but the design PartDef exposes it as `total_capex` via `:>>` redefinition.

Index lookup fails:
1. Direct lookup: `"Solar Battery Plant::total_capex"` not in index ✗
2. Dotted fallback (line 461-463): `bare = "total_capex"` → not in index (index has `"capital_cost"`) ✗
3. `::` fallback (lines 464-470): `dotted = "Solar Battery Plant.total_capex"` → not in index (index has `"solar_battery_plant.capital_cost"` with sanitized name AND different attribute name) ✗

**Two sub-bugs**:
1. **Alias mismatch**: Index keys use `capital_cost`, binding references `total_capex`. The `:>>` redefinition creates an alias that's never resolved.
2. **Case/sanitization mismatch**: `::` fallback uses raw PartDef name `"Solar Battery Plant"` but index uses sanitized `"solar_battery_plant"`.

**Fix**: The aggregation output index needs to also register EXPOSE_PURE aliases. When building the index, for each aggregation expression, also check if the owning PartDef has `:>>` redefinitions that alias the attribute_name, and add index entries for those alias names too. Additionally, the `::` fallback should sanitize the PartDef name.

**Evidence this is a regression**: Bug 2 (Item 3) fixed EXPOSE_PURE transitive resolution for CalcDef bindings. Item 4 built the aggregation output index but didn't account for EXPOSE_PURE aliases. The two systems were independently correct but don't compose. This is a composition regression -- not a destructive circular fix.

**Code References**:
- `src/sysml_codegen/analysis/dependency_backtracker.py:153-183` - Aggregation output index building
- `src/sysml_codegen/analysis/dependency_backtracker.py:457-482` - Aggregation lookup with failing fallbacks
- `src/sysml_codegen/analysis/dependency_backtracker.py:464-470` - `::` fallback with unsanitized names

---

## Circular Fix Assessment

**Are we going in circles?** No. Here's the evidence:

### Prior Bug Fixes (Item 3 / commit 93f0a55)

The 6 bugs fixed in commit 93f0a55 were:
1. **Bug 1**: `Evaluation()` proxy handling in expression compiler → Fixed correctly, not regressed
2. **Bug 2**: EXPOSE_PURE transitive resolution → Fixed correctly for CalcDef bindings, but **composition gap** with new aggregation index (Deviation 4)
3. **Bug 3**: Duplicate module deduplication → Fixed correctly, not regressed
4. **Bug 5**: Channel name case sensitivity → Fixed correctly, not regressed
5. **Bug 6**: Binding source_path extraction → Fixed correctly, not regressed
6. **Bug 7**: Entry point default value extraction → Fixed correctly, not regressed

### Current Deviations vs Prior Fixes

| Deviation | Prior Fix Related? | Nature | Circular? |
|-----------|-------------------|--------|-----------|
| 1 (No impl files) | None | New gap in Item 4 | No |
| 2 (site_infra missing) | None | New bug in Item 4 | No |
| 3 (No multiplicity EPs) | Semi: Bug 1 architecture | New filtering gap in Item 4 | No |
| 4 (total_capex wiring) | Yes: Bug 2 EXPOSE_PURE | Composition failure | Partial |

**Deviation 4 is the only one related to a prior fix**, and it's a composition failure (two independently correct systems) not a destructive regression. The Bug 2 fix itself is still correct -- it properly resolves EXPOSE_PURE for CalcDef bindings. The gap is that the new aggregation output index (Item 4) doesn't know about EXPOSE_PURE aliases.

**Why these bugs exist**: Item 4 was a large architectural addition (hierarchy extraction + aggregation pipeline) that created 4 new subsystems:
1. Hierarchy extraction (hierarchy_resolver.py) - works correctly
2. Aggregation scoping (initialization.py) - has name matching bug
3. Aggregation module building (graph_builder.py) - works correctly
4. Aggregation stencil generation (cli/__init__.py) - missing compilation step

The subsystems work individually but have integration gaps at their boundaries.

## Fix Recommendations

### Fix 1: Aggregation Expression Compilation (Deviation 1)

**Approach**: Add a compilation step that maps symbolic refs to `inputs.X` form using the `ModuleInput.param_name` mappings already computed in `_build_aggregation_module()`.

**Location**: Either:
- (A) In `_build_aggregation_module()` after building inputs, compile the expression and store on the module. Then `_generate_aggregation_stencils()` reads from the module.
- (B) In `_generate_aggregation_stencils()`, build the ref→param_name mapping from `ScopedAggregationData.expression` terms and do string replacement.

Option (A) is cleaner -- keeps compilation near the data that defines the mapping.

**Effort**: Small-medium. The mapping data exists; needs connecting.

### Fix 2: Site Infrastructure Scoping (Deviation 2)

**Approach**: Fix Strategy 2 in `_scope_aggregation_expressions()` to handle PartDef→PartUsage name mismatches.

**Best option**: Use `hierarchy_data.part_hierarchy` (if available) to build a PartDef QN → PartUsage name mapping, then match on PartUsage name instead of sanitized PartDef name.

**Fallback option**: Use substring/prefix matching: `seg.lower().startswith(owning_name[:4])` or check if either name is a prefix of the other.

**Effort**: Small. Single function fix.

### Fix 3: Multiplicity Entry Point Surfacing (Deviation 3)

**Approach**: After Step 6.6 filtering, collect orphan entry points and either:
- (A) Add them to the nearest matching existing group based on instance_path prefix
- (B) Create a synthetic "system_design" group for all multiplicity/count parameters

**Effort**: Small. Post-filtering step.

### Fix 4: EXPOSE_PURE Alias in Aggregation Index (Deviation 4)

**Approach**: When building `_aggregation_output_index`, also register `:>>` redefinition aliases. For each aggregation expression, check if the owning PartDef has redefinitions that map `attribute_name` to an alias, and add index entries for those aliases.

Additionally, normalize the `::` fallback to sanitize PartDef names before lookup.

**Data source**: `hierarchy_data.redefinitions` (already passed to `build_computation_graph()` and available during backtracker construction).

**Effort**: Small-medium. Need to thread redefinitions into backtracker constructor.

### Recommended Fix Order

1. **Fix 2** (site_infra scoping) - quickest, unblocks aggregation module count from 3 → 4
2. **Fix 4** (EXPOSE_PURE alias) - unblocks total_capex wiring, fixes the only regression
3. **Fix 3** (multiplicity EPs) - unblocks count parameters in input JSONs
4. **Fix 1** (expression compilation) - largest, unblocks auto-impl generation

## Open Questions

1. **Fix 1 storage**: Should compiled aggregation expressions be stored on `ScopedAggregationData.expression` (data model change) or on the `PipelineModule` (already has compilability)?
2. **Fix 2 robustness**: Is there a reliable PartDef→PartUsage mapping in `hierarchy_data` we can use, or do we need to build one?
3. **Fix 3 grouping**: Should multiplicity parameters go in a "system_design" group or be distributed to the assembly's group?
4. **Scope**: Should these 4 fixes be a new Item (5b) or rolled into Item 5 (E2E validation)?
