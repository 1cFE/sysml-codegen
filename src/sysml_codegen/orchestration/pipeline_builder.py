"""Pipeline orchestration: build_pipeline_context() and helpers.

Extracted from generation/initialization.py (Step 7.1).
Coordinates the multi-step pipeline initialization sequence:
hierarchy extraction, binding rewrite, aggregation scoping,
computed attribute extraction, and full graph assembly.
"""

import logging
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.sysml.types import BindingType

from sysml_codegen.analysis.dependency_backtracker import (
    DependencyBacktracker,
)
from sysml_codegen.analysis.parameter_groups import (
    DesignAttributeData,
    ParameterGroupDeriver,
    extract_design_attributes,
)
from sysml_codegen.core.models import ChannelAlias
from sysml_codegen.core.qualified_names import sanitize_qualified_name
from sysml_codegen.extraction.data_models import (
    ComputedAttributeClassification,
    ComputedAttributeData,
    HierarchyExtractionResult,
    RedefinitionData,
    RedefinitionType,
    ScopedAggregationData,
)
from sysml_codegen.extraction.expression_compiler import (
    CalcDefCompilationResult,
    compile_calc_def,
)
from sysml_codegen.extraction.usage_extractor import CalcUsageData, extract_calculation_usages
from sysml_codegen.orchestration.pipeline_context import (
    CodeGenerationError,
    PipelineContext,
    SysMLParsingError,
)
from sysml_codegen.orchestration.output_registry_builder import build_output_registry
from sysml_codegen.resolution.graph_builder import build_computation_graph

logger = logging.getLogger(__name__)


def _remove_formula_from_design_attrs(
    computed_attrs: list[ComputedAttributeData],
    design_attrs: dict[Path, list[DesignAttributeData]],
) -> int:
    """Remove FORMULA computed attributes from design_attrs in-place.

    FORMULA attributes must be removed before ParameterGroupDeriver to prevent
    false entry points. The QN format built here must match what
    build_element_qualified_name() produces for DesignAttributeData.qualified_name.

    Args:
        computed_attrs: All computed attributes (only FORMULA classification filtered).
        design_attrs: Design attributes dict to modify in-place.

    Returns:
        Count of removed attributes.
    """
    formula_qns: set[str] = set()
    for ca in computed_attrs:
        if ca.classification == ComputedAttributeClassification.FORMULA:
            # Site 4 of the FORMULA sysml-QN lockstep flip (Item 7 / INV-1):
            # this twin builds the FORMULA-removal match set; it must derive the
            # part QN the same per-segment-sanitized way the registration side does.
            part_qn_python = sanitize_qualified_name(ca.owning_part_qualified_name)
            formula_qns.add(f"{part_qn_python}__{ca.python_name}")

    if not formula_qns:
        return 0

    removed = 0
    for path in design_attrs:
        original_len = len(design_attrs[path])
        design_attrs[path] = [
            a for a in design_attrs[path]
            if a.qualified_name not in formula_qns
        ]
        removed += original_len - len(design_attrs[path])

    return removed


