# Design: Pipeline Integration -- Hierarchy-Aware Module Generation

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-10 19:53 UTC
**Branch:** cost-pattern
**Epic:** COST-PATTERN (Item 4)
**Commit:** 7887d07

## Overview

Wire template CalcUsage instantiation (Item 2), redefinition resolution (Item 3), and aggregation expression compilation (Item 3) into the full extraction -> analysis -> resolution -> generation pipeline. This produces hierarchy-aware modules, auto-implementations, and pipeline YAML for the Costed Component pattern.

## Related Artifacts

- **Spec:** `.project/active/hierarchy-pipeline/spec.md`
- **Spike Report:** `.project/active/hierarchy-spike/report.md`
- **Item 2 Design:** `.project/active/template-detection/design.md`
- **Item 3 Design:** `.project/active/hierarchy-resolution/design.md`
- **Epic:** `.project/backlog/epic_costed_component_pattern.md`

---

## Research Findings

### Pipeline Orchestration (`generation/initialization.py`)

- **`PipelineContext`** (line 67): Dataclass with 10 fields. Must be extended with `hierarchy_data` and `aggregation_expressions`.
- **`build_pipeline_context()`** (lines 199-343): Steps 1-7 plus sub-steps 4.5, 6.5, 6.6. Step 4.5 (`_extract_and_filter_computed_attributes()`, lines 140-196) is the canonical pattern for adding new pipeline steps: helper function with late import, side-effects on existing data, downstream threading to backtracker + graph builder + PipelineContext.
- **Step 3** (lines 251-255): `extract_calculation_usages()` already expands templates via `expand_templates=True`. Virtual CalcUsages flow out with verbatim bindings.
- **Step 6** (lines 268-278): Backtracker accepts `computed_attributes` as keyword arg. Same pattern for aggregation data.
- **Step 7** (lines 322-330): `build_computation_graph()` accepts `computed_attributes` as keyword arg. Same pattern.

### Virtual CalcUsage Bindings (`extraction/usage_extractor.py`)

- **`_create_virtual_calc_usage()`** (lines 232-268): Copies bindings via `bindings=list(template.bindings)` (line 259) -- shallow copy, BindingInfo objects shared. Sets `owning_part_def_qn=None` (line 266).
- **`BindingInfo`** (lines 48-88): Key fields: `param_name`, `source_path`, `binding_type` (from `agentic_mbse.sysml.types.BindingType`), `literal_value`.
- **Critical gap**: Virtual CalcUsage bindings have `source_path="wattage"` (bare PartDef attribute name) -- no resolution strategy in the backtracker handles these bare names.

### Hierarchy Resolver (`extraction/hierarchy_resolver.py`)

- **`extract_hierarchy_data(model)`** (lines 451-499): Accepts only the SysIDE model. Returns `HierarchyExtractionResult` with 5 fields.
- **`RedefinitionData`** (`data_models.py:231-253`): `redefinition_type` distinguishes LITERAL/CHAIN/EXPRESSION. `target_path` list + `is_deep_path` flag for design-level deep-path overrides. `owning_part_qn` is the QN of the PartDef/PartUsage the `:>>` lives on.
- **`AggregationExpressionData`** (`data_models.py:296-325`): `input_channels` are symbolic references (e.g., `"pv_module.capital_cost"`). `entry_points` are multiplicity count attribute names. `compilability=UNKNOWN` and `has_unsupported_nodes` flag signal downstream resolution status.

### Backtracker (`analysis/dependency_backtracker.py`)

- **`_computed_attr_index`** (lines 138-149): Three key patterns per attr (dotted, bare, SysML QN). Checked at lines 400-421 in `_trace_dependencies()` BEFORE `_resolve_binding_to_usage()`. Creates `MODULE_OUTPUT` resolution with `_build_computed_attr_channel()` (lines 546-550) and `continue`s. This is the exact pattern for adding aggregation output awareness.
- **`_output_catalog`** (lines 177-190): Maps `"instance.output"` -> `CalcUsageData`. Built from all CalcUsage outputs including virtual CalcUsages.
- **`_design_attr_binding_index`** (lines 193-195, built by lines 796-832): Maps `"part.attr"` -> resolved channel target. Used by Strategy 4 (transitive resolution).
- **6 resolution strategies** in `_resolve_binding_to_usage()` (lines 699-794): Strategy 5 normalizes `::` to dotted format for design attr lookup.
- **`binding_resolutions`** dict (line 213): Key format `"{usage_qn}|{param_name}"` -> `BindingResolution`.

### Graph Builder (`resolution/graph_builder.py`)

- **`build_computation_graph()`** (lines 65-194): Steps 1-8 plus sub-steps 2.5, 6.5, 6.6. Step 2.5 extends output catalog with computed attr outputs. Step 6.5 builds computed attr modules. Step 6.6 rebuilds param_groups.
- **`_build_computed_attr_module()`** (lines 654-769): Creates `PipelineModule` from `ComputedAttributeData`. Extracts input names from `compiled_expression` via regex. Creates entry points for unresolved inputs. Sets `is_computed_attribute=True`. This is the template for `_build_aggregation_module()`.
- **`_build_pipeline_module()`** (lines 845-959): Uses `binding_resolutions` as single source of truth with fail-fast semantics.
- **`_unified_topological_sort()`** (lines 772-842): Kahn's algorithm over all modules. Handles interleaving correctly.
- **`_extend_output_catalog_with_computed_attrs()`** (lines 525-552): Pattern for extending catalog.

