"""Single source of truth for computation graph construction.

This module builds the complete computation graph from backtracking results.
The BacktrackingResult already HAS the graph - we just need to
transform it into PipelineModule objects.

KEY DESIGN DECISIONS:
1. Uses ParameterGroupDeriver for grouping logic
2. Leverages backtracker's existing binding resolution
3. Converts dataclasses (CalcUsageData) to Pydantic models (PipelineModule)
"""

import logging
import re
from collections import deque
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# UPDATED: Import from sysml_codegen package structure
from sysml_codegen.analysis.dependency_backtracker import (
    BacktrackingResult,
    CircularDependencyError,
)
from sysml_codegen.analysis.parameter_groups import (
    DesignAttributeData,
    ParameterGroupDeriver,
)
from sysml_codegen.core.identifier_types import ScopedKey, derive_module_type
from sysml_codegen.core.models import (
    BindingResolution,
    BindingResolutionType,
    ChannelAlias,
)
from sysml_codegen.core.qualified_names import (
    get_channel_name,
    get_module_name,
    owning_part_leaf,
    sanitize_name,
    sanitize_qualified_name,
)
from sysml_codegen.extraction.data_models import (
    ComputedAttributeClassification,
    ComputedAttributeData,
    RedefinitionData,
    RedefinitionType,
    ScopedAggregationData,
)
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.extraction.expression_compiler import (
    CalcDefCompilationResult,
    Compilability,
)
from sysml_codegen.extraction.usage_extractor import CalcUsageData
from sysml_codegen.resolution.input_resolver import (
    AGG_STRATEGIES,
    ResolutionContext,
    resolve_input,
)
from sysml_codegen.resolution.models import (
    ComputationGraph,
    EntryPoint,
    EntryPointType,
    InputSource,
    ModuleInput,
    ModuleOutput,
    OutputAlias,
    ParameterGroup,
    PipelineModule,
)

logger = logging.getLogger(__name__)


class MissingCalcDefError(Exception):
    """Raised when a calc usage references a calc def that doesn't exist.

    This indicates a model inconsistency - every usage should have a matching definition.
    """

    pass


def _build_auto_impl_context_for_calcusage(
    compilation_result: CalcDefCompilationResult,
    output_attr_names: list[str],
) -> dict:
    """Build auto-implementation context dict for a FULLY_COMPILABLE CalcUsage module.

    Mirrors the logic in generation/stencils.py:_build_auto_impl_context() but
    takes output_attr_names directly instead of a CalculationDefinitionData.

    Args:
        compilation_result: Compilation result with per-output expressions
        output_attr_names: Ordered output attribute names from calc_def
    """
    output_attr_set = set(output_attr_names)
    result_map = {r.output_name: r for r in compilation_result.output_results}

    has_output_crossrefs = any(
        set(result_map[name].intermediate_refs) & output_attr_set
        for name in output_attr_names
        if name in result_map and result_map[name].intermediate_refs
    )

    execution_steps = []
    output_expressions = []

    if has_output_crossrefs:
        for name in compilation_result.execution_order:
            r = result_map.get(name)
            if r and r.python_expression:
                execution_steps.append({
                    "name": r.output_name,
                    "expression": r.python_expression,
                })
        for name in output_attr_names:
            if name in result_map:
                output_expressions.append({
                    "name": name,
                    "expression": name,
                })
    else:
        for name in compilation_result.execution_order:
            r = result_map.get(name)
            if r and r.python_expression and r.is_undeclared_intermediate:
                execution_steps.append({
                    "name": r.output_name,
                    "expression": r.python_expression,
                })
        for name in output_attr_names:
            r = result_map.get(name)
            if r and r.python_expression:
                output_expressions.append({
                    "name": r.output_name,
                    "expression": r.python_expression,
                })

    return {
        "execution_steps": execution_steps,
        "output_expressions": output_expressions,
        "output_count": len(output_expressions),
        "single_output_expression": (
            output_expressions[0]["expression"]
            if len(output_expressions) == 1
            else None
        ),
    }


def _build_simple_auto_impl_context(compiled_expression: str, output_name: str) -> dict:
    """Build auto-impl context for single-output FORMULA/aggregation modules."""
    return {
        "execution_steps": [],
        "output_expressions": [{"name": output_name, "expression": compiled_expression}],
        "output_count": 1,
        "single_output_expression": compiled_expression,
    }