def _extract_and_filter_computed_attributes(
    model: Any,
    calc_usages: list[CalcUsageData],
    design_attrs: dict[Path, list[DesignAttributeData]],
) -> tuple[list[ComputedAttributeData], list[ChannelAlias]]:
    """Step 4.5: Extract computed attributes and remove FORMULAs from design_attrs.

    Iterates PartDefinition and PartUsage elements from the model, calls
    extract_computed_attributes() for each, then removes FORMULA-classified
    attributes from design_attrs to prevent false entry points.

    Args:
        model: Parsed SysIDE model (from extractor.model).
        calc_usages: Pipeline's calc usages (reserved for future use).
        design_attrs: Design attributes dict, modified in-place to remove FORMULAs.

    Returns:
        Tuple of (computed_attributes, expose_pure_aliases).
    """
    from sysml_codegen.extraction.computed_attribute_extractor import (
        extract_computed_attributes,
    )

    all_computed_attrs: list[ComputedAttributeData] = []
    all_expose_aliases: list[ChannelAlias] = []

    # Iterate PartDefinition and PartUsage elements
    part_elements = list(SysideAdapter.elements_of_type(model, "PartDefinition"))
    part_elements.extend(SysideAdapter.elements_of_type(model, "PartUsage"))

    for part_elem in part_elements:
        # Build calc_usage_names for this part from its owned members
        calc_usage_names = {
            m.name for m in part_elem.owned_members
            if SysideAdapter.is_instance(m, "CalculationUsage")
        }

        computed, expose_aliases = extract_computed_attributes(None, part_elem, calc_usage_names)
        all_computed_attrs.extend(computed)
        all_expose_aliases.extend(expose_aliases)

    # Remove FORMULA attributes from design_attrs
    removed_count = _remove_formula_from_design_attrs(all_computed_attrs, design_attrs)

    # Log summary
    by_classification: dict[str, int] = {}
    for ca in all_computed_attrs:
        key = ca.classification.value
        by_classification[key] = by_classification.get(key, 0) + 1

    breakdown = ", ".join(f"{v} {k}" for k, v in sorted(by_classification.items()))
    logger.info(
        "Step 4.5: Extracted %d computed attributes (%s), removed %d FORMULA from design_attrs, "
        "%d EXPOSE_PURE aliases",
        len(all_computed_attrs),
        breakdown or "none",
        removed_count,
        len(all_expose_aliases),
    )

    return (all_computed_attrs, all_expose_aliases)


def _extract_hierarchy_and_rewrite_bindings(
    model: Any,
    calc_usages: list[CalcUsageData],
) -> tuple[HierarchyExtractionResult, list[ScopedAggregationData], list[ChannelAlias]]:
    """Step 3.5: Extract hierarchy data, rewrite bindings, scope aggregation, build CHAIN aliases.

    Consolidates hierarchy extraction + binding rewrite + aggregation scoping
    (was Step 4.7) + CHAIN alias production into a single step.
    """
    from sysml_codegen.extraction.hierarchy_resolver import extract_hierarchy_data

    hierarchy_data = extract_hierarchy_data(model)

    rewrite_count = _rewrite_virtual_bindings(calc_usages, hierarchy_data)

    # Scope aggregation expressions (moved from Step 4.7)
    scoped_agg_data = _scope_aggregation_expressions(hierarchy_data, calc_usages)

    # Build CHAIN aliases
    chain_aliases = _build_chain_aliases(hierarchy_data, calc_usages)

    logger.info(
        "Step 3.5: Hierarchy extraction complete — %d redefinitions, "
        "%d design overrides, %d aggregation expressions, %d bindings rewritten, "
        "%d scoped aggregations, %d CHAIN aliases",
        len(hierarchy_data.redefinitions),
        len(hierarchy_data.design_overrides),
        len(hierarchy_data.aggregation_expressions),
        rewrite_count,
        len(scoped_agg_data),
        len(chain_aliases),
    )

    return (hierarchy_data, scoped_agg_data, chain_aliases)


def _rewrite_virtual_bindings(
    calc_usages: list[CalcUsageData],
    hierarchy_data: HierarchyExtractionResult,
) -> int:
    """Rewrite virtual CalcUsage bindings using :>> design overrides.

    Mutates BindingInfo objects in-place. Returns count of rewritten bindings.

    Phase 1: Build override index from design_overrides.
    Phase 2: Extract leaf name from source_path (SYSML_QN, DOTTED, or bare),
             match against overrides, and rewrite (LITERAL or CHAIN).
    """
    # Phase 1: Build override index
    # Key: (full_target_parent_path, leaf_attribute_name) -> RedefinitionData
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

            # Extract leaf name from source_path
            source = binding.source_path
            if "::" in source:
                leaf = source.rsplit("::", 1)[-1]
            elif "." in source:
                leaf = source.rsplit(".", 1)[-1]
            else:
                raise ValueError(f"Unexpected bare-name source_path: {source!r}")

            key = (parent_path, leaf)
            matched = override_index.get(key)

            if matched:
                if matched.redefinition_type == RedefinitionType.LITERAL:
                    binding.binding_type = BindingType.LITERAL
                    binding.literal_value = matched.literal_value
                    binding.source_path = None
                    rewrite_count += 1
                elif matched.redefinition_type == RedefinitionType.CHAIN:
                    binding.source_path = matched.source_path
                    rewrite_count += 1

    return rewrite_count