### CLI Generation (`cli/__init__.py`)

- **`_generate_computed_attr_modules()`** (lines 216-321): Pattern for synthetic module wrapper generation. Uses `PythonModulePath.from_sysml()`, `derive_module_type()`, and `teax_module.py.jinja2`.
- **`_generate_computed_attr_stencils()`** (lines 324-407): Pattern for auto-impl generation. Uses `auto_implementation.py.jinja2`.
- **`is_computed_attribute` usage** in `pipeline.py:123-125`: Controls YAML `name` field comment.
- **`_ensure_package_init_files()`** (lines 31-41): Already handles deep hierarchy directories.
- **Registry** (`generation/registry.py:91-119`): Appends computed attr modules to `all_modules`. Must also append aggregation modules.

### Resolution Models (`resolution/models.py`)

- **`PipelineModule`** (lines 149-168): `is_computed_attribute: bool = False` is the only discriminator flag. Adding `is_aggregation: bool = False` follows the same pattern.

---

## Design Decisions

### DD-1: Add `is_aggregation` flag on PipelineModule

**Decision**: Add `is_aggregation: bool = False` to `PipelineModule` (Option A).

**Rationale**: The spec requires `# source: aggregation` comments in pipeline YAML, distinct from `# source: computed_attribute`. The existing `is_computed_attribute` flag controls computed attr comments in `pipeline.py:123-125`. Reusing it for aggregation would produce misleading YAML. A dedicated flag is one field and gives correct semantics.

---

## Proposed Design

### Architecture Overview

Six integration surfaces, each following established patterns from Phase 2 (computed attributes):

```
                     Step 3.5 (NEW)                    Step 4.7 (NEW)
                   ┌──────────────┐                  ┌──────────────┐
extract_hierarchy  │ 1. Extract   │  rewrite         │ 3. Store on  │
_data()  ────────> │ 2. Rewrite   │  bindings        │ PipelineCtx  │
                   │    bindings  │─────────────────> │ 4. Derive    │
                   └──────────────┘                  │    scoped    │
                                                     │    agg data  │
                                                     └──────┬───────┘
                                                            │
                  ┌─────────────────────────────────────────┘
                  v
     Step 6                        Step 7
   ┌──────────────┐              ┌──────────────────────┐
   │ Backtracker  │              │ Graph Builder         │
   │ +agg output  │─────────────>│ +_build_aggregation   │
   │  index       │              │  _module()            │
   └──────────────┘              │ +output catalog ext   │
                                 └──────────┬───────────┘
                                            │
                                            v
                                 ┌──────────────────────┐
                                 │ CLI Generation        │
                                 │ Extend computed attr  │
                                 │ functions for agg     │
                                 └──────────────────────┘
```

---

### Component A: Data Model Changes

#### A.1: `PipelineModule` -- add `is_aggregation`

**File:** `src/sysml_codegen/resolution/models.py:168`

Add field after `is_computed_attribute`:

```python
is_aggregation: bool = False
```

#### A.2: `PipelineContext` -- new fields

**File:** `src/sysml_codegen/generation/initialization.py:66-99`

Add two fields to `PipelineContext` dataclass:

```python
hierarchy_data: HierarchyExtractionResult | None = None
aggregation_expressions: list[ScopedAggregationData] = field(default_factory=list)
```

#### A.3: Preserve `owning_part_def_qn` on Virtual CalcUsages

**File:** `src/sysml_codegen/extraction/usage_extractor.py:266`

Change `owning_part_def_qn=None` to `owning_part_def_qn=template.owning_part_def_qn`. The `is_template=False` flag (line 265) already discriminates templates from instances. Preserving the PartDef QN enables downstream code to determine which PartDef a virtual instance came from, which is required for:
- Binding rewriting: matching design overrides to the correct virtual CalcUsage
- Aggregation scoping: finding instance paths for assembly PartDefs

#### A.4: New `ScopedAggregationData` dataclass

**File:** `src/sysml_codegen/extraction/data_models.py` (new, after `HierarchyExtractionResult`)

```python
@dataclass
class ScopedAggregationData:
    """Aggregation expression scoped to a specific design instance.

    Produced by Step 4.7 from PartDef-level AggregationExpressionData.
    Each ScopedAggregationData maps a PartDef aggregation to one design
    instance path. Uses composition to avoid field drift with
    AggregationExpressionData.
    """
    expression: AggregationExpressionData  # All PartDef-level data (delegated)
    instance_path: str  # Design scope (e.g., "solar_battery_plant__solar_array")

    @property
    def module_eqn(self) -> str:
        """Module execution qualified name (ADR-003).

        Single source of truth -- used by backtracker (D.2), graph builder
        (E.2, E.4), and CLI generation (F.1).
        """
        return f"{self.instance_path}__{self.expression.attribute_name}"
```