def build_computation_graph(
    result: BacktrackingResult,
    calc_defs: list,
    design_attrs: dict[Path, list[DesignAttributeData]],
    group_deriver: ParameterGroupDeriver,
    output_registry: OutputRegistry,
    compilation_results: dict | None = None,
    computed_attributes: list[ComputedAttributeData] | None = None,
    aggregation_data: list[ScopedAggregationData] | None = None,
    hierarchy_redefinitions: list[RedefinitionData] | None = None,
    usage_type_map: dict[tuple[str, str], str] | None = None,
    channel_aliases: list[ChannelAlias] | None = None,
    include_all: bool = True,
) -> ComputationGraph:
    """Build the complete computation graph from backtracking result.

    This is the SINGLE place where the pipeline structure is determined.
    No more redundant graph building in multiple places.

    Args:
        result: The BacktrackingResult from DependencyBacktracker
        calc_defs: All calculation definitions
        design_attrs: Design attributes by file
        group_deriver: Existing ParameterGroupDeriver for entry point grouping
        output_registry: OutputRegistry for channel resolution and validation
        compilation_results: Expression compilation results keyed by calc_def.name.
            If provided, sets each module's compilability field.
        computed_attributes: Computed attributes from Step 4.5. FORMULA+FULLY_COMPILABLE
            attrs produce synthetic PipelineModule objects alongside CalcUsage modules.
        aggregation_data: Scoped aggregation expressions from Step 4.7.
            Each produces a synthetic aggregation PipelineModule.
        hierarchy_redefinitions: PartDef-level :>> redefinitions for CHAIN
            resolution during aggregation input channel wiring.
        usage_type_map: Maps (owning_part_def_qn, usage_name) → type_part_def_qn.
            Used to resolve usage names to their type PartDef QNs for LITERAL
            redefinition lookup (e.g., ("Lib__Site_Infra", "permitting") →
            "Lib__Permitting_Interconnect").
        channel_aliases: All ChannelAliases (CHAIN + EXPOSE_PURE + design_override).
            Item 11 reads only the ``expose_pure`` subset to surface shape-B
            (part-usage) EXPOSE names into ``output_aliases``. If omitted, shape B
            silently does not surface — both call sites (live + snapshot) must
            thread it (F-A).
        include_all: Run mode, forwarded to ``_build_output_aliases``'s dangling
            filter (D4). True for full runs (every baseline); False for targeted
            generation, where a referenced channel may be legitimately pruned.

    Returns:
        ComputationGraph ready for YAML and JSON generation
    """
    # Step 1: Build calc def lookup
    calc_def_map = {cd.name: cd for cd in calc_defs}

    # Step 3: Build attribute resolution map (for FORMULA module input wiring)
    calc_usage_names = {u.instance_name for u in result.required_usages}
    attr_resolution_map: dict[str, dict[str, AttributeResolution]] = {}
    if computed_attributes:
        attr_resolution_map = _build_attribute_resolution_map(
            computed_attributes, design_attrs, output_registry, calc_usage_names
        )

    # Step 4: Classify entry points with full context
    entry_points = _classify_entry_points(
        result.entry_points,
        result.entry_point_sources,
        design_attrs,
        result.required_usages,
        calc_def_map,
        group_deriver,
    )

    # Step 5 removed (D4b): the former _group_entry_points_via_deriver call bound
    # param_groups here, but Step 6.6 unconditionally rebuilds it with ALL entry points
    # and nothing reads it in between — the binding was fully discarded. Its non-float
    # warning was a duplicate of Step 6.6's (both route through derive_groups()), so
    # deletion loses no warning (pinned by test_silent_failure_sc5.py).

    # Step 6: Build CalcUsage pipeline modules from required_usages
    modules = []
    for idx, usage in enumerate(result.required_usages):
        calc_def = calc_def_map.get(usage.calc_def_name)
        if not calc_def:
            raise MissingCalcDefError(
                f"Usage '{usage.instance_name}' references calc def '{usage.calc_def_name}' "
                f"which was not found in calc_defs. This indicates a model inconsistency."
            )

        module, new_eps = _build_pipeline_module(
            usage=usage,
            calc_def=calc_def,
            entry_points=entry_points,
            execution_order=idx,
            binding_resolutions=result.binding_resolutions,
        )
        entry_points.update(new_eps)

        # Set compilability and auto_impl_context from compilation results
        if compilation_results and usage.calc_def_name in compilation_results:
            cr = compilation_results[usage.calc_def_name]
            module.compilability = cr.overall_compilability
            if cr.overall_compilability == Compilability.FULLY_COMPILABLE:
                output_attr_names = [attr.name for attr in calc_def.output_attributes]
                module.auto_impl_context = _build_auto_impl_context_for_calcusage(
                    cr, output_attr_names,
                )

        modules.append(module)

    # Step 6.5: Build computed attribute modules
    if computed_attributes:
        for ca in computed_attributes:
            if (
                ca.classification == ComputedAttributeClassification.FORMULA
                and ca.compilability == Compilability.FULLY_COMPILABLE
            ):
                module, new_eps = _build_computed_attr_module(
                    ca, attr_resolution_map, entry_points,
                    design_attrs, group_deriver,
                )
                entry_points.update(new_eps)
                modules.append(module)
            elif ca.classification == ComputedAttributeClassification.EXPOSE_CHAIN_TENTATIVE:
                # INV-F: the confirm pass (Step 5.5) finalizes every tentative to
                # EXPOSE_PURE or FORMULA. Reaching the graph builder with one means
                # a tentative leaked — raise rather than silently drop it.
                raise ValueError(
                    "INV-F violation: EXPOSE_CHAIN_TENTATIVE reached module build "
                    f"for '{ca.owning_part_name}.{ca.name}'"
                )

    # Step 6.6b: Build EXPOSE_PURE alias map for aggregation LocalTerm resolution.
    # Maps (owning_part_qn, python_name) -> expression_text (e.g., "allocation_model.total_allocation").
    # Used by _build_aggregation_module() to wire LocalTerms that are computed attribute aliases.
    # NOTE: ComputedAttributeData.owning_part_qualified_name uses "::" separator with raw names
    # (e.g., "SolarBatteryLibrary::'Solar Array'"), while AggregationExpressionData.owning_part_qn
    # uses "__" separator with sanitized names (e.g., "SolarBatteryLibrary__Solar_Array").
    # sanitize_qualified_name does the per-segment "::"-> "__" normalization (D3: this was an
    # inline "__".join(sanitize_name(seg) ...) -- character-for-character the helper body).
    expose_aliases: dict[tuple[str, str], str] = {}
    for ca in (computed_attributes or []):
        if ca.classification == ComputedAttributeClassification.EXPOSE_PURE:
            normalized_qn = sanitize_qualified_name(ca.owning_part_qualified_name)
            expose_aliases[(normalized_qn, ca.python_name)] = ca.expression_text
        elif ca.classification == ComputedAttributeClassification.EXPOSE_CHAIN_TENTATIVE:
            # INV-F: no tentative survives the confirm pass (see module-build reader).
            raise ValueError(
                "INV-F violation: EXPOSE_CHAIN_TENTATIVE reached the aggregation "
                f"alias map for '{ca.owning_part_name}.{ca.name}'"
            )

    # Step 6.7: Build aggregation modules
    for agg in (aggregation_data or []):
        agg_module, new_eps = _build_aggregation_module(
            agg, hierarchy_redefinitions or [], output_registry,
            entry_points, group_deriver, expose_aliases,
            usage_type_map or {},
        )
        entry_points.update(new_eps)
        modules.append(agg_module)

    # Step 6.6: Rebuild param_groups with ALL entry points
    # FORMULA modules (Step 6.5) and aggregation modules (Step 6.7) may have
    # added new entry points to the entry_points dict. Rebuild to include them.
    # param_groups is NOT used during module building (Steps 6 and 6.5 use
    # entry_points dict and group_deriver.classify() directly), so this is safe.
    all_ep_names = set(entry_points.keys())
    raw_groups = group_deriver.derive_groups()
    for dg in raw_groups:
        dg.parameters = [
            p for p in dg.parameters
            if p.name in all_ep_names
        ]
    filtered_groups = [g for g in raw_groups if g.parameters]
    param_groups = _convert_derived_groups(filtered_groups, entry_points)

    # Step 6.8: Collect orphan entry points not covered by any param group
    covered_ep_names: set[str] = set()
    for group in param_groups:
        for p in group.parameters:
            covered_ep_names.add(p.qualified_name)

    orphan_eps = {
        qn: ep for qn, ep in entry_points.items()
        if qn not in covered_ep_names
    }

    if orphan_eps:
        # Build ep_qn -> python_type lookup from ModuleInput sources
        ep_type_lookup: dict[str, str] = {}
        for m in modules:
            for inp in m.inputs:
                if inp.source.source_type == "entry_point" and inp.source.qualified_name:
                    ep_type_lookup[inp.source.qualified_name] = inp.python_type

        orphan_params = []
        for qn, ep in orphan_eps.items():
            orphan_params.append(EntryPoint(
                qualified_name=qn,
                simple_name=ep.simple_name,
                entry_type=ep.entry_type,
                default_value=ep.default_value,
                python_type=ep_type_lookup.get(qn, "float"),
            ))
        if orphan_params:
            param_groups.append(ParameterGroup(
                name="system_design",
                class_name="SystemDesign",
                source_file=Path("hierarchy"),
                parameters=orphan_params,
            ))

    # Step 6.9: Propagate param_group to all entry_point InputSources.
    # After orphan handling, every EP belongs to some ParameterGroup.
    # Walk module inputs and fill in any InputSource with param_group=None.
    qn_to_group: dict[str, str] = {}
    for group in param_groups:
        for param in group.parameters:
            qn_to_group[param.qualified_name] = group.name
    for m in modules:
        for inp in m.inputs:
            if (
                inp.source.source_type == "entry_point"
                and inp.source.param_group is None
                and inp.source.qualified_name in qn_to_group
            ):
                inp.source.param_group = qn_to_group[inp.source.qualified_name]

    # Step 7: Unified topological sort across ALL modules
    modules = _unified_topological_sort(modules)

    # Step 8: Early validation - verify all channel references resolve
    # This catches transitive binding resolution bugs before TEAx validation
    _validate_channel_references(modules)

    # Step 8.5: Surface EXPOSE_PURE modeler names onto their canonical channels
    # (Item 11 / SC-7). Reads the two provenance-carrying sources; recomputes its
    # own declared-channel set (M5).
    output_aliases = _build_output_aliases(
        output_registry, channel_aliases or [], modules, include_all,
    )

    # Step 9: Sort entry-point groups by name, and the parameters within each
    # group by qualified_name (REQ-BASE-06). Both the group order and the
    # within-group parameter order are derived in model-discovery order, which
    # shifts between runs/machines and reddens byte-exact baselines — and, for
    # Item 2, breaks live-vs-snapshot byte-identity (SC-1) since the two paths
    # discover design attributes in different orders. Sorting the graph — not just
    # the rendered YAML — makes every entry_point_groups consumer deterministic.
    # Group names are unique per design file and parameter qualified_names are
    # unique within a group, so both sorts are total.
    for group in param_groups:
        # param_groups is the converted ParameterGroup list (params carry
        # qualified_name). With the DerivedParameterGroup loop above renamed to `dg`
        # (D4), `group` binds cleanly as ParameterGroup — no type: ignore needed.
        group.parameters.sort(key=lambda p: p.qualified_name)
    param_groups = sorted(param_groups, key=lambda g: g.name)

    return ComputationGraph(
        modules=modules,
        entry_point_groups=param_groups,
        execution_order=[m.name for m in modules],
        fallback_entry_points=set(result.fallback_entry_points),
        output_aliases=output_aliases,
    )



