# Design: Aggregation Entry Point Literal Propagation (Remaining Unwired)

**Status:** Implemented
**Owner:** Reid Westwood
**Created:** 2026-02-16 20:40 UTC
**Updated:** 2026-02-16
**Branch:** cost-pattern
**Commit:** b626c59 (prerequisite), implementation on cost-pattern HEAD
**Prerequisite:** Backtracker literal propagation fix (b626c59) already landed

## Overview

The previous fix (b626c59) addressed CalcUsage-level LITERAL bindings that flow
through the backtracker. This design covers the **remaining 4 unwired items**
from Phase 4 validation that go through a completely different code path: the
aggregation module builder in `_build_aggregation_module()`.

**Both problems are fixed in this design. Zero manual workarounds.**

## Related Artifacts

- **Spec:** `.project/active/redefinition-literal-propagation/spec.md`
- **Previous design:** `.project/active/redefinition-literal-propagation/design.md`
- **Validation plan:** `~/1cfe/fusion-tea/.project/active/e2e-post-codegen-validation/plan.md` (Phase 4 "Remaining Unwired (16)")

---

## Problem Statement

There are 4 remaining unwired aggregation inputs that fall back to
`EntryPoint(default_value=None)`. They split into two distinct problems.

### Problem A: 3 Permitting Sub-Costs (SingletonTerm with LITERAL :>> redefinition)

The Permitting PartDef has:
```sysml
:>> raw_material_cost = 0.0;
:>> fabrication_cost = 0.0;
:>> installation_cost = 0.0;
```

These are `RedefinitionType.LITERAL` redefinitions. No CalcUsage produces them.

The site_infra aggregation expression references them as SingletonTerms:
```sysml
:>> raw_material_cost = racking.raw_material_cost
                      + electrical_panel.raw_material_cost
                      + permitting.raw_material_cost;
```

The code path:
1. `_build_aggregation_module()` processes `SingletonTerm("permitting.raw_material_cost")`
2. `_resolve_aggregation_input_channel()` is called (graph_builder.py:987-988)
3. Inside that function, the CHAIN redefinition check (line 789-797) runs:
   `redef.redefinition_type == RedefinitionType.CHAIN and redef.attribute_name == attr`
   — skips these because they're LITERAL, not CHAIN
4. Registry lookup fails — no module produces this output
5. Returns `None` → falls back to `EntryPoint(default_value=None)` at line 1020-1025

**The literal value 0.0 is available** in the `redefinitions` list (already
passed to `_build_aggregation_module()` at line 876). It just isn't consulted
in the fallback path.

### Problem B: 1 misc_hardware_cost (LocalTerm with attribute alias indirection)

The Solar Array PartDef has:
```sysml
attribute misc_hardware_cost : Real = allocation_model.total_allocation;
```

Then in the capital_cost aggregation:
```sysml
:>> capital_cost = sum(pv_module.capital_cost)
                 + sum(inverter.capital_cost)
                 + array_bos.capital_cost
                 + misc_hardware_cost;
```

`misc_hardware_cost` is classified as a `LocalTerm` (bare name, no dot).
The code path (graph_builder.py:1039-1070):
1. Tries sibling aggregation output: looks for channel
   `{instance_path}__misc_hardware_cost__misc_hardware_cost` — doesn't exist
2. Falls back to `EntryPoint(default_value=None)`

The allocation_model module IS generated and produces a `total_allocation`
channel. But the aggregation builder doesn't know that `misc_hardware_cost`
aliases `allocation_model.total_allocation`. That indirection lives in the
SysML attribute definition, which is currently not extracted for LocalTerms.

---

## Research Findings

### Existing matching logic (CHAIN redefinitions)

`_resolve_aggregation_input_channel()` already has CHAIN matching
(graph_builder.py:789-797):

```python
for redef in redefinitions:
    if redef.redefinition_type == RedefinitionType.CHAIN and redef.attribute_name == attr:
        redef_part_name = redef.owning_part_qn.split("__")[-1]
        if sanitize_name(redef_part_name).lower() == part_usage.lower():
            chain_redef = redef
            break
```

This matches a redefinition to a SingletonTerm by comparing
`attribute_name == attr` and `sanitize_name(owning_part_qn tail) == part_usage`.
The LITERAL check would use the identical matching logic.

### Where `redefinitions` is available

- `_build_aggregation_module(agg, redefinitions, ...)` — line 876, parameter
- Passed to `_resolve_aggregation_input_channel()` for CHAIN resolution
- Available but unused in the SingletonTerm and SumTerm fallback paths

### LocalTerm data model

