# Spec 07: Graph Builder + Orchestration Changes

**Epic**: OUTPUT-REGISTRY (Items 3, 4)
**Target files**:
- `src/sysml_codegen/resolution/graph_builder.py`
- `src/sysml_codegen/generation/initialization.py`
- `src/sysml_codegen/resolution/models.py`
**Status**: Draft
**Created**: 2026-02-13

---

## 1. Overview

This spec describes the changes to `build_computation_graph()` (Step 7) and `build_pipeline_context()` (orchestration) required by the OutputRegistry redesign. The core change is that the graph builder **no longer builds its own output catalog** -- the OutputRegistry (built in Step 5) replaces this. The orchestration function gains a new Step 5, loses Steps 3.6 and 4.7 as separate steps, and threads the `OutputRegistry` through to the backtracker.

### Traceability

| Design Doc Section | What it specifies | How this spec implements it |
|---|---|---|
| Section 9 (Step 7) | Three module families, sub-steps, fail-fast contract | Sections 3-5 below |
| Section 10 (Generation) | Templates read from ComputationGraph only | No changes to templates |
| Section 12 (OutputRegistry) | 4-phase registration protocol | Section 6 below |
| Appendix C (Migration Path) | Item ordering, parallel validation | Section 8 below |

---

## 2. Orchestration Changes (`initialization.py`)

### 2.1 New Pipeline Flow

The canonical `build_pipeline_context()` function changes as follows:

```python
def build_pipeline_context(
    model_paths: list[Path],
    targets: list[str] | None = None,
    include_all: bool = True,
    design_path_filter: str = "",
) -> PipelineContext:
    # Steps 1-3: UNCHANGED
    extractor = SysMLDataExtractor(model_paths)
    extractor.load_models()
    calc_defs = extractor.extract_calculation_definitions()
    calc_usages, _report = extract_calculation_usages(extractor.model, calc_defs=calc_defs)

    # Step 3.5: hierarchy + override + scoping + CHAIN aliases
    # CHANGED: Returns 3 values instead of 1
    hierarchy_data, scoped_agg_data, chain_aliases = _extract_hierarchy_and_rewrite_bindings(
        extractor.model, calc_usages
    )

    # Step 3.6: REMOVED -- _enrich_aliases_from_bindings() is eliminated entirely.
    # Aliases are now produced exclusively by Step 3.5 (CHAIN redefs) and Step 4.5 (EXPOSE_PURE).

    # Step 4: Extract design attributes (UNCHANGED)
    design_attrs = extract_design_attributes(extractor.model, design_path_filter=design_path_filter)

    # Step 4.5: computed attributes + EXPOSE_PURE aliases + synthetic CalcUsages
    # CHANGED: Returns 3 values (see Spec 04 for authoritative signature)
    computed_attrs, expose_pure_aliases, synthetic_usages = _extract_and_filter_computed_attributes(
        extractor.model, calc_usages, design_attrs
    )

    # Append synthetic CalcUsages to the main list BEFORE Step 5+6
    calc_usages.extend(synthetic_usages)

    # Step 5: Build OutputRegistry (NEW STEP)
    output_registry = _build_output_registry(
        calc_usages, calc_defs, scoped_agg_data, computed_attrs,
        chain_aliases, expose_pure_aliases, design_attrs,
    )

    # Step 5.5: Create parameter group deriver (UNCHANGED, renumbered)
    group_deriver = ParameterGroupDeriver(design_attrs, calc_usages, calc_defs)

    # Step 6: backtracking with OutputRegistry
    # CHANGED: Constructor takes output_registry instead of computed_attributes + aggregation_data
    backtracker = DependencyBacktracker(
        calc_usages,
        calc_defs,
        design_attributes=design_attrs,
        output_registry=output_registry,
    )
    backtracking_result = backtracker.find_required_modules(
        targets or [],
        include_all=include_all,
    )

    # Step 6.5: expression compilation (UNCHANGED)
    compilation_results = _compile_expressions(calc_defs)

    # Step 7: build computation graph
    # CHANGED: no longer receives hierarchy_redefinitions (output catalog removed)
    computation_graph = build_computation_graph(
        result=backtracking_result,
        calc_defs=calc_defs,
        design_attrs=design_attrs,
        group_deriver=group_deriver,
        compilation_results=compilation_results,
        computed_attributes=computed_attrs,
        aggregation_data=scoped_agg_data,
    )

    return PipelineContext(
        extractor=extractor,
        calc_defs=calc_defs,
        calc_usages=calc_usages,
        design_attributes=design_attrs,
        group_deriver=group_deriver,
        backtracker=backtracker,
        backtracking_result=backtracking_result,
        computation_graph=computation_graph,
        compilation_results=compilation_results,
        computed_attributes=computed_attrs,
        hierarchy_data=hierarchy_data,
        aggregation_expressions=scoped_agg_data,
        output_registry=output_registry,
    )
```

