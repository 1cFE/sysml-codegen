# C26 PipelineModule Migration: Debug Analysis

**Date**: 2026-02-20
**Branch**: `cost-pattern-refactor`
**Commit**: `27b24dc` (wip C26)
**Status**: RESOLVED — 1780 passed, 0 failed, 2 skipped, 6 xfailed

---

## Executive Summary

The C26 field expansion (models + factories) is correct — all 19 field-population
tests pass. **13 test failures** across 4 categories, all traceable to 3 root causes:

| # | Root Cause | Failing Tests | Fix Complexity |
|---|-----------|---------------|----------------|
| RC-1 | Single-output attribute name lost behind `"root"` field_name | 2 identity tests | Low — wire existing helper |
| RC-2 | Aggregation/FORMULA module ordering (topological vs snapshot) | 1 identity test | Medium — align sort strategy |
| RC-3 | New fields in models break conformance assertions + baselines | 10 tests | Low — update expected sets + regenerate baselines |

### Failure Breakdown

| Category | Count | Tests | Root Cause |
|----------|-------|-------|------------|
| C01 data model field assertions | 3 | `test_req_dm_03_fields_{pipeline_module,module_input,module_output}` | RC-3 |
| C18/E2E baseline comparisons | 7 | `test_baseline_comparison_{solar_battery,chain_spike,attr_expr_probe,catf_mfe}` | RC-3 |
| C26 identity tests | 3 | `test_{module_wrapper,stencil,registry}_output_identity` | RC-1, RC-2 |

---

## RC-1: Output Attribute Name Recovery (modules.py, stencils.py)

### Symptom

For **single-output modules**, the `_from_graph()` variants use `module.calc_def_name`
(e.g., `EnergyProductionCalc`) where the old code uses the actual output attribute
name (e.g., `annual_energy_mwh`).

Diff in generated module wrapper:
```python
# OLD (correct):
annual_energy_mwh = run_energyproductioncalc(validated_inputs)
return ModuleResult(data=Float(annual_energy_mwh))

# NEW (wrong):
EnergyProductionCalc = run_energyproductioncalc(validated_inputs)
return ModuleResult(data=Float(EnergyProductionCalc))
```

### Root Cause

For single-output modules, `ModuleOutput.field_name` is deliberately set to `"root"`
during graph construction (graph_builder.py:1424):

```python
field_name = output_attr.name if is_multi_output else "root"
```

The actual attribute name (`annual_energy_mwh`) is only preserved in the channel_name
field as a PQN suffix: `Design__plant__energy_production__annual_energy_mwh`.

The `_from_graph()` code uses a **broken fallback**:

```python
out_name = out.field_name if out.field_name != "root" else module.calc_def_name
```

This falls back to `calc_def_name` (PascalCase class stem), not the attribute name.

### Evidence: Helper Exists But Is Unused

`modules.py:172-181` defines `_output_attr_name()` which correctly recovers the
attribute name from the channel_name PQN:

```python
def _output_attr_name(out) -> str:
    if out.field_name != "root":
        return out.field_name
    return out.channel_name.split("__")[-1]
```

This function is **never called** anywhere. It was written for exactly this purpose
but not wired in.

### Affected Call Sites (5 total)

| File | Line | Context |
|------|------|---------|
| `modules.py` | 210 | `_build_docstring_from_graph()` — output description in docstring |
| `modules.py` | 256 | `generate_teax_module_from_graph()` — output_attributes context |
| `stencils.py` | 563 | `_build_stub_docstring_from_graph()` — docstring output name |
| `stencils.py` | 589 | `_build_stub_docstring_from_graph()` — Returns section |
| `stencils.py` | 639 | `generate_implementation_from_graph()` — output_names list |

All 5 use the pattern:
```python
out.field_name if out.field_name != "root" else module.calc_def_name
```

### Fix (not applied — analysis only)

