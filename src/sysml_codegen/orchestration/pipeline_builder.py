"""Pipeline orchestration: build_pipeline_context() and helpers.

Extracted from generation/initialization.py (Step 7.1).
Coordinates the multi-step pipeline initialization sequence:
hierarchy extraction, binding rewrite, aggregation scoping,
computed attribute extraction, and full graph assembly.
"""

import logging
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.constraint_extraction import extract_constraint_facts
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.sysml.types import BindingType

from sysml_codegen.analysis.constraint_lowering import (
    collect_bare_actual_demand,
    extend_graph_with_constraints,
    lower_constraints,
)
from sysml_codegen.analysis.dependency_backtracker import (
    DependencyBacktracker,
)
from sysml_codegen.analysis.parameter_groups import (
    DesignAttributeData,
    ParameterGroupDeriver,
    extract_design_attributes,
)
from sysml_codegen.analysis.part_instance_index import (
    InstanceOccurrence,
    RecordingOccurrenceIndex,
    build_part_instance_index,
)
from sysml_codegen.core.identifier_types import ScopedAliasKey, ScopedKey
from sysml_codegen.core.models import ChannelAlias
from sysml_codegen.core.output_registry import OutputRegistry
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
from sysml_codegen.extraction.usage_extractor import (
    CalcUsageData,
    ExtractionReport,
    extract_calculation_usages,
)
from sysml_codegen.orchestration.output_registry_builder import build_output_registry
from sysml_codegen.orchestration.pipeline_context import (
    CodeGenerationError,
    PipelineContext,
    SysMLParsingError,
)
from sysml_codegen.resolution.graph_builder import build_computation_graph
from sysml_codegen.resolution.models import ConcreteConstraint, ConstraintInputResolution
from sysml_codegen.resolution.supplied_values import materialize_supplied_values
from sysml_codegen.snapshot import (
    CONSTRAINT_LOWERING_MODE_APPLIED,
    CONSTRAINT_LOWERING_MODE_GRANDFATHERED_OFF,
)

logger = logging.getLogger(__name__)


def _render_extraction_report(report: ExtractionReport) -> None:
    """Surface the usage-extraction report (D3-4), Item-4 house style.

    Emits an always-present INFO summary (scanned/bindings/unbound), then one
    WARN per collected diagnostic — but only when there is at least one, so a
    clean model stays zero-WARNING (INV-6). The report was previously bound and
    discarded, silencing every Family-1 dispatch diagnostic it carries.
    """
    logger.info(
        "Usage extraction: %d usages, %d bindings, %d unbound params, "
        "%d cross-file bindings, %d warning(s).",
        report.total_usages,
        report.total_bindings,
        report.unbound_params,
        report.cross_file_bindings,
        len(report.warnings),
    )
    for warning in report.warnings:
        logger.warning("Extraction: %s", warning)


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


def _rewrite_specialized_chain(
    binding: Any,
    usage: CalcUsageData,
    redef_by_def: dict[tuple[str, str], RedefinitionData],
    usage_type_map: dict[tuple[str, str], str],
) -> bool:
    """Item 10 #3 / REQ-VBR-10: rewrite a ``part_usage.attr`` CHAIN binding through the
    retyped part usage's specialized-def ``:>>`` redefinition. Returns True if rewritten.

    The consumer binds ``driver.cost_per_joule``. ``driver`` is retyped to ``'HIF Driver'``
    for this instance (``usage_type_map``), and ``'HIF Driver'`` redefines
    ``cost_per_joule :>> meier_cost.gamma``. So the binding is rewritten to
    ``driver.meier_cost.gamma``, which the chain dispatch then wires to the gamma channel
    (the gamma -> lcoe edge, SC-2). Non-recursive single hop — a base def whose attribute
    carries no redefinition falls through unchanged (the base-def tier).
    """
    if binding.binding_type != BindingType.CHAIN:
        return False
    src = binding.source_path
    if not src or "." not in src or "::" in src:
        return False
    owning_def = usage.owning_part_def_qn
    if not owning_def:
        return False
    part_usage, rest = src.split(".", 1)
    attr = rest.split(".", 1)[0]
    # Instance-aware type-select (Item 10 two-level specialization, Phase 8). Try the
    # consumer INSTANCE's own retype of the inherited part usage first, keyed by the
    # instance path (e.g. ``TwoLevelDesign__hif_plant``). This catches a usage-level
    # ``:>> driver : 'HIF Driver'`` that the declaring-def key cannot see. Fall back to
    # the declaring-def key (single-level shape, spec_chain_channel).
    instance_path = usage.qualified_name.rsplit("__", 1)[0]
    target_def = usage_type_map.get((instance_path, part_usage)) or usage_type_map.get(
        (owning_def, part_usage)
    )
    if not target_def:
        return False
    redef = redef_by_def.get((target_def, attr))
    if (
        redef is None
        or redef.redefinition_type != RedefinitionType.CHAIN
        or not redef.source_path
    ):
        return False
    tail = rest[len(attr):]  # "" for driver.attr, ".deeper" for driver.attr.deeper
    binding.source_path = f"{part_usage}.{redef.source_path}{tail}"
    return True