### 2.2 Removed Steps

#### Step 3.6: `_enrich_aliases_from_bindings()` -- ELIMINATED

**Current code** (lines 297-343 of `initialization.py`):
```python
alias_count = _enrich_aliases_from_bindings(hierarchy_data, calc_usages)
```

**Action**: Delete the function `_enrich_aliases_from_bindings()` entirely. Delete the call site (lines 473-475). The function is semantically wrong -- it heuristically derives aliases from CalcUsage param_name divergence. Aliases are now produced exclusively by authoritative sources: CHAIN redefinitions (Step 3.5D) and EXPOSE_PURE classification (Step 4.5).

**Rationale**: The design document (Section 4, DELTA callout) explicitly eliminates Step 3.6.

### 2.3 Modified Function Signatures

#### `_extract_hierarchy_and_rewrite_bindings()`

**Current signature** (line 211):
```python
def _extract_hierarchy_and_rewrite_bindings(
    model: Any,
    calc_usages: list[CalcUsageData],
) -> HierarchyExtractionResult:
```

**New signature**:
```python
def _extract_hierarchy_and_rewrite_bindings(
    model: Any,
    calc_usages: list[CalcUsageData],
) -> tuple[HierarchyExtractionResult, list[ScopedAggregationData], list[ChannelAlias]]:
```

**Changes**:
1. **Returns a 3-tuple** instead of `HierarchyExtractionResult` alone
2. **Aggregation scoping** (currently Step 4.7, `_scope_aggregation_expressions()`) moves into this function as a sub-step. The scoping logic depends on hierarchy extraction results, not on the OutputRegistry, so it belongs here.
3. **CHAIN alias production** (new sub-step 3.5D): extracts `ChannelAlias` objects from CHAIN `:>>` redefinitions. Only DOTTED source_paths produce aliases; BARE CAS codes are filtered.

**Implementation sketch**:
```python
def _extract_hierarchy_and_rewrite_bindings(
    model: Any,
    calc_usages: list[CalcUsageData],
) -> tuple[HierarchyExtractionResult, list[ScopedAggregationData], list[ChannelAlias]]:
    from sysml_codegen.extraction.hierarchy_resolver import extract_hierarchy_data

    hierarchy_data = extract_hierarchy_data(model)

    # (E) Apply overrides to virtual CalcUsage bindings
    rewrite_count = _rewrite_virtual_bindings(calc_usages, hierarchy_data)

    # (F) Scope aggregation expressions (moved from Step 4.7)
    scoped_agg_data = _scope_aggregation_expressions(hierarchy_data, calc_usages)

    # (D) Extract CHAIN aliases from :>> redefinitions
    chain_aliases = _extract_chain_aliases(hierarchy_data, calc_usages)

    logger.info(
        "Step 3.5: Hierarchy extraction complete -- %d redefs, %d overrides, "
        "%d aggregation modules, %d CHAIN aliases, %d bindings rewritten",
        len(hierarchy_data.redefinitions),
        len(hierarchy_data.design_overrides),
        len(scoped_agg_data),
        len(chain_aliases),
        rewrite_count,
    )

    return hierarchy_data, scoped_agg_data, chain_aliases
```

#### `_extract_and_filter_computed_attributes()`

**Current signature** (line 152):
```python
def _extract_and_filter_computed_attributes(
    model: Any,
    calc_usages: list[CalcUsageData],
    design_attrs: dict[Path, list[DesignAttributeData]],
) -> list[ComputedAttributeData]:
```

**New signature** (see Spec 04 for authoritative definition):
```python
def _extract_and_filter_computed_attributes(
    model: Any,
    calc_usages: list[CalcUsageData],
    design_attrs: dict[Path, list[DesignAttributeData]],
) -> tuple[list[ComputedAttributeData], list[ChannelAlias], list[CalcUsageData]]:
```

**Changes**:
1. **Returns a 3-tuple**: computed attributes + EXPOSE_PURE channel aliases + synthetic CalcUsages (returned separately, NOT mutated in-place)
2. **EXPOSE_PURE classification** produces `ChannelAlias` objects using the `references` field (NOT `expression_text`). PartDef-level EXPOSE_PURE is filtered out (Spike 8: Issue 21). The `alias_name` is **bare** (e.g., `"total_capex"`); scoping happens at Phase 3 registration (Spec 05).
3. **FORMULA classification** produces synthetic `CalcUsageData` objects. Only `FULLY_COMPILABLE` FORMULAs produce synthetic usages. The caller appends these to `calc_usages` before Step 5.

