# 06 -- Entry Point Classification

## What Are Entry Points?

An entry point is a pipeline input that no upstream module produces. When
the resolver finishes wiring module-to-module connections, some inputs
remain unresolved -- they have `source_type == "entry_point"`. These
values must come from the user at runtime, delivered through JSON files.

Example: a `unit_cost` parameter from a design specification. No module
computes it, so the user supplies it via a JSON input file.

---

## Step 1: Collection

The backtracker already identifies entry points during binding resolution.
`_classify_entry_points()` in `graph_builder.py` receives them directly:

```
BacktrackingResult.entry_points       -> set[str]         (qualified names)
BacktrackingResult.entry_point_sources -> dict[str, str]  (qname -> binding source)
```

Concrete scenario: a model with 10 modules and 25 total inputs might
resolve 17 to upstream outputs and leave 8 as entry points.

---

## Step 2: Classification -- The Three Types

Each entry point is classified into one of three types defined in
`EntryPointType` (`resolution/models.py`). The classifier applies a
precedence-ordered decision:

### DESIGN_ATTRIBUTE

A value defined on a part definition in the design model.

```sysml
part def SolarPanel {
    attribute area : Real = 1.6;
}
```

Becomes `DesignAttributeData` with `qualified_name =
"SolarBatteryLibrary__SolarPanel__area"`. JSON template pre-fills `1.6`.

### LIBRARY_DEFAULT

An unbound calc parameter with a default in the calc definition. The
user CAN override it but does not have to.

```sysml
calc def battery_cost_calc {
    in efficiency : Real default 0.95;
    return cost : Real;
}
```

When `efficiency` is never bound, the classifier finds
`default_value = "0.95"` from the calc def's input attributes.

### USAGE_LITERAL

A literal value bound directly in a calc usage.

```sysml
calc battery_cost : battery_cost_calc {
    in unit_cost = 4.50;
}
```

The backtracker records `4.50` in `entry_point_sources`. The classifier
parses it as the default value.

---

## Decision Logic (Pseudocode)

```
for each qname in entry_point_names:

    if qname in design_attr_index:        --> DESIGN_ATTRIBUTE
        default = float(design_attr.default_value)

    elif qname in unbound_lookup:         --> LIBRARY_DEFAULT
        default = calc_def.input_attributes[param].default_value

    else:                                 --> USAGE_LITERAL
        default = float(entry_point_sources[qname])
```

The indexes built at the top of `_classify_entry_points()`:

- **design_attr_index**: Flattens all `DesignAttributeData` into
  `dict[qualified_name, DesignAttributeData]`.
- **unbound_lookup**: For every calc usage, for every unbound param,
  builds `"{usage_qn}__{param_name}" -> (usage, param_name)`.
- **entry_point_sources**: From the backtracker; maps
  `qualified_name -> literal_value_string` for literal bindings.

Each classified entry point becomes an `EntryPoint` Pydantic model:

```python
EntryPoint(
    qualified_name="Lib__Design__battery_cost__efficiency",
    simple_name="efficiency",
    entry_type=EntryPointType.LIBRARY_DEFAULT,
    default_value=0.95,
    source_calc_usage="battery_cost_calc",
    param_group="design_params",   # assigned via group_deriver.classify()
)
```

---

## Step 3: Grouping

Entry points are organized into `ParameterGroup` objects. Each group
maps to one JSON input file and one Pydantic schema class.

`_group_entry_points_via_deriver()` delegates to `ParameterGroupDeriver`,
which groups parameters by SysML source file:

1. `group_deriver.derive_groups_filtered()` produces `DerivedParameterGroup`
   objects filtered to only true entry points.
2. `_convert_derived_groups()` converts each to a `ParameterGroup` Pydantic
   model, looking up each parameter's `EntryPoint` by qualified name.

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

This generates `inputs/solar_battery_params.json` (pre-filled template)
and `schemas/solar_battery_params.py` (Pydantic validation class). The
JSON the user edits looks like:

```json
{
  "SolarBatteryLibrary__SolarPanel__area": 1.6,
  "SolarBatteryLibrary__battery_cost__efficiency": 0.95,
  "Design__plant__battery_cost__unit_cost": 4.5
}
```

### Orphan Entry Points

After all modules are built (including computed attribute and aggregation
modules, which may add new entry points), the graph builder checks for
orphans not covered by any group. Orphans land in a fallback
`"system_design"` group.

### Rebuild After Module Construction

The initial grouping happens at Step 5 of `build_computation_graph()`.
Steps 6.5 (computed attribute modules) and 6.7 (aggregation modules) can
create new entry points. Step 6.6 rebuilds parameter groups from the
complete entry point set to capture them all.

---

## The Refactoring Improvement

Pre-refactor, entry points were discovered and mutated as a side effect
during module construction. Building a `PipelineModule` would modify a
shared mutable dict, and grouping logic was interleaved with module
wiring. This created ordering dependencies and made classification hard
to reason about.

Post-refactor, classification is a **pure computation from resolution
results**:

1. The backtracker produces `entry_points: set[str]` and
   `entry_point_sources: dict[str, str]` as outputs.
2. `_classify_entry_points()` reads those plus design attributes and calc
   defs, returning `dict[str, EntryPoint]` with no side effects.
3. Grouping reads the classified entry points and produces
   `list[ParameterGroup]`.

Each step takes data in and returns data out.

The one remaining mutation: computed attribute and aggregation module
builders can add new entry points to the dict during wiring. This is
handled by the Step 6.6 rebuild, which re-derives groups from the
complete set. The mutation is contained and predictable rather than
scattered across the build process.
