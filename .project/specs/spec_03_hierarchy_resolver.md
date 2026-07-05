# Spec 03: Step 3.5 Hierarchy Resolver Changes

**Status**: Draft
**Spec ID**: SPEC-03
**Epic**: OUTPUT-REGISTRY
**Affected files**:
- `src/sysml_codegen/extraction/hierarchy_resolver.py` (modified)
- `src/sysml_codegen/generation/initialization.py` (modified)
- `src/sysml_codegen/extraction/data_models.py` (modified -- add `ChannelAlias` import forwarding)
- `src/sysml_codegen/core/models.py` (prerequisite -- `ChannelAlias` must exist; see Change 1 in epic)

**Design reference**: `.project/reports/08_algorithm_revised.md` Section 4 (Step 3.5)

---

## Summary of Changes

Step 3.5 currently performs three sub-steps (A-C) and has two follow-on steps (3.6, 4.7) that partially compensate for missing functionality. This spec adds a fourth sub-step (D: CHAIN alias production), enhances sub-step C (override rewriting), moves aggregation scoping from Step 4.7 into Step 3.5, and eliminates Step 3.6 entirely.

| Current | Target | Rationale |
|---------|--------|-----------|
| Step 3.5(A): Extract redefinitions | Unchanged | Already correct |
| Step 3.5(B): Extract multiplicities | Unchanged | Already correct |
| Step 3.5(C): Build aggregation expressions | Enhanced: drop `AggregationDecomposer` Protocol, add operand validation | Direct sum() handling is sufficient (one function) |
| Step 3.5 override rewriting: LITERAL only, bare-name match | Enhanced: LITERAL + CHAIN overrides, SYSML_QN + DOTTED leaf extraction | Spike 1: no bare names exist; CHAIN overrides currently ignored |
| Step 3.6: `_enrich_aliases_from_bindings()` | **ELIMINATED** | Heuristic param_name matching is semantically wrong; authoritative aliases come from :>> CHAIN (here) and EXPOSE_PURE (Step 4.5) |
| Step 4.7: `_scope_aggregation_expressions()` | **MOVED** into Step 3.5 as sub-step | Scoping depends on hierarchy data, not on OutputRegistry |
| (none) | **NEW** Step 3.5(D): CHAIN alias production | Produces `list[ChannelAlias]` from :>> CHAIN redefinitions |

---

## Prerequisite: `ChannelAlias` Data Model

This spec assumes `ChannelAlias` exists in `src/sysml_codegen/core/models.py` per epic Change 1:

```python
@dataclass
class ChannelAlias:
    """An explicit alias for a pipeline output channel.

    Produced by two authoritative sources:
    - Step 3.5(D): :>> CHAIN redefinitions on PartDefs
    - Step 4.5: EXPOSE_PURE classifications on PartUsages

    Attributes:
        alias_name: Scoped dotted key (e.g., "solar_array.total_capex")
        canonical_name: Scoped dotted key of the target
            (e.g., "solar_array.cost_model.total_cost")
        owning_part_qn: QN of the PartDef/PartUsage where the alias originates
        source: Provenance tag for debugging/tracing
    """
    alias_name: str
    canonical_name: str
    owning_part_qn: str
    source: str  # "redefinition" | "expose_pure" (per Spec 01)
```

---

## Change A: Eliminate Step 3.6 (`_enrich_aliases_from_bindings`)

### What is removed

The function `_enrich_aliases_from_bindings()` in `initialization.py` (lines 297-343) is deleted entirely. Its call site in `build_pipeline_context()` (lines 473-475) is removed.

### Why

`_enrich_aliases_from_bindings()` detects aliases by comparing `binding.param_name` against `binding.source_path` leaf names. This is a heuristic that:
1. Can produce false aliases when param_name coincidentally differs from source leaf.
2. Misses aliases that are not expressed through CalcUsage bindings.
3. Operates on `AggregationExpressionData.aliases: list[str]` which is an unscoped bare-name list -- incompatible with the scoped dotted keys the OutputRegistry requires.

Aliases are now produced ONLY from authoritative sources:
- `:>>` CHAIN redefinitions (this spec, sub-step D)
- EXPOSE_PURE classification (Spec 04, Step 4.5)

### Impact on `AggregationExpressionData.aliases`

