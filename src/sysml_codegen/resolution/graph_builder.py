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
from sysml_codegen.core.models import BindingResolution, BindingResolutionType
from sysml_codegen.core.qualified_names import (
    get_channel_name,
    get_module_name,
    sanitize_name,
    sysml_to_python_qualified_name,
)
from sysml_codegen.extraction.data_models import (
    ComputedAttributeClassification,
    ComputedAttributeData,
    RedefinitionData,
    RedefinitionType,
    ScopedAggregationData,
)
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.extraction.usage_extractor import CalcUsageData
from sysml_codegen.resolution.models import (
    ComputationGraph,
    EntryPoint,
    EntryPointType,
    InputSource,
    ModuleInput,
    ModuleOutput,
    ParameterGroup,
    PipelineModule,
)

logger = logging.getLogger(__name__)


class MissingCalcDefError(Exception):
    """Raised when a calc usage references a calc def that doesn't exist.

    This indicates a model inconsistency - every usage should have a matching definition.
    """

    pass


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

    # Step 5: Group entry points using EXISTING ParameterGroupDeriver
    # This reuses the deriver's sophisticated grouping logic
    param_groups = _group_entry_points_via_deriver(
        entry_points=entry_points,
        group_deriver=group_deriver,
        backtracking_result=result,
        calc_defs=calc_defs,
    )

    # Step 6: Build CalcUsage pipeline modules from required_usages
    modules = []
    for idx, usage in enumerate(result.required_usages):
        calc_def = calc_def_map.get(usage.calc_def_name)
        if not calc_def:
            raise MissingCalcDefError(
                f"Usage '{usage.instance_name}' references calc def '{usage.calc_def_name}' "
                f"which was not found in calc_defs. This indicates a model inconsistency."
            )

        module = _build_pipeline_module(
            usage=usage,
            calc_def=calc_def,
            entry_points=entry_points,
            execution_order=idx,
            binding_resolutions=result.binding_resolutions,
        )

        # Set compilability from compilation results
        if compilation_results and usage.calc_def_name in compilation_results:
            module.compilability = compilation_results[usage.calc_def_name].overall_compilability

        modules.append(module)

    # Step 6.5: Build computed attribute modules
    if computed_attributes:
        for ca in computed_attributes:
            if (
                ca.classification == ComputedAttributeClassification.FORMULA
                and ca.compilability == Compilability.FULLY_COMPILABLE
            ):
                module = _build_computed_attr_module(
                    ca, attr_resolution_map, entry_points,
                    design_attrs, group_deriver,
                )
                modules.append(module)

    # Step 6.6b: Build EXPOSE_PURE alias map for aggregation LocalTerm resolution.
    # Maps (owning_part_qn, python_name) -> expression_text (e.g., "allocation_model.total_allocation").
    # Used by _build_aggregation_module() to wire LocalTerms that are computed attribute aliases.
    # NOTE: ComputedAttributeData.owning_part_qualified_name uses "::" separator with raw names
    # (e.g., "SolarBatteryLibrary::'Solar Array'"), while AggregationExpressionData.owning_part_qn
    # uses "__" separator with sanitized names (e.g., "SolarBatteryLibrary__Solar_Array").
    # We normalize by splitting on "::", sanitizing each segment, and joining with "__".
    expose_aliases: dict[tuple[str, str], str] = {}
    for ca in (computed_attributes or []):
        if ca.classification == ComputedAttributeClassification.EXPOSE_PURE:
            segments = ca.owning_part_qualified_name.split("::")
            normalized_qn = "__".join(sanitize_name(seg) for seg in segments)
            expose_aliases[(normalized_qn, ca.python_name)] = ca.expression_text

    # Step 6.7: Build aggregation modules
    for agg in (aggregation_data or []):
        agg_module = _build_aggregation_module(
            agg, hierarchy_redefinitions or [], output_registry,
            entry_points, group_deriver, expose_aliases,
            usage_type_map or {},
        )
        modules.append(agg_module)

    # Step 6.6: Rebuild param_groups with ALL entry points
    # FORMULA modules (Step 6.5) and aggregation modules (Step 6.7) may have
    # added new entry points to the entry_points dict. Rebuild to include them.
    # param_groups is NOT used during module building (Steps 6 and 6.5 use
    # entry_points dict and group_deriver.classify() directly), so this is safe.
    all_ep_names = set(entry_points.keys())
    raw_groups = group_deriver.derive_groups()
    for group in raw_groups:
        group.parameters = [
            p for p in group.parameters
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

    # Step 7: Unified topological sort across ALL modules
    modules = _unified_topological_sort(modules)

    # Step 8: Early validation - verify all channel references resolve
    # This catches transitive binding resolution bugs before TEAx validation
    _validate_channel_references(modules)

    return ComputationGraph(
        modules=modules,
        entry_point_groups=param_groups,
        execution_order=[m.name for m in modules],
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
            if attr.default_value:
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


def _group_entry_points_via_deriver(
    entry_points: dict[str, EntryPoint],
    group_deriver: ParameterGroupDeriver,
    backtracking_result: BacktrackingResult,
    calc_defs: list,
) -> list[ParameterGroup]:
    """Use existing ParameterGroupDeriver for grouping, convert to Pydantic models.

    This reuses existing deriver logic instead of duplicating it.

    IMPORTANT: DerivedParameterGroup.parameters[].name contains QUALIFIED names
    (per ADR-001 Phase 2), so we can look up directly in entry_points dict.

    Note on source_file: dg.source_identifier is a filename like "physics.sysml",
    not a full path. We store it as-is since it's used for display/grouping,
    not file operations.

    Args:
        entry_points: Classified entry points by qualified name
        group_deriver: ParameterGroupDeriver instance
        backtracking_result: For filtering to true entry points
        calc_defs: Calculation definitions (for API compatibility)

    Returns:
        List of ParameterGroup Pydantic models
    """
    # Get derived groups (already filtered for entry points only)
    derived_groups = group_deriver.derive_groups_filtered(
        backtracking_result,
        calc_defs,
    )

    return _convert_derived_groups(derived_groups, entry_points)


def _convert_derived_groups(
    derived_groups: list,
    entry_points: dict[str, EntryPoint],
) -> list[ParameterGroup]:
    """Convert DerivedParameterGroup list to ParameterGroup Pydantic models.

    Shared by _group_entry_points_via_deriver (Step 5) and Step 6.6 rebuild.

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
            "EXPOSE_PURE %s: key '%s' not found in output registry",
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
    - EXPOSE_PURE computed attr -> kind="expose_alias", channel from upstream calc
    - Not found -> kind="literal" (conservative: becomes entry point)

    Args:
        computed_attrs: All computed attributes from Step 4.5
        design_attrs: Design attributes indexed by file
        output_registry: OutputRegistry for channel resolution
        calc_usage_names: CalcUsage instance names for EXPOSE_PURE resolution
    """
    result: dict[str, dict[str, AttributeResolution]] = {}

    for ca in computed_attrs:
        part_name = ca.owning_part_name
        if part_name not in result:
            result[part_name] = {}

        if (
            ca.classification == ComputedAttributeClassification.FORMULA
            and ca.compilability == Compilability.FULLY_COMPILABLE
        ):
            # FORMULA -> wire to synthetic module output channel
            sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
            module_eqn = sysml_to_python_qualified_name(sysml_qn)
            channel_name = get_channel_name(module_eqn, ca.python_name)
            result[part_name][ca.python_name] = AttributeResolution(
                kind=AttributeResolutionKind.FORMULA, channel_name=channel_name,
            )

        elif ca.classification == ComputedAttributeClassification.EXPOSE_PURE:
            # EXPOSE_PURE -> resolve through alias to upstream calc output
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

    return result


def _build_computed_attr_module(
    ca: ComputedAttributeData,
    resolution_map: dict[str, dict[str, AttributeResolution]],
    entry_points: dict[str, EntryPoint],
    design_attrs: dict[Path, list[DesignAttributeData]],
    group_deriver: ParameterGroupDeriver,
) -> PipelineModule:
    """Build a PipelineModule from a FORMULA ComputedAttributeData.

    Args:
        ca: The FORMULA computed attribute (must be FULLY_COMPILABLE)
        resolution_map: Per-part attribute resolution map
        entry_points: Mutable dict -- new entry points may be added
        design_attrs: Design attributes for default value lookup
        group_deriver: For classifying new entry points
    """
    # Naming per ADR-003
    sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
    module_eqn = sysml_to_python_qualified_name(sysml_qn)
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

    part_eqn = sysml_to_python_qualified_name(ca.owning_part_qualified_name)

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

            if ep_qname not in entry_points:
                # Look up default value from design attrs
                default_value: float | None = None
                da = design_attr_by_qname.get(ep_qname)
                if da and da.default_value:
                    try:
                        default_value = float(da.default_value)
                    except (ValueError, TypeError):
                        pass

                param_group = group_deriver.classify(ep_qname) if group_deriver else None

                entry_points[ep_qname] = EntryPoint(
                    qualified_name=ep_qname,
                    simple_name=input_name,
                    entry_type=EntryPointType.DESIGN_ATTRIBUTE,
                    default_value=default_value,
                    param_group=param_group,
                )

            ep = entry_points[ep_qname]
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
    )

    return PipelineModule(
        name=module_name,
        module_type=module_type,
        inputs=inputs,
        outputs=[output],
        execution_order=0,  # Assigned during unified toposort
        compilability=Compilability.FULLY_COMPILABLE,
        is_computed_attribute=True,
    )



def _resolve_aggregation_input_channel(
    symbolic_ref: str,
    instance_path: str,
    redefinitions: list[RedefinitionData],
    output_registry: OutputRegistry,
    _visited: set[str] | None = None,
) -> str | None:
    """Resolve a symbolic aggregation input to a pipeline channel name.

    Resolution chain:
    1. Parse "part_usage.attribute" from symbolic ref
    2. Find CHAIN :>> redefinition on child PartDef for that attribute
    3. Follow chain to CalcUsage output -> build pipeline channel name
    4. Fall back to output registry lookup

    Cycle detection: tracks visited (part_usage, attr) pairs. If a CHAIN
    redefinition leads back to an already-visited pair, logs a warning and
    returns None (caller should set MANUAL_REQUIRED compilability).

    Args:
        symbolic_ref: Dotted symbolic reference (e.g., "pv_module.capital_cost")
        instance_path: Design scope (e.g., "Design__plant__solar_array")
        redefinitions: PartDef-level :>> redefinitions
        output_registry: OutputRegistry for channel verification and lookup
        _visited: Internal cycle guard (set of visited keys)

    Returns:
        Pipeline channel name if resolved, None otherwise
    """
    if _visited is None:
        _visited = set()

    if "." not in symbolic_ref:
        return None  # LocalTerm -- handled as entry point, not channel

    part_usage, attr = symbolic_ref.rsplit(".", 1)

    # Cycle guard
    visit_key = f"{part_usage}.{attr}"
    if visit_key in _visited:
        logger.warning(
            "Circular CHAIN detected: %s already visited in %s", visit_key, _visited
        )
        return None
    _visited.add(visit_key)

    # Capture canonical channels once for O(1) membership checks
    canonical_channels = output_registry.canonical_channels

    # Find CHAIN redefinition for this attribute on the child PartDef
    chain_redef = None
    for redef in redefinitions:
        if redef.redefinition_type == RedefinitionType.CHAIN and redef.attribute_name == attr:
            # Extract part name from QN (last segment after __)
            redef_part_name = redef.owning_part_qn.split("__")[-1]
            if sanitize_name(redef_part_name).lower() == part_usage.lower():
                chain_redef = redef
                break

    if chain_redef and chain_redef.source_path:
        # Parse chain source "calc_usage.output"
        if "." in chain_redef.source_path:
            calc_usage, output = chain_redef.source_path.rsplit(".", 1)
            channel = get_channel_name(
                f"{instance_path}__{part_usage}__{calc_usage}", output
            )
            # Verify channel exists in registry
            if channel in canonical_channels:
                return channel
        # If channel not found or source has no dot, recurse with cycle guard
        return _resolve_aggregation_input_channel(
            chain_redef.source_path, instance_path, redefinitions,
            output_registry, _visited,
        )

    # Fall back to output registry lookup with scoped keys.
    # The instance_path provides full hierarchy scope; stripping the design
    # prefix (segments[0]) produces the dotted format that Phase 2 CHAIN
    # aliases and Phase 1b aggregation keys are registered under.
    instance_parts = instance_path.split("__")
    if len(instance_parts) > 1:
        dotted_scope = ".".join(instance_parts[1:])
        scoped_key = f"{dotted_scope}.{part_usage}.{attr}"
        channel = output_registry.scoped_lookup(ScopedKey(scoped_key))
        if channel is None:
            channel = output_registry.alias_lookup(ScopedKey(scoped_key))
        if channel is not None:
            logger.debug(
                "Aggregation input '%s.%s' resolved via scoped registry key '%s'",
                part_usage, attr, scoped_key,
            )
            return channel

    # Unscoped fallback (e.g., "solar_array.capital_cost")
    catalog_key = f"{part_usage}.{attr}"
    channel = output_registry.scoped_lookup(ScopedKey(catalog_key))
    if channel is None:
        channel = output_registry.alias_lookup(ScopedKey(catalog_key))
    if channel is not None:
        logger.debug(
            "Aggregation input '%s.%s' resolved via unscoped key '%s'",
            part_usage, attr, catalog_key,
        )
        return channel

    logger.debug(
        "Aggregation input '%s.%s' unresolved (tried scoped '%s', unscoped '%s')",
        part_usage, attr,
        f"{'.'.join(instance_parts[1:])}.{part_usage}.{attr}" if len(instance_parts) > 1 else "N/A",
        catalog_key,
    )
    return None


def _find_literal_redefinition(
    part_usage: str,
    attr: str,
    redefinitions: list[RedefinitionData],
    usage_type_map: dict[tuple[str, str], str] | None = None,
    owning_part_qn: str | None = None,
) -> float | None:
    """Find a LITERAL :>> redefinition value for a part usage attribute.

    Mirrors the CHAIN matching pattern in _resolve_aggregation_input_channel()
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

    for redef in redefinitions:
        if redef.redefinition_type == RedefinitionType.LITERAL and redef.attribute_name == attr:
            matched = False
            if target_partdef_qn is not None:
                # Strategy 1: exact PartDef QN match (handles aliased usage names)
                matched = redef.owning_part_qn == target_partdef_qn
            else:
                # Strategy 2: name-based fallback (last segment match)
                redef_part_name = redef.owning_part_qn.split("__")[-1]
                matched = sanitize_name(redef_part_name).lower() == part_usage.lower()

            if matched and redef.literal_value is not None:
                try:
                    return float(redef.literal_value)
                except (ValueError, TypeError):
                    return None
    return None


def _build_aggregation_module(
    agg: ScopedAggregationData,
    redefinitions: list[RedefinitionData],
    output_registry: OutputRegistry,
    entry_points: dict[str, EntryPoint],
    group_deriver: ParameterGroupDeriver | None,
    expose_aliases: dict[tuple[str, str], str] | None = None,
    usage_type_map: dict[tuple[str, str], str] | None = None,
) -> PipelineModule:
    """Build a PipelineModule from a ScopedAggregationData.

    Follows the _build_computed_attr_module() pattern. Creates inputs from
    SumTerms (channel + multiplicity EP), SingletonTerms (channel), and
    LocalTerms (entry point).

    Args:
        agg: Scoped aggregation expression
        redefinitions: PartDef-level :>> redefinitions for CHAIN resolution
        output_registry: OutputRegistry for channel verification and lookup
        entry_points: Mutable dict -- new entry points may be added
        group_deriver: For classifying new entry points (None in tests)
        expose_aliases: EXPOSE_PURE alias map for LocalTerm resolution
        usage_type_map: Maps (owning_partdef_qn, usage_name) → type_partdef_qn
    """
    # Naming per ADR-003, using module_eqn property
    module_name = get_module_name(agg.module_eqn)
    module_type = derive_module_type(
        f"{agg.expression.owning_part_qn}::{agg.expression.attribute_name}"
    )

    inputs: list[ModuleInput] = []
    ref_to_inputs: dict[str, str] = {}
    compilability = Compilability.FULLY_COMPILABLE

    if agg.expression.has_unsupported_nodes:
        compilability = Compilability.MANUAL_REQUIRED

    # Process SumTerms (array child costs with multiplicity)
    for term in agg.expression.sum_terms:
        symbolic_ref = f"{term.part_usage_name}.{term.attribute_name}"
        param_name = f"{term.part_usage_name}_{term.attribute_name}"

        channel = _resolve_aggregation_input_channel(
            symbolic_ref, agg.instance_path, redefinitions, output_registry,
        )

        if channel:
            source = InputSource(
                source_type="module_output",
                producer_channel=channel,
            )
        else:
            # Check for LITERAL :>> redefinition before falling back (defensive).
            literal_default = _find_literal_redefinition(
                term.part_usage_name, term.attribute_name, redefinitions,
                usage_type_map, agg.expression.owning_part_qn,
            )

            if literal_default is None:
                logger.warning(
                    "Aggregation SumTerm '%s' in '%s' unresolved → ENTRY_POINT",
                    symbolic_ref, agg.instance_path,
                )
                compilability = Compilability.MANUAL_REQUIRED

            ep_qn = f"{agg.module_eqn}__{param_name}"
            if ep_qn not in entry_points:
                param_group = group_deriver.classify(ep_qn) if group_deriver else None
                entry_points[ep_qn] = EntryPoint(
                    qualified_name=ep_qn,
                    simple_name=param_name,
                    entry_type=EntryPointType.DESIGN_ATTRIBUTE,
                    default_value=literal_default,
                    param_group=param_group,
                )
            elif literal_default is not None and entry_points[ep_qn].default_value is None:
                ep = entry_points[ep_qn]
                entry_points[ep_qn] = EntryPoint(
                    qualified_name=ep.qualified_name,
                    simple_name=ep.simple_name,
                    entry_type=ep.entry_type,
                    default_value=literal_default,
                    source_calc_usage=ep.source_calc_usage,
                    param_group=ep.param_group,
                )
            source = InputSource(
                source_type="entry_point",
                qualified_name=ep_qn,
                param_group=entry_points[ep_qn].param_group,
            )

        inputs.append(ModuleInput(
            param_name=param_name,
            python_type="float",
            source=source,
        ))
        ref_to_inputs[f"{term.part_usage_name}.{term.attribute_name}"] = f"inputs.{param_name}"

        # Multiplicity entry point
        if term.multiplicity_attr:
            mult_ep_qn = f"{agg.instance_path}__{term.multiplicity_attr}"
            if mult_ep_qn not in entry_points:
                param_group = group_deriver.classify(mult_ep_qn) if group_deriver else None
                entry_points[mult_ep_qn] = EntryPoint(
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
            ep = entry_points[mult_ep_qn]
            inputs.append(ModuleInput(
                param_name=term.multiplicity_attr,
                python_type="int",
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

        s_source: InputSource | None = None
        if "." in s_term.source_path:
            # Try 1: Registry-first resolution (handles both CalcUsage and
            # aggregation targets via Phase 1/2 keys and aliases).
            resolved = _resolve_aggregation_input_channel(
                s_term.source_path, agg.instance_path, redefinitions, output_registry,
            )
            if resolved:
                s_source = InputSource(
                    source_type="module_output",
                    producer_channel=resolved,
                )
            else:
                # Try 2: Direct channel construction (CalcUsage targets only).
                # Builds instance_path__prefix__output_name — correct for CalcUsage
                # EQN format but wrong for aggregation outputs (double-attr).
                prefix, output_name = s_term.source_path.rsplit(".", 1)
                calc_path = prefix.replace(".", "__")
                channel = get_channel_name(
                    f"{agg.instance_path}__{calc_path}", output_name,
                )
                if channel in canonical_channels:
                    s_source = InputSource(
                        source_type="module_output",
                        producer_channel=channel,
                    )

        if s_source is None:
            # Check for LITERAL :>> redefinition before falling back to entry point.
            # e.g., Permitting defines `:>> raw_material_cost = 0.0` — the value
            # becomes the entry point default so the JSON template is pre-populated.
            literal_default: float | None = None
            if "." in s_term.source_path:
                s_part_usage, s_attr = s_term.source_path.rsplit(".", 1)
                literal_default = _find_literal_redefinition(
                    s_part_usage, s_attr, redefinitions,
                    usage_type_map, agg.expression.owning_part_qn,
                )

            if literal_default is None:
                logger.warning(
                    "Aggregation SingletonTerm '%s' in '%s' unresolved → ENTRY_POINT",
                    s_term.source_path, agg.instance_path,
                )
                compilability = Compilability.MANUAL_REQUIRED

            ep_qn = f"{agg.module_eqn}__{param_name}"
            if ep_qn not in entry_points:
                param_group = group_deriver.classify(ep_qn) if group_deriver else None
                entry_points[ep_qn] = EntryPoint(
                    qualified_name=ep_qn,
                    simple_name=param_name,
                    entry_type=EntryPointType.DESIGN_ATTRIBUTE,
                    default_value=literal_default,
                    param_group=param_group,
                )
            elif literal_default is not None and entry_points[ep_qn].default_value is None:
                # Backfill default if entry point was created earlier without it
                ep = entry_points[ep_qn]
                entry_points[ep_qn] = EntryPoint(
                    qualified_name=ep.qualified_name,
                    simple_name=ep.simple_name,
                    entry_type=ep.entry_type,
                    default_value=literal_default,
                    source_calc_usage=ep.source_calc_usage,
                    param_group=ep.param_group,
                )
            s_source = InputSource(
                source_type="entry_point",
                qualified_name=ep_qn,
                param_group=entry_points[ep_qn].param_group,
            )

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
            # The expression_text is a dotted path that _resolve_aggregation_input_channel
            # already handles via scoped/unscoped registry lookups.
            alias_key = (agg.expression.owning_part_qn, l_term.attribute_name)
            alias_source = expose_aliases.get(alias_key)
            if alias_source:
                channel = _resolve_aggregation_input_channel(
                    alias_source, agg.instance_path,
                    redefinitions, output_registry,
                )
                if channel:
                    l_source = InputSource(
                        source_type="module_output",
                        producer_channel=channel,
                    )

        if l_source is None:
            # Genuinely unresolvable → entry point
            ep_qn = f"{agg.module_eqn}__{l_term.attribute_name}"
            if ep_qn not in entry_points:
                param_group = group_deriver.classify(ep_qn) if group_deriver else None
                entry_points[ep_qn] = EntryPoint(
                    qualified_name=ep_qn,
                    simple_name=l_term.attribute_name,
                    entry_type=EntryPointType.DESIGN_ATTRIBUTE,
                    param_group=param_group,
                )
            ep = entry_points[ep_qn]
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

    return PipelineModule(
        name=module_name,
        module_type=module_type,
        inputs=inputs,
        outputs=[output],
        execution_order=0,  # Reassigned during unified toposort
        compilability=compilability,
        compiled_expression=compiled_expression,
        is_aggregation=True,
    )


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
) -> PipelineModule:
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
        entry_points: All classified entry points
        execution_order: Position in topological order
        binding_resolutions: Unified mapping for ALL binding resolutions (REQUIRED).
            Maps "{usage_qn}|{param_name}" -> BindingResolution.

    Returns:
        PipelineModule ready for YAML rendering

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
            )
        )

    return PipelineModule(
        name=module_name,
        module_type=module_type,
        inputs=inputs,
        outputs=outputs,
        execution_order=execution_order,
    )


__all__ = [
    "AttributeResolution",
    "AttributeResolutionKind",
    "MissingCalcDefError",
    "_build_aggregation_module",
    "_build_attribute_resolution_map",
    "_build_computed_attr_module",
    "_find_literal_redefinition",
    "_resolve_aggregation_input_channel",
    "_resolve_expose_pure",
    "_unified_topological_sort",
    "build_computation_graph",
]