**EXPOSE_PURE alias construction** (see Spec 04 Change B for authoritative version):
```python
expose_pure_aliases: list[ChannelAlias] = []
for ca in all_computed_attrs:
    if ca.classification != ComputedAttributeClassification.EXPOSE_PURE:
        continue
    if ca.is_on_part_definition:
        continue  # PartDef EXPOSE_PURE filtered (Spike 8: Issue 21)
    if len(ca.references) < 2:
        logger.warning("EXPOSE_PURE '%s' has %d refs (need >= 2), skipping", ca.python_name, len(ca.references))
        continue

    expose_pure_aliases.append(ChannelAlias(
        alias_name=ca.python_name,  # BARE -- scoped at Phase 3 registration (Spec 05)
        canonical_name=f"{ca.references[1].name}.{ca.references[0].name}",
        owning_part_qn=sysml_to_python_qualified_name(ca.owning_part_qualified_name),
        source="expose_pure",
    ))
```

**FORMULA synthetic CalcUsage construction** (see Spec 04 Change C for authoritative version):
```python
synthetic_usages: list[CalcUsageData] = []
for ca in all_computed_attrs:
    if ca.classification != ComputedAttributeClassification.FORMULA:
        continue
    if ca.compilability != Compilability.FULLY_COMPILABLE:
        continue

    parent_eqn = sysml_to_python_qualified_name(ca.owning_part_qualified_name)
    parent_short = ca.owning_part_name

    synthetic_usage = CalcUsageData(
        instance_name=ca.python_name,
        calc_def_name="",  # No CalcDef for inline expressions
        calc_def_qualified_name="",
        module_type="",
        qualified_name=f"{parent_eqn}__{ca.python_name}",
        bindings=[
            BindingInfo(
                param_name=ref.name,
                binding_type=BindingType.CHAIN,
                source_path=f"{parent_short}.{ref.name}",
            )
            for ref in ca.references
            if ref.name != ca.python_name
        ],
        unbound_params=[],
        is_template=False,
        owning_part_def_qn=None,
        is_computed_attribute=True,
    )
    synthetic_usages.append(synthetic_usage)
```

#### `DependencyBacktracker.__init__()`

**Current signature** (line 117):
```python
def __init__(
    self,
    all_usages: list[CalcUsageData],
    calc_defs: list,
    design_attributes: dict[Path, list[DesignAttributeData]] | None = None,
    computed_attributes: list | None = None,
    aggregation_data: list | None = None,
):
```

**New signature**:
```python
def __init__(
    self,
    all_usages: list[CalcUsageData],
    calc_defs: list,
    design_attributes: dict[Path, list[DesignAttributeData]] | None = None,
    output_registry: OutputRegistry | None = None,
):
```

**Changes**:
- `computed_attributes` parameter REMOVED -- the OutputRegistry replaces `_computed_attr_index`
- `aggregation_data` parameter REMOVED -- the OutputRegistry replaces `_aggregation_output_index`
- `output_registry` parameter ADDED -- single lookup for all CHAIN binding resolution and alias lookups

### 2.4 New Function: `_build_output_registry()`

```python
def _build_output_registry(
    calc_usages: list[CalcUsageData],
    calc_defs: list[CalculationDefinitionData],
    scoped_agg_data: list[ScopedAggregationData],
    computed_attrs: list[ComputedAttributeData],
    chain_aliases: list[ChannelAlias],
    expose_pure_aliases: list[ChannelAlias],
    design_attrs: dict[Path, list[DesignAttributeData]],
) -> OutputRegistry:
    """Step 5: Build the OutputRegistry with 4-phase registration protocol.

    Phase 1: Register canonical channels (CalcUsage, aggregation, FORMULA outputs)
    Phase 2: Register CHAIN aliases (resolve canonical_name against Phase 1)
    Phase 3: Register EXPOSE_PURE aliases (PartUsage only, resolve against Phase 1+2)
    Phase 4: Register design-attribute transitive aliases (filter numeric defaults)

    See design doc Section 12 for the authoritative key format contract.
    """
```

Full registration protocol is specified in Section 6 below.

### 2.5 `_scope_aggregation_expressions()` Relocation