This composes `AggregationExpressionData` rather than copying its 12 fields, preventing field drift if Item 3 data models evolve. Downstream code accesses fields via `agg.expression.attribute_name`, `agg.expression.sum_terms`, etc. The `module_eqn` property eliminates the `f"{agg.instance_path}__{agg.attribute_name}"` pattern that would otherwise appear in 3+ locations (D.2, E.2, E.4).

---

### Component B: Pipeline Orchestration

**File:** `src/sysml_codegen/generation/initialization.py`

#### B.1: Step 3.5 -- Hierarchy Extraction & Binding Rewriting

Insert after Step 3 (line 255), before Step 4 (line 257):

```python
# Step 3.5: Extract hierarchy data and rewrite virtual CalcUsage bindings
hierarchy_data = _extract_hierarchy_and_rewrite_bindings(
    extractor.model, calc_usages
)
```

New helper function `_extract_hierarchy_and_rewrite_bindings()` (following the `_extract_and_filter_computed_attributes()` pattern at lines 140-196):

1. Late import `extract_hierarchy_data` from `hierarchy_resolver`
2. Call `extract_hierarchy_data(model)` -> `hierarchy_data`
3. Call `_rewrite_virtual_bindings(calc_usages, hierarchy_data)` (see Component C)
4. Log summary: count of rewritten bindings, count of design overrides applied
5. Return `hierarchy_data`

#### B.2: Step 4.7 -- Scope Aggregation Expressions

Insert after Step 4.5 (line 263), before Step 5 (line 265):

```python
# Step 4.7: Scope aggregation expressions to design instances
scoped_agg_data = _scope_aggregation_expressions(
    hierarchy_data, calc_usages
)
```

New helper function `_scope_aggregation_expressions()`:

```python
def _scope_aggregation_expressions(
    hierarchy_data: HierarchyExtractionResult,
    calc_usages: list[CalcUsageData],
) -> list[ScopedAggregationData]:
    """Scope PartDef-level aggregation expressions to design instances.

    Returns one ScopedAggregationData per (AggregationExpressionData, instance_path)
    pair found in the virtual CalcUsage list.
    """
    result: list[ScopedAggregationData] = []

    # Build index: owning_part_def_qn -> list of virtual CalcUsage QNs
    # Only include non-template virtual CalcUsages
    virtual_qns_by_partdef: dict[str, list[str]] = {}
    for usage in calc_usages:
        if usage.is_template or not usage.owning_part_def_qn:
            continue
        virtual_qns_by_partdef.setdefault(
            usage.owning_part_def_qn, []
        ).append(usage.qualified_name)

    for agg_expr in hierarchy_data.aggregation_expressions:
        instance_paths: set[str] = set()

        # Strategy 1: Direct match -- virtual CalcUsages on the SAME PartDef
        # that owns the aggregation expression
        direct_qns = virtual_qns_by_partdef.get(agg_expr.owning_part_qn, [])
        for qn in direct_qns:
            # QN: "SolarBatteryDesign__solar_battery_plant__solar_array__cost_model"
            # Instance path = everything before the last segment (calc name)
            parent = qn.rsplit("__", 1)[0]
            instance_paths.add(parent)

        # Strategy 2: Child match -- no direct CalcUsage on this PartDef,
        # but its child PartUsages have virtual CalcUsages. Derive the
        # assembly instance path by going one level up from the child.
        if not instance_paths:
            owning_name = sanitize_name(agg_expr.owning_part_name).lower()
            for partdef_qn, qns in virtual_qns_by_partdef.items():
                for qn in qns:
                    # Look for QN segments containing the owning PartDef's name
                    # as a parent segment:
                    # QN: "SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model"
                    #                                               ^^^^^^^^^^^^ matches "solar_array"
                    # Instance path = up to and including the matching segment
                    segments = qn.split("__")
                    for i, seg in enumerate(segments):
                        if seg.lower() == owning_name and i < len(segments) - 1:
                            instance_paths.add("__".join(segments[: i + 1]))
                            break

        for path in sorted(instance_paths):
            result.append(ScopedAggregationData(
                expression=agg_expr,
                instance_path=path,
            ))

    logger.info(f"Scoped {len(result)} aggregation module(s)")
    return result
```

**Worked example** using actual solar_battery model QNs:

```
Input:
  AggregationExpressionData:
    owning_part_qn = "Lib__Solar_Array"
    owning_part_name = "Solar_Array"
    attribute_name = "capital_cost"

  Virtual CalcUsages (from expand_templates=True):
    QN = "SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model"
         owning_part_def_qn = "Lib__PV_Module"      # child PartDef, not Solar_Array
    QN = "SolarBatteryDesign__solar_battery_plant__solar_array__inverter__cost_model"
         owning_part_def_qn = "Lib__Inverter"        # child PartDef, not Solar_Array

Strategy 1 (direct match on "Lib__Solar_Array"):
  -> No virtual CalcUsages have owning_part_def_qn == "Lib__Solar_Array"
  -> instance_paths = {}

Strategy 2 (child match, owning_name = "solar_array"):
  -> Scan QN segments for "solar_array":
     "SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model"
                                                ^^^^^^^^^^^^ match at index 2
  -> Instance path = "SolarBatteryDesign__solar_battery_plant__solar_array"
  -> instance_paths = {"SolarBatteryDesign__solar_battery_plant__solar_array"}

Output:
  ScopedAggregationData(
      expression=<the AggregationExpressionData above>,
      instance_path="SolarBatteryDesign__solar_battery_plant__solar_array",
  )
  -> module_eqn = "SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost"
```