`LocalTerm` has only `attribute_name: str` (data_models.py:291-294). It carries
no information about what the attribute resolves to. The extraction phase
(`_walk_aggregation_ast` in hierarchy_resolver.py) classifies bare-name
FeatureReferenceExpression nodes as LocalTerms without following the attribute's
definition.

### Where attribute alias data exists (CONFIRMED)

The `misc_hardware_cost = allocation_model.total_allocation` definition is a
**computed attribute** on the SolarArray PartDef. The extraction phase already
has `extract_computed_attributes()` which produces `ComputedAttributeData`
objects. These carry `expression_text` (e.g., "allocation_model.total_allocation")
and `references` (the referenced features).

**Key finding:** `ComputedAttributeData` IS produced for EXPOSE_PURE attributes
on PartDefs. The `is_part_def` guard at `computed_attribute_extractor.py:245`
only blocks `ChannelAlias` production, not the `ComputedAttributeData` itself.
The CAD for `misc_hardware_cost` is in the `computed_attributes` list passed
to `build_computation_graph()` (initialization.py:827). It has:

- `classification = EXPOSE_PURE`
- `expression_text = "allocation_model.total_allocation"`
- `owning_part_qualified_name = "SolarBatteryLibrary::Solar_Array"`

This data is **already available** in `build_computation_graph()` but is only
consumed for FORMULA attributes (line 162 filters to `FORMULA` +
`FULLY_COMPILABLE`). The EXPOSE_PURE entries are ignored. The fix is to
build an alias map from these entries and pass it to the aggregation builder.

### Why no module exists for misc_hardware_cost

`build_computation_graph()` Step 6.5 (line 159-169) only builds modules for
FORMULA attributes. `misc_hardware_cost` is EXPOSE_PURE — it's a pure alias
to another module's output (`allocation_model.total_allocation`), not a
computation. No separate module is needed; we just need to wire the LocalTerm
to the existing `allocation_model` module's output channel.

---

## Proposed Fixes

### Fix A: LITERAL Redefinition Lookup in Aggregation Fallbacks

**Scope:** 3 permitting sub-costs
**Complexity:** Low — same matching pattern as existing CHAIN logic

#### Approach

Add a helper function that looks up LITERAL redefinition values:

```python
def _find_literal_redefinition(
    part_usage: str,
    attr: str,
    redefinitions: list[RedefinitionData],
) -> float | None:
    """Find a LITERAL :>> redefinition value for a child attribute.

    Used when an aggregation input can't resolve to a MODULE_OUTPUT
    (e.g., permitting.:>> raw_material_cost = 0.0).
    """
    for redef in redefinitions:
        if redef.redefinition_type == RedefinitionType.LITERAL and redef.attribute_name == attr:
            redef_part_name = redef.owning_part_qn.split("__")[-1]
            if sanitize_name(redef_part_name).lower() == part_usage.lower():
                if redef.literal_value is not None:
                    try:
                        return float(redef.literal_value)
                    except (ValueError, TypeError):
                        return None
    return None
```

**Location:** `graph_builder.py`, above `_build_aggregation_module()`.

This is the same matching pattern as the CHAIN check at line 789-797, just
for LITERAL instead of CHAIN.

#### Call sites (2)

**SingletonTerm fallback** (graph_builder.py:1016-1031) — the permitting case:

```python
if s_source is None:
    # Check for LITERAL :>> redefinition before creating entry point
    literal_default: float | None = None
    if "." in s_term.source_path:
        s_part, s_attr = s_term.source_path.rsplit(".", 1)
        literal_default = _find_literal_redefinition(s_part, s_attr, redefinitions)

    if literal_default is None:
        logger.warning(
            "Aggregation SingletonTerm '%s' in '%s' unresolved → ENTRY_POINT",
            s_term.source_path, agg.instance_path,
        )
    compilability = Compilability.MANUAL_REQUIRED
    ep_qn = f"{agg.module_eqn}__{param_name}"
    if ep_qn not in entry_points:
        param_group = group_deriver.classify(ep_qn) if group_deriver else None
        entry_points[ep_qn] = EntryPoint(
            qualified_name=ep_qn,
            simple_name=param_name,
            entry_type=EntryPointType.DESIGN_ATTRIBUTE,
            default_value=literal_default,     # <-- propagate value
            param_group=param_group,
        )
```

**SumTerm fallback** (graph_builder.py:921-936) — same pattern, uses
`term.part_usage_name` and `term.attribute_name` directly instead of splitting:

```python
else:
    literal_default = _find_literal_redefinition(
        term.part_usage_name, term.attribute_name, redefinitions,
    )
    if literal_default is None:
        logger.warning(
            "Aggregation SumTerm '%s' in '%s' unresolved → ENTRY_POINT",
            symbolic_ref, agg.instance_path,
        )
    compilability = Compilability.MANUAL_REQUIRED
    ep_qn = f"{agg.module_eqn}__{param_name}"
    if ep_qn not in entry_points:
        param_group = group_deriver.classify(ep_qn) if group_deriver else None
        entry_points[ep_qn] = EntryPoint(
            qualified_name=ep_qn,
            simple_name=param_name,
            entry_type=EntryPointType.DESIGN_ATTRIBUTE,
            default_value=literal_default,     # <-- propagate value
            param_group=param_group,
        )
```

#### Behavioral note

The entry point is still created (the pipeline still has an input for
`permitting_raw_material_cost`). The difference is `default_value=0.0` instead
of `None`, so the JSON template gets populated. The warning is suppressed when
we find a LITERAL match since it's a known-resolved case, not a genuinely
unresolvable input.

The `compilability = Compilability.MANUAL_REQUIRED` stays — the entry point
still exists and the implementation still needs the input wired. This is
conservative. An alternative would be to set `FULLY_COMPILABLE` when the
literal is found, since the value is constant. That's a judgment call.

#### Testing

- Unit test in `test_graph_builder_aggregation.py`: create a
  `ScopedAggregationData` with a SingletonTerm referencing
  `"permitting.raw_material_cost"`, pass a `RedefinitionData` with
  `LITERAL` / `literal_value=0.0` / `owning_part_qn="Lib__Permitting"`,
  verify the resulting EntryPoint has `default_value=0.0`.

---

### Fix B: EXPOSE_PURE Alias Resolution for LocalTerms

**Scope:** 1 item (misc_hardware_cost), generalizes to all EXPOSE_PURE LocalTerms
**Complexity:** Low — ~15 lines, data already available, uses existing resolution

#### Root Cause

`misc_hardware_cost` is classified as `EXPOSE_PURE` by the computed attribute
extractor. Its `ComputedAttributeData` is in the `computed_attributes` list
passed to `build_computation_graph()`. But Step 6.5 (line 162) only builds
modules for `FORMULA` attributes — EXPOSE_PURE entries are ignored.

When the aggregation builder encounters `misc_hardware_cost` as a LocalTerm,
it tries sibling aggregation output lookup (line 1022-1028), finds nothing,
and falls back to an entry point. The `computed_attributes` list is never
consulted.

The upstream `allocation_model` module IS generated and its output channel
(`SolarBatteryDesign__solar_battery_plant__solar_array__allocation_model__total_allocation`)
IS registered in the OutputRegistry. The data to resolve this is present
on both sides — it just needs to be connected.

#### Approach

Build an EXPOSE_PURE alias map in `build_computation_graph()` from the
`computed_attributes` list that's already a parameter. Pass it to
`_build_aggregation_module()`. In the LocalTerm fallback, check the alias
map before creating an entry point.

**Step 1: Build alias map** (in `build_computation_graph()`, between Steps 6.5 and 6.7):

```python
# Build EXPOSE_PURE alias map: (owning_part_qn, attr_name) -> source_path
# e.g., ("SolarBatteryLibrary::Solar_Array", "misc_hardware_cost")
#    -> "allocation_model.total_allocation"
expose_aliases: dict[tuple[str, str], str] = {}
for ca in (computed_attributes or []):
    if ca.classification == ComputedAttributeClassification.EXPOSE_PURE:
        expose_aliases[
            (ca.owning_part_qualified_name, ca.python_name)
        ] = ca.expression_text
```

**Step 2: Pass to aggregation builder** (Step 6.7 call site, line 173):

```python
agg_module = _build_aggregation_module(
    agg, hierarchy_redefinitions or [], output_registry,
    entry_points, group_deriver, expose_aliases,
)
```

**Step 3: LocalTerm resolution** (graph_builder.py:1030, before entry point
fallback):

```python
if l_source is None:
    # Check EXPOSE_PURE alias: attribute that aliases a CalcUsage output
    # e.g., misc_hardware_cost = allocation_model.total_allocation
    alias_key = (agg.expression.owning_part_qn, l_term.attribute_name)
    alias_source = expose_aliases.get(alias_key)
    if alias_source:
        channel = _resolve_aggregation_input_channel(
            alias_source, agg.instance_path,
            redefinitions, output_registry,
        )
        if channel:
            l_source = InputSource(
                source_type="module_output",
                producer_channel=channel,
            )

if l_source is None:
    # Genuinely unresolvable → entry point
    ...
```

#### Why this works

`expression_text` for `misc_hardware_cost` is `"allocation_model.total_allocation"`.
This is a dotted path in exactly the format `_resolve_aggregation_input_channel()`
already handles. The function will:

1. Parse `"allocation_model.total_allocation"` → `part_usage="allocation_model"`,
   `attr="total_allocation"`