**Current location**: Standalone function called at Step 4.7 (line 486)
**New location**: Called inside `_extract_hierarchy_and_rewrite_bindings()` as sub-step

The function itself is unchanged. Only its call site moves.

### 2.6 `_rewrite_virtual_bindings()` Enhancement

**Current behavior**: Only handles LITERAL overrides with bare-name matching.

**New behavior**: Handles both LITERAL and CHAIN overrides. Extracts leaf names from SYSML_QN (`::` split) and DOTTED (`.` split) formats, not just bare names.

**Changes to matching logic** (lines 283-284):
```python
# CURRENT (bare-name only):
if "." not in binding.source_path and "::" not in binding.source_path:
    key = (parent_path, binding.source_path)

# NEW (leaf extraction from any format):
if "::" in binding.source_path:
    attr_name = binding.source_path.rsplit("::", 1)[-1]
elif "." in binding.source_path:
    attr_name = binding.source_path.rsplit(".", 1)[-1]
else:
    attr_name = binding.source_path  # defensive fallback (never observed)
key = (parent_path, attr_name)
```

**Changes to override handling** (lines 288-293):
```python
# CURRENT (LITERAL only):
if matched and matched.redefinition_type == RedefinitionType.LITERAL:
    binding.binding_type = BindingType.LITERAL
    binding.literal_value = matched.literal_value
    binding.source_path = None
    rewrite_count += 1

# NEW (LITERAL + CHAIN):
if matched:
    if matched.redefinition_type == RedefinitionType.LITERAL:
        binding.binding_type = BindingType.LITERAL
        binding.literal_value = matched.literal_value
        binding.source_path = None
        rewrite_count += 1
    elif matched.redefinition_type == RedefinitionType.CHAIN:
        binding.source_path = matched.source_path
        rewrite_count += 1
    # EXPRESSION overrides: don't rewrite -- aggregation module handles them
```

---

## 3. Graph Builder Changes (`graph_builder.py`)

### 3.1 Output Catalog Removal

**Current code** (lines 107-115):
```python
# Step 2: Build output channel catalog
output_catalog = _build_output_catalog(result.required_usages, calc_def_map)

# Step 2.5: Extend output catalog with computed attribute outputs
if computed_attributes:
    _extend_output_catalog_with_computed_attrs(output_catalog, computed_attributes)

# Step 2.7: Extend output catalog with aggregation module outputs
if aggregation_data:
    _extend_output_catalog_with_aggregation(output_catalog, aggregation_data)
```

**Action**: Remove the output catalog construction entirely (Steps 2, 2.5, 2.7). The OutputRegistry already has all channel mappings from Step 5. The graph builder's output catalog was used for two purposes:
1. **CalcUsage module input wiring**: Now handled by `binding_resolutions` from the backtracker (already the case since ADR-003 Phase 7)
2. **Computed attribute module input wiring**: The `_build_attribute_resolution_map()` function uses the output catalog. This needs to be replaced.
3. **Aggregation module input wiring**: The `_build_aggregation_module()` function uses the output catalog for `_resolve_aggregation_input_channel()`. Aggregation modules still construct input channels from pre-scoped data.
4. **Channel reference validation** (`_validate_channel_references()`): Validates that all `module_output` references point to declared output channels. This validation uses the modules list directly (not the output catalog).

**Functions to remove**:
- `_build_output_catalog()` (lines 255-303)
- `_extend_output_catalog_with_computed_attrs()` (lines 583-611)
- `_extend_output_catalog_with_aggregation()` (lines 830-853)

**Functions to modify**:
- `_build_attribute_resolution_map()`: Replace `output_catalog` parameter with `OutputRegistry` or derive channel names from registry
- `_build_aggregation_module()`: Replace `output_catalog` parameter. Aggregation modules construct input channels from `ScopedAggregationData` fields directly (they do NOT go through the OutputRegistry for channel construction)
- `_build_computed_attr_module()`: Update to not use `resolution_map` that depends on output catalog

### 3.2 `build_computation_graph()` Signature Change

**Current signature** (line 69):
```python
def build_computation_graph(
    result: BacktrackingResult,
    calc_defs: list,
    design_attrs: dict[Path, list[DesignAttributeData]],
    group_deriver: ParameterGroupDeriver,
    compilation_results: dict | None = None,
    computed_attributes: list[ComputedAttributeData] | None = None,
    aggregation_data: list[ScopedAggregationData] | None = None,
    hierarchy_redefinitions: list[RedefinitionData] | None = None,
) -> ComputationGraph:
```