#### B.3: Thread Data Downstream

Following the computed attr pattern:

- Pass `scoped_agg_data` to `DependencyBacktracker.__init__()` as `aggregation_data=scoped_agg_data`
- Pass `scoped_agg_data` and `hierarchy_data.redefinitions` to `build_computation_graph()` as keyword args
- Store on `PipelineContext`:
  ```python
  hierarchy_data=hierarchy_data,
  aggregation_expressions=scoped_agg_data,
  ```

---

### Component C: Virtual CalcUsage Binding Rewriting

**File:** `src/sysml_codegen/generation/initialization.py` (new helper function)

#### C.1: Function Signature

```python
def _rewrite_virtual_bindings(
    calc_usages: list[CalcUsageData],
    hierarchy_data: HierarchyExtractionResult,
) -> int:
    """Rewrite virtual CalcUsage bindings using :>> design overrides.

    Mutates BindingInfo objects in-place. Returns count of rewritten bindings.
    """
```

#### C.2: Algorithm

**Phase 1 -- Build override index:**

Index design overrides by `(full_target_parent_path, leaf_attribute_name)`:

```
For each design_override in hierarchy_data.design_overrides:
    if override.is_deep_path and len(override.target_path) >= 2:
        # target_path e.g. ["pv_module", "wattage"]
        intermediate = "__".join(override.target_path[:-1])
        full_parent = f"{override.owning_part_qn}__{intermediate}"
        leaf_attr = override.target_path[-1]
        index[(full_parent, leaf_attr)] = override
    elif not override.is_deep_path:
        # Simple override e.g. :>> wattage = 400.0 directly on PartUsage
        full_parent = override.owning_part_qn
        index[(full_parent, override.attribute_name)] = override
```

**Phase 2 -- Rewrite bindings:**

```
For each usage in calc_usages:
    if usage.is_template:
        continue  # Only process virtual instances

    # Derive parent path (instance path of the PartUsage containing this CalcUsage)
    # QN: "Design__plant__solar_array__pv_module__cost_model"
    # Parent path: "Design__plant__solar_array__pv_module"
    parts = usage.qualified_name.rsplit("__", 1)
    if len(parts) < 2:
        continue
    parent_path = parts[0]

    for binding in usage.bindings:
        if binding.binding_type == BindingType.LITERAL:
            continue  # Already resolved
        if not binding.source_path:
            continue  # Unbound

        # Check: is this a bare PartDef attribute reference?
        if "." not in binding.source_path and "::" not in binding.source_path:
            # Try to match against design override index
            key = (parent_path, binding.source_path)
            override = index.get(key)

            if override and override.redefinition_type == RedefinitionType.LITERAL:
                # Rewrite to LITERAL
                binding.binding_type = BindingType.LITERAL
                binding.literal_value = override.literal_value
                binding.source_path = None
                rewrite_count += 1
```

#### C.3: Design Rationale

- **Only bare-name bindings** are rewritten. Dotted paths (`"instance.output"`) and SysML QN paths (`"Package::Part::attr"`) already have resolution strategies in the backtracker.
- **Only LITERAL design overrides** are applied. CHAIN redefinitions (`:>> capital_cost = cost_model.total_cost`) are PartDef attribute definitions that affect the aggregation channel resolution path, not CalcUsage input bindings. **FR-11 compliance note**: FR-11 requires CHAIN handling. This is satisfied via Component E.5 (`_resolve_aggregation_input_channel()`), which traces CHAIN redefinitions to resolve aggregation module input channels. The binding rewriting step (C.2) deliberately does NOT handle CHAIN because CHAIN `:>>` statements define PartDef-level attribute aliases (e.g., `capital_cost` -> `cost_model.total_cost`), not CalcUsage input parameter bindings. CalcUsage inputs reference CalcDef parameters (e.g., `wattage`), while CHAIN targets reference other part usages' outputs.
- **Mutation in-place** follows the established pattern from Step 4.5 (`_remove_formula_from_design_attrs()` mutates `design_attrs` in-place).
- **Shallow copy safety**: `_create_virtual_calc_usage()` copies `bindings=list(template.bindings)` which is a shallow list copy. But since multiple virtual instances from the same template share the same `BindingInfo` objects, in-place mutation of BindingInfo would affect all instances. Since all instances of the same template should get the same override (uniform arrays), this is correct behavior. If non-uniform arrays are ever needed, deep copy would be required (out of scope per spec).

#### C.4: Edge Cases

- **No matching override**: Binding remains as-is. The backtracker will handle it (CalcDef default -> LIBRARY_DEFAULT entry point, or no default -> entry point from unbound param).
- **Circular chains**: Not possible in the LITERAL-only rewriting path. CHAIN resolution is deferred to aggregation module building.
- **Virtual CalcUsages at different hierarchy depths**: The index key uses the full parent_path, so `plant__solar_array__pv_module` and `plant__battery_system__pv_module` (hypothetical) would correctly resolve to different overrides.

---

### Component D: Backtracker Integration

**File:** `src/sysml_codegen/analysis/dependency_backtracker.py`

#### D.1: Constructor Extension