The `aliases: list[str]` field on `AggregationExpressionData` remains for backward compatibility during migration. The BF-7 alias detection in `extract_hierarchy_data()` (hierarchy_resolver.py lines 536-544) also remains -- it detects CHAIN siblings that alias aggregation attributes at extraction time. However, the OutputRegistry will use the scoped `ChannelAlias` objects from sub-step D, not the bare-name `aliases` list.

---

## Change B: CHAIN Alias Production (NEW Sub-step D in Step 3.5)

### New function: `extract_chain_aliases`

```python
def extract_chain_aliases(
    redefinitions: list[RedefinitionData],
    calc_usages: list[CalcUsageData],
) -> list[ChannelAlias]:
    """Produce ChannelAlias objects from :>> CHAIN redefinitions.

    Scans CHAIN-type redefinitions for DOTTED source_paths (e.g.,
    "cost_model.total_cost") and constructs scoped aliases. BARE
    non-reference values (CAS category codes) are filtered out.

    Args:
        redefinitions: All redefinitions from extract_hierarchy_data().
        calc_usages: All calc usages (for instance path derivation).

    Returns:
        List of ChannelAlias with scoped dotted alias_name and canonical_name.

    Spike 6 data:
        solar_battery: 41 DOTTED (produce aliases), 13 BARE CAS codes (filtered)
        e2e_attr_expr: 0 CHAIN redefs (empty result)
    """
```

### Algorithm

```python
def extract_chain_aliases(
    redefinitions: list[RedefinitionData],
    calc_usages: list[CalcUsageData],
) -> list[ChannelAlias]:
    from sysml_codegen.core.models import ChannelAlias

    aliases: list[ChannelAlias] = []

    # Group CHAIN redefinitions by owning_part_qn
    chain_by_partdef: dict[str, list[RedefinitionData]] = {}
    for redef in redefinitions:
        if redef.redefinition_type != RedefinitionType.CHAIN:
            continue
        if not redef.source_path:
            continue

        # FILTER: Skip BARE non-reference values (CAS codes, enums, etc.)
        # Spike 6: 24% of CHAIN redefs are CAS category codes like "CAS220101"
        # These have no dot in the source_path -- they are string literal values,
        # NOT channel references.
        if "." not in redef.source_path:
            continue

        chain_by_partdef.setdefault(redef.owning_part_qn, []).append(redef)

    if not chain_by_partdef:
        return aliases

    # For each PartDef with CHAIN redefs, find instance paths
    for partdef_qn, redefs in chain_by_partdef.items():
        instance_paths = find_instance_paths_for_partdef(partdef_qn, calc_usages)

        if not instance_paths:
            logger.warning(
                "No instance paths found for PartDef '%s' with %d CHAIN redefs",
                partdef_qn, len(redefs),
            )
            continue

        for instance_path_dotted in instance_paths:
            for redef in redefs:
                aliases.append(ChannelAlias(
                    alias_name=f"{instance_path_dotted}.{redef.attribute_name}",
                    canonical_name=f"{instance_path_dotted}.{redef.source_path}",
                    owning_part_qn=redef.owning_part_qn,
                    source="redefinition",
                ))

    logger.info(
        "Step 3.5(D): Produced %d CHAIN aliases from %d PartDefs",
        len(aliases),
        len(chain_by_partdef),
    )
    return aliases
```

### New helper: `find_instance_paths_for_partdef`

```python
def find_instance_paths_for_partdef(
    partdef_qn: str,
    calc_usages: list[CalcUsageData],
) -> list[str]:
    """Find dotted instance paths for a PartDef by examining virtual CalcUsages.

    Instance path derivation:
    1. Find virtual CalcUsages whose owning_part_def_qn matches partdef_qn.
    2. For each, extract parent QN: qualified_name.rsplit("__", 1)[0].
    3. Split parent QN on "__", drop first segment (design PartDef prefix).
    4. Join remaining segments with "." to get consumer-facing dotted path.

    Example:
        CalcUsage QN: "SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model"
        Parent QN:    "SolarBatteryDesign__solar_battery_plant__solar_array__pv_module"
        Segments:     ["SolarBatteryDesign", "solar_battery_plant", "solar_array", "pv_module"]
        Drop first:   ["solar_battery_plant", "solar_array", "pv_module"]
        Dotted:       "solar_battery_plant.solar_array.pv_module"

    Note: ScopedAggregationData.instance_path uses __ separator and INCLUDES
    the design prefix. This function returns the CONSUMER-FACING dotted format
    with the prefix stripped.

    Args:
        partdef_qn: Qualified name of the PartDef (__ separator format).
        calc_usages: All calc usages (both real and virtual).

    Returns:
        Deduplicated sorted list of dotted instance paths.
    """
    instance_paths: set[str] = set()

    for usage in calc_usages:
        if usage.is_template:
            continue
        if usage.owning_part_def_qn != partdef_qn:
            continue

        # Extract parent QN (the PartUsage instance, not the CalcUsage itself)
        parent_qn = usage.qualified_name.rsplit("__", 1)[0]

        # Split on __, drop first segment (design PartDef prefix), join with "."
        segments = parent_qn.split("__")
        if len(segments) < 2:
            continue  # Shouldn't happen -- all virtual CalcUsages have depth >= 2
        dotted = ".".join(segments[1:])
        instance_paths.add(dotted)

    return sorted(instance_paths)
```