**New signature**:
```python
def build_computation_graph(
    result: BacktrackingResult,
    calc_defs: list,
    design_attrs: dict[Path, list[DesignAttributeData]],
    group_deriver: ParameterGroupDeriver,
    compilation_results: dict | None = None,
    computed_attributes: list[ComputedAttributeData] | None = None,
    aggregation_data: list[ScopedAggregationData] | None = None,
) -> ComputationGraph:
```

**Changes**:
- `hierarchy_redefinitions` parameter REMOVED: This was passed through to `_build_aggregation_module()` for CHAIN resolution during aggregation input channel wiring. The aggregation module builder will use `ScopedAggregationData` directly, which already contains the pre-scoped channel references.

### 3.3 Three Module Families (Unchanged Logic)

The three module families are built the same way. The key insight is that the OutputRegistry replaces how the **backtracker** resolves bindings (Step 6), not how the **graph builder** constructs modules (Step 7). The graph builder consumes `binding_resolutions` from the backtracker as its single source of truth for CalcUsage wiring.

#### Family 1: CalcUsage Modules

Built from `binding_resolutions` in `BacktrackingResult`. The `_build_pipeline_module()` function is UNCHANGED -- it already uses `binding_resolutions` as the single source of truth per ADR-003 Phase 7.

```python
# UNCHANGED (lines 1212-1326):
for idx, usage in enumerate(result.required_usages):
    module = _build_pipeline_module(
        usage=usage,
        calc_def=calc_def,
        output_catalog=...,  # no longer needed (see 3.4 below)
        entry_points=entry_points,
        execution_order=idx,
        binding_resolutions=result.binding_resolutions,
    )
```

The `output_catalog` parameter on `_build_pipeline_module()` is currently passed but NOT USED for input wiring (input wiring uses `binding_resolutions`). It can be removed from the signature.

#### Family 2: FORMULA Computed Attribute Modules

In the target design, FORMULA attributes produce synthetic `CalcUsageData` objects in Step 4.5. These synthetic CalcUsages flow through normal backtracking in Step 6. Their bindings resolve through the OutputRegistry like any other CalcUsage.

**The graph builder no longer has a separate `_build_computed_attr_module()` step.** FORMULA modules appear in `result.required_usages` as normal CalcUsage modules (marked with `is_computed_attribute=True`). They are built by the same `_build_pipeline_module()` loop as Family 1.

**Functions to remove (eventually)**:
- `_build_computed_attr_module()` (lines 712-827) -- replaced by synthetic CalcUsage flow
- `_build_attribute_resolution_map()` (lines 656-709) -- no longer needed
- `_resolve_expose_pure()` (lines 613-653) -- EXPOSE_PURE is now a ChannelAlias, not a module
- `AttributeResolution` and `AttributeResolutionKind` classes (lines 567-578)

**NOTE**: EXPOSE_PURE does NOT produce a module. It is a ChannelAlias only. The current `_resolve_expose_pure()` function maps EXPOSE_PURE to upstream channels for the `_build_attribute_resolution_map()`. This entire mechanism is replaced by the OutputRegistry's Phase 3 alias registration.

#### Family 3: Aggregation Modules

Built directly from `ScopedAggregationData`. Aggregation modules construct input channels from pre-scoped data -- they do NOT go through the OutputRegistry or `binding_resolutions` for input wiring.

The `_build_aggregation_module()` function changes:
- Remove `output_catalog` parameter (replaced by direct channel construction from scoped data)
- Remove `redefinitions` parameter (CHAIN resolution for aggregation inputs is handled differently)

The `_resolve_aggregation_input_channel()` function currently resolves symbolic references through CHAIN redefinitions and the output catalog. In the target design, this function can use the OutputRegistry for channel verification, but the primary resolution path remains the same: parse the symbolic ref, build a scoped channel name from `ScopedAggregationData.instance_path`.

### 3.4 `_build_pipeline_module()` Cleanup

**Current signature** (line 1212):
```python
def _build_pipeline_module(
    usage: CalcUsageData,
    calc_def,
    output_catalog: dict[str, tuple[str, str, str]],
    entry_points: dict[str, EntryPoint],
    execution_order: int,
    binding_resolutions: dict[str, BindingResolution],
) -> PipelineModule:
```

**New signature**:
```python
def _build_pipeline_module(
    usage: CalcUsageData,
    calc_def,
    entry_points: dict[str, EntryPoint],
    execution_order: int,
    binding_resolutions: dict[str, BindingResolution],
) -> PipelineModule:
```

**Change**: Remove `output_catalog` parameter. The function already uses `binding_resolutions` exclusively for input source resolution (the output_catalog was a leftover from before ADR-003 Phase 7).