def _rewrite_virtual_bindings(
    calc_usages: list[CalcUsageData],
    hierarchy_data: HierarchyExtractionResult,
) -> int:
    """Rewrite virtual CalcUsage bindings using :>> design overrides and specialized-def
    redefinitions (the three-tier merge: usage override > specialized-def :>> > base def).

    Mutates BindingInfo objects in-place. Returns count of rewritten bindings.

    Phase 1: Build the override index (design_overrides) AND the specialized-def
             redefinition index keyed by owning (specializing) PartDef QN (Item 10 #3).
    Phase 2: Extract leaf name from source_path (SYSML_QN, DOTTED, or bare); match a
             usage override first (tier 1), else a retyped part-usage's specialized-def
             :>> chain (tier 2, REQ-VBR-10), and rewrite.
    """
    # Phase 1a: usage-override index (tier 1).
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

    # Phase 1b: specialized-def redefinition index (tier 2, Item 10 #3). Keyed by the
    # SPECIALIZING def QN so the retyped part usage's applicable def (picked per instance
    # via usage_type_map) selects its :>> chain. Distinct from override_index.
    redef_by_def: dict[tuple[str, str], RedefinitionData] = {
        (redef.owning_part_qn, redef.attribute_name): redef
        for redef in hierarchy_data.redefinitions
    }
    usage_type_map = hierarchy_data.usage_type_map

    if not override_index and not redef_by_def:
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
                # Bare-name source_path (self-named binding, e.g. ``in x = x``).
                # Resolving it to the outer attribute is Item 10's per-instance
                # rewrite (mechanism D, _rescue_self_named_bindings); here we only
                # stay crash-safe (REQ-VBR-09). No deep-path key can match a bare leaf.
                logger.debug(
                    "bare-name source_path %r on %s; skipping override match",
                    source,
                    usage.qualified_name,
                )
                continue

            key = (parent_path, leaf)
            matched = override_index.get(key)

            if matched:
                # Tier 1: usage override wins.
                if matched.redefinition_type == RedefinitionType.LITERAL:
                    binding.binding_type = BindingType.LITERAL
                    binding.literal_value = matched.literal_value
                    binding.source_path = None
                    rewrite_count += 1
                elif matched.redefinition_type == RedefinitionType.CHAIN:
                    binding.source_path = matched.source_path
                    rewrite_count += 1
            elif _rewrite_specialized_chain(
                binding, usage, redef_by_def, usage_type_map
            ):
                # Tier 2: retyped part-usage's specialized-def :>> chain.
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