### Invariants

1. **BARE filter**: Any `redef.source_path` without a `"."` is a CAS code or enum value, not a channel reference. It MUST be skipped.
2. **Instance path format**: The dotted instance path MUST have the design PartDef prefix stripped. The first segment of the `__`-separated QN is always the design PartDef name (e.g., `"SolarBatteryDesign"`).
3. **Uniqueness**: Multiple virtual CalcUsages on the same PartDef may produce the same parent QN. Deduplication via `set` is required.
4. **Empty result**: If a PartDef has CHAIN redefs but no virtual CalcUsages (e.g., a PartDef that is never instantiated), log a warning and produce no aliases.

### Traceability

- Spike 6: 41 DOTTED CHAIN redefs, 13 BARE CAS codes in solar_battery. Filter logic validated.
- Spike 8: All 41 Phase 2 CHAIN aliases resolve exclusively via Key_C (dotted hierarchy path). The `canonical_name` format produced here matches Key_C format.

---

## Change C: Enhanced Override Rewriting in `_rewrite_virtual_bindings`

### Current behavior (lines 238-294 in initialization.py)

- Only matches bare-name source_paths (`"." not in` and `"::" not in`).
- Only rewrites LITERAL overrides.
- Misses CHAIN overrides and all bindings with SYSML_QN or DOTTED source_paths.

### Target behavior

Extract leaf attribute names from both SYSML_QN and DOTTED source_path formats. Handle LITERAL and CHAIN override types.

### New signature (unchanged)

```python
def _rewrite_virtual_bindings(
    calc_usages: list[CalcUsageData],
    hierarchy_data: HierarchyExtractionResult,
) -> int:
    """Rewrite virtual CalcUsage bindings using :>> design overrides.

    Mutates BindingInfo objects in-place. Returns count of rewritten bindings.

    Phase 1: Build override index from design_overrides.
    Phase 2: Match bindings on virtual CalcUsages to overrides using
             leaf attribute name extraction from SYSML_QN and DOTTED formats.
             Rewrites LITERAL and CHAIN overrides.

    Spike 1 confirmed: binding source_paths are either SYSML_QN (REFERENCE)
    or DOTTED (CHAIN). No bare names ever observed (94 bindings, 3 models).
    """
```

### Target implementation