def find_instance_paths_for_partdef(
    owning_part_qn: str,
    calc_usages: list[CalcUsageData],
    part_usage_names: dict[str, set[str]] | None = None,
) -> list[str]:
    """Find dotted design instance paths for a PartDef.

    Derives instance paths from virtual CalcUsage parent QNs, strips
    the design PartDef prefix, and converts to dotted format.

    Strategy 1: Direct -- virtual CalcUsages on same PartDef.
    Strategy 2: Child-walk -- match PartDef's child PartUsage names
        against CalcUsage QN segments (handles PartDef/PartUsage naming
        differences, BF-6).

    Args:
        owning_part_qn: Qualified name of the PartDef.
        calc_usages: All calc usages (filters to virtual only).
        part_usage_names: Optional child PartUsage names by PartDef QN.

    Returns:
        Sorted list of dotted, design-prefix-stripped instance paths
        (e.g., "solar_battery_plant.solar_array").
    """
    # Build index: owning_part_def_qn -> list of virtual CalcUsage QNs
    virtual_qns_by_partdef: dict[str, list[str]] = {}
    for usage in calc_usages:
        if usage.is_template or not usage.owning_part_def_qn:
            continue
        virtual_qns_by_partdef.setdefault(
            usage.owning_part_def_qn, []
        ).append(usage.qualified_name)

    instance_paths: set[str] = set()

    # Strategy 1: Direct match -- virtual CalcUsages on the SAME PartDef
    direct_qns = virtual_qns_by_partdef.get(owning_part_qn, [])
    for qn in direct_qns:
        parent = qn.rsplit("__", 1)[0]
        instance_paths.add(parent)

    # Strategy 2: Child-walk — find parent instance path via child PartUsages
    if not instance_paths and part_usage_names:
        children = {
            name.lower()
            for name in part_usage_names.get(owning_part_qn, set())
        }
        if children:
            for _partdef_qn, qns in virtual_qns_by_partdef.items():
                for qn in qns:
                    segments = qn.split("__")
                    for i, seg in enumerate(segments):
                        if seg.lower() in children and i > 0:
                            parent_path = "__".join(segments[:i])
                            instance_paths.add(parent_path)
                            break

    # Convert __-separated paths to dotted, design-prefix-stripped
    dotted_paths: list[str] = []
    for path in instance_paths:
        segments = path.split("__")
        if len(segments) > 1:
            dotted_paths.append(".".join(segments[1:]))
        else:
            dotted_paths.append(segments[0])

    return sorted(dotted_paths)


def _build_chain_aliases(
    hierarchy_data: HierarchyExtractionResult,
    calc_usages: list[CalcUsageData],
) -> list[ChannelAlias]:
    """Build ChannelAlias objects from :>> CHAIN redefinitions.

    For each non-deep-path CHAIN redefinition on a PartDef, finds the
    design instance paths and produces scoped aliases.

    Filters:
    - Skip if redef.redefinition_type != CHAIN
    - Skip if redef.is_deep_path (design overrides, not aliases)
    - Skip if "." not in redef.source_path (bare CAS codes like "CAS220101")

    Args:
        hierarchy_data: Extraction result with redefinitions.
        calc_usages: For instance path resolution.

    Returns:
        List of scoped ChannelAlias objects with source="redefinition".
    """
    aliases: list[ChannelAlias] = []

    # Group CHAIN redefinitions by owning_part_qn
    chain_redefs_by_part: dict[str, list[RedefinitionData]] = {}
    for redef in hierarchy_data.redefinitions:
        if redef.redefinition_type != RedefinitionType.CHAIN:
            continue
        if redef.is_deep_path:
            continue
        if not redef.source_path or "." not in redef.source_path:
            continue
        chain_redefs_by_part.setdefault(redef.owning_part_qn, []).append(redef)

    if not chain_redefs_by_part:
        return aliases

    for owning_part_qn, redefs in chain_redefs_by_part.items():
        instance_paths = find_instance_paths_for_partdef(
            owning_part_qn,
            calc_usages,
            part_usage_names=hierarchy_data.part_usage_names,
        )

        for redef in redefs:
            for dotted_path in instance_paths:
                aliases.append(ChannelAlias(
                    alias_name=f"{dotted_path}.{redef.attribute_name}",
                    canonical_name=f"{dotted_path}.{redef.source_path}",
                    owning_part_qn=redef.owning_part_qn,
                    source="redefinition",
                ))

    return aliases