def _classify_entry_points(
    entry_point_names: set[str],
    entry_point_sources: dict[str, str],
    design_attrs: dict[Path, list[DesignAttributeData]],
    usages: list[CalcUsageData],
    calc_def_map: dict,
    group_deriver: ParameterGroupDeriver,
) -> dict[str, EntryPoint]:
    """Classify all entry points with full type information.

    Classification logic (in order of precedence):
    1. Check if qualified name matches a DesignAttributeData -> DESIGN_ATTRIBUTE
    2. Check if qualified name ends with an unbound param -> LIBRARY_DEFAULT
    3. Otherwise -> USAGE_LITERAL (binding was literal in usage)

    Default value sources:
    - DESIGN_ATTRIBUTE: DesignAttributeData.default_value
    - LIBRARY_DEFAULT: calc_def.input_attributes[param].default_value (via _get_library_default)
    - USAGE_LITERAL: BindingInfo.literal_value from the usage

    Args:
        entry_point_names: Set of qualified entry point names from backtracker
        entry_point_sources: Maps qualified name -> binding source path
        design_attrs: Design attributes indexed by file
        usages: All calc usages
        calc_def_map: Calc def lookup
        group_deriver: For determining param_group

    Returns:
        Dict mapping qualified_name -> EntryPoint
    """
    # Build design attribute index by qualified name
    design_attr_by_qname: dict[str, DesignAttributeData] = {}
    for attrs in design_attrs.values():
        for attr in attrs:
            if attr.qualified_name:
                design_attr_by_qname[attr.qualified_name] = attr

    # Build unbound param lookup: qualified_name -> (usage, param_name)
    unbound_lookup: dict[str, tuple[CalcUsageData, str]] = {}
    for usage in usages:
        for param_name in usage.unbound_params:
            qname = f"{usage.qualified_name}__{param_name}"
            unbound_lookup[qname] = (usage, param_name)

    result: dict[str, EntryPoint] = {}

    for qname in entry_point_names:
        simple_name = qname.split("__")[-1]
        entry_type: EntryPointType
        default_value: float | None = None
        source_calc_usage: str | None = None

        # Strategy 1: Design attribute match
        if qname in design_attr_by_qname:
            attr = design_attr_by_qname[qname]
            entry_type = EntryPointType.DESIGN_ATTRIBUTE
            # INV-6 (F2): `is not None`, not truthiness — a supplied `0.0` (or `""`)
            # design attribute must carry as `0.0`, not silently drop to `None` and
            # emit `null`, which would escape V11 (`collect_uncovered_params` keys on
            # the fell-through set, so a Step-3-resolved 0.0 EP dropped to None lies).
            if attr.default_value is not None:
                try:
                    default_value = float(attr.default_value)
                except (ValueError, TypeError):
                    pass

        # Strategy 2: Unbound param (library default)
        elif qname in unbound_lookup:
            usage, param_name = unbound_lookup[qname]
            entry_type = EntryPointType.LIBRARY_DEFAULT
            source_calc_usage = usage.calc_def_name

            calc_def = calc_def_map.get(usage.calc_def_name)
            if not calc_def:
                raise MissingCalcDefError(
                    f"Usage '{usage.instance_name}' references calc def '{usage.calc_def_name}' "
                    f"which was not found when classifying entry point '{qname}'."
                )
            default_value = _get_library_default(calc_def, param_name)

        # Strategy 3: Usage literal (ADR-001 Type 3)
        # This is a valid classification, not a fallback - the entry point
        # was created from a literal binding in a calc usage
        else:
            entry_type = EntryPointType.USAGE_LITERAL
            # Find the literal value from the binding source
            source_path = entry_point_sources.get(qname)
            if source_path:
                try:
                    default_value = float(source_path)
                except (ValueError, TypeError):
                    pass

        # Determine param group using deriver
        param_group = group_deriver.classify(qname) if group_deriver else None

        result[qname] = EntryPoint(
            qualified_name=qname,
            simple_name=simple_name,
            entry_type=entry_type,
            default_value=default_value,
            source_calc_usage=source_calc_usage,
            param_group=param_group,
        )

    return result


def _convert_derived_groups(
    derived_groups: list,
    entry_points: dict[str, EntryPoint],
) -> list[ParameterGroup]:
    """Convert DerivedParameterGroup list to ParameterGroup Pydantic models.

    Used by the Step 6.6 param_groups rebuild.

    Args:
        derived_groups: DerivedParameterGroup list (already filtered)
        entry_points: Classified entry points by qualified name

    Returns:
        List of ParameterGroup Pydantic models
    """
    result = []
    for dg in derived_groups:
        # Map parameters to EntryPoint objects
        # NOTE: ps.name is QUALIFIED per Phase 2 implementation in parameter_group_derivation.py
        params = []
        for ps in dg.parameters:
            # ps.name is already qualified (e.g., "CATFMFEPhysics__catf_physics__p_fusion")
            if ps.name in entry_points:
                ep = entry_points[ps.name]
                # Merge default_value from ParameterSource if EntryPoint has None
                # ParameterSource may have resolved bindings that EntryPoint classification missed
                if ep.default_value is None and ps.default_value is not None:
                    ep = EntryPoint(
                        qualified_name=ep.qualified_name,
                        simple_name=ep.simple_name,
                        entry_type=ep.entry_type,
                        default_value=ps.default_value,
                        source_calc_usage=ep.source_calc_usage,
                        param_group=ep.param_group,
                    )
                params.append(ep)
            else:
                # Log warning - should not happen if both use same qualified names
                logger.warning(
                    f"Entry point '{ps.name}' from deriver not found in classified entry_points"
                )

        # source_identifier is filename like "physics.sysml" - keep as Path for consistency
        source_file = (
            Path(dg.source_identifier) if dg.source_identifier else Path("unknown.sysml")
        )

        result.append(
            ParameterGroup(
                name=dg.name,
                class_name=dg.class_name,
                source_file=source_file,
                parameters=params,
            )
        )

    return result


def _get_library_default(
    calc_def,
    param_name: str,
) -> float | None:
    """Get default value from calc def input, if parseable as float.

    Handles the complexity of library defaults which may be:
    - None (no default specified)
    - A string like "0.3" (needs parsing)
    - An expression like "1.0 / q_eng" (can't be used as JSON default)

    Args:
        calc_def: CalculationDefinitionData
        param_name: Parameter name to find

    Returns:
        Float value if parseable, None otherwise
    """
    attr = next((a for a in calc_def.input_attributes if a.name == param_name), None)
    if attr and attr.default_value:
        try:
            return float(attr.default_value)
        except (ValueError, TypeError):
            return None  # Expression or non-numeric
    return None


def _validate_channel_references(modules: list[PipelineModule]) -> None:
    """Validate that all module_output channel references exist.

    Early validation catches transitive binding resolution bugs before
    TEAx validation, providing clearer error messages.

    Args:
        modules: All pipeline modules to validate

    Raises:
        ValueError: If a module_output reference points to unknown channel
    """
    # Collect all declared output channels
    declared_channels: set[str] = set()
    for module in modules:
        for output in module.outputs:
            declared_channels.add(output.channel_name)

    # Validate all module_output references
    for module in modules:
        for input_def in module.inputs:
            if input_def.source.source_type == "module_output":
                channel = input_def.source.producer_channel
                if channel and channel not in declared_channels:
                    # Show first 10 channels for debugging context
                    sample_channels = sorted(declared_channels)[:10]
                    raise ValueError(
                        f"Module '{module.name}' input '{input_def.param_name}' "
                        f"references unknown channel '{channel}'. "
                        f"This may indicate a transitive binding resolution bug. "
                        f"Available channels ({len(declared_channels)} total): "
                        f"{sample_channels}..."
                    )


