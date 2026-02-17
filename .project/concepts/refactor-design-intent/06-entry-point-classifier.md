# 06 -- Entry Point Classification

## What Are Entry Points?

An entry point is a pipeline input that no upstream module produces. When
the [input resolver](04-input-resolver.md) finishes wiring module-to-module
connections, some inputs remain unresolved -- they have
`source_type == "entry_point"`. These values must come from the user at
runtime, delivered through JSON files.

Example: a `unit_cost` parameter from a design specification. No module
computes it, so the user supplies it via a JSON input file.

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-EPC-01 | Every entry point SHALL be classified as exactly one [EntryPointType](09-data-models.md#resolution-models): {`DESIGN_ATTRIBUTE`, `LIBRARY_DEFAULT`, `USAGE_LITERAL`}. | `all(ep.entry_type in EntryPointType for ep in entry_points.values())` |
| REQ-EPC-02 | Classification SHALL follow strict precedence: `DESIGN_ATTRIBUTE` > `LIBRARY_DEFAULT` > `USAGE_LITERAL`. | Decision tree in `_classify_entry_points()`: design_attr_by_qname checked first, then unbound_lookup, then fallback |
| REQ-EPC-03 | `default_value` SHALL be converted to `float` at classification time; if conversion fails, `default_value` SHALL be `None`. | `float()` with try/except in all 3 branches (lines 324, 340, 351) |
| REQ-EPC-04 | Every classified entry point SHALL be assigned a `param_group` via [ParameterGroupDeriver](17-parameter-group-deriver.md). `classify()` may return `None` for deeply-nested QNs that don't match any group pattern; the graph-level orphan handling (REQ-EPC-05) ensures every EP belongs to a group after full assembly. | Line 356: `param_group = group_deriver.classify(qname)` |
| REQ-EPC-05 | Every entry point SHALL belong to exactly one [ParameterGroup](09-data-models.md#resolution-models). Orphans SHALL land in a `"system_design"` fallback group. | Step 6.8: orphan detection + `ParameterGroup(name="system_design", ...)` |
| REQ-EPC-06 | After [FORMULA](16-computed-attributes.md) and [aggregation](13-aggregation-scoping.md) module construction, parameter groups SHALL be rebuilt from the complete entry point set. | Step 6.6: `group_deriver.derive_groups()` re-invoked on full `entry_points` dict |
| REQ-EPC-07 | `_classify_entry_points()` SHALL be a pure function: input data in, `dict[str, EntryPoint]` out, no side effects. | Function signature returns `dict[str, EntryPoint]`; no mutation of arguments |
| REQ-EPC-08 | Entry points created by [FORMULA](16-computed-attributes.md) and [aggregation](13-aggregation-scoping.md) factories SHALL have `entry_type=DESIGN_ATTRIBUTE`. They bypass the 3-strategy classification. See [Two Creation Paths](#two-entry-point-creation-paths). | All factory EP creation sites set `entry_type=EntryPointType.DESIGN_ATTRIBUTE` |

---

## Step 1: Collection

The [backtracker](11-analysis-backtracker.md) identifies entry points during
binding resolution. `_classify_entry_points()` in `graph_builder.py` receives:

```
BacktrackingResult.entry_points       -> set[str]         (qualified names)
BacktrackingResult.entry_point_sources -> dict[str, str]  (qname -> binding source)
```

Concrete scenario: a model with 10 modules and 25 total inputs might resolve
17 to upstream outputs (via the [OutputRegistry](10-output-registry.md)) and
leave 8 as entry points.

---

## Step 2: Classification -- The Three Types

Each entry point is classified into one of three types defined in
[`EntryPointType`](09-data-models.md#resolution-models) (`resolution/models.py`).
The classifier applies a precedence-ordered decision (REQ-EPC-02):

### DESIGN_ATTRIBUTE

A value defined on a [PartDefinitionData](09-data-models.md#extraction-models)
in the design model.

```sysml
part def SolarPanel {
    attribute area : Real = 1.6;
}
```

Becomes `DesignAttributeData` with `qualified_name =
"SolarBatteryLibrary__SolarPanel__area"`. JSON template pre-fills `1.6`.

### LIBRARY_DEFAULT

An unbound calc parameter with a default in the [calc definition](01-extraction.md#1-calculation-definitions-calculationdefinitiondata). The user CAN override it.

```sysml
calc def battery_cost_calc {
    in efficiency : Real default 0.95;
    return cost : Real;
}
```

When `efficiency` is never bound, the classifier calls
`_get_library_default(calc_def, param_name)` to extract `default_value = 0.95`.

### USAGE_LITERAL

A literal value bound directly in a [calc usage](01-extraction.md#2-calculation-usages-calcusagedata).

```sysml
calc battery_cost : battery_cost_calc {
    in unit_cost = 4.50;
}
```

The backtracker records `4.50` in `entry_point_sources`. The classifier
parses it via `float("4.50")` (REQ-EPC-03).

---

## Decision Logic (Pseudocode)

```
for each qname in entry_point_names:

    if qname in design_attr_by_qname:     --> DESIGN_ATTRIBUTE
        default = float(attr.default_value)

    elif qname in unbound_lookup:          --> LIBRARY_DEFAULT
        default = _get_library_default(calc_def, param_name)

    else:                                  --> USAGE_LITERAL
        default = float(entry_point_sources[qname])
```

The indexes built at the top of `_classify_entry_points()`:

- **design_attr_by_qname**: `dict[str, DesignAttributeData]` -- flattens all
  design attributes by `attr.qualified_name` for O(1) lookup.
- **unbound_lookup**: `dict[str, tuple[CalcUsageData, str]]` -- for every
  usage's `unbound_params`, maps `"{usage_qn}__{param_name}" -> (usage, param_name)`.
- **entry_point_sources**: From the [backtracker](11-analysis-backtracker.md);
  maps `qualified_name -> literal_value_string` for LITERAL bindings.

Each classified entry point becomes an [`EntryPoint`](09-data-models.md#resolution-models):

```python
EntryPoint(
    qualified_name="Lib__Design__battery_cost__efficiency",
    simple_name="efficiency",
    entry_type=EntryPointType.LIBRARY_DEFAULT,
    default_value=0.95,
    source_calc_usage="battery_cost_calc",
    param_group="design_params",
    python_type="float",   # default; overridden for orphans via module input lookup
)
```

---

## Step 3: Grouping

Entry points are organized into [`ParameterGroup`](09-data-models.md#resolution-models) objects. Each group maps to one JSON input file and one Pydantic schema class.

`_group_entry_points_via_deriver()` delegates to
[ParameterGroupDeriver](17-parameter-group-deriver.md):

1. `group_deriver.derive_groups_filtered(backtracking_result, calc_defs)`
   produces `DerivedParameterGroup` objects filtered to true entry points.
2. `_convert_derived_groups(derived_groups, entry_points)` converts each to
   a `ParameterGroup`, looking up each parameter's `EntryPoint` by qualified name.

Result:

```python
ParameterGroup(
    name="solar_battery_params",
    class_name="SolarBatteryParams",
    source_file=Path("solar_battery.sysml"),
    parameters=[
        EntryPoint(qn="...__area", entry_type=DESIGN_ATTRIBUTE, default=1.6),
        EntryPoint(qn="...__efficiency", entry_type=LIBRARY_DEFAULT, default=0.95),
        EntryPoint(qn="...__unit_cost", entry_type=USAGE_LITERAL, default=4.5),
    ],
)
```

This generates `inputs/solar_battery_params.json` and
`schemas/solar_battery_params.py`. The JSON contains the qualified names as
keys with defaults pre-filled.

### Orphan Entry Points (REQ-EPC-05)

After all modules are built (including [FORMULA](16-computed-attributes.md)
and [aggregation](13-aggregation-scoping.md) modules, which add new entry
points via [Path 2](#path-2-factory-fallback--hardcoded-design_attribute-steps-65-67)),
Step 6.8 checks for orphans not covered by any group. Orphans land in a
fallback `ParameterGroup(name="system_design")`. Their `python_type` is
resolved by scanning module inputs that reference them.

### Rebuild After Module Construction (REQ-EPC-06)

Initial grouping happens at Step 5 of `build_computation_graph()`.
Steps 6.5 ([FORMULA modules](16-computed-attributes.md)) and 6.7
([aggregation modules](13-aggregation-scoping.md)) can create new entry
points. Step 6.6 rebuilds parameter groups from the complete entry point set:

1. Get fresh groups via `group_deriver.derive_groups()` (unfiltered).
2. Filter each group's parameters to only those present in `entry_points` dict.
3. Remove empty groups.
4. Convert to `ParameterGroup` Pydantic models via `_convert_derived_groups()`.

---

## Two Entry Point Creation Paths

Entry points are created at two different points in the pipeline, with
**different classification logic** (REQ-EPC-08):

### Path 1: Backtracker → `_classify_entry_points()` (Step 4)

The [backtracker](11-analysis-backtracker.md) discovers entry points during DFS
(see [24-dual-resolution](24-dual-resolution-architecture.md)). Then
`_classify_entry_points()` applies the **3-strategy classification** above:

```
backtracker.entry_points  →  _classify_entry_points()  →  {qn: EntryPoint(...)}
                              ↑ uses design_attr_by_qname, unbound_lookup,
                                entry_point_sources for full classification
```

This path handles CalcUsage entry points with correct `entry_type` assignment:
DESIGN_ATTRIBUTE, LIBRARY_DEFAULT, or USAGE_LITERAL.

> **Coverage note (C17 conformance, 2026-02-17)**: solar_battery has **zero
> DESIGN_ATTRIBUTE EPs from Path 1** classifier. Design attribute QNs use
> library-qualified names (e.g., `SolarBatteryLibrary__PVModuleCostCalc__cost_per_watt`)
> while EP QNs use design-qualified names (e.g., `SolarBatteryDesign__solar_battery_plant__...`).
> The QNs never match in `design_attr_by_qname`, so all solar_battery EPs are
> classified as LIBRARY_DEFAULT or USAGE_LITERAL. DESIGN_ATTRIBUTE EPs come
> exclusively from factory construction (Path 2). catf_mfe exercises all 3 types
> from the classifier.

### Path 2: Factory fallback → hardcoded DESIGN_ATTRIBUTE (Steps 6.5, 6.7)

When [FORMULA](16-computed-attributes.md) or [aggregation](13-aggregation-scoping.md)
modules encounter an unresolvable input, the factory creates a new `EntryPoint`
directly with `entry_type=DESIGN_ATTRIBUTE`:

```python
# In _build_computed_attr_module and _build_aggregation_module:
entry_points[ep_qname] = EntryPoint(
    entry_type=EntryPointType.DESIGN_ATTRIBUTE,  # always hardcoded
    param_group=group_deriver.classify(ep_qname),
    default_value=literal_default,  # from :>> if available
)
```

**Why hardcoded?** Factory-created entry points lack the binding context needed
for 3-strategy classification. They are not in `unbound_lookup` (not CalcUsage
params) and not in `entry_point_sources` (not literal bindings). They are
unresolvable references from expressions or aggregation terms -- values the
user must provide, which aligns with DESIGN_ATTRIBUTE semantics.

**These are never re-classified.** Step 6.6 rebuilds parameter groups but
does not re-run `_classify_entry_points()`. The `entry_type` set at creation
time is final.

## Related Documents

- **Upstream**: [05-module-factory](05-module-factory.md) -- builds modules that may add entry points; [04-input-resolver](04-input-resolver.md) -- identifies `source_type == "entry_point"` inputs
- **Downstream**: [07-graph-assembly](07-graph-assembly.md) -- packs entry point groups into [ComputationGraph](09-data-models.md#resolution-models); [08-generation](08-generation.md) -- renders JSON templates and schemas from groups
- **Sub-processes**: [17-parameter-group-deriver](17-parameter-group-deriver.md) -- grouping logic; [11-analysis-backtracker](11-analysis-backtracker.md) -- provides entry point set
- **Data models**: [09-data-models](09-data-models.md) -- `EntryPoint`, `EntryPointType`, `ParameterGroup` field definitions
- **Related classifiers**: [18-literal-value-propagation](18-literal-value-propagation.md) -- carries `:>>` literal defaults into entry points