Add `aggregation_data` parameter (following `computed_attributes` pattern at line 118):

```python
def __init__(
    self,
    all_usages: list[CalcUsageData],
    calc_defs: list,
    design_attributes: dict[Path, list[DesignAttributeData]] | None = None,
    computed_attributes: list | None = None,
    aggregation_data: list | None = None,  # NEW: list[ScopedAggregationData]
):
```

#### D.2: Build Aggregation Output Index

After `_computed_attr_index` construction (line 149), build `_aggregation_output_index`:

```python
self._aggregation_output_index: dict[str, str] = {}
# Maps symbolic references -> aggregation module output channel names

for agg in (aggregation_data or []):
    channel = get_channel_name(agg.module_eqn, agg.expression.attribute_name)

    # Extract design-level part name from instance_path
    # e.g., "solar_battery_plant__solar_array" -> last segment "solar_array"
    instance_parts = agg.instance_path.split("__")
    part_usage_name = instance_parts[-1] if instance_parts else agg.expression.owning_part_name

    # Key 1: "part_usage_name.attribute_name" (dotted, matches binding source_path)
    self._aggregation_output_index[f"{part_usage_name}.{agg.expression.attribute_name}"] = channel

    # Key 2: bare attribute_name (for top-level aggregation)
    # Only if not already present (avoid collision)
    if agg.expression.attribute_name not in self._aggregation_output_index:
        self._aggregation_output_index[agg.expression.attribute_name] = channel

    # Key 3: full instance path dotted (for explicit references)
    dotted_path = ".".join(instance_parts + [agg.expression.attribute_name])
    self._aggregation_output_index[dotted_path] = channel
```

#### D.3: Check Aggregation Index in `_trace_dependencies()`

After the computed attr check (line 421) and before `_resolve_binding_to_usage()` (line 423), add:

```python
# Check aggregation output index (same pattern as computed attr check)
agg_channel = self._aggregation_output_index.get(binding.source_path)
if agg_channel is None and "." in binding.source_path:
    bare = binding.source_path.split(".")[-1]
    agg_channel = self._aggregation_output_index.get(bare)
if agg_channel is None and "::" in binding.source_path:
    # Normalize :: to dotted, try lookup
    parts = binding.source_path.split("::")
    if len(parts) >= 2:
        dotted = f"{parts[-2]}.{parts[-1]}"
        agg_channel = self._aggregation_output_index.get(dotted)

if agg_channel is not None:
    self._binding_resolutions[mapping_key] = BindingResolution(
        resolution_type=BindingResolutionType.MODULE_OUTPUT,
        qualified_name=agg_channel,
        source_path=binding.source_path,
        is_transitive=False,
    )
    self._trace_log.append(
        f"    {param_name} -> AGGREGATION ({agg_channel})"
    )
    continue  # No recursive tracing -- graph builder creates the module
```

This follows the exact same pattern as the computed attr check (lines 400-421). The `continue` skips normal resolution since the graph builder will create the aggregation module.

#### D.4: Design Rationale

- **Pre-computed channel names**: The aggregation output index uses channel names computed from `ScopedAggregationData` (which has `instance_path`). This ensures the backtracker and graph builder produce consistent channel names.
- **Three-level cascade**: Exact match, then dotted-bare, then `::` normalization. Same pattern as computed attr index (lines 400-421).
- **No recursion**: Aggregation modules are synthetic -- the graph builder creates them. The backtracker just needs to know about their outputs for downstream wiring.

---

### Component E: Graph Builder Integration

**File:** `src/sysml_codegen/resolution/graph_builder.py`

#### E.1: Extend `build_computation_graph()` Signature

Add parameters (following `computed_attributes` pattern):

```python
def build_computation_graph(
    result: BacktrackingResult,
    calc_defs: list,
    design_attrs: dict[Path, list[DesignAttributeData]],
    group_deriver: ParameterGroupDeriver,
    compilation_results: dict | None = None,
    computed_attributes: list[ComputedAttributeData] | None = None,
    aggregation_data: list | None = None,       # NEW: list[ScopedAggregationData]
    hierarchy_redefinitions: list | None = None, # NEW: list[RedefinitionData] for chain resolution
) -> ComputationGraph:
```

#### E.2: New Step 2.7 -- Extend Output Catalog with Aggregation Outputs

After Step 2.5, add catalog entries for aggregation modules:

```python
# Step 2.7: Extend output catalog with aggregation module outputs
_extend_output_catalog_with_aggregation(output_catalog, aggregation_data or [])
```

New function `_extend_output_catalog_with_aggregation()`:

```python
def _extend_output_catalog_with_aggregation(
    output_catalog: dict[str, tuple[str, str, str]],
    aggregation_data: list[ScopedAggregationData],
) -> None:
    for agg in aggregation_data:
        module_type = derive_module_type(f"{agg.expression.owning_part_qn}::{agg.expression.attribute_name}")
        channel_name = get_channel_name(agg.module_eqn, agg.expression.attribute_name)

        # Key: "part_name.attr_name" for binding resolution
        instance_parts = agg.instance_path.split("__")
        part_name = instance_parts[-1] if instance_parts else agg.expression.owning_part_name
        key = f"{part_name}.{agg.expression.attribute_name}"
        output_catalog[key] = (module_type, channel_name, "root")
```