def _scope_aggregation_expressions(
    hierarchy_data: HierarchyExtractionResult | None,
    calc_usages: list[CalcUsageData],
) -> list[ScopedAggregationData]:
    """Scope PartDef-level aggregation expressions to design instances.

    Returns one ScopedAggregationData per (AggregationExpressionData, instance_path)
    pair found in the virtual CalcUsage list.
    """
    if not hierarchy_data or not hierarchy_data.aggregation_expressions:
        return []

    result: list[ScopedAggregationData] = []

    # Derive the design prefix from the first virtual CalcUsage QN.
    # The prefix is segment[0] of any virtual QN (e.g., "SolarBatteryDesign").
    design_prefix: str | None = None
    for usage in calc_usages:
        if not usage.is_template and usage.owning_part_def_qn:
            segments = usage.qualified_name.split("__")
            if segments:
                design_prefix = segments[0]
            break

    for agg_expr in hierarchy_data.aggregation_expressions:
        dotted_paths = find_instance_paths_for_partdef(
            agg_expr.owning_part_qn,
            calc_usages,
            part_usage_names=hierarchy_data.part_usage_names,
        )

        if not dotted_paths:
            logger.warning(
                "Aggregation expression '%s' on PartDef '%s' produced zero "
                "scoped modules — PartDef may not be instantiated in the design",
                agg_expr.attribute_name,
                agg_expr.owning_part_qn,
            )
            continue

        for dotted in dotted_paths:
            # Reconstruct __-separated path for ScopedAggregationData.instance_path
            if design_prefix:
                underscore_path = design_prefix + "__" + "__".join(dotted.split("."))
            else:
                underscore_path = "__".join(dotted.split("."))
            result.append(ScopedAggregationData(
                expression=agg_expr,
                instance_path=underscore_path,
            ))

    logger.info("Scoped %d aggregation module(s)", len(result))
    return result


