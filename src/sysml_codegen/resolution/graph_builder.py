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
from pathlib import Path

# UPDATED: Import from sysml_codegen package structure
from sysml_codegen.analysis.dependency_backtracker import BacktrackingResult
from sysml_codegen.analysis.parameter_groups import (
    DesignAttributeData,
    ParameterGroupDeriver,
)
from sysml_codegen.core.identifier_types import derive_module_type
from sysml_codegen.core.models import BindingResolution, BindingResolutionType
from sysml_codegen.core.qualified_names import get_channel_name, get_module_name
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
) -> ComputationGraph:
    """Build the complete computation graph from backtracking result.

    This is the SINGLE place where the pipeline structure is determined.
    No more redundant graph building in multiple places.

    Args:
        result: The BacktrackingResult from DependencyBacktracker
        calc_defs: All calculation definitions
        design_attrs: Design attributes by file
        group_deriver: Existing ParameterGroupDeriver for entry point grouping

    Returns:
        ComputationGraph ready for YAML and JSON generation
    """
    # Step 1: Build calc def lookup
    calc_def_map = {cd.name: cd for cd in calc_defs}

    # Step 2: Build output channel catalog
    # ADR-003: Module names use full EQN (guaranteed unique), no collision check needed
    # Uses backtracker's already-resolved bindings, just maps to channel names
    output_catalog = _build_output_catalog(result.required_usages, calc_def_map)

    # Step 3: Classify entry points with full context
    entry_points = _classify_entry_points(
        result.entry_points,
        result.entry_point_sources,
        design_attrs,
        result.required_usages,
        calc_def_map,
        group_deriver,
    )

    # Step 4: Group entry points using EXISTING ParameterGroupDeriver
    # This reuses the deriver's sophisticated grouping logic
    param_groups = _group_entry_points_via_deriver(
        entry_points=entry_points,
        group_deriver=group_deriver,
        backtracking_result=result,
        calc_defs=calc_defs,
    )

    # Step 5: Build pipeline modules from required_usages (already sorted!)
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
            output_catalog=output_catalog,
            entry_points=entry_points,
            param_groups=param_groups,
            execution_order=idx,
            binding_resolutions=result.binding_resolutions,
        )
        modules.append(module)

    # Step 6: Early validation - verify all channel references resolve
    # This catches transitive binding resolution bugs before TEAx validation
    _validate_channel_references(modules)

    return ComputationGraph(
        modules=modules,
        entry_point_groups=param_groups,
        execution_order=[m.name for m in modules],
    )


def _build_output_catalog(
    usages: list[CalcUsageData],
    calc_def_map: dict,
) -> dict[str, tuple[str, str, str]]:
    """Build catalog mapping binding sources to (module_name, channel_name, field_name).

    Key insight: The backtracker has ALREADY resolved which usages are in
    the required set and sorted them. We just need to build the channel
    name mapping for YAML generation.

    Args:
        usages: Required usages (already sorted by backtracker)
        calc_def_map: Calc def lookup by name

    Returns:
        Dict mapping source patterns to (module_name, channel_name, field_name):
        - "alpha_neutron_split.p_neutron" -> ("AlphaNeutronSplitModule", "..._p_neutron", "p_neutron")
        - For single-output modules, field_name is "root"
        - Qualified pattern also supported for disambiguation
    """
    catalog: dict[str, tuple[str, str, str]] = {}

    for usage in usages:
        calc_def = calc_def_map.get(usage.calc_def_name)
        if not calc_def:
            raise MissingCalcDefError(
                f"Usage '{usage.instance_name}' references calc def '{usage.calc_def_name}' "
                f"which was not found in calc_def_map. This indicates a model inconsistency."
            )

        # ADR-003: Derive namespaced module_type from calc def qualified_name
        module_type = derive_module_type(calc_def.qualified_name)

        # Determine if this is a single-output or multi-output module
        is_multi_output = len(calc_def.output_attributes) > 1

        for output_attr in calc_def.output_attributes:
            # ADR-003: Channel name is PQN format (usage EQN + output name)
            channel_name = get_channel_name(usage.qualified_name, output_attr.name)

            # Field name: "root" for single-output, attr.name for multi-output
            field_name = output_attr.name if is_multi_output else "root"

            # Key format matches binding.source_path from usage_extractor
            # (e.g., "alpha_neutron_split.p_neutron")
            key = f"{usage.instance_name}.{output_attr.name}"
            catalog[key] = (module_type, channel_name, field_name)

    return catalog


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

    # Convert DerivedParameterGroup -> ParameterGroup (Pydantic)
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


def _build_pipeline_module(
    usage: CalcUsageData,
    calc_def,
    output_catalog: dict[str, tuple[str, str, str]],
    entry_points: dict[str, EntryPoint],
    param_groups: list[ParameterGroup],
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
        output_catalog: Maps binding sources to (module_name, channel_name, field_name)
        entry_points: All classified entry points
        param_groups: All parameter groups (for finding group name)
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
    "MissingCalcDefError",
    "build_computation_graph",
]