This must happen BEFORE Step 6 so CalcUsage modules that reference aggregation outputs (e.g., system-level CalcUsages referencing `solar_battery_plant.capital_cost`) can validate their channels.

#### E.3: New Step 6.7 -- Build Aggregation Modules

After Step 6.5 (computed attr modules), add:

```python
# Step 6.7: Build aggregation modules
for agg in (aggregation_data or []):
    agg_module = _build_aggregation_module(
        agg, hierarchy_redefinitions or [], output_catalog, entry_points, group_deriver
    )
    all_modules.append(agg_module)
```

#### E.4: `_build_aggregation_module()` Function

New function following `_build_computed_attr_module()` pattern (lines 654-769):

```python
def _build_aggregation_module(
    agg: ScopedAggregationData,
    redefinitions: list[RedefinitionData],
    output_catalog: dict[str, tuple[str, str, str]],
    entry_points: dict[str, EntryPoint],
    group_deriver: ParameterGroupDeriver,
) -> PipelineModule:
```

**Naming** (following ADR-003, using `module_eqn` property from A.4):
```python
module_name = get_module_name(agg.module_eqn)
module_type = derive_module_type(f"{agg.expression.owning_part_qn}::{agg.expression.attribute_name}")
```

**Input wiring** -- three categories from `AggregationExpressionData`:

1. **SumTerm inputs** (array child costs with multiplicity):
   - Resolve `"pv_module.capital_cost"` through `:>>` CHAIN redefinition chain via `_resolve_aggregation_input_channel()` (E.5)
   - Create `ModuleInput` with `InputSource(source_type="module_output", producer_channel=resolved_channel)`
   - Also create multiplicity count entry point from `SumTerm.multiplicity_attr`

2. **SingletonTerm inputs** (non-multiplied child references):
   - Same channel resolution as SumTerm but without multiplicity entry point
   - Dotted symbolic ref converted to `__`-separated pipeline path: `"allocation_model.total_allocation"` -> `get_channel_name(f"{agg.instance_path}__allocation_model", "total_allocation")`, yielding `"{instance_path}__allocation_model__total_allocation"`
   - If direct channel build fails, fall back to `_resolve_aggregation_input_channel()` (same as SumTerm)

3. **LocalTerm inputs** (PartDef-local attribute references):
   - `"misc_hardware_cost"` becomes an entry point
   - Entry point QN: `"{agg.module_eqn}__{local_term_name}"`
   - Create `EntryPoint(entry_type=DESIGN_ATTRIBUTE)` in the shared `entry_points` dict

**Multiplicity entry points:**
- For each `SumTerm` with `multiplicity_attr` (e.g., `"module_count"`):
  - Entry point QN: `"{agg.instance_path}__{multiplicity_attr}"`
  - `EntryPointType.DESIGN_ATTRIBUTE` with `default_value` from `SumTerm.multiplicity_count`
  - Python type: "int" (not "float")

**Compiled expression resolution:**
- The `transformed_expression` contains symbolic refs (e.g., `"module_count * pv_module.capital_cost + ..."`)
- Replace each symbolic ref with `inputs.{param_name}` where `param_name` is a sanitized input identifier
- Build the mapping: `"pv_module.capital_cost"` -> `"pv_module_capital_cost"` (input param name)
- Track the mapping for input wiring

**Output:**
```python
output = ModuleOutput(
    field_name="root",
    python_type="float",
    channel_name=get_channel_name(agg.module_eqn, agg.expression.attribute_name),
)
```

**Compilability:**
- If `agg.expression.has_unsupported_nodes`: `Compilability.MANUAL_REQUIRED`
- Otherwise: `Compilability.FULLY_COMPILABLE`

**Return:**
```python
return PipelineModule(
    name=module_name,
    module_type=module_type,
    inputs=inputs,
    outputs=[output],
    execution_order=0,  # Reassigned during unified toposort
    compilability=compilability,
    is_aggregation=True,
)
```

#### E.5: `_resolve_aggregation_input_channel()` Helper

