"""Extract calculation usages from SysML models with binding awareness.

This module provides structured extraction of CalculationUsage elements from
SysML v2 models, capturing comprehensive binding information for code generation.

Key features:
- Binding expression type tracking (chain, reference, literal, unbound)
- Cross-file reference detection via AST document URL comparison
- Unbound parameter identification for entry point candidates
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.helpers import (
    get_calc_def_name,
    get_document_url,
    get_source_location,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter

# CRITICAL: Import shared types from agentic-mbse
from agentic_mbse.sysml.types import BindingType

from sysml_codegen.core.qualified_names import (
    build_element_qualified_name,
    sanitize_name,
)
from sysml_codegen.core.identifier_types import derive_module_type
from sysml_codegen.extraction.expression_utils import (
    is_literal_expression as _is_literal_expression,
    extract_literal_value as _extract_literal_value,
)

logger = logging.getLogger(__name__)

__all__ = [
    "BindingType",  # Re-export from agentic-mbse
    "BindingInfo",
    "CalcUsageData",
    "ExtractionReport",
    "extract_calculation_usages",
]


@dataclass
class BindingInfo:
    """Information about a parameter binding.

    Attributes:
        param_name: Simple name of the bound parameter
        source_path: The binding source path
        binding_type: Classification of the binding expression
        is_cross_file: True if binding references element in different file
        raw_expression: Original expression text for debugging
        source_instance_elem: AST element for instance (CHAIN bindings)
        source_attribute_elem: AST element for attribute
        literal_value: Parsed literal value (LITERAL bindings)
    """

    param_name: str
    source_path: str | None  # None if unbound
    binding_type: BindingType
    is_cross_file: bool = False
    raw_expression: str = ""
    source_instance_elem: object | None = None
    source_attribute_elem: object | None = None
    literal_value: float | int | str | bool | None = None

    # Raw AST node for EXPRESSION bindings (Phase 2 will use this)
    expression_ast: Any = None

    @property
    def source_instance_name(self) -> str | None:
        """Get name of source instance element if available."""
        if self.source_instance_elem and hasattr(self.source_instance_elem, "name"):
            return self.source_instance_elem.name
        return None

    @property
    def source_attribute_name(self) -> str | None:
        """Get name of source attribute element if available."""
        if self.source_attribute_elem and hasattr(self.source_attribute_elem, "name"):
            return self.source_attribute_elem.name
        return None


@dataclass
class CalcUsageData:
    """Enhanced calculation usage data with binding metadata.

    Attributes:
        instance_name: Instance name (e.g., "net_electric")
        calc_def_name: Calculation definition name (e.g., "NetElectricPower")
        calc_def_qualified_name: Full SysML qualified name of the calc def
        module_type: Namespaced module type for registry lookup
        bindings: List of BindingInfo for each parameter binding
        unbound_params: List of parameter names without bindings (entry points)
        source_file: Path to source SysML file
        source_line: Line number in source file
        parent_part_path: Dot-separated path of parent parts
        qualified_name: Full qualified path with __ separator
    """

    instance_name: str
    calc_def_name: str
    calc_def_qualified_name: str
    module_type: str
    bindings: list[BindingInfo] = field(default_factory=list)
    unbound_params: list[str] = field(default_factory=list)
    source_file: Path = field(default_factory=lambda: Path("unknown"))
    source_line: int = 0
    parent_part_path: str = ""
    qualified_name: str = ""
    # Template detection fields (COST-PATTERN Item 2)
    is_template: bool = False
    owning_part_def_qn: str | None = None
    raw_element: object | None = None

    @property
    def parameter_bindings(self) -> dict[str, str]:
        """Backward-compatible dict of param_name -> source_path."""
        return {b.param_name: b.source_path for b in self.bindings if b.source_path}

    @property
    def has_cross_file_bindings(self) -> bool:
        """True if any binding references a cross-file element."""
        return any(b.is_cross_file for b in self.bindings)


@dataclass
class ExtractionReport:
    """Statistics from usage extraction."""

    total_usages: int
    total_bindings: int
    unbound_params: int
    cross_file_bindings: int
    warnings: list[str] = field(default_factory=list)


def _build_part_usage_index(model: Any) -> dict[str, list[Any]]:
    """Build index mapping PartDef qualified names to their PartUsage elements.

    Iterates all PartUsage elements in the model. For each, resolves its
    typed PartDefinition via ``usage.types``, computes the PartDef's qualified
    name, and indexes the PartUsage under that key.

    Args:
        model: Parsed SysIDE model.

    Returns:
        Dict mapping PartDef QN to list of PartUsage AST elements.
    """
    from collections import defaultdict

    index: dict[str, list[Any]] = defaultdict(list)

    for usage in SysideAdapter.elements_of_type(model, "PartUsage"):
        try:
            part_def = next(iter(usage.types))
        except (StopIteration, TypeError, AttributeError):
            continue
        part_def_qn = build_element_qualified_name(part_def)
        if part_def_qn:
            index[part_def_qn].append(usage)

    return dict(index)


def _find_instantiation_paths(
    target_part_def_qn: str,
    part_usage_index: dict[str, list[Any]],
    _visited: set[str] | None = None,
) -> list[str]:
    """Find all design-relative qualified paths to PartUsages of a target PartDef.

    Recursively resolves the instantiation chain from design root through
    intermediate PartDefs to the target. Returns fully qualified paths using
    the ``__`` separator per ADR-003.

    Args:
        target_part_def_qn: QN of the PartDef to find instantiation paths for.
        part_usage_index: Prebuilt index from :func:`_build_part_usage_index`.
        _visited: Recursion guard set (internal).

    Returns:
        List of design-relative qualified name prefixes (deduplicated).
    """
    if _visited is None:
        _visited = set()

    if target_part_def_qn in _visited:
        return []
    _visited = _visited | {target_part_def_qn}

    usages = part_usage_index.get(target_part_def_qn, [])
    if not usages:
        return []

    seen_paths: set[str] = set()
    result: list[str] = []

    for usage in usages:
        owning_type = getattr(usage, "owning_type", None)
        if owning_type is not None and SysideAdapter.is_instance(
            owning_type, "PartDefinition"
        ):
            # PartUsage inside another PartDef → recurse
            parent_def_qn = build_element_qualified_name(owning_type)
            parent_paths = _find_instantiation_paths(
                parent_def_qn, part_usage_index, _visited
            )
            usage_name = sanitize_name(getattr(usage, "name", ""))
            for parent_path in parent_paths:
                path = f"{parent_path}__{usage_name}"
                if path not in seen_paths:
                    seen_paths.add(path)
                    result.append(path)
        else:
            # Terminal node: owned by Package, PartUsage, or other non-PartDef
            path = build_element_qualified_name(usage)
            if path and path not in seen_paths:
                seen_paths.add(path)
                result.append(path)

    return result


def _create_virtual_calc_usage(
    template: CalcUsageData,
    instantiation_path: str,
) -> CalcUsageData:
    """Create a virtual CalcUsage for a specific instantiation path.

    Args:
        template: The template CalcUsageData from the PartDefinition.
        instantiation_path: Full design-relative path to the PartUsage.

    Returns:
        New CalcUsageData with design-relative qualified name and
        bindings copied from the template.
    """
    calc_name = sanitize_name(template.instance_name)
    qualified_name = f"{instantiation_path}__{calc_name}"

    # Build dot-separated parent_part_path from the instantiation path
    path_segments = instantiation_path.split("__")
    part_segments = path_segments[1:] if len(path_segments) > 1 else path_segments
    parent_part_path = ".".join(part_segments)

    return CalcUsageData(
        instance_name=qualified_name,
        calc_def_name=template.calc_def_name,
        calc_def_qualified_name=template.calc_def_qualified_name,
        module_type=template.module_type,
        bindings=list(template.bindings),
        unbound_params=list(template.unbound_params),
        source_file=template.source_file,
        source_line=template.source_line,
        parent_part_path=parent_part_path,
        qualified_name=qualified_name,
        is_template=False,
        owning_part_def_qn=template.owning_part_def_qn,
        raw_element=template.raw_element,
    )


def _expand_template_calc_usages(
    model: Any,
    calc_usages: list[CalcUsageData],
    warnings: list[str],
) -> list[CalcUsageData]:
    """Replace template CalcUsages with virtual per-instance CalcUsages.

    Args:
        model: Parsed SysIDE model.
        calc_usages: Extracted CalcUsages (may include templates).
        warnings: List to append warnings to.

    Returns:
        Expanded list: concrete CalcUsages unchanged, templates replaced
        by virtual instances (one per PartUsage instantiation).
    """
    index = _build_part_usage_index(model)

    concrete: list[CalcUsageData] = []
    templates: list[CalcUsageData] = []
    for usage in calc_usages:
        if usage.is_template:
            templates.append(usage)
        else:
            concrete.append(usage)

    if templates:
        template_count = len(templates)
        logger.info(
            "Template detection: %d templates, %d concrete CalcUsages",
            template_count,
            len(concrete),
        )

    virtual_usages: list[CalcUsageData] = []
    seen_qns: set[str] = set()

    for template in templates:
        if not template.owning_part_def_qn:
            msg = (
                f"Template CalcUsage '{template.instance_name}' "
                f"has is_template=True but no owning_part_def_qn — skipped"
            )
            logger.warning(msg)
            warnings.append(msg)
            continue
        paths = _find_instantiation_paths(template.owning_part_def_qn, index)
        if not paths:
            msg = (
                f"Template CalcUsage '{template.instance_name}' "
                f"(PartDef '{template.owning_part_def_qn}') has no "
                f"PartUsage instantiations — dropped"
            )
            logger.warning(msg)
            warnings.append(msg)
            continue

        for path in paths:
            virtual = _create_virtual_calc_usage(template, path)
            if virtual.qualified_name not in seen_qns:
                seen_qns.add(virtual.qualified_name)
                virtual_usages.append(virtual)

    if virtual_usages:
        logger.info(
            "Template expansion: %d templates → %d virtual instances",
            len(templates),
            len(virtual_usages),
        )

    return concrete + virtual_usages


def extract_calculation_usages(
    model: Any,
    known_calc_defs: set[str] | None = None,
    calc_defs: list | None = None,
    expand_templates: bool = True,
) -> tuple[list[CalcUsageData], ExtractionReport]:
    """Extract all calculation usages from a SysML model.

    Args:
        model: Parsed SysIDE model
        known_calc_defs: Set of known calc def names for validation (optional)
        calc_defs: List of CalculationDefinitionData for detecting algorithm params
        expand_templates: If True, replace template CalcUsages (owned by PartDefs)
            with virtual per-instance CalcUsages. Default True.

    Returns:
        Tuple of (list of CalcUsageData, ExtractionReport with statistics)
    """
    usages: list[CalcUsageData] = []
    warnings: list[str] = []

    calc_def_map: dict[str, object] = {}
    if calc_defs:
        calc_def_map = {cd.name: cd for cd in calc_defs}

    for elem in SysideAdapter.elements_of_type(model, "CalculationUsage"):
        usage_data = _extract_single_usage(elem, known_calc_defs, warnings, calc_def_map)
        if usage_data:
            usages.append(usage_data)

    if expand_templates:
        usages = _expand_template_calc_usages(model, usages, warnings)

    report = ExtractionReport(
        total_usages=len(usages),
        total_bindings=sum(len(u.bindings) for u in usages),
        unbound_params=sum(len(u.unbound_params) for u in usages),
        cross_file_bindings=sum(1 for u in usages for b in u.bindings if b.is_cross_file),
        warnings=warnings,
    )

    return usages, report


def _extract_single_usage(
    elem: Any,
    known_calc_defs: set[str] | None,
    warnings: list[str],
    calc_def_map: dict[str, object] | None = None,
) -> CalcUsageData | None:
    """Extract data from a single CalculationUsage element."""
    instance_name = sanitize_name(elem.name)
    if not instance_name:
        return None

    calc_def_name = sanitize_name(get_calc_def_name(elem))
    if not calc_def_name:
        warnings.append(f"Could not resolve calc def for usage '{instance_name}'")
        return None

    if known_calc_defs and calc_def_name not in known_calc_defs:
        warnings.append(
            f"Calc usage '{instance_name}' references unknown calc def '{calc_def_name}'"
        )

    # Get calc def qualified name from map
    if not calc_def_map or calc_def_name not in calc_def_map:
        warnings.append(f"Calc def '{calc_def_name}' not found in calc_def_map")
        calc_def_qualified_name = calc_def_name
        module_type = f"{calc_def_name}Module"
    else:
        calc_def = calc_def_map[calc_def_name]
        calc_def_qualified_name = getattr(calc_def, 'qualified_name', calc_def_name)
        module_type = derive_module_type(calc_def_qualified_name)

    source_file, source_line = get_source_location(elem)
    parent_part_path = _get_parent_part_path(elem)
    qualified_name = build_element_qualified_name(elem)

    bindings, unbound_params = _extract_bindings(elem, instance_name, warnings)

    # Detect algorithm params
    if calc_def_map and calc_def_name in calc_def_map:
        calc_def = calc_def_map[calc_def_name]
        expected_inputs: set[str] = set()
        if hasattr(calc_def, 'input_attributes'):
            for attr in calc_def.input_attributes:
                if hasattr(attr, 'name') and attr.name:
                    expected_inputs.add(attr.name)

        declared_params = {b.param_name for b in bindings}
        algorithm_params = expected_inputs - declared_params

        if algorithm_params:
            unbound_params.extend(sorted(algorithm_params))

    # Template detection: check if owning type is PartDefinition
    owning_type = getattr(elem, "owning_type", None)
    is_template = False
    owning_part_def_qn = None
    if owning_type is not None and SysideAdapter.is_instance(
        owning_type, "PartDefinition"
    ):
        is_template = True
        owning_part_def_qn = build_element_qualified_name(owning_type)

    return CalcUsageData(
        instance_name=instance_name,
        calc_def_name=calc_def_name,
        calc_def_qualified_name=calc_def_qualified_name,
        module_type=module_type,
        bindings=bindings,
        unbound_params=unbound_params,
        source_file=source_file,
        source_line=source_line,
        parent_part_path=parent_part_path,
        qualified_name=qualified_name,
        is_template=is_template,
        owning_part_def_qn=owning_part_def_qn,
        raw_element=elem,
    )


def _extract_bindings(
    elem: Any,
    instance_name: str,
    warnings: list[str],
) -> tuple[list[BindingInfo], list[str]]:
    """Extract all parameter bindings from a calc usage."""
    bindings: list[BindingInfo] = []
    unbound_params: list[str] = []

    if not hasattr(elem, "owned_members"):
        return bindings, unbound_params

    for member in elem.owned_members:
        if not (
            SysideAdapter.is_instance(member, "AttributeUsage")
            or SysideAdapter.is_instance(member, "ReferenceUsage")
        ):
            continue

        if not _is_input_parameter(member):
            continue

        param_name = sanitize_name(member.name)
        if not param_name:
            continue

        binding_info = _extract_single_binding(elem, member, param_name)

        if binding_info.binding_type == BindingType.UNBOUND:
            unbound_params.append(param_name)
        else:
            bindings.append(binding_info)

    return bindings, unbound_params


def _extract_single_binding(
    usage_elem: Any,
    param_elem: Any,
    param_name: str,
) -> BindingInfo:
    """Extract binding info from a single parameter element."""
    if (
        not hasattr(param_elem, "feature_value_expression")
        or not param_elem.feature_value_expression
    ):
        return BindingInfo(
            param_name=param_name,
            source_path=None,
            binding_type=BindingType.UNBOUND,
        )

    expr = param_elem.feature_value_expression

    # FeatureChainExpression MUST be before OperatorExpression -- FCE is a
    # subtype of OE in SysIDE's type system (doc 19 invariant).
    if SysideAdapter.is_instance(expr, "FeatureChainExpression"):
        source_path, instance_elem, target_elem = _parse_chain_expression(expr)
        is_cross_file = _detect_cross_file_reference(usage_elem, instance_elem)
        return BindingInfo(
            param_name=param_name,
            source_path=source_path,
            binding_type=BindingType.CHAIN,
            is_cross_file=is_cross_file,
            raw_expression=f"FeatureChainExpression -> {source_path}",
            source_instance_elem=instance_elem,
            source_attribute_elem=target_elem,
        )

    elif SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
        source_path, referenced_elem = _parse_reference_expression(expr)
        is_cross_file = _detect_cross_file_reference(usage_elem, referenced_elem)
        return BindingInfo(
            param_name=param_name,
            source_path=source_path,
            binding_type=BindingType.REFERENCE,
            is_cross_file=is_cross_file,
            raw_expression=f"FeatureReferenceExpression -> {source_path}",
            source_attribute_elem=referenced_elem,
        )

    elif _is_literal_expression(expr):
        literal_value = _extract_literal_value(expr)
        return BindingInfo(
            param_name=param_name,
            source_path=str(literal_value) if literal_value is not None else None,
            binding_type=BindingType.LITERAL,
            is_cross_file=False,
            raw_expression=f"LiteralExpression -> {literal_value}",
            literal_value=literal_value,
        )

    elif SysideAdapter.is_instance(expr, "OperatorExpression"):
        return BindingInfo(
            param_name=param_name,
            source_path=None,
            binding_type=BindingType.EXPRESSION,
            raw_expression=f"OperatorExpression: {type(expr).__name__}",
            expression_ast=expr,
        )

    return BindingInfo(
        param_name=param_name,
        source_path=None,
        binding_type=BindingType.UNBOUND,
        raw_expression=f"Unknown expression type: {type(expr).__name__}",
    )


def _parse_chain_expression(
    expr: Any,
) -> tuple[str | None, object | None, object | None]:
    """Parse FeatureChainExpression to extract binding path and elements."""
    path_parts: list[str] = []
    instance_elem = None
    target_elem = None

    operands = list(expr.operands)
    if operands:
        first_operand = operands[0]
        if SysideAdapter.is_instance(first_operand, "FeatureReferenceExpression"):
            _, instance_elem = _parse_reference_expression(first_operand)
            if instance_elem and hasattr(instance_elem, "name") and instance_elem.name:
                path_parts.append(instance_elem.name)

    if hasattr(expr, "target_feature") and expr.target_feature:
        target = expr.target_feature
        if hasattr(target, "name") and target.name:
            path_parts.append(target.name)
            target_elem = target

    source_path = ".".join(path_parts) if path_parts else None
    return source_path, instance_elem, target_elem


def _parse_reference_expression(
    expr: Any,
) -> tuple[str | None, object | None]:
    """Parse FeatureReferenceExpression to extract qualified path and element."""
    if not SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
        return None, None

    if not hasattr(expr, "referent") or expr.referent is None:
        return None, None

    referent = expr.referent
    qname = getattr(referent, "qualified_name", None)

    if not qname:
        return None, None

    return str(qname), referent


def _detect_cross_file_reference(
    usage_elem: Any,
    referenced_elem: object | None,
) -> bool:
    """Detect if a binding references an element in a different file."""
    if not referenced_elem:
        return False

    usage_doc_url = get_document_url(usage_elem)
    if not usage_doc_url:
        return False

    ref_doc_url = get_document_url(referenced_elem)
    if not ref_doc_url:
        return False

    return usage_doc_url != ref_doc_url


def _is_input_parameter(member: Any) -> bool:
    """Check if member is an input parameter."""
    if not hasattr(member, "direction"):
        return False
    direction_str = str(member.direction)
    return "In" in direction_str or "inout" in direction_str.lower()


def _get_parent_part_path(elem: Any) -> str:
    """Get parent part path for nested calc usages."""
    parts: list[str] = []
    current = elem

    while hasattr(current, "owner") and current.owner:
        owner = current.owner
        if hasattr(owner, "owning_related_element"):
            owning_elem = owner.owning_related_element
            if owning_elem and hasattr(owning_elem, "name") and owning_elem.name:
                if SysideAdapter.is_instance(owning_elem, "PartUsage"):
                    parts.insert(0, owning_elem.name)
        current = owner

    return ".".join(parts)