def _build_output_aliases(
    output_registry: OutputRegistry,
    channel_aliases: list[ChannelAlias],
    modules: list[PipelineModule],
    include_all: bool,
) -> list[OutputAlias]:
    """Surface EXPOSE_PURE modeler names onto their canonical channels (Item 11).

    Reads the two provenance-carrying EXPOSE_PURE sources — never the
    source-erased flat ``_alias`` (INV-1) — normalizes each into an
    ``OutputAlias``, drops any whose channel is not a declared graph output
    (INV-3, run-mode split per D4), and stable-sorts by
    ``(instance_path, alias_name)`` (INV-5).

    Shape A (part def): the ``_scoped_alias`` registry, already keyed
    ``(instance_path, python_name) → channel``. The channel is read straight
    from the registry (INV-2); the scope half is the instance path.

    Shape B (part usage): the ``expose_pure`` ``ChannelAlias`` objects. Each
    carries a bare ``canonical_name`` (``instance.attr``) resolved the same
    two-step way Item 10 registered it — ``alias_lookup`` first (the persisted
    Key_A twin written at ``output_registry_builder`` Phase 1a), ``scoped_lookup``
    as fallback. C1: ``scoped_lookup`` alone keeps the full nested path and would
    miss every nested part-usage EXPOSE (it resolves none of the in-repo shape-B
    aliases), so alias-first is load-bearing, not interchangeable — do not "fix"
    it to ``scoped_lookup``-only. The ``alias_lookup`` read does not violate
    INV-1: the entry is already source-selected as ``expose_pure``; the lookup
    only resolves that already-chosen alias's channel string, it does not *source*
    entries from ``_alias``.

    Args:
        output_registry: Carries both EXPOSE_PURE sources.
        channel_aliases: All ChannelAliases; filtered to ``.source == "expose_pure"``.
        modules: The built pipeline modules. The declared-channel set is
            recomputed here locally — ``_validate_channel_references`` returns
            ``None``, it does not hand its set over (M5).
        include_all: Run mode. On a full run a dropped alias is a real wiring
            regression (raise); on a targeted run a channel an EXPOSE references
            may be legitimately pruned (drop + debug-log). (D4 / M3.)

    Raises:
        ValueError: On an ``include_all`` run, if any emitted entry's channel is
            not a declared graph output.
    """
    declared_channels: set[str] = set()
    for module in modules:
        for output in module.outputs:
            declared_channels.add(output.channel_name)

    candidates: list[OutputAlias] = []

    # Shape A: part-def EXPOSE_PURE, expanded per instance into _scoped_alias.
    for (scope, leaf), channel in output_registry.scoped_alias_items():
        candidates.append(OutputAlias(
            alias_name=leaf,
            canonical_channel=channel,
            instance_path=scope,
            shape="part_def",
        ))

    # Shape B: part-usage EXPOSE_PURE ChannelAliases.
    for alias in channel_aliases:
        if alias.source != "expose_pure":
            continue
        resolved = output_registry.alias_lookup(ScopedKey(alias.canonical_name))
        if resolved is None:
            resolved = output_registry.scoped_lookup(ScopedKey(alias.canonical_name))
        if resolved is None:
            # Genuinely unresolvable shape B — no name to surface. The
            # resolution-map path (_resolve_expose_pure :796) owns that warning;
            # here we simply do not emit an entry.
            continue
        candidates.append(OutputAlias(
            alias_name=alias.alias_name,
            canonical_channel=resolved,
            instance_path=owning_part_leaf(alias.owning_part_qn),
            shape="part_usage",
        ))

    # INV-3: every emitted entry's channel is a declared output. D4 splits the
    # drop by run mode.
    surfaced: list[OutputAlias] = []
    for entry in candidates:
        if entry.canonical_channel in declared_channels:
            surfaced.append(entry)
            continue
        if include_all:
            raise ValueError(
                f"output_aliases: EXPOSE_PURE alias '{entry.alias_name}' on "
                f"'{entry.instance_path}' targets channel "
                f"'{entry.canonical_channel}', which is not a declared graph "
                f"output. On a full (include_all) run nothing legitimately prunes, "
                f"so this is a wiring regression, not a targeted-run drop (D4)."
            )
        logger.debug(
            "output_aliases: dropping alias '%s' on '%s' — channel '%s' pruned "
            "on this targeted run",
            entry.alias_name, entry.instance_path, entry.canonical_channel,
        )

    # INV-5: deterministic order. (instance_path, alias_name) is unique because
    # one name cannot be both part-def- and part-usage-exposed on one instance,
    # so shape A and shape B never emit the same key; source iteration order
    # then never affects the result.
    surfaced.sort(key=lambda a: (a.instance_path, a.alias_name))
    return surfaced


@dataclass(frozen=True)
class UncoveredInput:
    """A module input wired to a params key that no parameter group provides.

    A genuine coverage gap (Item 7 / D4): a bound binding that fell through all
    resolution (its EP QN is in ``fallback_entry_points``), carries no value
    (EP ``default_value is None``), and is still referenced by a surviving
    module input. The pipeline emits the params key but the JSON never mints it
    — a guaranteed runtime ``KeyError`` at load. Names the offender precisely.
    """

    module: str
    input: str
    missing_key: str


def collect_uncovered_params(graph: ComputationGraph) -> list[UncoveredInput]:
    """Return every module input wired to an uncovered params key.

    Pure (INV-3): returns a (possibly empty) list, raises nothing. Only the
    generation boundary raises V11 on a non-empty result.

    A module ``entry_point`` input is a violation when all three hold:
    - its ``qualified_name`` is in ``graph.fallback_entry_points`` (fell through
      Step-4),
    - its entry point carries no value (``default_value is None`` — valueless),
    - a surviving module input references it (wired — the iteration itself).

    Fell-through EPs that carry a value (a bound literal parsed to a float, or a
    deriver-back-filled default) and non-fall-through null-default EPs
    (legitimate user-fill) are not violations.
    """
    # Index entry point default values by qualified name (valueless test).
    ep_default: dict[str, float | None] = {}
    for group in graph.entry_point_groups:
        for ep in group.parameters:
            ep_default[ep.qualified_name] = ep.default_value

    violations: list[UncoveredInput] = []
    for module in graph.modules:
        for inp in module.inputs:
            src = inp.source
            if src.source_type != "entry_point" or not src.qualified_name:
                continue
            qn = src.qualified_name
            if qn not in graph.fallback_entry_points:
                continue
            # Valueless: the entry point carries no default (None). A fell-through
            # EP that got a value is minted normally and is not a gap.
            if ep_default.get(qn) is not None:
                continue
            missing_key = (
                f"{src.param_group}.{qn}" if src.param_group else qn
            )
            violations.append(
                UncoveredInput(
                    module=module.name,
                    input=inp.param_name,
                    missing_key=missing_key,
                )
            )
    return violations


def collect_unwired_fallthrough(graph: ComputationGraph) -> list[str]:
    """Return fell-through, valueless entry points that no module input wires.

    The other half of the M1 partition (Item 7): fell-through ∧ valueless ∧
    **unwired**. These carry no value but nothing references them, so they are
    tracked residue (reconciliation summary, WARNING) — not a runtime
    ``KeyError`` like the wired half (V11). Pure; returns a sorted QN list.
    """
    ep_default: dict[str, float | None] = {}
    for group in graph.entry_point_groups:
        for ep in group.parameters:
            ep_default[ep.qualified_name] = ep.default_value

    wired: set[str] = {
        inp.source.qualified_name
        for module in graph.modules
        for inp in module.inputs
        if inp.source.source_type == "entry_point" and inp.source.qualified_name
    }

    remainder: list[str] = []
    for qn in graph.fallback_entry_points:
        if qn in wired:
            continue
        if ep_default.get(qn) is not None:  # valueless only
            continue
        remainder.append(qn)
    return sorted(remainder)


class AttributeResolutionKind(str, Enum):
    """Classification of how an attribute reference should be wired."""

    FORMULA = "formula"
    EXPOSE_ALIAS = "expose_alias"
    LITERAL = "literal"


@dataclass
class AttributeResolution:
    """How an attribute reference in a FORMULA expression should be wired."""

    kind: AttributeResolutionKind
    channel_name: str | None = None  # For formula and expose_alias



def _resolve_expose_pure(
    ca: ComputedAttributeData,
    calc_usage_names: set[str],
    output_registry: OutputRegistry,
) -> str | None:
    """Resolve an EXPOSE_PURE attribute to its upstream calc output channel.

    An EXPOSE_PURE attribute like ``p_alpha_out = alpha_split.p_alpha`` has
    references containing both the calc usage instance name and the calc output
    attribute name. This function separates them and looks up the output registry.

    Returns:
        channel_name if resolved, None if the registry key is not found.
    """
    instance_name: str | None = None
    output_attr_name: str | None = None

    for ref in ca.references:
        if ref.name in calc_usage_names:
            instance_name = ref.name
        else:
            output_attr_name = ref.name

    if instance_name is None or output_attr_name is None:
        logger.warning(
            "EXPOSE_PURE %s: could not identify instance/output from refs %s",
            ca.name, [r.name for r in ca.references],
        )
        return None

    catalog_key = f"{instance_name}.{output_attr_name}"
    channel_name = output_registry.scoped_lookup(ScopedKey(catalog_key))
    if channel_name is None:
        channel_name = output_registry.alias_lookup(ScopedKey(catalog_key))
    if channel_name is None:
        logger.warning(
            "EXPOSE_PURE %s: derived-attribute name is dropped from generated "
            "output — no alias is emitted. Its value was expected on canonical "
            "channel '%s', which is not registered (name-form mismatch; part-def "
            "shape-A resolution is Item 10/11).",
            ca.name, catalog_key,
        )
        return None

    return channel_name