```python
def _rewrite_virtual_bindings(
    calc_usages: list[CalcUsageData],
    hierarchy_data: HierarchyExtractionResult,
) -> int:
    # Phase 1: Build override index (unchanged)
    override_index: dict[tuple[str, str], RedefinitionData] = {}
    for override in hierarchy_data.design_overrides:
        if override.is_deep_path and len(override.target_path) >= 2:
            intermediate = "__".join(override.target_path[:-1])
            full_parent = f"{override.owning_part_qn}__{intermediate}"
            leaf_attr = override.target_path[-1]
            override_index[(full_parent, leaf_attr)] = override
        elif not override.is_deep_path:
            full_parent = override.owning_part_qn
            override_index[(full_parent, override.attribute_name)] = override

    if not override_index:
        return 0

    # Phase 2: Rewrite bindings
    rewrite_count = 0
    for usage in calc_usages:
        if usage.is_template:
            continue

        parts = usage.qualified_name.rsplit("__", 1)
        if len(parts) < 2:
            continue
        parent_path = parts[0]

        for binding in usage.bindings:
            if binding.binding_type == BindingType.LITERAL:
                continue
            if not binding.source_path:
                continue

            # CHANGED: Extract leaf attribute name from ALL source_path formats.
            # Spike 1 confirmed: REFERENCE bindings use SYSML_QN ("Ns::Part::attr"),
            # CHAIN bindings use DOTTED ("instance.output"). No bare names exist.
            if "::" in binding.source_path:
                attr_name = binding.source_path.rsplit("::", 1)[-1]
            elif "." in binding.source_path:
                attr_name = binding.source_path.rsplit(".", 1)[-1]
            else:
                attr_name = binding.source_path  # defensive fallback

            key = (parent_path, attr_name)
            matched = override_index.get(key)

            if matched is None:
                continue

            if matched.redefinition_type == RedefinitionType.LITERAL:
                # LITERAL override: rewrite binding to LITERAL (existing behavior)
                binding.binding_type = BindingType.LITERAL
                binding.literal_value = matched.literal_value
                binding.source_path = None
                rewrite_count += 1

            elif matched.redefinition_type == RedefinitionType.CHAIN:
                # CHAIN override: rewrite source_path to override target (NEW)
                binding.source_path = matched.source_path
                rewrite_count += 1

            # EXPRESSION overrides: skip (aggregation module handles these)
            # No mutation needed -- the binding stays as-is and resolves
            # through the OutputRegistry to the aggregation module output.

    return rewrite_count
```

### Delta from current code

| Aspect | Current (lines 283-293) | Target |
|--------|------------------------|--------|
| Source path matching | Bare-name only (`"." not in` and `"::" not in`) | Leaf extraction from SYSML_QN and DOTTED formats |
| Override types | LITERAL only | LITERAL + CHAIN |
| CHAIN override behavior | N/A | Rewrite `source_path` to override target |
| EXPRESSION override | N/A | Explicitly skipped (comment documents why) |

---

## Change D: Aggregation Decomposition Simplification

### What changes

The current aggregation code in `hierarchy_resolver.py` (lines 254-484) already uses direct `sum()` handling without a Protocol. No structural change is needed. The spec clarifies the target design constraints:

1. **No `AggregationDecomposer` Protocol.** The current direct `sum()` handling in `_walk_aggregation_ast()` is the target design. No Protocol/registry abstraction should be added.

2. **Operand validation.** The existing `_walk_aggregation_ast()` function already validates that sum() operands are `FeatureChainExpression` nodes referencing child-part attributes (lines 370-407). This validation is correct and should be preserved.

3. **Uniform-array assumption.** The sum-to-multiply transformation (`sum(child.attr)` becomes `count * child.attr`) relies on the assumption that all instances in a PartUsage array are identical. This assumption is documented in the `build_aggregation_expression()` docstring (line 443) and is a precondition of the transformation, not an implementation detail.

4. **Known wrapper function unwrapping.** The `_KNOWN_WRAPPER_FUNCTIONS` set (`frozenset({"Evaluation", "evaluate", "collect", "select"})`) and the `_unwrap_invocation()` function are correct and should be preserved.

### No code changes required

This sub-step confirms the current implementation is already aligned with the target design.

---

## Change E: Aggregation Scoping Moves INTO Step 3.5

### What moves

`_scope_aggregation_expressions()` currently lives in `initialization.py` (lines 346-406) and runs as Step 4.7 in `build_pipeline_context()` (line 486). It moves to be called as a sub-step within `_extract_hierarchy_and_rewrite_bindings()`.

### Current call site in `build_pipeline_context()` (to be removed)

```python
# Step 4.7: Scope aggregation expressions to design instances
scoped_agg_data = _scope_aggregation_expressions(hierarchy_data, calc_usages)
```

### Target: called within Step 3.5

The scoping logic stays in `initialization.py` (the function itself does not move files). It is called from `_extract_hierarchy_and_rewrite_bindings()` instead of from `build_pipeline_context()`.

### Function signature (unchanged)

```python
def _scope_aggregation_expressions(
    hierarchy_data: HierarchyExtractionResult | None,
    calc_usages: list[CalcUsageData],
) -> list[ScopedAggregationData]:
    """Scope PartDef-level aggregation expressions to design instances.

    Returns one ScopedAggregationData per (AggregationExpressionData, instance_path)
    pair found in the virtual CalcUsage list.
    """
```