def _register_partdef_expose_scoped_aliases(
    registry: OutputRegistry,
    computed_attrs: list[ComputedAttributeData],
    calc_usages: list[CalcUsageData],
    hierarchy_data: HierarchyExtractionResult | None,
) -> int:
    """#4 (Item 10, D7 / REQ-CA-03): expand each PartDef-level EXPOSE_PURE per
    design instance path into the structured ``_scoped_alias`` namespace.

    A part def has no instances at extraction, so a derived ``leaf = calc.output``
    on a part *def* (shape A, e.g. wi014_toy's ``total_cost = cost_calc.cost``) is a
    template. This resolves it per instance the same way ``_build_chain_aliases``
    expands CHAIN redefs — ``find_instance_paths_for_partdef`` gives the instance
    scope, ``scoped_lookup`` gives the calc-output channel — and writes
    ``(instance_path, leaf) -> channel``. The consumer-side reader is
    ``dependency_backtracker._resolve_chain_dispatch`` (#1). Part *usage* exposes
    (the two V11 pins) are ``is_on_part_definition=False`` and untouched here.

    Returns the count of registered scoped aliases.
    """
    part_usage_names = hierarchy_data.part_usage_names if hierarchy_data else None
    registered = 0
    scanned = 0  # pattern-3: count part-def EXPOSE_PURE candidates scanned.
    for ca in computed_attrs:
        if ca.classification != ComputedAttributeClassification.EXPOSE_PURE:
            continue
        if not ca.is_on_part_definition:
            continue
        chain = ca.reference_chain
        if not chain or len(chain) < 2:
            continue
        scanned += 1
        rel = ".".join(chain)  # calc-usage-rooted, e.g. "cost_calc.cost"
        # CA carries the raw ``::`` QN; calc usages key on the sanitized ``__``
        # EQN (e.g. "toy_plant::'Toy Plant'" -> "toy_plant__Toy_Plant"). Convert
        # once at this boundary so the instance-path lookup matches.
        owning_eqn = sanitize_qualified_name(ca.owning_part_qualified_name)
        for inst in find_instance_paths_for_partdef(
            owning_eqn, calc_usages, part_usage_names
        ):
            channel = registry.scoped_lookup(ScopedKey(f"{inst}.{rel}"))
            if channel is None:
                continue
            registry.register_scoped_alias(
                ScopedAliasKey((inst, ca.python_name)), channel
            )
            registered += 1

    # Pattern-3 sentinel (zero-found ≠ silence): always report the scan, so a
    # "scanned N, registered 0" is distinguishable from "nothing scanned". Only
    # a real gap (scanned but none registered) escalates to WARN.
    if scanned or registered:
        logger.info(
            "Step 5.55: part-def EXPOSE scoped aliases — scanned %d candidate(s), "
            "registered %d.",
            scanned,
            registered,
        )
    if scanned and not registered:
        logger.warning(
            "Step 5.55: scanned %d part-def EXPOSE_PURE candidate(s) but "
            "registered 0 scoped alias(es) — their channels did not resolve.",
            scanned,
        )
    return registered