def _build_attribute_resolution_map(
    computed_attrs: list[ComputedAttributeData],
    design_attrs: dict[Path, list[DesignAttributeData]],
    output_registry: OutputRegistry,
    calc_usage_names: set[str],
) -> dict[str, dict[str, AttributeResolution]]:
    """Build per-part map: owning_part_name -> {attr_name -> AttributeResolution}.

    This map tells the graph builder how to wire each FORMULA module input.

    Resolution logic per attribute:
    - FORMULA computed attr -> kind="formula", channel from synthetic module
    - EXPOSE_PURE part usage (shape B) -> kind="expose_alias", channel from upstream
    - EXPOSE_PURE part def (shape A) -> kind="literal"; warning gated on _scoped_alias
    - Not found -> kind="literal" (conservative: becomes entry point)

    Args:
        computed_attrs: All computed attributes from Step 4.5
        design_attrs: Design attributes indexed by file
        output_registry: OutputRegistry for channel resolution
        calc_usage_names: CalcUsage instance names for EXPOSE_PURE resolution
    """
    # D3-7 (closed-by-construction). This resolution map is keyed by the *bare*
    # owning_part_name, so two same-named PartDefs in different packages could in
    # principle merge buckets and silently cross-wire. The reachable silent-
    # cross-wire shape is already loud-rejected upstream: any FORMULA channel
    # registers a scoped key `{owning_part_name}.{python_name}` via
    # OutputRegistry.register_scoped (core/output_registry.py:72), which RAISES on
    # a duplicate key with a different channel — before this map is built. So a
    # cross-wire needing two entries at the same (bare part_name, python_name)
    # *with a channel* cannot reach here silently. EXPOSE resolutions are
    # LITERAL/no-channel, so a same-key overwrite mis-wires nothing. The bare->QN
    # re-key is optional defense-in-depth, deferred (no reachable silent failure).
    result: dict[str, dict[str, AttributeResolution]] = {}

    # Shape-A resolvability probe (Item 11): the leaves registered in the
    # structured part-def EXPOSE namespace. A shape-A EXPOSE whose python_name is
    # among these resolved (Item 10) and surfaces (Item 11), so it warns no more.
    scoped_alias_leaves = {
        leaf for (_scope, leaf), _chan in output_registry.scoped_alias_items()
    }

    for ca in computed_attrs:
        part_name = ca.owning_part_name
        if part_name not in result:
            result[part_name] = {}

        if (
            ca.classification == ComputedAttributeClassification.FORMULA
            and ca.compilability == Compilability.FULLY_COMPILABLE
        ):
            # FORMULA -> wire to synthetic module output channel.
            # M1: build the module_eqn leaf from python_name (never re-sanitize
            # ca.name), so the produced (registry) and consumed (here) channels
            # are identical by construction -- see design B2/INV-5.
            module_eqn = (
                f"{sanitize_qualified_name(ca.owning_part_qualified_name)}"
                f"__{ca.python_name}"
            )
            channel_name = get_channel_name(module_eqn, ca.python_name)
            result[part_name][ca.python_name] = AttributeResolution(
                kind=AttributeResolutionKind.FORMULA, channel_name=channel_name,
            )

        elif ca.classification == ComputedAttributeClassification.EXPOSE_PURE:
            if ca.is_on_part_definition:
                # Shape A (part def). _resolve_expose_pure can't split the refs
                # here — the calc-usage instance names are absent from
                # calc_usage_names on a part def — so it would fire the
                # malformed-refs warning at :796. Item 10 resolves shape A per
                # instance via _scoped_alias instead; this per-def map is
                # structurally instance-blind and no in-repo FORMULA consumes a
                # shape-A exposed name (B3), so the LITERAL fallback — identical to
                # today's post-warning behavior — mis-wires nothing. Consult
                # _scoped_alias only to decide the warning: a registered leaf means
                # the name resolves and surfaces (Item 11) → silent; an
                # unregistered one names the real cause, not "Item 10/11".
                result[part_name][ca.python_name] = AttributeResolution(
                    kind=AttributeResolutionKind.LITERAL,
                )
                if ca.python_name not in scoped_alias_leaves:
                    logger.warning(
                        "EXPOSE_PURE %s on part def %s: no scoped alias registered "
                        "for '%s' — the derived-attribute name cannot be surfaced "
                        "(the referenced calc output did not resolve on any design "
                        "instance).",
                        ca.name, ca.owning_part_name, ca.python_name,
                    )
            else:
                # Shape B (part usage): unchanged _resolve_expose_pure path — an
                # unresolvable shape B still warns at :796.
                channel = _resolve_expose_pure(ca, calc_usage_names, output_registry)
                if channel is not None:
                    result[part_name][ca.python_name] = AttributeResolution(
                        kind=AttributeResolutionKind.EXPOSE_ALIAS, channel_name=channel,
                    )
                else:
                    # Fallback: treat as literal (entry point)
                    result[part_name][ca.python_name] = AttributeResolution(
                        kind=AttributeResolutionKind.LITERAL,
                    )

        elif ca.classification == ComputedAttributeClassification.EXPOSE_CHAIN_TENTATIVE:
            # INV-F: no tentative survives the confirm pass. Without this branch a
            # survivor would fall through to the implicit literal default below and
            # silently mis-wire — raise instead.
            raise ValueError(
                "INV-F violation: EXPOSE_CHAIN_TENTATIVE reached the attribute "
                f"resolution map for '{ca.owning_part_name}.{ca.name}'"
            )

    return result


def _build_computed_attr_module(
    ca: ComputedAttributeData,
    resolution_map: dict[str, dict[str, AttributeResolution]],
    entry_points: dict[str, EntryPoint],
    design_attrs: dict[Path, list[DesignAttributeData]],
    group_deriver: ParameterGroupDeriver,
) -> tuple[PipelineModule, dict[str, EntryPoint]]:
    """Build a PipelineModule from a FORMULA ComputedAttributeData.

    Args:
        ca: The FORMULA computed attribute (must be FULLY_COMPILABLE)
        resolution_map: Per-part attribute resolution map
        entry_points: Read-only dict of classified entry points
        design_attrs: Design attributes for default value lookup
        group_deriver: For classifying new entry points

    Returns:
        (PipelineModule, dict of new entry points created by this factory)
    """
    new_entry_points: dict[str, EntryPoint] = {}
    # Naming per ADR-003. M1: module_eqn leaf from python_name (identical to the
    # registry producer by construction); module_type is a *different*
    # identifier derived from ca.name via from_sysml (sanitized in Phase 2), so
    # it keeps the raw sysml_qn.
    sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
    module_eqn = (
        f"{sanitize_qualified_name(ca.owning_part_qualified_name)}__{ca.python_name}"
    )
    module_name = get_module_name(module_eqn)
    module_type = derive_module_type(sysml_qn)

    # Extract input names from compiled expression, deduplicate preserving order
    # compiled_expression is guaranteed non-None for FULLY_COMPILABLE FORMULA attrs
    if ca.compiled_expression is None:
        raise ValueError(
            f"FORMULA attr {ca.name} has no compiled_expression "
            f"(compilability={ca.compilability})"
        )
    raw_inputs = re.findall(r"inputs\.(\w+)", ca.compiled_expression)
    seen: set[str] = set()
    input_names: list[str] = []
    for name in raw_inputs:
        if name not in seen:
            seen.add(name)
            input_names.append(name)

    # Build per-part resolution lookup
    part_resolutions = resolution_map.get(ca.owning_part_name, {})

    # Build design attr index for default value lookup
    design_attr_by_qname: dict[str, DesignAttributeData] = {}
    for attrs in design_attrs.values():
        for attr in attrs:
            if attr.qualified_name:
                design_attr_by_qname[attr.qualified_name] = attr

    part_eqn = sanitize_qualified_name(ca.owning_part_qualified_name)

    # Build inputs
    inputs: list[ModuleInput] = []
    for input_name in input_names:
        attr_res = part_resolutions.get(input_name)

        _wirable = (AttributeResolutionKind.FORMULA, AttributeResolutionKind.EXPOSE_ALIAS)
        if attr_res and attr_res.kind in _wirable and attr_res.channel_name:
            # Wire to upstream module output
            source = InputSource(
                source_type="module_output",
                producer_channel=attr_res.channel_name,
            )
        else:
            # Create/reuse entry point (literal or unresolved)
            ep_qname = f"{part_eqn}__{input_name}"

            if ep_qname not in entry_points and ep_qname not in new_entry_points:
                # Look up default value from design attrs
                default_value: float | None = None
                da = design_attr_by_qname.get(ep_qname)
                # INV-6 (F2), second drop site: same `is not None` guard as `:482`.
                # A FORMULA computed-attr input can wire to a materialized subsystem
                # attribute valued `0.0`; truthiness would drop it to `null` here too.
                if da and da.default_value is not None:
                    try:
                        default_value = float(da.default_value)
                    except (ValueError, TypeError):
                        pass

                param_group = group_deriver.classify(ep_qname) if group_deriver else None

                new_entry_points[ep_qname] = EntryPoint(
                    qualified_name=ep_qname,
                    simple_name=input_name,
                    entry_type=EntryPointType.DESIGN_ATTRIBUTE,
                    default_value=default_value,
                    param_group=param_group,
                )

            ep = new_entry_points.get(ep_qname) or entry_points[ep_qname]
            source = InputSource(
                source_type="entry_point",
                param_group=ep.param_group,
                qualified_name=ep_qname,
            )

        inputs.append(
            ModuleInput(
                param_name=input_name,
                python_type="float",
                source=source,
            )
        )

    # Build single output
    output = ModuleOutput(
        field_name="root",
        python_type="float",
        channel_name=get_channel_name(module_eqn, ca.python_name),
        description=getattr(ca, "description", None),
    )

    return PipelineModule(
        name=module_name,
        module_type=module_type,
        inputs=inputs,
        outputs=[output],
        execution_order=0,  # Assigned during unified toposort
        compilability=Compilability.FULLY_COMPILABLE,
        compiled_expression=ca.compiled_expression,
        is_computed_attribute=True,
        auto_impl_context=_build_simple_auto_impl_context(
            ca.compiled_expression, ca.python_name,
        ),
        calc_def_name=ca.name,
        calc_def_qualified_name=ca.owning_part_qualified_name,
        doc_comment=getattr(ca, "description", None),
        calc_expressions=[ca.expression_text] if ca.expression_text else None,
        source_file=str(ca.source_file),
        source_line=ca.source_line,
    ), new_entry_points