Replace all 5 sites with `_output_attr_name(out)` from modules.py:172. For
stencils.py, either import the helper or duplicate it (it's 4 lines).

This recovers the actual attribute name from `channel_name.split("__")[-1]` which
matches what the old code gets from `calc_def.output_attributes[0].name`.

### Risk Assessment

**Low risk**. The channel_name PQN format (`{usage_eqn}__{attr_name}`) is an
architectural invariant established in ADR-003 and validated by C02 (naming
conventions) and C18 (graph assembly). The `split("__")[-1]` extraction is safe
for all module types:

- CalcUsage: `Design__plant__energy_production__annual_energy_mwh` → `annual_energy_mwh`
- FORMULA: always single-output with `field_name="root"`, same PQN format
- Aggregation: always single-output, same PQN format

Multi-output modules use `field_name != "root"` so the fallback is never hit.

---

## RC-2: Registry Module Ordering (registry.py)

### Symptom

The `generate_registry_from_graph()` output has import statements and module list
entries in a **different order** than `generate_registry_function()`, even though
both produce the same set of modules.

### Root Cause

The old path and new path iterate modules from different sources with different
inherent orderings:

| Module Type | Old Path Source | New Path Source |
|-------------|----------------|-----------------|
| CalcUsage | `calc_defs` list (snapshot input order) | `graph.modules` filtered (topological order) |
| FORMULA | `computed_attributes` list (snapshot order) | `graph.modules` filtered (topological order) |
| Aggregation | `aggregation_data` list (snapshot order) | `graph.modules` filtered (topological order) |

**CalcUsage imports are sorted alphabetically** in both paths, so they match.
But **FORMULA and aggregation imports are appended without sorting** in both paths,
so their ordering depends on the iteration source:

- Old: snapshot order (order of extraction/scoping output)
- New: topological order (dependency-driven from graph builder)

These orderings are NOT guaranteed to match.

### Specific Divergence Observed

In the test diff, the aggregation imports appear in different positions:
- Old: `SiteInfra_capital_cost` appears between `SiteInfra_installation_cost` and
  `SolarArray_capital_cost` (snapshot order)
- New: `SolarArray_capital_cost` appears before `SiteInfra_capital_cost`
  (topological order)

### Fix Options (not applied — analysis only)

**Option A: Sort FORMULA and aggregation imports**
Add `.sort()` to both FORMULA and aggregation import lists in `_from_graph()`,
and add the same sorting to the old path. This makes both deterministic and
order-independent. But it **changes the old path's output**, requiring baseline
updates.

**Option B: Preserve snapshot order in `_from_graph()`**
Instead of iterating `graph.modules`, reconstruct the snapshot order from
PipelineModule metadata. This is fragile and defeats the purpose of being
graph-only.

**Option C: Sort all non-CalcUsage imports in `_from_graph()` AND old path**
Both paths alphabetically sort FORMULA and aggregation imports. This produces
identical output regardless of iteration order. Requires updating baselines
since old output changes too.

**Option D: Sort only in `_from_graph()` to match old output**
Determine what order the old path produces and replicate it in the new path.
This is the tightest fix but couples the new path to snapshot iteration order
semantics.

### Risk Assessment

**Medium risk**. The registry import order doesn't affect runtime behavior (Python
imports are order-independent). But REQ-PMM-04 requires byte-identical output,
so the ordering must match. Option A (sort both) is the cleanest architectural
fix and makes both paths deterministic.

---

## Summary of Findings

### What Works (19 passing tests)

- All 6 PipelineModule metadata fields populated correctly for CalcUsage modules
- ModuleInput.description and default_value populated from CalcDef input_attributes
- ModuleOutput.description, default_value, and unit populated from CalcDef output_attributes
- FORMULA modules: is_computed_attribute flag, metadata from ComputedAttributeData
- Aggregation modules: is_aggregation flag, metadata from ScopedAggregationData
- Cross-model validation: no CalcUsage module has None calc_def_name (4 models)
- All modules have at least calc_def_name populated (4 models)
- Schema identity passes (solar_battery + catf_mfe)
- Old generators still work, _from_graph variants importable, old fields unchanged

### What's Broken (3 failing tests)

| Test | Root Cause | Fix Complexity |
|------|-----------|----------------|
| `test_module_wrapper_output_identity` | RC-1: `_output_attr_name()` not used | Low — wire existing helper |
| `test_stencil_output_identity` | RC-1: same pattern in stencils.py | Low — import or duplicate helper |
| `test_registry_output_identity` | RC-2: topological vs snapshot ordering | Medium — need to align sort strategy |

### Recommended Next Steps

1. **Wire `_output_attr_name()`** into all 5 call sites (RC-1 fix)
2. **Add alphabetical sorting** for FORMULA + aggregation imports in both old and
   new registry paths (RC-2 fix)
3. **Re-run identity tests** to verify byte-identical output
4. **Regenerate baselines** if RC-2 fix changes old path output
5. **Run full test suite** (1753+ tests) to verify no regressions

---

## RC-3: Model Field Expansions Break Conformance Tests + Baselines

### Symptom

10 tests fail because the C26 commit added new fields to PipelineModule, ModuleInput,
and ModuleOutput, but:

1. **C01 conformance tests** (3 failures) assert exact field sets:
   - `test_req_dm_03_fields_pipeline_module`: expects 9 fields, now has 15
   - `test_req_dm_03_fields_module_input`: expects 3 fields, now has 5
   - `test_req_dm_03_fields_module_output`: expects 3 fields, now has 6

2. **Baseline comparison tests** (7 failures) compare ComputationGraph JSON:
   - JSON now includes `description`, `default_value`, `unit`, `source_file`,
     `source_line`, `calc_def_name`, `calc_def_qualified_name`, `doc_comment`,
     `calc_expressions`, `is_computed_attribute`, `is_aggregation`
   - Baselines were captured before C26 and don't include these fields

### Fix