def build_pipeline_context(
    model_paths: list[Path],
    targets: list[str] | None = None,
    include_all: bool = True,
    design_path_filter: str = "",
) -> PipelineContext:
    """Build complete pipeline context from SysML models.

    This is the canonical initialization sequence used by all codegen scripts.
    It performs the following 7-step sequence:

    1. Load models via SysMLDataExtractor
    2. Extract calculation definitions
    3. Extract calculation usages with enhanced algorithm param detection
    4. Extract design attributes for group derivation
    5. Create parameter group deriver
    6. Create backtracker and run dependency analysis
    7. Build ComputationGraph (single source of truth)

    Args:
        model_paths: Paths to SysML model directories (library + designs)
        targets: Target outputs for subset generation (e.g., ["net_electric.p_net"])
        include_all: If True, include all usages; if False, only those needed for targets

    Returns:
        PipelineContext with all components initialized

    Raises:
        SysMLParsingError: If model loading fails
        CodeGenerationError: If no calculation definitions found
    """
    # Late import to avoid circular import
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    # Step 1: Load models via SysMLDataExtractor
    extractor = SysMLDataExtractor(model_paths)
    try:
        if not extractor.load_models():
            raise SysMLParsingError(
                f"Failed to load SysML models from: {[str(p) for p in model_paths]}"
            )
    except ValueError as e:
        raise SysMLParsingError(f"Failed to load SysML models: {e}") from e

    # Step 2: Extract calculation definitions
    calc_defs = extractor.extract_calculation_definitions()
    if not calc_defs:
        raise CodeGenerationError(
            "No calculation definitions found in models. "
            "Ensure library models contain calc definitions."
        )

    # Step 2.5: Report dropped constraint usages (REQ-EXT-09). Detection only —
    # constraints are not executable, so this makes the silent drop loud.
    extractor.report_dropped_constraints()

    # Step 3: Extract calculation usages with enhanced algorithm param detection
    calc_usages, _report = extract_calculation_usages(
        extractor.model,
        calc_defs=calc_defs,
    )

    # Step 3.5: Extract hierarchy + rewrite bindings + scope aggregation + build CHAIN aliases
    hierarchy_data, scoped_agg_data, chain_aliases = _extract_hierarchy_and_rewrite_bindings(
        extractor.model, calc_usages
    )

    # Step 4: Extract design attributes for group derivation
    design_attrs = extract_design_attributes(extractor.model, design_path_filter=design_path_filter)

    # Step 4.5: Extract computed attributes + EXPOSE_PURE aliases
    computed_attrs, expose_aliases = _extract_and_filter_computed_attributes(
        extractor.model, calc_usages, design_attrs
    )

    # Merge all channel aliases (CHAIN from Step 3.5 + EXPOSE_PURE from Step 4.5)
    all_channel_aliases = chain_aliases + expose_aliases

    # Step 5: Create parameter group deriver (uses filtered design_attrs)
    group_deriver = ParameterGroupDeriver(design_attrs, calc_usages, calc_defs)

    # Step 5.5: Build OutputRegistry (4-phase registration protocol)
    output_registry = build_output_registry(
        calc_usages=calc_usages,
        calc_defs=calc_defs,
        aggregation_data=scoped_agg_data,
        computed_attributes=computed_attrs,
        channel_aliases=all_channel_aliases,
        design_attributes=design_attrs,
    )

    # Step 6: Create backtracker and run
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

    # Step 6.5: Compile expressions and classify compilability
    logger.info(
        "Step 6.5: Compiling expressions for %d calculation definitions",
        len(calc_defs),
    )
    compilation_results: dict[str, CalcDefCompilationResult] = {}
    for calc_def in calc_defs:
        if calc_def.output_expression_asts:
            try:
                result_comp = compile_calc_def(
                    calc_def=calc_def,
                    expression_asts=calc_def.output_expression_asts,
                    all_member_names=calc_def.all_member_names or None,
                    member_expressions=calc_def.member_expressions or None,
                )
                compilation_results[calc_def.name] = result_comp
                logger.info(
                    "  Compiled '%s': %s",
                    calc_def.name,
                    result_comp.overall_compilability.value,
                )
            except Exception:
                logger.warning(
                    "Expression compilation failed for '%s', "
                    "falling back to UNKNOWN compilability",
                    calc_def.name,
                    exc_info=True,
                )

    skipped = len(calc_defs) - len(compilation_results)
    compilability_counts: dict[str, int] = {}
    for result in compilation_results.values():
        key = result.overall_compilability.value
        compilability_counts[key] = compilability_counts.get(key, 0) + 1
    breakdown = ", ".join(f"{v} {k}" for k, v in sorted(compilability_counts.items()))
    logger.info(
        "Step 6.5 complete: %d compiled (%s), %d skipped (no expressions)",
        len(compilation_results),
        breakdown or "none",
        skipped,
    )

    # Step 7: Build ComputationGraph (single source of truth)
    computation_graph = build_computation_graph(
        result=backtracking_result,
        calc_defs=calc_defs,
        design_attrs=design_attrs,
        group_deriver=group_deriver,
        output_registry=output_registry,
        compilation_results=compilation_results,
        computed_attributes=computed_attrs,
        aggregation_data=scoped_agg_data,
        hierarchy_redefinitions=hierarchy_data.redefinitions if hierarchy_data else None,
        usage_type_map=hierarchy_data.usage_type_map if hierarchy_data else None,
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
        channel_aliases=all_channel_aliases,
        output_registry=output_registry,
    )


__all__ = [
    "_build_chain_aliases",
    "_extract_and_filter_computed_attributes",
    "_extract_hierarchy_and_rewrite_bindings",
    "_remove_formula_from_design_attrs",
    "_rewrite_virtual_bindings",
    "_scope_aggregation_expressions",
    "build_pipeline_context",
    "find_instance_paths_for_partdef",
]