2. Try CHAIN redefinition matching → miss (no CHAIN for allocation_model)
3. Try scoped registry lookup with key
   `"solar_battery_plant.solar_array.allocation_model.total_allocation"` → hit
4. Return channel
   `SolarBatteryDesign__solar_battery_plant__solar_array__allocation_model__total_allocation`

The LocalTerm wires to MODULE_OUTPUT. No entry point created. No manual
workaround.

#### Scoping safety

The alias map is keyed by `(owning_part_qn, attr_name)`. This ensures that
if multiple PartDefs define attributes with the same name but different aliases,
the correct alias is selected based on the aggregation's owning part. The
registry lookup is further scoped by `agg.instance_path`, so even in a
multi-instance scenario, the correct channel is resolved.

#### Testing

- Unit test in `test_graph_builder_aggregation.py`: create a
  `ScopedAggregationData` with a LocalTerm `"misc_hardware_cost"`, pass an
  `expose_aliases` map with `("Lib::SolarArray", "misc_hardware_cost") ->
  "allocation_model.total_allocation"`, register the allocation_model output
  in the OutputRegistry, verify the resulting ModuleInput has
  `source_type="module_output"` (not "entry_point").

---

## Summary of Changes

| Fix | Files | Lines changed | Items resolved |
|-----|-------|---------------|----------------|
| A: LITERAL redef lookup | `graph_builder.py` | ~30 (helper + 2 call sites) | 3 permitting sub-costs |
| B: EXPOSE_PURE alias map | `graph_builder.py` | ~15 (map build + 1 call site + LocalTerm check) | 1 misc_hardware_cost |

**Total: ~45 lines in 1 file. No extraction changes. No new dependencies.**

Combined with the already-landed backtracker fix (b626c59):

| Fix | Items |
|-----|-------|
| Backtracker literal propagation | 13 design parameter literals |
| Fix A: Aggregation LITERAL lookup | 3 permitting sub-costs |
| Fix B: EXPOSE_PURE alias resolution | 1 misc_hardware_cost |

Remaining unwired after all fixes: **0 items** (the 12 multiplicity items
already have values in JSON from the `SumTerm.multiplicity_count` path and
are not truly unwired — they wire to entry points with correct defaults).

---

## Validation Approach

After Fix A + Fix B:
1. All existing tests pass
2. New unit test for `_find_literal_redefinition()` and SingletonTerm fallback
3. New unit test for EXPOSE_PURE alias resolution in LocalTerm path
4. Regenerate solar_battery_v3 → verify:
   - `system_design.json` includes `permitting_raw_material_cost=0.0`,
     `permitting_fabrication_cost=0.0`, `permitting_installation_cost=0.0`
   - `misc_hardware_cost` no longer appears as an entry point in pipeline.yaml
   - `misc_hardware_cost` wires to
     `allocation_model__total_allocation` (MODULE_OUTPUT)
   - Codegen log shows 0 unresolved warnings for these 4 items
5. Phase 5 pipeline execution requires **zero manual workarounds**

---

## Implementation Notes

Both fixes landed with additional complexity beyond the original design:

**Fix A** required a `usage_type_map` (new field on `HierarchyExtractionResult`)
because the usage name `"permitting"` doesn't match the PartDef name
`"Permitting_Interconnect"` (aliased via `part permitting : 'Permitting & Interconnect'`).
The original name-matching approach from the CHAIN pattern failed. The fix extracts
`(owning_partdef_qn, usage_name) → type_partdef_qn` from `member.types` during
hierarchy extraction and threads it through to `_find_literal_redefinition()`.

**Fix B** required QN normalization because `ComputedAttributeData.owning_part_qualified_name`
uses `"::"` separator with raw names (e.g., `"SolarBatteryLibrary::'Solar Array'"`)
while `AggregationExpressionData.owning_part_qn` uses `"__"` with sanitized names
(e.g., `"SolarBatteryLibrary__Solar_Array"`). The expose_aliases map key is
normalized by splitting on `"::"`, sanitizing each segment, and joining with `"__"`.

**Files modified (6):**
- `src/sysml_codegen/extraction/data_models.py` — added `usage_type_map` field
- `src/sysml_codegen/extraction/hierarchy_resolver.py` — extracts usage→type mapping
- `src/sysml_codegen/resolution/graph_builder.py` — core fixes
- `src/sysml_codegen/generation/initialization.py` — threads new params
- `tests/integration/test_hierarchy_e2e.py` — 3 new E2E tests (Class 5)
- `tests/fixtures/baseline_yaml/solar_battery.yaml` — updated baseline

**Validation:** 667 tests pass (3 new + 664 existing). All 4 previously-unwired
items now resolve correctly.

**Next Steps:** Proceed to Phase 5 (pipeline execution validation)