### 3.5 Fail-Fast Contract (Unchanged)

The fail-fast contract remains exactly as specified:

```python
resolution = binding_resolutions.get(mapping_key)
if resolution is None:
    raise ValueError(f"ADR-003 VIOLATION: no resolution for {mapping_key}")
```

This is in `_build_pipeline_module()` (lines 1263-1268). No change.

### 3.6 Remaining Sub-Steps (Step 7)

After removing the output catalog, the sub-steps within `build_computation_graph()` become:

1. Build calc def lookup (`calc_def_map`)
2. Classify entry points (3 types: DESIGN_ATTRIBUTE, LIBRARY_DEFAULT, USAGE_LITERAL) -- unchanged
3. Group entry points via ParameterGroupDeriver -- unchanged
4. Build CalcUsage modules (Family 1) from `binding_resolutions` -- unchanged
5. Build FORMULA modules (Family 2) -- now handled by Family 1 loop (synthetic CalcUsages in `required_usages`)
6. Build aggregation modules (Family 3) from `ScopedAggregationData` -- simplified
7. Rebuild param_groups with ALL entry points -- unchanged
8. Collect orphan entry points -> "system_design" group -- unchanged
9. Unified topological sort -- unchanged
10. Validate channel references -- unchanged

---

## 4. PipelineContext Changes (`models.py` in `resolution/`)

No changes to `resolution/models.py`. The `PipelineModule`, `ComputationGraph`, and related Pydantic models are unchanged.

---

## 5. PipelineContext Dataclass Changes (`initialization.py`)

### 5.1 Add `output_registry` Field

```python
@dataclass
class PipelineContext:
    # ... existing fields ...
    output_registry: OutputRegistry | None = None  # Added by OutputRegistry redesign
```

The field is `Optional` with default `None` for backward compatibility during migration. After cut-over (Item 4), it becomes required.

### 5.2 Field Name Clarification

The `aggregation_expressions` field keeps its current name. No rename needed.

---

## 6. OutputRegistry Construction Protocol (`_build_output_registry()`)

This is the new Step 5 function. It implements the 4-phase registration protocol from design doc Section 12.

