# 17 -- ParameterGroupDeriver

## What It Does

`ParameterGroupDeriver` answers: "which JSON input file should each
pipeline entry point live in?" Every entry point -- a parameter the user
supplies at runtime -- needs to land in exactly one JSON file. The deriver
groups entry points by the SysML source file they originate from, so the
generated JSON files mirror the model's file structure.

Without grouping, the system would produce one monolithic JSON file. The
deriver organizes parameters into coherent per-file groups (e.g.,
`design_params.json`, `library_params.json`).

Source: `src/sysml_codegen/analysis/parameter_groups.py`

---

## Where It Fits in the Pipeline

Constructed at **Step 5** of `build_pipeline_context()` in
`src/sysml_codegen/generation/initialization.py`:

```python
group_deriver = ParameterGroupDeriver(design_attrs, calc_usages, calc_defs)
```

Consumed in `src/sysml_codegen/resolution/graph_builder.py` two ways:
1. **`derive_groups_filtered()`** -- Step 5 of graph building produces the
   initial `ParameterGroup` list.
2. **`classify(qualified_name)`** -- called during Steps 6.5--6.7 to assign
   new entry points discovered during computed attribute / aggregation wiring.

---

## Constructor: The Four Indexes

`__init__()` builds four internal indexes mapping qualified parameter names
to source files. A strict precedence prevents duplicate claims.

| Index | Tracks | Source | Key example |
|-------|--------|--------|-------------|
| `_attr_index` | Direct design attributes with defaults | `design_attributes` dict | `SolarBatteryLibrary__SolarPanel__area` |
| `_binding_index` | Calc inputs bound to design attrs via bindings | `calc_usages[].bindings` (non-LITERAL) | `Design__plant__cost_model__wattage` |
| `_unbound_index` | Unbound calc inputs (library defaults) | `calc_usages[].unbound_params` | `Design__plant__lcoe__discount_rate` |
| `_literal_index` | Literal-bound calc inputs | `calc_usages[].bindings` (LITERAL) | `Design__plant__cost__unit_cost` |

**Precedence:** `_attr_index` > `_binding_index` > `_unbound_index` > `_literal_index`. A name claimed by an earlier index is skipped by later builders.

---

## Data Models

### DesignAttributeData (input)

Extracted from SysML `AttributeUsage` elements with a `feature_value_expression`. Produced by `extract_design_attributes()`.

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Sanitized attribute name |
| `sysml_type` | `str` | Type from heritage (e.g., `"Real"`) |
| `default_value` | `str \| None` | Literal default as string |
| `unit` | `str \| None` | Unit annotation (unimplemented) |
| `source_file` | `Path` | SysML source file path |
| `source_line` | `int` | Line number in source |
| `parent_part` | `str` | Owning part definition name |
| `qualified_name` | `str` | Full `__`-separated qualified name |

### ParameterSource (intermediate)

Wraps a single parameter inside a group.

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Qualified parameter name |
| `source_type` | `"design" \| "library"` | Origin classification |
| `source_file` | `str` | File stem (no extension) |
| `default_value` | `float \| None` | Parsed numeric default |
| `calc_def` | `str` | Owning calc def name (unbound params) |
| `sysml_type` | `str` | SysML type (defaults `"Real"`) |
| `description` | `str` | Human-readable description |

### DerivedParameterGroup (output)

One group per SysML source file. Converted to `ParameterGroup` Pydantic models by `_convert_derived_groups()` in graph_builder.

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Snake-case group name (`"design_params"`) |
| `class_name` | `str` | PascalCase class name (`"DesignParams"`) |
| `source_type` | `"design" \| "library"` | Origin classification |
| `source_identifier` | `str` | Source filename (`"design.sysml"`) |
| `parameters` | `list[ParameterSource]` | Parameters in this group |

---

## Grouping Logic: `derive_groups()`

Merges results from two internal methods:

**Phase 1 -- `_derive_from_design_attributes()`** iterates three indexes:
1. **Direct attributes** (`_attr_index`) -- each `DesignAttributeData` with a parseable numeric default becomes a `ParameterSource` grouped by `source_file.stem`.
2. **Binding-traced** (`_binding_index`) -- parameters traced to design attributes via bindings. Grouped by resolved source file, deduped.
3. **Literal-bound** (`_literal_index`) -- literal-value bindings from calc usages. Grouped by usage source file, deduped.

**Phase 2 -- `_derive_from_unbound_params_v2()`** processes `_unbound_index`. Each unbound parameter looks up its default from the calc definition's `input_attributes`. Grouped by usage source file stem.

**Merge:** Phase 2 groups are merged into Phase 1. Existing groups get new parameters appended (deduped by name); new groups are added directly.

---

## Filtering and Classification

**`derive_groups_filtered(backtracking_result, calc_defs)`** calls `derive_groups()`, removes parameters not in `backtracking_result.entry_points`, and drops empty groups. This is the primary API used by graph_builder.

**`derive_for_entry_points(entry_points)`** keeps entire groups containing at least one matching parameter (no per-parameter trimming).

**`classify(qualified_name)`** returns the group name for a single parameter by checking each index in precedence order. Returns `None` if unclaimed. Called during module construction for late-discovered entry points.

**`get_default_value(qualified_name)`** returns the numeric default. For binding-traced parameters, resolves through `_attr_index` to the source attribute.

**`_generate_group_names(base_name)`** converts a file stem to `(group_name, class_name)`:
```
"SolarBatteryDesign" -> ("solar_battery_design_params", "SolarBatteryDesignParams")
```

---

## Concrete Example: Solar Battery Model

**Input: two source files with design attributes**

```python
{
  Path("SolarBatteryDesign.sysml"): [
    DesignAttributeData(name="p_net_mw",
      qualified_name="SolarBatteryDesign__solar_battery_plant__energy_production__p_net_mw",
      default_value="100.0", source_file=Path("SolarBatteryDesign.sysml"), ...),
    DesignAttributeData(name="discount_rate",
      qualified_name="SolarBatteryDesign__solar_battery_plant__annualized_financial__discount_rate",
      default_value="0.08", source_file=Path("SolarBatteryDesign.sysml"), ...),
  ],
  Path("SolarBatteryLibrary.sysml"): [
    DesignAttributeData(name="cost_per_watt",
      qualified_name="SolarBatteryLibrary__PVModuleCostCalc__cost_per_watt",
      default_value="0.35", source_file=Path("SolarBatteryLibrary.sysml"), ...),
  ],
}
```

**Output: `derive_groups()` returns two groups**

```python
[
  DerivedParameterGroup(
    name="solar_battery_design_params", class_name="SolarBatteryDesignParams",
    source_type="design", source_identifier="SolarBatteryDesign.sysml",
    parameters=[
      ParameterSource(name="...energy_production__p_net_mw", default_value=100.0, ...),
      ParameterSource(name="...annualized_financial__discount_rate", default_value=0.08, ...),
      # + binding-traced, literal-bound, and unbound params from this file
    ]),
  DerivedParameterGroup(
    name="solar_battery_library_params", class_name="SolarBatteryLibraryParams",
    source_type="design", source_identifier="SolarBatteryLibrary.sysml",
    parameters=[
      ParameterSource(name="...PVModuleCostCalc__cost_per_watt", default_value=0.35, ...),
      # + fab_factor, install_factor defaults from library calc defs
    ]),
]
```

After `derive_groups_filtered()` trims to true entry points, these become
the groups in the generated YAML's `entry_fusion` block:

```yaml
entry_fusion:
  module_type: EntryPoint
  inputs:
    library_params: LibraryParams ../inputs/library_params.json
    design_params: DesignParams ../inputs/design_params.json
```

Each JSON file is pre-filled with default values from the deriver, so the
user only edits values they want to override.