def _find_literal_redefinition(
    part_usage: str,
    attr: str,
    redefinitions: list[RedefinitionData],
    usage_type_map: dict[tuple[str, str], str] | None = None,
    owning_part_qn: str | None = None,
) -> float | None:
    """Find a LITERAL :>> redefinition value for a part usage attribute.

    Mirrors the CHAIN matching pattern used by ChainRedefinitionFollow (input_resolver.py)
    but for RedefinitionType.LITERAL. Used to propagate default values for
    entry points when a PartDef sets e.g. `:>> raw_material_cost = 0.0`.

    Matching strategy:
    1. If usage_type_map is available, resolve (owning_part_qn, part_usage)
       to the child's type PartDef QN and match redefinitions by owning_part_qn.
    2. Fall back to the original name-based matching (last segment of owning_part_qn).

    Args:
        part_usage: Part usage name (e.g., "permitting")
        attr: Attribute name (e.g., "raw_material_cost")
        redefinitions: PartDef-level :>> redefinitions
        usage_type_map: Maps (owning_partdef_qn, usage_name) → type_partdef_qn
        owning_part_qn: QN of the PartDef that owns the aggregation expression

    Returns:
        Float value if a matching LITERAL redefinition is found, None otherwise.
    """
    # Resolve usage name to its type PartDef QN if possible
    target_partdef_qn: str | None = None
    if usage_type_map and owning_part_qn:
        target_partdef_qn = usage_type_map.get((owning_part_qn, part_usage))

    first_value: float | None = None
    # D3-10: Strategy 2 (name-based leaf match) is first-wins across ALL partdefs
    # sharing a leaf name. A leaf-name match is structurally required in this
    # fallback (there is no PartDef QN to key on), so instead of a silent
    # first-wins we collect the colliding literals and warn (INV-3
    # require-unique-or-warn). Strategy 1 (exact QN) stays unambiguous.
    strategy2_hits: list[float] = []
    for redef in redefinitions:
        if redef.redefinition_type == RedefinitionType.LITERAL and redef.attribute_name == attr:
            via_strategy2 = False
            if target_partdef_qn is not None:
                matched = redef.owning_part_qn == target_partdef_qn
            else:
                redef_part_name = redef.owning_part_qn.split("__")[-1]
                matched = sanitize_name(redef_part_name).lower() == part_usage.lower()
                via_strategy2 = matched

            if matched and redef.literal_value is not None:
                try:
                    value = float(redef.literal_value)
                except (ValueError, TypeError):
                    return None
                if not via_strategy2:
                    return value  # Strategy 1: exact QN match, unambiguous.
                strategy2_hits.append(value)
                if first_value is None:
                    first_value = value

    if len(set(strategy2_hits)) > 1:
        logger.warning(
            "Redefinition leaf collision for '%s.%s': name-matched partdefs carry "
            "differing literals %s; resolved first-wins to %s (ambiguous — no "
            "PartDef QN to disambiguate).",
            part_usage,
            attr,
            sorted(set(strategy2_hits)),
            first_value,
        )
    return first_value


def _build_agg_input_source(
    ref: str,
    ctx: ResolutionContext,
    literal_lookup_key: tuple[str, str] | None,
    redefinitions: list[RedefinitionData],
    usage_type_map: dict[tuple[str, str], str],
    owning_part_qn: str,
    group_deriver: ParameterGroupDeriver | None,
    entry_points: dict[str, EntryPoint],
    new_entry_points: dict[str, EntryPoint],
) -> tuple[InputSource, bool]:
    """Resolve one aggregation term to an InputSource, owning the EP side effects.

    The reconciliation choke point for SumTerm/SingletonTerm inputs. Wraps the pure
    ``resolve_input(ref, ctx, AGG_STRATEGIES)``:

    - A ``module_output`` result is returned as-is (not manual-required).
    - An ``entry_point`` result triggers the side effects the old inline ``else:``
      blocks owned: look up a ``LITERAL :>>`` default, register/dedup/backfill the
      ``DESIGN_ATTRIBUTE`` EntryPoint into ``new_entry_points``, classify its
      param-group, and report ``manual_required`` (True when the term is unresolved
      and has no literal default — the caller sets ``MANUAL_REQUIRED`` compilability).

    The EP QN is ``resolve_input``'s reconciled fallback key
    ``{ctx.module_eqn}__{ref.replace('.','_')}`` (INV-1). ``ctx.module_eqn`` MUST be
    ``agg.module_eqn`` (INV-7), else every fallback key shifts.

    ``literal_lookup_key`` is the ``(part_usage, attr)`` to look up a LITERAL default
    for, or ``None`` to skip the lookup (the dotless-SingletonTerm case, which has no
    part-usage to look up — its default stays ``None``).

    Returns ``(InputSource, manual_required)``. Mutates ``new_entry_points`` only.
    """
    resolved = resolve_input(ref, ctx, AGG_STRATEGIES)
    if resolved.source_type == "module_output":
        return resolved, False

    # Entry-point fallback: reproduce the inline else-block's side effects.
    ep_qn = resolved.qualified_name
    assert ep_qn is not None  # resolve_input always sets qualified_name on entry_point
    param_name = ref.replace(".", "_")

    literal_default: float | None = None
    if literal_lookup_key is not None:
        lu_part_usage, lu_attr = literal_lookup_key
        literal_default = _find_literal_redefinition(
            lu_part_usage, lu_attr, redefinitions, usage_type_map, owning_part_qn,
        )

    manual_required = literal_default is None

    if ep_qn not in entry_points and ep_qn not in new_entry_points:
        param_group = group_deriver.classify(ep_qn) if group_deriver else None
        new_entry_points[ep_qn] = EntryPoint(
            qualified_name=ep_qn,
            simple_name=param_name,
            entry_type=EntryPointType.DESIGN_ATTRIBUTE,
            default_value=literal_default,
            param_group=param_group,
        )
    elif literal_default is not None:
        # Backfill the default onto an EP created earlier without one.
        existing_ep = new_entry_points.get(ep_qn) or entry_points.get(ep_qn)
        if existing_ep and existing_ep.default_value is None:
            new_entry_points[ep_qn] = EntryPoint(
                qualified_name=existing_ep.qualified_name,
                simple_name=existing_ep.simple_name,
                entry_type=existing_ep.entry_type,
                default_value=literal_default,
                source_calc_usage=existing_ep.source_calc_usage,
                param_group=existing_ep.param_group,
            )

    ep = new_entry_points.get(ep_qn) or entry_points[ep_qn]
    source = InputSource(
        source_type="entry_point",
        qualified_name=ep_qn,
        param_group=ep.param_group,
    )
    return source, manual_required