The function body is unchanged. Only its call location moves.

---

## Orchestration: Updated `_extract_hierarchy_and_rewrite_bindings`

### Current signature

```python
def _extract_hierarchy_and_rewrite_bindings(
    model: Any,
    calc_usages: list[CalcUsageData],
) -> HierarchyExtractionResult:
```

### Target signature

```python
def _extract_hierarchy_and_rewrite_bindings(
    model: Any,
    calc_usages: list[CalcUsageData],
) -> tuple[HierarchyExtractionResult, list[ScopedAggregationData], list[ChannelAlias]]:
    """Step 3.5: Extract hierarchy data, rewrite bindings, scope aggregations,
    and produce CHAIN aliases.

    Sub-steps:
      A. extract_hierarchy_data() -- redefinitions, multiplicities, aggregations
      B. _rewrite_virtual_bindings() -- LITERAL + CHAIN overrides (ENHANCED)
      C. _scope_aggregation_expressions() -- aggregation scoping (MOVED from 4.7)
      D. extract_chain_aliases() -- CHAIN alias production (NEW)

    Args:
        model: Parsed SysIDE model.
        calc_usages: All calc usages (mutated: bindings rewritten in-place).

    Returns:
        Tuple of:
        - HierarchyExtractionResult (redefinitions, multiplicities, aggregations)
        - list[ScopedAggregationData] (aggregation expressions scoped to design instances)
        - list[ChannelAlias] (from :>> CHAIN redefinitions)
    """
```

### Target implementation

```python
def _extract_hierarchy_and_rewrite_bindings(
    model: Any,
    calc_usages: list[CalcUsageData],
) -> tuple[HierarchyExtractionResult, list[ScopedAggregationData], list[ChannelAlias]]:
    from sysml_codegen.extraction.hierarchy_resolver import (
        extract_chain_aliases,
        extract_hierarchy_data,
    )

    # Sub-step A: Extract hierarchy data (unchanged)
    hierarchy_data = extract_hierarchy_data(model)

    # Sub-step B: Rewrite virtual bindings (ENHANCED: LITERAL + CHAIN)
    rewrite_count = _rewrite_virtual_bindings(calc_usages, hierarchy_data)

    # Sub-step C: Scope aggregation expressions (MOVED from Step 4.7)
    scoped_agg_data = _scope_aggregation_expressions(hierarchy_data, calc_usages)

    # Sub-step D: Produce CHAIN aliases (NEW)
    chain_aliases = extract_chain_aliases(
        hierarchy_data.redefinitions,
        calc_usages,
    )

    logger.info(
        "Step 3.5: Hierarchy extraction complete -- %d redefinitions, "
        "%d design overrides, %d aggregation expressions, %d bindings rewritten, "
        "%d scoped aggregations, %d CHAIN aliases",
        len(hierarchy_data.redefinitions),
        len(hierarchy_data.design_overrides),
        len(hierarchy_data.aggregation_expressions),
        rewrite_count,
        len(scoped_agg_data),
        len(chain_aliases),
    )

    return hierarchy_data, scoped_agg_data, chain_aliases
```

---

## Orchestration: Updated `build_pipeline_context`

### Changes to `build_pipeline_context()` in initialization.py

1. **Step 3.5 call site**: Updated to receive the 3-tuple return value.
2. **Step 3.6**: Removed entirely (lines 473-475).
3. **Step 4.7**: Removed from `build_pipeline_context()` (line 486) -- now runs inside Step 3.5.

### Target call sequence (relevant excerpt)

```python
# Step 3.5: Extract hierarchy data, rewrite bindings, scope aggregations,
#           and produce CHAIN aliases
hierarchy_data, scoped_agg_data, chain_aliases = _extract_hierarchy_and_rewrite_bindings(
    extractor.model, calc_usages
)

# Step 3.6: ELIMINATED
# (aliases now come from Step 3.5 CHAIN redefs and Step 4.5 EXPOSE_PURE)

# Step 4: Extract design attributes
design_attrs = extract_design_attributes(extractor.model, design_path_filter=design_path_filter)

# Step 4.5: Extract computed attributes, remove FORMULAs, produce EXPOSE_PURE aliases
# NOTE: Signature changes per Spec 04 -- returns additional outputs
computed_attrs, expose_pure_aliases, synthetic_usages = _extract_and_filter_computed_attributes(
    extractor.model, calc_usages, design_attrs
)

# Merge aliases from Steps 3.5 and 4.5
all_channel_aliases = chain_aliases + expose_pure_aliases

# Append synthetic CalcUsages from FORMULA attributes (Spec 04)
calc_usages.extend(synthetic_usages)

# Step 4.7: MOVED into Step 3.5 (scoped_agg_data already available)

# Step 5: Build OutputRegistry (NEW -- separate spec)
# ... uses all_channel_aliases, scoped_agg_data, calc_usages, computed_attrs ...
```