1. **C01 tests**: Update `expected` sets in 3 test functions to include new fields
2. **Baselines**: Regenerate `computation_graph.json` for all 4 models:
   `scripts/capture_pipeline_baselines.py`

### Risk Assessment

**Low risk**. These are expected consequences of adding new fields to Pydantic models.
The baselines just need regeneration, and the C01 tests need their expected field
sets expanded.

---

## Recommended Fix Sequence

### Step 1: Wire `_output_attr_name()` helper (RC-1)

Replace all 5 occurrences of the broken pattern:
```python
# FROM:
out.field_name if out.field_name != "root" else module.calc_def_name
# TO:
_output_attr_name(out)
```

Files: `modules.py` (lines 210, 256), `stencils.py` (lines 563, 589, 639)

For stencils.py, import or duplicate the 4-line helper from modules.py.

### Step 2: Sort FORMULA + aggregation imports (RC-2)

In **both** `generate_registry_function()` and `generate_registry_from_graph()`,
add alphabetical sorting for FORMULA and aggregation import sections (matching
the CalcUsage sorting that already exists). This makes both paths deterministic
and order-independent.

### Step 3: Update C01 field assertions (RC-3)

Update expected field sets in `test_data_models.py`:
- PipelineModule: add 6 new fields (15 total)
- ModuleInput: add `description`, `default_value` (5 total)
- ModuleOutput: add `description`, `default_value`, `unit` (6 total)

### Step 4: Regenerate baselines (RC-3)

Run `scripts/capture_pipeline_baselines.py` to regenerate `computation_graph.json`
for all 4 models with the new fields included.

### Step 5: Full test suite validation

Run `uv run pytest tests/` — target: 0 failures.

---

## Architectural Notes

### RC-1: Design Gap in ModuleOutput

The `ModuleOutput` model loses the semantic attribute name for single-output
modules by storing `field_name="root"`. The information is recoverable from
`channel_name` via PQN parsing (`split("__")[-1]`), but this is implicit.

**Spike confirmed**: `_output_attr_name()` correctly recovers the attribute name
for all 15 CalcUsage single-output modules in solar_battery. Zero mismatches.

A future improvement could add an explicit `original_attr_name: str | None` field
to `ModuleOutput` to make this recovery unnecessary.

### RC-2: Import Ordering Determinism

The old registry path produces non-deterministic FORMULA/aggregation ordering
(depends on snapshot iteration order). The new path produces different
non-deterministic ordering (depends on topological sort). Neither is wrong,
but both should be made deterministic via sorting. This is a pre-existing issue
exposed by the migration.

---

## C26 Completion Status

**7.5 (C26 checklist scope) is complete.** All 3 ACs pass:
- Fields populated, `_from_graph()` variants exist, identity verified.

### Known Gaps for 7.6 (Phases 3-4 of doc 26 migration)

These are NOT C26 blockers — they are landmines for 7.6 when call sites switch
from old generators to `_from_graph()` variants.

#### Gap 1: Stencil auto-implementation not in `_from_graph()` variant

`generate_implementation_from_graph()` always generates **stubs** (`NotImplementedError`).
The old `generate_implementation()` dispatches on `CalcDefCompilationResult.compilability`
to generate auto-implemented stencils for `FULLY_COMPILABLE` calcs (the
`auto_implementation.py.jinja2` template path).

The `_from_graph()` variant doesn't have access to `CalcDefCompilationResult` (it's
not on `PipelineModule` — only `compilability` enum and `compiled_expression` string
are carried). When 7.6 switches call sites, either:
- (a) The `_from_graph()` variant must be extended to use `PipelineModule.compilability`
  + `compiled_expression` to dispatch into auto-impl, or
- (b) `CalcDefCompilationResult` must be carried on `PipelineModule` (heavier).

The identity tests don't catch this because `generate_implementation()` is called
**without** a `compilation_result` arg in the test, so both paths produce stubs.
In production, the CLI passes `compilation_result` and gets auto-impl for
FULLY_COMPILABLE calcs.

**Impact**: When 7.6 switches stencil generation to `_from_graph()`, all
FULLY_COMPILABLE calcs will silently downgrade from auto-implemented to stubs.

#### Gap 2: FORMULA/aggregation module identity not tested

The identity tests only build CalcUsage → CalcDef mappings via
`_build_calcusage_module_to_calcdef_map()`. FORMULA and aggregation modules don't
have corresponding `CalculationDefinitionData` objects, so they can't be compared
old-vs-new in the current test structure.

For **modules.py** and **stencils.py**, the old generators don't handle FORMULA or
aggregation modules at all (those are generated by separate code paths in
`generation/initialization.py`). So identity testing doesn't apply in the same way.

For **registry.py**, the identity test implicitly covers FORMULA and aggregation
imports because it compares the full registry output. This gap is narrow.

**Impact**: Low — mostly a coverage documentation issue rather than a real risk.
