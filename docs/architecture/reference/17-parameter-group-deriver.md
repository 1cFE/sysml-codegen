# 17 -- ParameterGroupDeriver

## What It Does

`ParameterGroupDeriver` answers: "which JSON input file should each
pipeline [entry point](06-entry-point-classifier.md) live in?" Every entry point — a parameter the user
supplies at runtime — needs to land in exactly one JSON file. The deriver
groups entry points by the SysML source file they originate from, so the
generated JSON files mirror the model's file structure.

Without grouping, the system would produce one monolithic JSON file. The
deriver organizes parameters into coherent per-file groups (e.g.,
`design_params.json`, `library_params.json`).

Source: `src/sysml_codegen/analysis/parameter_groups.py`

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-PGD-01 | Every entry point SHALL be assigned to exactly one parameter group | Precedence prevents duplicate claims; `classify()` returns first match |
| REQ-PGD-02 | Four indexes SHALL be built with strict precedence: attr > binding > unbound > literal | Each builder skips names claimed by earlier indexes |
| REQ-PGD-03 | Grouping SHALL mirror SysML source file structure (one group per file) | `_generate_group_names()` derives from `source_file.stem` |
| REQ-PGD-04 | `derive_groups_filtered()` SHALL remove parameters not in `backtracking_result.entry_points` | Filter loop retains only names present in entry_points dict |
| REQ-PGD-05 | `classify()` SHALL check indexes in precedence order and return group name or `None` | 4-index cascade with early return; `None` if unclaimed |
| REQ-PGD-06 | `get_default_value()` SHALL resolve through binding index to source attribute | Binding-traced params look up `_attr_index` for the resolved attribute |
| REQ-PGD-07 | Group names SHALL follow `{snake_case_stem}_params` / `{PascalCaseStem}Params` convention | `_generate_group_names()` output verified in test |
| REQ-PGD-08 | No deriver change is required for def-owned design-attribute matching (D1): once the backtracker (REQ-BT-10) returns the design-attr QN, the deriver's `_attr_index`-keyed `classify`/`get_default_value` resolve grouping and default automatically | `_attr_index` is keyed by qualified name, so a def-owned attr QN hits it directly; backtracker propagation covered in Item 7 matcher tests |

---

## Where It Fits in the Pipeline

Constructed at **Step 5.7** of `build_pipeline_context()` in
`src/sysml_codegen/orchestration/pipeline_builder.py` ([orchestration](02-orchestration.md)),
deliberately after the Step-5.6 FORMULA re-removal so `design_attrs` reflects the
final attribute classifications (INV-G):

```python
group_deriver = ParameterGroupDeriver(design_attrs, calc_usages, calc_defs)
```

The snapshot path builds the same deriver from loaded snapshot data
(`build_classifier_inputs_from_snapshot` in `src/sysml_codegen/snapshot/graph_rebuild.py`),
so `--from-snapshot` grouping matches live grouping.

Consumed in `src/sysml_codegen/resolution/graph_builder.py` ([graph assembly](07-graph-assembly.md)) three ways:
1. **`derive_groups_filtered()`** — Step 5 of graph building produces the
   initial [`ParameterGroup`](09-data-models.md) list (REQ-PGD-04).
2. **`classify(qualified_name)`** — called at Step 4 for initial classification and
   during Steps 6.5 and 6.7 to assign new entry points from [FORMULA](16-computed-attributes.md) / [aggregation](13-aggregation-scoping.md) wiring (REQ-PGD-05).
3. **`derive_groups()`** — the Step 6.6 rebuild calls it unfiltered, then re-filters
   against the full entry-point set so late-discovered FORMULA/aggregation entry
   points land in groups. Entry points no index claims (`classify()` returned
   `None`) are collected at Step 6.8 into a synthetic `system_design` group.

---

## Constructor: The Four Indexes

`__init__()` builds four internal indexes mapping qualified parameter names
to source files (REQ-PGD-02). A strict precedence prevents duplicate claims (REQ-PGD-01).

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

Extracted from SysML `AttributeUsage` elements with a `feature_value_expression`. Produced by `extract_design_attributes()` during [extraction](01-extraction.md).

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Sanitized attribute name |
| `sysml_type` | `str` | Type from heritage (e.g., `"Real"`) |
| `default_value` | `str \| None` | Literal default as string |
| `unit` | `str \| None` | Unit annotation (unimplemented) |
| `source_file` | `Path` | SysML source file path |
| `source_line` | `int` | Line number in source |
| `parent_part` | `str` | Owning part usage name; empty when the attribute is owned directly by a part definition |
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