```python
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.core.models import ChannelAlias
from sysml_codegen.core.qualified_names import get_channel_name, sysml_to_python_qualified_name
from sysml_codegen.core.identifier_types import derive_module_type


def _build_output_registry(
    calc_usages: list[CalcUsageData],
    calc_defs: list[CalculationDefinitionData],
    scoped_agg_data: list[ScopedAggregationData],
    computed_attrs: list[ComputedAttributeData],
    chain_aliases: list[ChannelAlias],
    expose_pure_aliases: list[ChannelAlias],
    design_attrs: dict[Path, list[DesignAttributeData]],
) -> OutputRegistry:
    """Step 5: Build the OutputRegistry with 4-phase registration protocol."""
    registry = OutputRegistry()
    calc_def_map = {cd.name: cd for cd in calc_defs}

    # ---- Phase 1: Register canonical channels ----

    # CalcUsage outputs (concrete + virtual)
    for usage in calc_usages:
        if usage.is_template:
            continue
        calc_def = calc_def_map.get(usage.calc_def_name)
        if calc_def is None:
            continue

        for output_attr in calc_def.output_attributes:
            channel = get_channel_name(usage.qualified_name, output_attr.name)

            # Key_A: instance_name.output_name (dotted short)
            key_a = f"{usage.instance_name}.{output_attr.name}"
            # Key_B: EQN__output_name (full qualified)
            key_b = f"{usage.qualified_name}__{output_attr.name}"
            # Key_C: dotted hierarchy path (strips design prefix)
            segments = usage.qualified_name.split("__")
            key_c = ".".join(segments[1:]) + "." + output_attr.name

            registry.register(channel, [key_a, key_b, key_c])

    # Aggregation outputs
    for agg in scoped_agg_data:
        channel = get_channel_name(agg.module_eqn, agg.expression.attribute_name)
        instance_parts = agg.instance_path.split("__")
        part_usage_name = instance_parts[-1] if instance_parts else agg.expression.owning_part_name

        # Key_D: part_usage.attribute_name
        key_d = f"{part_usage_name}.{agg.expression.attribute_name}"
        # Key_E: full dotted (includes prefix)
        key_e = ".".join(instance_parts) + "." + agg.expression.attribute_name

        registry.register(channel, [key_d, key_e])

        # Alias variants from legacy AggregationExpressionData.aliases
        for alias_name in getattr(agg.expression, "aliases", []):
            registry.register_alias(f"{part_usage_name}.{alias_name}", channel)
            dotted_alias = ".".join(instance_parts) + "." + alias_name
            registry.register_alias(dotted_alias, channel)

    # FORMULA computed attribute outputs
    for ca in computed_attrs:
        if ca.classification != ComputedAttributeClassification.FORMULA:
            continue
        if ca.compilability != Compilability.FULLY_COMPILABLE:
            continue

        # EQN construction must match Spec 04 synthetic CalcUsage qualified_name
        parent_eqn = sysml_to_python_qualified_name(ca.owning_part_qualified_name)
        module_eqn = f"{parent_eqn}__{ca.python_name}"
        channel = get_channel_name(module_eqn, ca.python_name)

        # Key_F: owning_part.python_name
        key_f = f"{ca.owning_part_name}.{ca.python_name}"
        registry.register(channel, [key_f])

    # ---- Phase 2: Register CHAIN aliases ----
    for alias in chain_aliases:
        canonical_channel = registry.resolve(alias.canonical_name)
        if canonical_channel:
            registry.register_alias(alias.alias_name, canonical_channel)
        else:
            logger.warning(
                "CHAIN alias '%s' -> '%s' could not resolve (Phase 2)",
                alias.alias_name, alias.canonical_name,
            )

    # ---- Phase 3: Register EXPOSE_PURE aliases (PartUsage only) ----
    # alias_name is BARE (e.g., "total_capex"); scope with owning_part here (Spec 05 Section 5)
    for alias in expose_pure_aliases:
        canonical_channel = registry.resolve(alias.canonical_name)
        if canonical_channel:
            owning_part_short = alias.owning_part_qn.split("__")[-1]
            scoped_alias = f"{owning_part_short}.{alias.alias_name}"
            registry.register_alias(scoped_alias, canonical_channel)
        else:
            logger.warning(
                "EXPOSE_PURE alias '%s' -> '%s' could not resolve (Phase 3)",
                alias.alias_name, alias.canonical_name,
            )

    # ---- Phase 4: Register transitive design-attribute aliases ----
    for path_attrs in design_attrs.values():
        for attr in path_attrs:
            if not _is_transitive_default(attr):
                continue
            canonical_channel = registry.resolve(str(attr.default_value))
            if canonical_channel:
                registry.register_alias(
                    f"{attr.parent_part}.{attr.name}",
                    canonical_channel,
                )

    logger.info(
        "Step 5: OutputRegistry built -- %d canonical channels, %d total keys",
        len(registry._canonical),
        len(registry._index),
    )

    return registry


def _is_transitive_default(attr: DesignAttributeData) -> bool:
    """Check if a design attribute's default_value is a dotted path (not numeric/None).

    Transitive defaults like "cost_model.total_cost" should be registered as aliases.
    Numeric defaults like "3.14" and None values should not.
    """
    val = str(attr.default_value) if attr.default_value is not None else ""
    if "." not in val:
        return False
    try:
        float(val)
        return False  # numeric like "3.14"
    except (ValueError, TypeError):
        return True   # dotted path like "cost_model.total_cost"
```

---

## 7. `__all__` Export Updates

### `graph_builder.py`

Remove from `__all__`:
- `_build_attribute_resolution_map`
- `_build_computed_attr_module`
- `_extend_output_catalog_with_aggregation`
- `_extend_output_catalog_with_computed_attrs`
- `_resolve_expose_pure`
- `AttributeResolution`
- `AttributeResolutionKind`

Keep in `__all__`:
- `build_computation_graph`
- `MissingCalcDefError`
- `_build_aggregation_module`
- `_resolve_aggregation_input_channel`
- `_unified_topological_sort`

### `initialization.py`

Add to `__all__`:
- `_build_output_registry`
- `_is_transitive_default`

Remove from `__all__`:
- (none -- `_enrich_aliases_from_bindings` was not exported)

---

## 8. Migration Safety

### Phase 1: Parallel Validation (Item 3)

During the transition, `build_pipeline_context()` runs BOTH resolution paths:

```python
# OLD path (current backtracker with 5 indexes):
old_backtracker = DependencyBacktracker(
    calc_usages, calc_defs,
    design_attributes=design_attrs,
    computed_attributes=computed_attrs,
    aggregation_data=scoped_agg_data,
)
old_result = old_backtracker.find_required_modules(targets, include_all=include_all)

# NEW path (OutputRegistry-backed backtracker):
new_backtracker = DependencyBacktracker(
    calc_usages, calc_defs,
    design_attributes=design_attrs,
    output_registry=output_registry,
)
new_result = new_backtracker.find_required_modules(targets, include_all=include_all)

# Compare binding_resolutions
_validate_parallel_results(old_result, new_result)
```