def _rescue_self_named_bindings(
    registry: OutputRegistry,
    calc_usages: list[CalcUsageData],
) -> int:
    """Mechanism D (Item 10 stage (b), REQ-VBR-10 / amendment D-E): rewrite a
    self-named binding (``in x = x``) to its upstream EXPOSE channel when one exists.

    Extraction resolves a self-named binding to a full REFERENCE QN pointing at the
    consuming calc's OWN parameter (e.g. ``RescueLib::'Rescue Plant'::sink_calc::throughput``
    for ``sink_calc { in throughput = throughput }``) — it never reaches the rewrite as a
    bare name. This detects that self-reference (the QN's parent segment is the consuming
    usage's own short name) and, when an outer same-named part EXPOSE resolves to a real
    channel (the ``_scoped_alias`` populated by ``_register_partdef_expose_scoped_aliases``),
    rewrites the binding to the instance-scoped attribute path as a CHAIN. The existing
    chain dispatch (#1, Step 1c) then wires it to the upstream channel.

    No resolvable outer EXPOSE → the binding is left as-is: that is the genuine modeling
    error the ``self_named_binding_trap`` fixture pins. Runs after the scoped-alias
    registry is populated (so "resolves to a real channel" is a real lookup) and before
    the backtracker reads the bindings. Mutates ``BindingInfo`` in place; returns the
    rescue count.
    """
    rescued = 0
    for usage in calc_usages:
        if usage.is_template:
            continue
        segments = usage.qualified_name.split("__")
        if len(segments) < 3:
            continue
        instance = ".".join(segments[1:-1])
        usage_short = segments[-1]

        for binding in usage.bindings:
            if binding.binding_type != BindingType.REFERENCE:
                continue
            source = binding.source_path
            if not source or "::" not in source:
                continue
            qn_segs = source.split("::")
            if len(qn_segs) < 2:
                continue
            leaf = qn_segs[-1]
            parent_short = qn_segs[-2]
            # Self-reference: the binding points at the consuming usage's own param.
            if sanitize_qualified_name(parent_short) != usage_short:
                continue
            # Resolvable upstream EXPOSE? The scoped alias is the "resolves to a real
            # channel" test D-E requires — absent for the trap, present for the rescue.
            channel = registry.scoped_alias_lookup(ScopedAliasKey((instance, leaf)))
            if channel is None:
                continue
            binding.source_path = f"{instance}.{leaf}"
            binding.binding_type = BindingType.CHAIN
            rescued += 1

    if rescued:
        logger.info("Step 5.56: rescued %d self-named binding(s) to upstream", rescued)
    return rescued


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
    # D3-15: this is first-wins. If two designs coexist in one model, their
    # aggregations share the first design's prefix and are mis-keyed silently.
    # Collect the distinct prefixes and warn on >1 (INV-3) before taking the
    # first — one model = one design is the expected shape.
    design_prefix: str | None = None
    seen_prefixes: list[str] = []
    for usage in calc_usages:
        if not usage.is_template and usage.owning_part_def_qn:
            segments = usage.qualified_name.split("__")
            if segments and segments[0] not in seen_prefixes:
                seen_prefixes.append(segments[0])
    if seen_prefixes:
        design_prefix = seen_prefixes[0]
    if len(seen_prefixes) > 1:
        logger.warning(
            "Multiple design prefixes %s found; aggregation scoping keys off the "
            "first ('%s') — a second design's aggregations will be mis-keyed "
            "(D3-15).",
            seen_prefixes,
            design_prefix,
        )

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
    lower_constraints_enabled: bool = True,
) -> PipelineContext:
    """Build complete pipeline context from SysML models.

    This is the canonical initialization sequence used by all codegen scripts.
    The major steps (see the inline ``Step N`` markers for the full sub-step order):

    1. Load models via SysMLDataExtractor (Step 1)
    2. Extract calculation definitions (Step 2)
    3. Extract calculation usages with enhanced algorithm param detection (Step 3)
    4. Extract hierarchy, rewrite bindings, scope aggregation, build CHAIN aliases (Step 3.5)
    5. Extract design attributes and computed attributes / EXPOSE_PURE aliases (Steps 4, 4.5)
    6. Build the OutputRegistry — 4-phase registration incl. Phase 3b (Step 5.5)
    7. Create the parameter group deriver — **at Step 5.7, after the registry**, once
       design_attrs is FORMULA-free (INV-G)
    8. Create backtracker and run dependency analysis (Step 6)
    9. Compile expressions and classify compilability (Step 6.5)
    10. Build ComputationGraph — single source of truth (Step 7)

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

    # Step 2.6 (Item 5): extract neutral constraint facts. P1/P2/P3 below are
    # guarded on `constraint_facts.usages` being non-empty (INV-7) — when no
    # assertion exists in the model, lowering never runs and the corpus is
    # byte-identical to the pre-Item-5 pipeline. `lower_constraints` itself
    # runs the Item 3 executable-profile preflight before touching the
    # registry, so an out-of-profile/blocked assert is caught there, not here.
    constraint_facts = extract_constraint_facts(extractor.model)

    # Step 3: Extract calculation usages with enhanced algorithm param detection
    calc_usages, extraction_report = extract_calculation_usages(
        extractor.model,
        calc_defs=calc_defs,
    )
    # D3-4: surface the usage-extraction report instead of discarding it. The
    # report carries the Family-1 dispatch diagnostics (dropped usages,
    # unresolved calc defs, unhandled/over-long bindings); discarding it defeated
    # its purpose. Rendered on the live path here. (INV-2 parity to the
    # from-snapshot path is limited: the usage-extraction warnings are computed at
    # extraction time and are not serialized into the snapshot, so the offline
    # path has no report to replay — see 27-snapshot-generation.md.)
    _render_extraction_report(extraction_report)

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

    # Step 5.5: Build OutputRegistry (4-phase registration protocol). Its Phase 3b
    # confirm pass finalizes every EXPOSE_CHAIN_TENTATIVE in place (Item 10) —
    # resolving to EXPOSE_PURE or reverting to FORMULA. So design_attr removal and
    # group derivation must run AFTER this (INV-G), not before.
    output_registry = build_output_registry(
        calc_usages=calc_usages,
        calc_defs=calc_defs,
        aggregation_data=scoped_agg_data,
        computed_attributes=computed_attrs,
        channel_aliases=all_channel_aliases,
        design_attributes=design_attrs,
    )

    # Step 5.55: Expand PartDef-level EXPOSE aliases per instance into the
    # structured _scoped_alias namespace (Item 10 #4). Runs after the registry's
    # channels exist and before the backtracker's #1 lookup reads them.
    _register_partdef_expose_scoped_aliases(
        output_registry, computed_attrs, calc_usages, hierarchy_data
    )

    # Step 5.56: Rescue self-named bindings (mechanism D, Item 10 stage (b)). A
    # self-named ``in x = x`` that has a resolvable outer EXPOSE (now in _scoped_alias)
    # is rewritten to that upstream channel; one without an upstream (the trap) is left
    # as-is. Runs after the scoped aliases exist and before the backtracker reads bindings.
    _rescue_self_named_bindings(output_registry, calc_usages)

    # Step 5.6: Re-run FORMULA removal (INV-G). The Step-4.5 removal ran before the
    # confirm pass, so a tentative that reverted to FORMULA is still in design_attrs
    # and would leak a valueless entry point (C6b). This second pass removes it. The
    # Step-4.5 removal stays for genuine (never-tentative) FORMULAs.
    _remove_formula_from_design_attrs(computed_attrs, design_attrs)

    # Step 5.65 (Item 2, REQ-SVM-01..04): materialize supplied subsystem-attr values
    # so Step-3 design-attribute resolution carries them to the plant-calc inputs and
    # collapses renamed-consumer fan-out by source QN. The synthetic attrs enrich a
    # GRAPH-ONLY copy (deriver + backtracker + graph builder); `design_attrs` stays the
    # pure extraction boundary, so a snapshot captured from this run serializes only
    # real attributes and the materializer reconstructs the synth ones at from-snapshot
    # generate time from the raw redefinitions/overrides.
    graph_design_attrs = {k: list(v) for k, v in design_attrs.items()}
    if hierarchy_data is not None:
        # D2: widen the demand set to a constraint actual with no calc-usage binding
        # of its own (a self-named `in gain = gain`) — otherwise invisible to the
        # calc-usage-only sweep above. Read-only probe (collect_bare_actual_demand
        # docstring); gated the same as the real `lower_constraints` call below so it
        # never runs when lowering itself won't.
        constraint_actual_demand = (
            collect_bare_actual_demand(
                constraint_facts, build_part_instance_index(extractor.model), calc_usages
            )
            if lower_constraints_enabled and constraint_facts.usages
            else []
        )
        synth_attrs = materialize_supplied_values(
            calc_usages,
            hierarchy_data.redefinitions,
            hierarchy_data.design_overrides,
            hierarchy_data.usage_type_map,
            design_attrs,
            constraint_actual_demand=constraint_actual_demand,
        )
        for attr in synth_attrs:
            # Bucket by the attribute's own source file (the consuming usage's file) so
            # it groups into a valid, existing parameter group.
            graph_design_attrs.setdefault(Path(attr.source_file), []).append(attr)

    # Step 5.7: Create parameter group deriver, now that design_attrs reflects the
    # FINAL classifications (moved after confirm per INV-G).
    group_deriver = ParameterGroupDeriver(graph_design_attrs, calc_usages, calc_defs)

    # [P1 RESOLVE] (Item 5): expand + strictly resolve every constraint fact into
    # concrete graph structure. Guarded on non-empty usages (INV-7) — the output
    # registry and graph_design_attrs are final here, and occ_index is built once
    # for this call. lower_constraints runs the Item 3 executable-profile preflight
    # first (evaluate_profile) — a blocked assert halts here with a named
    # diagnostic; a non-admitted usage catalogs unassessed, never reaching the
    # strict resolver.
    # Default True (Item 8 Phase 4): snapshot v3 carries constraint facts +
    # the resolved occurrence table, and Phase 3 proved from-snapshot
    # regeneration re-lowers to a byte-identical graph/catalog on the clean
    # fixtures — so live and offline stay in parity by default. The
    # `plant_values`/`fusion_tea` pair is grandfathered flag-off via the
    # named `GRANDFATHERED` set in the capture scripts (D3); their live CLI
    # generation still halts on the `gain` gap (Item 14's prerequisite),
    # unaffected by this default — the grandfather only ever routes through
    # `capture_snapshot`'s `lower_constraints_enabled` param, never the CLI.
    concrete_constraints: list[ConcreteConstraint] = []
    part_occurrences: dict[str, list[InstanceOccurrence]] = {}
    if lower_constraints_enabled and constraint_facts.usages:
        # Recording wrapper (Item 8, MF3): the table serialized into snapshot v3
        # is exactly the transcript of the `occurrences_of` queries this real
        # `lower_constraints` call makes — never a re-derived owner set.
        recorder = RecordingOccurrenceIndex(build_part_instance_index(extractor.model))
        concrete_constraints = lower_constraints(
            constraint_facts,
            occ_index=recorder,
            registry=output_registry,
            design_attrs=graph_design_attrs,
            calc_usages=calc_usages,
        )
        part_occurrences = recorder.recorded

    # Step 6: Create backtracker and run
    backtracker = DependencyBacktracker(
        calc_usages,
        calc_defs,
        design_attributes=graph_design_attrs,
        output_registry=output_registry,
    )

    # [P2 INJECT] (Item 5): each module_output-resolved constraint input channel
    # joins the backtracking roots BEFORE pruning (spec Roots-before-pruning,
    # S4-proven), so a calculation whose only consumer is an assertion survives.
    # Reuses `_find_usage_for_channel` unchanged.
    constraint_root_targets: list[str] = []
    for bound_channel in sorted(
        {
            inp.bound_channel
            for c in concrete_constraints
            for inp in c.inputs
            if inp.resolution == ConstraintInputResolution.MODULE_OUTPUT
            and inp.bound_channel is not None
        }
    ):
        producing_usage = backtracker._find_usage_for_channel(bound_channel)  # noqa: SLF001
        if producing_usage is None:
            raise CodeGenerationError(
                f"no producing usage for constraint root channel '{bound_channel}' "
                "(a resolved module_output binding must name a real producer)"
            )
        output_name = bound_channel.rsplit("__", 1)[1]
        constraint_root_targets.append(f"{producing_usage.instance_name}.{output_name}")

    backtracking_result = backtracker.find_required_modules(
        (targets or []) + constraint_root_targets,
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
        design_attrs=graph_design_attrs,
        group_deriver=group_deriver,
        output_registry=output_registry,
        compilation_results=compilation_results,
        computed_attributes=computed_attrs,
        aggregation_data=scoped_agg_data,
        hierarchy_redefinitions=hierarchy_data.redefinitions if hierarchy_data else None,
        usage_type_map=hierarchy_data.usage_type_map if hierarchy_data else None,
        # Item 11 (F-A): surface shape-B EXPOSE_PURE names. include_all carries the
        # run mode into the dangling-alias filter (D4).
        channel_aliases=all_channel_aliases,
        include_all=include_all,
    )

    # [P3 EXTEND] (Item 5): append constraint + report-aggregator nodes and
    # mint their entry points. Guarded on eligible constraints existing —
    # `extend_graph_with_constraints` itself no-ops the aggregator when none
    # are eligible, but skipping the call entirely when nothing was resolved
    # keeps the corpus byte-identical with zero re-validation cost (INV-7).
    if concrete_constraints:
        computation_graph = extend_graph_with_constraints(
            computation_graph, concrete_constraints, group_deriver
        )
        # [P4 CATALOG] (Item 7 / D6): assemble the ConstraintCatalog and set it on the graph
        # before generation — every generation seam reads it from the graph, never from ctx
        # (Appendix A). `assemble_constraint_catalog` returns None when every concrete record
        # is unassessed (D7, zero eligible), so a facts-bearing-but-nothing-admitted model
        # still leaves the graph's `constraint_catalog` at its INV-7-preserving default.
        from sysml_codegen.generation.constraint_catalog import assemble_constraint_catalog

        computation_graph.constraint_catalog = assemble_constraint_catalog(
            concrete_constraints, constraint_facts
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
        concrete_constraints=concrete_constraints,
        constraint_facts=constraint_facts,
        part_occurrences=part_occurrences,
        constraint_lowering_mode=(
            CONSTRAINT_LOWERING_MODE_APPLIED
            if lower_constraints_enabled
            else CONSTRAINT_LOWERING_MODE_GRANDFATHERED_OFF
        ),
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