One group per SysML source file (REQ-PGD-03). Converted to [`ParameterGroup`](09-data-models.md) Pydantic models by `_convert_derived_groups()` in [graph_builder](07-graph-assembly.md).

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
2. **Binding-traced** (`_binding_index`) -- parameters traced to design attributes via bindings. Grouped by resolved source file, deduped. The source-file lookup (`_find_source_file`) sanitizes the binding's source path per segment (`sanitize_qualified_name`) before probing `_attr_index`, so quoted-owner qualified names resolve (Item 7 lockstep, site 6); if no design attribute matches, the parameter falls back to the usage's source file.
3. **Literal-bound** (`_literal_index`) -- literal-value bindings from calc usages. Grouped by usage source file, deduped.

**Phase 2 -- `_derive_from_unbound_params_v2()`** processes `_unbound_index`. Each unbound parameter looks up its default from the calc definition's `input_attributes`. Grouped by usage source file stem.

**Merge:** Phase 2 groups are merged into Phase 1. Existing groups get new parameters appended (deduped by name); new groups are added directly.

---

## Filtering and Classification

**`derive_groups_filtered(backtracking_result, calc_defs)`** calls `derive_groups()`, removes parameters not in `backtracking_result.entry_points`, and drops empty groups. This is the primary API used by graph_builder.

**`derive_for_entry_points(entry_points)`** keeps entire groups containing at least one matching parameter (no per-parameter trimming).

**`classify(qualified_name)`** returns the group name for a single parameter by checking each index in precedence order (REQ-PGD-05). Returns `None` if unclaimed. Called during [graph assembly](07-graph-assembly.md) Steps 6.5 and 6.7 for late-discovered entry points from FORMULA and aggregation modules.

**`get_default_value(qualified_name)`** returns the numeric default (REQ-PGD-06). For binding-traced parameters, resolves through `_attr_index` to the source attribute. See [literal value propagation](18-literal-value-propagation.md) for how defaults flow into entry points.

**`_generate_group_names(base_name)`** converts a file stem to `(group_name, class_name)` (REQ-PGD-07):
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
the groups in the generated [pipeline YAML's](21-pipeline-yaml-generation.md) `entry_fusion` block:

```yaml
entry_fusion:
  module_type: EntryPoint
  inputs:
    library_params: LibraryParams ../inputs/library_params.json
    design_params: DesignParams ../inputs/design_params.json
```

Each JSON file is pre-filled with the defaults the deriver resolved
(`generate_all_derived_jsons` in `src/sysml_codegen/generation/entry_point.py`).
An entry point whose default is `None` is **omitted** from the JSON template —
the generated schema still declares that key required, so the user must add it
before running. An omitted key on a *resolved* entry point is the legitimate
user-fill signature; only an input whose entry point fell through resolution,
carries no value, and is still wired trips V11 (see
[modeling-assumptions](../modeling-assumptions.md)). See
[output schema rules](22-output-schema-rules.md) for schema generation.

## Related Documents

- **Pipeline context**: [00-pipeline-overview](00-pipeline-overview.md) — grouping happens at Step 4 (classify) and Step 5 (build)
- **Orchestration**: [02-orchestration](02-orchestration.md) — `build_pipeline_context()` constructs deriver at Step 5.7
- **Entry points**: [06-entry-point-classifier](06-entry-point-classifier.md) — 3 entry point types that groups organize
- **Graph assembly**: [07-graph-assembly](07-graph-assembly.md) — `_convert_derived_groups()` converts to Pydantic models; FORMULA/aggregation builders call `classify()` for new EPs
- **Extraction**: [01-extraction](01-extraction.md) — produces `DesignAttributeData` and `CalcUsageData` inputs
- **Aggregation**: [13-aggregation-scoping](13-aggregation-scoping.md) — aggregation modules create new EPs needing classification
- **Computed attrs**: [16-computed-attributes](16-computed-attributes.md) — FORMULA modules create new EPs needing classification
- **Literal propagation**: [18-literal-value-propagation](18-literal-value-propagation.md) — default value flow into entry points
- **Pipeline YAML**: [21-pipeline-yaml-generation](21-pipeline-yaml-generation.md) — `entry_fusion` block uses group names
- **Data models**: [09-data-models](09-data-models.md) — `ParameterGroup`, `EntryPoint` field definitions