def _build_aggregation_module(
    agg: ScopedAggregationData,
    redefinitions: list[RedefinitionData],
    output_registry: OutputRegistry,
    entry_points: dict[str, EntryPoint],
    group_deriver: ParameterGroupDeriver | None,
    expose_aliases: dict[tuple[str, str], str] | None = None,
    usage_type_map: dict[tuple[str, str], str] | None = None,
) -> tuple[PipelineModule, dict[str, EntryPoint]]:
    """Build a PipelineModule from a ScopedAggregationData.

    Follows the _build_computed_attr_module() pattern. Creates inputs from
    SumTerms (channel + multiplicity EP), SingletonTerms (channel), and
    LocalTerms (entry point).

    Args:
        agg: Scoped aggregation expression
        redefinitions: PartDef-level :>> redefinitions for CHAIN resolution
        output_registry: OutputRegistry for channel verification and lookup
        entry_points: Read-only dict of classified entry points
        group_deriver: For classifying new entry points (None in tests)
        expose_aliases: EXPOSE_PURE alias map for LocalTerm resolution
        usage_type_map: Maps (owning_partdef_qn, usage_name) → type_partdef_qn

    Returns:
        (PipelineModule, dict of new entry points created by this factory)
    """
    new_entry_points: dict[str, EntryPoint] = {}
    # Naming per ADR-003, using module_eqn property
    module_name = get_module_name(agg.module_eqn)
    module_type = derive_module_type(agg.module_eqn.replace("__", "::"))

    inputs: list[ModuleInput] = []
    ref_to_inputs: dict[str, str] = {}
    compilability = Compilability.FULLY_COMPILABLE

    if agg.expression.has_unsupported_nodes:
        compilability = Compilability.MANUAL_REQUIRED

    # Build the resolution context once for this aggregation. consumer_scope is
    # derived from module_eqn (drop the design prefix [0] and self [-1]); module_eqn
    # MUST be agg.module_eqn (INV-7) so the reconciled fallback key matches the live
    # part-usage-prefixed EP QN. design_attrs is unused by AGG_STRATEGIES.
    agg_parts = agg.module_eqn.split("__")
    ctx = ResolutionContext(
        output_registry=output_registry,
        redefinitions=redefinitions,
        design_attrs={},
        module_eqn=agg.module_eqn,
        consumer_scope=".".join(agg_parts[1:-1]) if len(agg_parts) >= 3 else "",
        instance_path=agg.instance_path,
    )
    owning_part_qn = agg.expression.owning_part_qn

    # Process SumTerms (array child costs with multiplicity)
    for term in agg.expression.sum_terms:
        symbolic_ref = f"{term.part_usage_name}.{term.attribute_name}"
        param_name = f"{term.part_usage_name}_{term.attribute_name}"

        source, manual_required = _build_agg_input_source(
            symbolic_ref, ctx, (term.part_usage_name, term.attribute_name),
            redefinitions, usage_type_map or {}, owning_part_qn,
            group_deriver, entry_points, new_entry_points,
        )
        if manual_required:
            logger.warning(
                "Aggregation SumTerm '%s' in '%s' unresolved → ENTRY_POINT",
                symbolic_ref, agg.instance_path,
            )
            compilability = Compilability.MANUAL_REQUIRED

        inputs.append(ModuleInput(
            param_name=param_name,
            python_type="float",
            source=source,
        ))
        ref_to_inputs[f"{term.part_usage_name}.{term.attribute_name}"] = f"inputs.{param_name}"

        # Multiplicity entry point
        if term.multiplicity_attr:
            mult_ep_qn = f"{agg.instance_path}__{term.multiplicity_attr}"
            if mult_ep_qn not in entry_points and mult_ep_qn not in new_entry_points:
                param_group = group_deriver.classify(mult_ep_qn) if group_deriver else None
                new_entry_points[mult_ep_qn] = EntryPoint(
                    qualified_name=mult_ep_qn,
                    simple_name=term.multiplicity_attr,
                    entry_type=EntryPointType.DESIGN_ATTRIBUTE,
                    default_value=(
                        float(term.multiplicity_count)
                        if term.multiplicity_count is not None
                        else None
                    ),
                    param_group=param_group,
                )
            ep = new_entry_points.get(mult_ep_qn) or entry_points[mult_ep_qn]
            inputs.append(ModuleInput(
                param_name=term.multiplicity_attr,
                python_type="float",
                source=InputSource(
                    source_type="entry_point",
                    qualified_name=mult_ep_qn,
                    param_group=ep.param_group,
                ),
            ))
            ref_to_inputs[term.multiplicity_attr] = f"inputs.{term.multiplicity_attr}"

    # Process SingletonTerms (non-multiplied child references)
    canonical_channels = output_registry.canonical_channels
    for s_term in agg.expression.singleton_terms:
        param_name = s_term.source_path.replace(".", "_")

        # The literal-default lookup uses the split source_path; a dotless singleton
        # has no part-usage to look up, so it skips the lookup (default stays None).
        literal_key: tuple[str, str] | None = None
        if "." in s_term.source_path:
            s_part_usage, s_attr = s_term.source_path.rsplit(".", 1)
            literal_key = (s_part_usage, s_attr)

        s_source, manual_required = _build_agg_input_source(
            s_term.source_path, ctx, literal_key,
            redefinitions, usage_type_map or {}, owning_part_qn,
            group_deriver, entry_points, new_entry_points,
        )
        if manual_required:
            logger.warning(
                "Aggregation SingletonTerm '%s' in '%s' unresolved → ENTRY_POINT",
                s_term.source_path, agg.instance_path,
            )
            compilability = Compilability.MANUAL_REQUIRED

        inputs.append(ModuleInput(
            param_name=param_name,
            python_type="float",
            source=s_source,
        ))
        ref_to_inputs[s_term.source_path] = f"inputs.{param_name}"

    # Process LocalTerms (PartDef-local attribute references)
    for l_term in agg.expression.local_terms:
        l_source: InputSource | None = None

        # Try: sibling aggregation output at the same scope.
        # Aggregation modules use double-attr channel format:
        #   get_channel_name("{instance_path}__{attr}", attr) → "{ip}__{attr}__{attr}"
        sibling_eqn = f"{agg.instance_path}__{l_term.attribute_name}"
        sibling_channel = get_channel_name(sibling_eqn, l_term.attribute_name)
        if sibling_channel in canonical_channels:
            l_source = InputSource(
                source_type="module_output",
                producer_channel=sibling_channel,
            )

        if l_source is None and expose_aliases:
            # Try: EXPOSE_PURE alias resolution.
            # e.g., misc_hardware_cost = allocation_model.total_allocation
            # The alias target is a dotted path resolve_input handles via its
            # scoped/chain/direct strategies. D5 guard: take the channel ONLY when
            # resolve_input returns a module_output — resolve_input keys its never-None
            # entry_point fallback on the alias target, not l_term.attribute_name, so an
            # entry_point result must fall through to LocalTerm's own fallback below
            # (which keeps the {module_eqn}__{attribute_name} key).
            alias_key = (agg.expression.owning_part_qn, l_term.attribute_name)
            alias_source = expose_aliases.get(alias_key)
            if alias_source:
                alias_resolved = resolve_input(alias_source, ctx, AGG_STRATEGIES)
                if alias_resolved.source_type == "module_output":
                    l_source = InputSource(
                        source_type="module_output",
                        producer_channel=alias_resolved.producer_channel,
                    )

        if l_source is None:
            # Genuinely unresolvable → entry point
            ep_qn = f"{agg.module_eqn}__{l_term.attribute_name}"
            if ep_qn not in entry_points and ep_qn not in new_entry_points:
                param_group = group_deriver.classify(ep_qn) if group_deriver else None
                new_entry_points[ep_qn] = EntryPoint(
                    qualified_name=ep_qn,
                    simple_name=l_term.attribute_name,
                    entry_type=EntryPointType.DESIGN_ATTRIBUTE,
                    param_group=param_group,
                )
            ep = new_entry_points.get(ep_qn) or entry_points[ep_qn]
            l_source = InputSource(
                source_type="entry_point",
                qualified_name=ep_qn,
                param_group=ep.param_group,
            )

        inputs.append(ModuleInput(
            param_name=l_term.attribute_name,
            python_type="float",
            source=l_source,
        ))
        ref_to_inputs[l_term.attribute_name] = f"inputs.{l_term.attribute_name}"

    # Compile expression: replace symbolic refs with inputs.X form
    compiled_expression: str | None = None
    if not agg.expression.has_unsupported_nodes and agg.expression.transformed_expression:
        compiled = agg.expression.transformed_expression
        for ref in sorted(ref_to_inputs, key=len, reverse=True):
            compiled = compiled.replace(ref, ref_to_inputs[ref])
        compiled_expression = compiled

    # Single output
    output = ModuleOutput(
        field_name="root",
        python_type="float",
        channel_name=get_channel_name(agg.module_eqn, agg.expression.attribute_name),
    )

    auto_impl_ctx = None
    if compilability == Compilability.FULLY_COMPILABLE and compiled_expression:
        auto_impl_ctx = _build_simple_auto_impl_context(
            compiled_expression, agg.expression.attribute_name,
        )

    return PipelineModule(
        name=module_name,
        module_type=module_type,
        inputs=inputs,
        outputs=[output],
        execution_order=0,  # Reassigned during unified toposort
        compilability=compilability,
        compiled_expression=compiled_expression,
        is_aggregation=True,
        auto_impl_context=auto_impl_ctx,
        calc_def_name=agg.expression.attribute_name,
        calc_def_qualified_name=agg.expression.owning_part_qn,
        calc_expressions=[agg.expression.raw_expression_text] if agg.expression.raw_expression_text else None,
        source_file=str(agg.expression.source_file),
        source_line=agg.expression.source_line,
    ), new_entry_points