```python
def _resolve_aggregation_input_channel(
    symbolic_ref: str,
    instance_path: str,
    redefinitions: list[RedefinitionData],
    output_catalog: dict[str, tuple[str, str, str]],
    _visited: set[str] | None = None,  # Cycle guard (spec FR: circular chain detection)
) -> str | None:
    """Resolve a symbolic aggregation input to a pipeline channel name.

    Resolution chain:
    1. Parse "part_usage.attribute" from symbolic ref
    2. Find CHAIN :>> redefinition on child PartDef for that attribute
    3. Follow chain to CalcUsage output -> build pipeline channel name
    4. Fall back to output catalog lookup

    Cycle detection: tracks visited (part_usage, attr) pairs. If a CHAIN
    redefinition leads back to an already-visited pair, logs a warning and
    returns None (caller should set MANUAL_REQUIRED compilability).
    """
    if _visited is None:
        _visited = set()

    # Parse "part_usage.attribute"
    if "." not in symbolic_ref:
        return None  # LocalTerm -- handled as entry point, not channel
    part_usage, attr = symbolic_ref.rsplit(".", 1)

    # Cycle guard
    visit_key = f"{part_usage}.{attr}"
    if visit_key in _visited:
        logger.warning(f"Circular CHAIN detected: {visit_key} already visited in {_visited}")
        return None
    _visited.add(visit_key)

    # Step 1: Find CHAIN redefinition for this attribute on the child PartDef
    chain_redef = None
    for redef in redefinitions:
        if (redef.redefinition_type == RedefinitionType.CHAIN
                and redef.attribute_name == attr
                and sanitize_name(redef.owning_part_name).lower() == part_usage.lower()):
            chain_redef = redef
            break

    if chain_redef and chain_redef.source_path:
        # Step 2: Parse chain source "calc_usage.output"
        if "." in chain_redef.source_path:
            calc_usage, output = chain_redef.source_path.rsplit(".", 1)
            channel = get_channel_name(
                f"{instance_path}__{part_usage}__{calc_usage}", output
            )
            # Verify channel exists
            if any(v[1] == channel for v in output_catalog.values()):
                return channel
        # If chain source is itself a dotted reference, recurse with cycle guard
        return _resolve_aggregation_input_channel(
            chain_redef.source_path, instance_path, redefinitions,
            output_catalog, _visited
        )

    # Step 3: Fall back to output_catalog lookup (handles agg-to-agg references)
    catalog_key = f"{part_usage}.{attr}"
    if catalog_key in output_catalog:
        return output_catalog[catalog_key][1]  # channel_name

    return None
```

**Worked examples:**

For `"pv_module.capital_cost"` (SumTerm, CHAIN redefinition exists):
1. Parse: `part_usage="pv_module"`, `attr="capital_cost"`
2. Cycle guard: add `"pv_module.capital_cost"` to visited set
3. Find redefinition: on `Lib__PV_Module`, CHAIN `:>> capital_cost = cost_model.total_cost`
4. Parse chain source: `calc_usage="cost_model"`, `output="total_cost"`
5. Build channel: `get_channel_name("SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model", "total_cost")`
6. Verify channel exists in output_catalog -> return

For `"solar_array.capital_cost"` (top-level aggregation referencing child aggregation):
1. Parse: `part_usage="solar_array"`, `attr="capital_cost"`
2. Cycle guard: add `"solar_array.capital_cost"` to visited set
3. Find redefinition: on `Lib__Solar_Array`, EXPRESSION type (not CHAIN) -> no match
4. Fall back: check output_catalog for `"solar_array.capital_cost"` -> matches aggregation module output from Step 2.7

#### E.6: Verify Step 6.6 Handles Aggregation Entry Points

Step 6.6 (lines 168-181) rebuilds param_groups from the shared `entry_points` dict. Since `_build_aggregation_module()` adds entry points to this same dict (multiplicity counts and local terms), Step 6.6 will automatically include them. No changes needed.

---

### Component F: CLI Generation Extension

**File:** `src/sysml_codegen/cli/__init__.py`

#### F.1: Extend `_generate_computed_attr_modules()` for Aggregation

After the computed attribute loop (line 236-321), add an aggregation module loop:

```python
# Generate aggregation module wrappers
for agg in (ctx.aggregation_expressions or []):
    # Same pattern as computed attr: derive SysML QN, PythonModulePath, etc.
    sysml_qn = f"{agg.expression.owning_part_qn}::{agg.expression.attribute_name}"
    # ... (same template rendering as computed attrs)
    # Input names derived from resolved input list (not regex)
    # Use teax_module.py.jinja2 template
```

The template context follows the same structure as computed attrs (lines 288-308). Key differences:
- `doc_comment` references "Aggregation module" instead of "Computed attribute module"
- `calc_expressions` shows the `raw_expression_text` and `transformed_expression`
- `input_attributes` derived from the aggregation module's resolved inputs

#### F.2: Extend `_generate_computed_attr_stencils()` for Aggregation

After the computed attribute loop (line 342-407), add an aggregation auto-impl loop:

```python
for agg in (ctx.aggregation_expressions or []):
    if agg.expression.has_unsupported_nodes:
        # Generate stub (MANUAL_REQUIRED), not auto-impl
        continue  # or generate with TODO placeholder

    # Same pattern: derive paths, build context
    # single_output_expression = resolved compiled expression
    # Use auto_implementation.py.jinja2 template
```

#### F.3: Pipeline YAML Source Comments

**File:** `src/sysml_codegen/generation/pipeline.py:121-126`

Extend `_module_to_context()`:

```python
"name": (
    f"source: aggregation ({module.module_type})"
    if module.is_aggregation
    else f"source: computed_attribute ({module.module_type})"
    if module.is_computed_attribute
    else module.module_type
),
```

#### F.4: Registry Extension

**File:** `src/sysml_codegen/generation/registry.py:91-119`

After the computed attribute module append loop, add aggregation modules:

```python
for agg in (aggregation_data or []):
    sysml_qn = f"{agg.expression.owning_part_qn}::{agg.expression.attribute_name}"
    module_type_full = derive_module_type(sysml_qn)
    class_name = module_type_full.split(".")[-1]
    all_modules.append({"class_name": class_name, "module_type": module_type_full})
```

#### F.5: Backlog Extension

**File:** `src/sysml_codegen/generation/stencils.py` (in `generate_backlog_report()`)