This parallel validation gate is temporary. After all models pass with zero divergences, the old path is removed (Item 4).

### Phase 2: Cut-over (Item 4)

- Remove old backtracker indexes
- Remove `_enrich_aliases_from_bindings()` function
- Remove `_scope_aggregation_expressions()` as standalone call (moved into Step 3.5)
- Remove output catalog from graph builder
- Remove parallel validation code

---

## 9. File Diff Summary

### `src/sysml_codegen/generation/initialization.py`

```diff
+ from sysml_codegen.core.models import ChannelAlias
+ from sysml_codegen.core.output_registry import OutputRegistry

  @dataclass
  class PipelineContext:
      # existing fields...
+     output_registry: OutputRegistry | None = None

  def _extract_hierarchy_and_rewrite_bindings(
      model, calc_usages
- ) -> HierarchyExtractionResult:
+ ) -> tuple[HierarchyExtractionResult, list[ScopedAggregationData], list[ChannelAlias]]:
      ...
+     scoped_agg_data = _scope_aggregation_expressions(hierarchy_data, calc_usages)
+     chain_aliases = _extract_chain_aliases(hierarchy_data, calc_usages)
+     return hierarchy_data, scoped_agg_data, chain_aliases

  def _extract_and_filter_computed_attributes(
      model, calc_usages, design_attrs
- ) -> list[ComputedAttributeData]:
+ ) -> tuple[list[ComputedAttributeData], list[ChannelAlias], list[CalcUsageData]]:
      ...
+     expose_pure_aliases = _build_expose_pure_aliases(all_computed_attrs)
+     synthetic_usages = _build_formula_synthetic_usages(all_computed_attrs)
+     return all_computed_attrs, expose_pure_aliases, synthetic_usages

- def _enrich_aliases_from_bindings(...) -> int:
-     """REMOVED"""

+ def _build_output_registry(...) -> OutputRegistry:
+     """NEW: Step 5"""

+ def _is_transitive_default(attr) -> bool:
+     """NEW: filter for Phase 4"""

  def build_pipeline_context(...):
      ...
-     # Step 3.6: Enrich aggregation aliases from CalcUsage bindings
-     alias_count = _enrich_aliases_from_bindings(hierarchy_data, calc_usages)
      ...
+     # Step 5: Build OutputRegistry (NEW)
+     output_registry = _build_output_registry(...)
      ...
      backtracker = DependencyBacktracker(
          calc_usages, calc_defs,
          design_attributes=design_attrs,
-         computed_attributes=computed_attrs,
-         aggregation_data=scoped_agg_data,
+         output_registry=output_registry,
      )
```

### `src/sysml_codegen/resolution/graph_builder.py`

```diff
  def build_computation_graph(
      result, calc_defs, design_attrs, group_deriver,
      compilation_results=None,
      computed_attributes=None,
      aggregation_data=None,
-     hierarchy_redefinitions=None,
  ) -> ComputationGraph:
-     # Step 2: Build output channel catalog
-     output_catalog = _build_output_catalog(result.required_usages, calc_def_map)
-     # Step 2.5: Extend with computed attrs
-     # Step 2.7: Extend with aggregation
      ...
-     # Step 3: Build attribute resolution map
-     attr_resolution_map = _build_attribute_resolution_map(...)
      ...
      # Step 6: Build CalcUsage modules (now includes FORMULA synthetic CalcUsages)
      for idx, usage in enumerate(result.required_usages):
          module = _build_pipeline_module(
              usage=usage,
              calc_def=calc_def,
-             output_catalog=output_catalog,
              entry_points=entry_points,
              execution_order=idx,
              binding_resolutions=result.binding_resolutions,
          )
-     # Step 6.5: Build computed attribute modules -- REMOVED (synthetic CalcUsages)
      ...

- def _build_output_catalog(...): ...
- def _extend_output_catalog_with_computed_attrs(...): ...
- def _extend_output_catalog_with_aggregation(...): ...
- def _build_attribute_resolution_map(...): ...
- def _build_computed_attr_module(...): ...
- def _resolve_expose_pure(...): ...
- class AttributeResolution: ...
- class AttributeResolutionKind: ...

  def _build_pipeline_module(
      usage, calc_def,
-     output_catalog,
      entry_points, execution_order, binding_resolutions,
  ):
```

---

**Last Updated**: 2026-02-13