def _unified_topological_sort(modules: list[PipelineModule]) -> list[PipelineModule]:
    """Sort all modules by their inter-module dependencies using Kahn's algorithm.

    Replaces the assumption that backtracker pre-sort is sufficient once
    computed attribute modules are interleaved with CalcUsage modules.

    Args:
        modules: All modules (CalcUsage + computed attribute)

    Returns:
        Modules sorted in dependency order with execution_order reassigned
    """
    if not modules:
        return modules

    # Build channel -> module_name lookup
    channel_to_module: dict[str, str] = {}
    for m in modules:
        for out in m.outputs:
            channel_to_module[out.channel_name] = m.name

    # Build adjacency list: module_name -> [dependency module names]
    graph: dict[str, list[str]] = {m.name: [] for m in modules}
    in_degree: dict[str, int] = {m.name: 0 for m in modules}

    for m in modules:
        for inp in m.inputs:
            if inp.source.source_type == "module_output" and inp.source.producer_channel:
                dep_module = channel_to_module.get(inp.source.producer_channel)
                if dep_module and dep_module != m.name:
                    if dep_module not in graph[m.name]:
                        graph[m.name].append(dep_module)
                        in_degree[m.name] += 1

    # Note: graph[m.name] lists dependencies (predecessors), not successors.
    # For Kahn's we need: for each dependency edge A->B (A must come before B),
    # track successors: which modules depend on each module.
    successors: dict[str, list[str]] = {m.name: [] for m in modules}
    for m_name, deps in graph.items():
        for dep in deps:
            successors[dep].append(m_name)

    # Kahn's algorithm
    queue: deque[str] = deque()
    for m_name, degree in in_degree.items():
        if degree == 0:
            queue.append(m_name)

    sorted_names: list[str] = []
    while queue:
        current = queue.popleft()
        sorted_names.append(current)
        for successor in successors[current]:
            in_degree[successor] -= 1
            if in_degree[successor] == 0:
                queue.append(successor)

    if len(sorted_names) != len(modules):
        # Identify the modules involved in the cycle
        cycle_modules = [m.name for m in modules if m.name not in sorted_names]
        raise CircularDependencyError(
            f"Circular dependency detected among modules: {cycle_modules}. "
            f"Sorted {len(sorted_names)} of {len(modules)} modules."
        )

    # Reassign execution_order
    name_to_order = {name: i for i, name in enumerate(sorted_names)}
    for m in modules:
        m.execution_order = name_to_order[m.name]

    return sorted(modules, key=lambda m: m.execution_order)


def _build_pipeline_module(
    usage: CalcUsageData,
    calc_def,
    entry_points: dict[str, EntryPoint],
    execution_order: int,
    binding_resolutions: dict[str, BindingResolution],
) -> tuple[PipelineModule, dict[str, EntryPoint]]:
    """Build a single PipelineModule from a CalcUsageData.

    ADR-003 Phase 7: Uses binding_resolutions as the SINGLE SOURCE OF TRUTH.
    NO FALLBACK - if resolution is missing, we fail fast with a clear error.

    For each input:
    - If resolution_type == MODULE_OUTPUT: wire to producer_channel
    - If resolution_type == ENTRY_POINT: wire to entry point

    For each output:
    - Build channel name as PQN format via get_channel_name()
    - field_name is "root" for single-output, attr.name for multi-output

    Args:
        usage: The calc usage to convert
        calc_def: Corresponding calc definition
        entry_points: Read-only dict of classified entry points
        execution_order: Position in topological order
        binding_resolutions: Unified mapping for ALL binding resolutions (REQUIRED).
            Maps "{usage_qn}|{param_name}" -> BindingResolution.

    Returns:
        (PipelineModule, dict of new entry points) — new_entry_points is always
        empty for CalcUsage factories (they never create EPs).

    Raises:
        ValueError: If binding resolution is missing (ADR-003 VIOLATION)
        ValueError: If entry point is missing (ADR-003 VIOLATION)
    """
    # ADR-003: Module name is EQN lowercased (guaranteed unique)
    module_name = get_module_name(usage.qualified_name)
    # ADR-003: Derive namespaced module_type from calc def qualified_name
    module_type = derive_module_type(calc_def.qualified_name)

    # Build inputs - ADR-003 Phase 7: FAIL FAST, NO FALLBACK
    inputs: list[ModuleInput] = []
    input_attr_by_name = {a.name: a for a in calc_def.input_attributes}
    for input_attr in calc_def.input_attributes:
        param_name = input_attr.name
        mapping_key = f"{usage.qualified_name}|{param_name}"

        source: InputSource

        # ADR-003 Phase 7: binding_resolutions is the SINGLE SOURCE OF TRUTH
        if mapping_key not in binding_resolutions:
            raise ValueError(
                f"ADR-003 VIOLATION: No binding resolution for '{mapping_key}'. "
                f"All input params must have a resolution in binding_resolutions. "
                f"Usage: {usage.instance_name}, CalcDef: {calc_def.name}"
            )

        resolution = binding_resolutions[mapping_key]

        if resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT:
            # Wire to upstream calc output
            source = InputSource(
                source_type="module_output",
                producer_channel=resolution.qualified_name,
            )
        elif resolution.resolution_type == BindingResolutionType.ENTRY_POINT:
            # Wire to entry point - ADR-003 Phase 7: entry point MUST exist
            ep = entry_points.get(resolution.qualified_name)
            if not ep:
                raise ValueError(
                    f"ADR-003 VIOLATION: Entry point '{resolution.qualified_name}' "
                    f"not found in entry_points dict. Mapping key: {mapping_key}. "
                    f"All resolved entry points must exist in the classified entry_points."
                )
            source = InputSource(
                source_type="entry_point",
                param_group=ep.param_group,
                qualified_name=resolution.qualified_name,
            )
        else:
            raise ValueError(f"Unknown resolution type: {resolution.resolution_type}")

        inputs.append(
            ModuleInput(
                param_name=param_name,
                python_type="float",  # All numeric for now
                source=source,
                description=input_attr.description,
                default_value=input_attr.default_value,
            )
        )

    # Build outputs
    outputs: list[ModuleOutput] = []
    is_multi_output = len(calc_def.output_attributes) > 1

    for output_attr in calc_def.output_attributes:
        # ADR-003: Channel name is PQN format
        channel_name = get_channel_name(usage.qualified_name, output_attr.name)
        field_name = output_attr.name if is_multi_output else "root"

        outputs.append(
            ModuleOutput(
                field_name=field_name,
                python_type="float",
                channel_name=channel_name,
                description=output_attr.description,
                default_value=output_attr.default_value,
                unit=output_attr.unit,
            )
        )

    return PipelineModule(
        name=module_name,
        module_type=module_type,
        inputs=inputs,
        outputs=outputs,
        execution_order=execution_order,
        calc_def_name=calc_def.name,
        calc_def_qualified_name=calc_def.qualified_name,
        doc_comment=calc_def.doc_comment,
        calc_expressions=calc_def.calc_expressions,
        source_file=str(calc_def.source_file),
        source_line=calc_def.source_line,
    ), {}


__all__ = [
    "AttributeResolution",
    "AttributeResolutionKind",
    "MissingCalcDefError",
    "UncoveredInput",
    "_build_aggregation_module",
    "_build_attribute_resolution_map",
    "_build_computed_attr_module",
    "_build_output_aliases",
    "_build_agg_input_source",
    "_find_literal_redefinition",
    "_resolve_expose_pure",
    "_unified_topological_sort",
    "build_computation_graph",
    "collect_uncovered_params",
    "collect_unwired_fallthrough",
]