### PipelineContext changes

The `PipelineContext` dataclass needs a new field for channel aliases:

```python
@dataclass
class PipelineContext:
    # ... existing fields ...

    # Channel aliases from Steps 3.5 and 4.5 (for OutputRegistry construction in Step 5)
    channel_aliases: list[ChannelAlias] = field(default_factory=list)
```

---

## Step 3.5 Output Contract

After Step 3.5 completes, the following data is available:

| Output | Type | Source |
|--------|------|--------|
| Hierarchy data | `HierarchyExtractionResult` | `extract_hierarchy_data()` |
| Scoped aggregation data | `list[ScopedAggregationData]` | `_scope_aggregation_expressions()` |
| CHAIN aliases | `list[ChannelAlias]` | `extract_chain_aliases()` |
| CalcUsage bindings | mutated `list[CalcUsageData]` | `_rewrite_virtual_bindings()` |

### Post-conditions

1. All virtual CalcUsage bindings that match design overrides have been rewritten (LITERAL or CHAIN).
2. Aggregation expressions are scoped to design instance paths -- each `ScopedAggregationData` has an `instance_path` in `__`-separated format including the design prefix.
3. CHAIN aliases are scoped with dotted instance paths (design prefix stripped, `.`-separated). Only DOTTED source_paths are represented; BARE values (CAS codes) are filtered.
4. Step 3.6 no longer exists. No heuristic alias enrichment occurs.

---

## Test Plan

### Unit tests for `extract_chain_aliases`

1. **DOTTED CHAIN produces alias**: Given a CHAIN redef with `source_path="cost_model.total_cost"` on a PartDef with one virtual CalcUsage, verify one `ChannelAlias` is produced with correctly scoped `alias_name` and `canonical_name`.

2. **BARE CHAIN filtered**: Given a CHAIN redef with `source_path="CAS220101"` (no dot), verify no alias is produced.

3. **Multiple instance paths**: Given a PartDef with two virtual CalcUsages producing different parent paths, verify one alias per (path, redef) combination.

4. **No virtual CalcUsages**: Given a PartDef with CHAIN redefs but no virtual CalcUsages, verify warning logged and empty result.

### Unit tests for `find_instance_paths_for_partdef`

1. **Basic derivation**: Given CalcUsage QN `"SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model"` with `owning_part_def_qn` matching, verify returns `["solar_battery_plant.solar_array.pv_module"]`.

2. **Deduplication**: Given two CalcUsages on the same PartDef with the same parent QN, verify only one dotted path is returned.

3. **Template usages excluded**: Given a CalcUsage with `is_template=True`, verify it is skipped.

### Unit tests for enhanced `_rewrite_virtual_bindings`

1. **SYSML_QN leaf extraction**: Given a binding with `source_path="SolarBatteryLibrary::PV_Module::wattage"`, verify `attr_name="wattage"` is extracted and matched against the override index.

2. **DOTTED leaf extraction**: Given a binding with `source_path="cost_model.total_cost"`, verify `attr_name="total_cost"` is extracted.

3. **CHAIN override rewrite**: Given a CHAIN override in the index, verify `binding.source_path` is rewritten to the override's `source_path` (not set to `None`).

4. **EXPRESSION override skipped**: Given an EXPRESSION override in the index, verify the binding is not mutated.

### Integration tests

1. **Step 3.5 returns 3-tuple**: Verify `_extract_hierarchy_and_rewrite_bindings()` returns `(HierarchyExtractionResult, list[ScopedAggregationData], list[ChannelAlias])`.

2. **Step 3.6 removed**: Verify `_enrich_aliases_from_bindings` is not called anywhere in `build_pipeline_context()`.

3. **Step 4.7 removed from build_pipeline_context**: Verify `_scope_aggregation_expressions` is not called directly from `build_pipeline_context()`.