Add summary count for aggregation auto-implementations, following the computed attr summary pattern.

---

## Potential Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Instance path derivation produces wrong scope for aggregation modules | Medium | High | Unit test with solar_battery model virtual CalcUsage QNs. Verify instance paths match expected `solar_battery_plant__solar_array`, etc. |
| Channel resolution fails for nested aggregation (agg -> agg) | Medium | High | The output catalog extension (Step 2.7) must happen BEFORE aggregation module building (Step 6.7). Since both read/write the same catalog, ordering is critical. |
| Binding rewriting with shared BindingInfo objects affects sibling CalcUsages unintentionally | Low | Medium | For uniform arrays (all instances share same template), shared mutation is correct. Add warning log if non-uniform override detected. |
| Design override index key mismatch due to QN formatting differences | Medium | Medium | Use `sanitize_name()` consistently. Unit test override matching with actual solar_battery model QNs. |
| Aggregation input channel resolution fails (no CHAIN redefinition found) | Low | High | Fallback to output catalog lookup. Log warning if resolution fails -- module still generates but with MANUAL_REQUIRED compilability. |
| Step ordering in graph builder creates unresolvable channel references | Low | High | Step 2.7 (catalog extension) must precede Step 6 (CalcUsage modules) and Step 6.7 (aggregation modules). Validate with `_validate_channel_references()` in Step 8. |

---

## Integration Strategy

### Incremental Implementation Order

1. **Data model changes** (A.1-A.4): Foundation, no behavioral change
2. **Binding rewriting** (C.1-C.4): Enables virtual CalcUsages to flow through existing pipeline
3. **Pipeline orchestration** (B.1-B.3): Wires hierarchy data through the pipeline
4. **Backtracker integration** (D.1-D.4): Enables system-level CalcUsage wiring to aggregation outputs
5. **Graph builder** (E.1-E.6): Creates aggregation PipelineModules
6. **CLI generation** (F.1-F.5): Produces artifacts

Each step can be tested independently:
- After step 2-3: virtual CalcUsages produce modules with resolved bindings
- After step 4: system-level CalcUsages show MODULE_OUTPUT resolutions to aggregation channels
- After step 5: aggregation PipelineModules appear in ComputationGraph
- After step 6: full artifact generation

### Reuse Strategy

| Existing Pattern | What to Reuse | Where |
|-----------------|---------------|-------|
| `_extract_and_filter_computed_attributes()` | Helper function structure, late import, logging pattern | Step 3.5 |
| `_computed_attr_index` (backtracker) | Three-key index, cascade lookup, `continue` pattern | Aggregation output index |
| `_build_computed_attr_module()` | PipelineModule construction, entry point creation, naming | `_build_aggregation_module()` |
| `_extend_output_catalog_with_computed_attrs()` | Catalog extension pattern | Step 2.7 |
| `_generate_computed_attr_modules/stencils()` | Template rendering, path handling, `_ensure_package_init_files()` | Aggregation module/stencil generation |

---

## Validation Approach

### Unit Tests

**New file:** `tests/unit/test_hierarchy_pipeline.py` (or extend existing test files)

1. **Binding rewriting tests:**
   - Virtual CalcUsage with matching design override -> binding becomes LITERAL
   - Virtual CalcUsage with no matching override -> binding unchanged
   - Multiple virtual CalcUsages from same template -> all rewritten
   - Deep-path override at different hierarchy levels -> correct scoping

2. **Backtracker aggregation index tests:**
   - System-level CalcUsage binding resolves to aggregation channel
   - Dotted reference `"solar_array.capital_cost"` resolves correctly
   - Bare reference `"capital_cost"` resolves for top-level aggregation
   - `::` format reference normalizes and resolves

3. **Aggregation module building tests:**
   - SumTerm input resolves through CHAIN redefinition to virtual CalcUsage channel
   - SingletonTerm input resolves to direct CalcUsage channel
   - LocalTerm becomes entry point
   - Multiplicity count becomes DESIGN_ATTRIBUTE Integer entry point
   - `has_unsupported_nodes=True` -> MANUAL_REQUIRED compilability

4. **Channel resolution tests:**
   - `"pv_module.capital_cost"` resolves through `:>> capital_cost = cost_model.total_cost`
   - Nested aggregation: `"solar_array.capital_cost"` resolves to aggregation module output
   - Missing chain -> fallback to output catalog
   - Missing everywhere -> warning logged, MANUAL_REQUIRED

### Integration Tests

**New file:** `tests/integration/test_hierarchy_pipeline.py`

1. **Virtual CalcUsage through full pipeline**: Build pipeline context with solar_battery model, verify virtual CalcUsage modules in ComputationGraph
2. **Aggregation module in ComputationGraph**: Verify `solar_array__capital_cost` module has correct inputs/outputs
3. **Topological ordering**: Verify leaf -> aggregation -> system ordering
4. **Pipeline YAML generation**: Verify `# source: aggregation` comments appear

### Manual Verification

- Run `uv run sysml-codegen generate` on solar_battery model
- Inspect generated pipeline YAML for correct module ordering
- Inspect generated auto-implementations for aggregation modules
- Count modules: expect 9 leaf + 4 aggregation + 5 system-level (minimum)

---

**Next Step:** After approval -> `/_my_plan`
