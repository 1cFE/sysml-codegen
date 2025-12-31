"""Automated parameter group derivation from SysML models.

RENAMED: This was scripts/codegen/parameter_group_derivation.py.

This module extracts design attributes with default values from SysML design files
and derives parameter groups for code generation.
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from agentic_mbse.sysml.expression import evaluate_true_static_expression
from agentic_mbse.sysml.helpers import (
    get_parent_part_name,
    get_source_file,
    get_source_location,
)

# CRITICAL: Import from agentic-mbse, NOT direct syside import
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.core.qualified_names import (
    build_element_qualified_name,
    sanitize_name,
    sysml_to_python_qualified_name,
)

logger = logging.getLogger(__name__)

__all__ = [
    "DesignAttributeData",
    "ParameterSource",
    "DerivedParameterGroup",
    "ParameterGroupDeriver",
    "extract_design_attributes",
    "collect_entry_point_attributes",
]


# ============== Data Structures ==============


@dataclass
class DesignAttributeData:
    """Attribute with default value from a design file."""

    name: str
    sysml_type: str
    default_value: str | None
    unit: str | None
    source_file: Path
    source_line: int
    parent_part: str
    qualified_name: str = ""


@dataclass
class ParameterSource:
    """Classification of a parameter's source for grouping."""

    name: str
    source_type: Literal["design", "library"] = "design"
    source_file: str = ""
    default_value: float | None = None
    calc_def: str = ""
    sysml_type: str = "Real"
    description: str = ""


@dataclass
class DerivedParameterGroup:
    """Auto-derived parameter group for code generation."""

    name: str
    class_name: str
    source_type: Literal["design", "library"]
    source_identifier: str
    parameters: list[ParameterSource] = field(default_factory=list)


# ============== Design Attribute Extraction ==============


def extract_design_attributes(
    model: Any,
    design_path_filter: str = "models/designs",
) -> dict[Path, list[DesignAttributeData]]:
    """Extract all attributes with default values from DESIGN files only.

    Args:
        model: Parsed SysIDE model
        design_path_filter: Path substring to filter design files

    Returns:
        Dict mapping source file Path to list of DesignAttributeData
    """
    attrs_by_file: dict[Path, list[DesignAttributeData]] = {}

    for elem in SysideAdapter.elements_of_type(model, "AttributeUsage"):
        if not hasattr(elem, "feature_value_expression"):
            continue
        if not elem.feature_value_expression:
            continue

        if design_path_filter:
            source_file = get_source_file(elem)
            if design_path_filter not in str(source_file):
                continue

        attr_data = _extract_single_attribute(elem)
        if attr_data is None:
            continue

        if attr_data.source_file not in attrs_by_file:
            attrs_by_file[attr_data.source_file] = []
        attrs_by_file[attr_data.source_file].append(attr_data)

    total_attrs = sum(len(attrs) for attrs in attrs_by_file.values())
    logger.info(
        f"Extracted {total_attrs} design attributes from {len(attrs_by_file)} files "
        f"(filter: '{design_path_filter}')"
    )

    return attrs_by_file


def _extract_single_attribute(elem: Any) -> DesignAttributeData | None:
    """Extract data from a single AttributeUsage element with default value."""
    name = sanitize_name(elem.name)
    if not name:
        return None

    sysml_type = _get_attribute_type(elem)
    default_value = _extract_default_value(elem.feature_value_expression)
    unit = _get_attribute_unit(elem)
    source_file, source_line = get_source_location(elem)
    parent_part = get_parent_part_name(elem)
    qualified_name = build_element_qualified_name(elem)

    return DesignAttributeData(
        name=name,
        sysml_type=sysml_type,
        default_value=default_value,
        unit=unit,
        source_file=source_file,
        source_line=source_line,
        parent_part=parent_part,
        qualified_name=qualified_name,
    )


# ============== Value Extraction Helpers ==============


def _extract_default_value(expr: Any) -> str | None:
    """Extract default value from a feature value expression."""
    if expr is None:
        return None

    if SysideAdapter.is_instance(expr, "LiteralInteger"):
        if hasattr(expr, "value"):
            return str(expr.value)
    elif SysideAdapter.is_instance(expr, "LiteralRational"):
        if hasattr(expr, "value"):
            return str(expr.value)
    elif SysideAdapter.is_instance(expr, "LiteralBoolean"):
        if hasattr(expr, "value"):
            return str(expr.value).lower()
    elif SysideAdapter.is_instance(expr, "LiteralString"):
        if hasattr(expr, "value"):
            return expr.value

    elif SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
        ref_path = _extract_reference_path(expr)
        if ref_path:
            return ref_path

    elif SysideAdapter.is_instance(expr, "FeatureChainExpression"):
        chain_path = _extract_chain_path(expr)
        if chain_path:
            return chain_path

    elif SysideAdapter.is_instance(expr, "OperatorExpression"):
        # CRITICAL: Import from agentic-mbse
        result = evaluate_true_static_expression(expr)
        return str(result)

    if hasattr(expr, "__str__"):
        try:
            return str(expr)
        except Exception:
            pass

    return None


def _extract_reference_path(expr: Any) -> str | None:
    """Extract path from a FeatureReferenceExpression."""
    if not hasattr(expr, "memberships"):
        return None
    for membership in expr.memberships:
        if type(membership).__name__ == "Membership":
            if hasattr(membership, "member_element"):
                elem = membership.member_element
                if elem and hasattr(elem, "name") and elem.name:
                    return elem.name
    return None


def _extract_chain_path(expr: Any) -> str | None:
    """Extract path from a FeatureChainExpression (instance.attribute)."""
    path_parts: list[str] = []

    operands = list(expr.operands) if hasattr(expr, "operands") else []
    if operands:
        first_operand = operands[0]
        if SysideAdapter.is_instance(first_operand, "FeatureReferenceExpression"):
            instance_name = _extract_reference_path(first_operand)
            if instance_name:
                path_parts.append(instance_name)

    if hasattr(expr, "target_feature") and expr.target_feature:
        target = expr.target_feature
        if hasattr(target, "name") and target.name:
            path_parts.append(target.name)

    return ".".join(path_parts) if path_parts else None


# ============== Type and Unit Extraction ==============


def _get_attribute_type(elem: Any) -> str:
    """Get the SysML type of an attribute from heritage."""
    if not hasattr(elem, "heritage"):
        return "Unknown"

    for relationship, target in elem.heritage:
        if SysideAdapter.is_instance(relationship, "FeatureTyping"):
            if hasattr(target, "name") and target.name:
                return target.name

    return "Unknown"


def _get_attribute_unit(elem: Any) -> str | None:
    """Extract unit annotation from attribute if present."""
    # TODO: Implement unit extraction from type annotations
    return None


# ============== Entry Point Matching ==============


def collect_entry_point_attributes(
    backtracking_result: Any,
    design_attributes: dict[Path, list[DesignAttributeData]],
) -> dict[str, DesignAttributeData]:
    """Match entry point params from backtracking to design attributes with defaults."""
    design_attr_index: dict[str, DesignAttributeData] = {}
    for attrs in design_attributes.values():
        for attr in attrs:
            if attr.name not in design_attr_index:
                design_attr_index[attr.name] = attr

    matched: dict[str, DesignAttributeData] = {}
    for qualified_param_name in backtracking_result.entry_points:
        simple_param_name = qualified_param_name.split("__")[-1]
        if simple_param_name in design_attr_index:
            matched[simple_param_name] = design_attr_index[simple_param_name]

    logger.info(
        f"Matched {len(matched)}/{len(backtracking_result.entry_points)} "
        f"entry points to design attributes"
    )

    return matched


# ============== Parameter Group Derivation ==============


class ParameterGroupDeriver:
    """Derives parameter groups from SysML model data."""

    def __init__(
        self,
        design_attributes: dict[Path, list[DesignAttributeData]],
        calc_usages: list,
        calc_defs: list,
    ):
        """Initialize deriver with extracted model data."""
        self.design_attributes = design_attributes
        self.calc_usages = calc_usages
        self.calc_defs = calc_defs

        self._attr_index: dict[str, tuple[Path, DesignAttributeData]] = {}
        for file_path, attrs in design_attributes.items():
            for attr in attrs:
                qname = attr.qualified_name
                if not qname:
                    raise ValueError(
                        f"Attribute '{attr.name}' in {file_path} missing qualified_name."
                    )
                if qname not in self._attr_index:
                    self._attr_index[qname] = (file_path, attr)
                    logger.debug(f"Indexed attr: {qname} -> {file_path.name}")

        self._binding_index: dict[str, tuple[Path, str]] = {}
        self._build_binding_index()

        self._unbound_index: dict[str, tuple[Path, str]] = {}
        self._build_unbound_index()

        self._literal_index: dict[str, tuple[Path, float]] = {}
        self._build_literal_index()

        logger.debug(
            f"ParameterGroupDeriver initialized: "
            f"{len(self._attr_index)} direct attrs, "
            f"{len(self._binding_index)} binding-traced attrs, "
            f"{len(self._unbound_index)} algorithm params, "
            f"{len(self._literal_index)} literal-bound params"
        )

    def _build_binding_index(self) -> None:
        """Build index mapping calc input params to source design files via bindings."""
        # Import BindingType from agentic-mbse
        from agentic_mbse.sysml.types import BindingType

        for usage in self.calc_usages:
            for binding in usage.bindings:
                param_name = binding.param_name
                if not param_name or not binding.source_path:
                    continue

                if binding.binding_type == BindingType.LITERAL:
                    continue

                if not usage.qualified_name:
                    raise ValueError(
                        f"CalcUsage '{usage.calc_def_name}' missing qualified_name."
                    )
                qname = f"{usage.qualified_name}__{param_name}"

                if qname in self._attr_index:
                    continue

                if qname in self._binding_index:
                    continue

                source_attr = self._extract_attr_name(binding.source_path)
                if not source_attr:
                    continue

                source_file = self._find_source_file(binding.source_path)
                if source_file:
                    self._binding_index[qname] = (source_file, source_attr)
                else:
                    self._binding_index[qname] = (usage.source_file, source_attr)

    def _build_unbound_index(self) -> None:
        """Build index mapping algorithm params to (usage_source_file, calc_def_name)."""
        for usage in self.calc_usages:
            for param_name in usage.unbound_params:
                if not usage.qualified_name:
                    raise ValueError(
                        f"CalcUsage '{usage.calc_def_name}' missing qualified_name."
                    )
                qname = f"{usage.qualified_name}__{param_name}"

                if qname in self._unbound_index:
                    continue

                if qname in self._attr_index or qname in self._binding_index:
                    continue

                self._unbound_index[qname] = (usage.source_file, usage.calc_def_name)

    def _build_literal_index(self) -> None:
        """Build index for literal-bound parameters."""
        from agentic_mbse.sysml.types import BindingType

        for usage in self.calc_usages:
            for binding in usage.bindings:
                if binding.binding_type != BindingType.LITERAL:
                    continue

                param_name = binding.param_name
                if not param_name or not binding.source_path:
                    continue

                if not usage.qualified_name:
                    raise ValueError(
                        f"CalcUsage '{usage.calc_def_name}' missing qualified_name."
                    )
                qname = f"{usage.qualified_name}__{param_name}"

                if qname in self._attr_index:
                    continue
                if qname in self._binding_index:
                    continue
                if qname in self._unbound_index:
                    continue
                if qname in self._literal_index:
                    continue

                try:
                    value = float(binding.source_path)
                    self._literal_index[qname] = (usage.source_file, value)
                except (ValueError, TypeError):
                    logger.warning(
                        f"Could not parse literal value '{binding.source_path}' "
                        f"for param '{qname}'"
                    )

    def _extract_attr_name(self, source_path: str) -> str | None:
        """Extract attribute name from a binding source path."""
        if not source_path:
            return None

        if "::" in source_path:
            return source_path.split("::")[-1]

        if "." in source_path:
            return source_path.split(".")[-1]

        return source_path

    def _find_source_file(self, source_path: str) -> Path | None:
        """Find source file for an attribute by qualified name."""
        python_qname = sysml_to_python_qualified_name(source_path)

        if python_qname in self._attr_index:
            file_path, attr = self._attr_index[python_qname]
            return file_path

        return None

    def derive_groups(self) -> list[DerivedParameterGroup]:
        """Derive all parameter groups from model data."""
        design_groups = self._derive_from_design_attributes()

        if self._unbound_index:
            algorithm_groups = self._derive_from_unbound_params_v2(self._unbound_index)

            existing_names = {g.name for g in design_groups}
            for algo_group in algorithm_groups:
                if algo_group.name not in existing_names:
                    design_groups.append(algo_group)
                    existing_names.add(algo_group.name)
                else:
                    existing_group = next(g for g in design_groups if g.name == algo_group.name)
                    existing_param_names = {p.name for p in existing_group.parameters}
                    for param in algo_group.parameters:
                        if param.name not in existing_param_names:
                            existing_group.parameters.append(param)
                            existing_param_names.add(param.name)

        return design_groups

    def derive_groups_filtered(
        self,
        backtracking_result: Any,
        calc_defs: list,
    ) -> list[DerivedParameterGroup]:
        """Derive parameter groups filtered to only true entry points."""
        raw_groups = self.derive_groups()

        entry_points = backtracking_result.entry_points

        for group in raw_groups:
            group.parameters = [
                p for p in group.parameters
                if p.name in entry_points
            ]

        return [g for g in raw_groups if g.parameters]

    def derive_for_entry_points(
        self,
        entry_points: set[str],
    ) -> list[DerivedParameterGroup]:
        """Derive and filter groups to only those containing required entry points."""
        all_groups = self.derive_groups()

        filtered_groups = [
            group for group in all_groups
            if any(p.name in entry_points for p in group.parameters)
        ]

        logger.info(
            f"Filtered {len(all_groups)} groups to {len(filtered_groups)} "
            f"containing {len(entry_points)} entry points"
        )

        return filtered_groups

    def classify(self, qualified_name: str) -> str | None:
        """Classify a parameter to its group name using qualified name."""
        if qualified_name in self._attr_index:
            file_path, _attr_data = self._attr_index[qualified_name]
            group_name, _class_name = self._generate_group_names(file_path.stem)
            return group_name

        if qualified_name in self._binding_index:
            file_path, _source_attr = self._binding_index[qualified_name]
            group_name, _class_name = self._generate_group_names(file_path.stem)
            return group_name

        if qualified_name in self._unbound_index:
            file_path, _calc_def_name = self._unbound_index[qualified_name]
            group_name, _class_name = self._generate_group_names(file_path.stem)
            return group_name

        if qualified_name in self._literal_index:
            file_path, _literal_value = self._literal_index[qualified_name]
            group_name, _class_name = self._generate_group_names(file_path.stem)
            return group_name

        return None

    def get_default_value(self, qualified_name: str) -> float | None:
        """Get default value for any parameter type using qualified name."""
        if qualified_name in self._attr_index:
            _, attr_data = self._attr_index[qualified_name]
            return self._parse_default_value(attr_data.default_value)

        if qualified_name in self._binding_index:
            _, source_attr = self._binding_index[qualified_name]
            for qname, (_, attr) in self._attr_index.items():
                if attr.name == source_attr:
                    return self._parse_default_value(attr.default_value)
            return None

        if qualified_name in self._unbound_index:
            return None

        if qualified_name in self._literal_index:
            _, literal_value = self._literal_index[qualified_name]
            return literal_value

        return None

    def _derive_from_unbound_params_v2(
        self,
        unbound_index: dict[str, tuple[Path, str]],
    ) -> list[DerivedParameterGroup]:
        """Derive groups from _unbound_index with qualified names."""
        design_groups: dict[str, list[ParameterSource]] = {}

        calc_def_by_name = {cd.name: cd for cd in self.calc_defs}

        for qualified_name, (source_file, calc_def_name) in unbound_index.items():
            file_stem = self._get_file_stem(str(source_file.stem) if hasattr(source_file, 'stem') else str(source_file))
            simple_name = qualified_name.split("__")[-1]

            default_value = None
            calc_def = calc_def_by_name.get(calc_def_name)
            if calc_def:
                for input_attr in calc_def.input_attributes:
                    if input_attr.name == simple_name and input_attr.default_value:
                        default_value = self._parse_default_value(input_attr.default_value)
                        break

            param_source = ParameterSource(
                name=qualified_name,
                source_type="design",
                source_file=file_stem,
                default_value=default_value,
                calc_def=calc_def_name,
                sysml_type="Real",
                description=f"Algorithm param {simple_name} (default from {calc_def_name})",
            )

            if file_stem not in design_groups:
                design_groups[file_stem] = []
            design_groups[file_stem].append(param_source)

        return self._build_groups(design_groups, {})

    def _derive_from_design_attributes(self) -> list[DerivedParameterGroup]:
        """Derive groups from design attributes, binding-traced, and literal-bound params."""
        design_groups: dict[str, list[ParameterSource]] = {}

        for file_path, attrs in self.design_attributes.items():
            file_stem = file_path.stem

            for attr in attrs:
                default_value = self._parse_default_value(attr.default_value)
                if default_value is None:
                    continue

                param_source = ParameterSource(
                    name=attr.qualified_name,
                    source_type="design",
                    source_file=file_stem,
                    default_value=default_value,
                    calc_def="",
                    sysml_type=attr.sysml_type or "Real",
                    description=f"Parameter {attr.qualified_name} from {file_stem}",
                )

                if file_stem not in design_groups:
                    design_groups[file_stem] = []
                design_groups[file_stem].append(param_source)

        for param_name, (file_path, source_attr) in self._binding_index.items():
            file_stem = file_path.stem

            if file_stem in design_groups:
                existing_names = {p.name for p in design_groups[file_stem]}
                if param_name in existing_names:
                    continue

            default_value = None
            for qname, (_, attr) in self._attr_index.items():
                if attr.name == source_attr:
                    default_value = self._parse_default_value(attr.default_value)
                    break

            param_source = ParameterSource(
                name=param_name,
                source_type="design",
                source_file=file_stem,
                default_value=default_value,
                calc_def="",
                sysml_type="Real",
                description=f"Bound to {source_attr}"
                + (f" (default {default_value})" if default_value else ""),
            )

            if file_stem not in design_groups:
                design_groups[file_stem] = []
            design_groups[file_stem].append(param_source)

        for param_name, (file_path, literal_value) in self._literal_index.items():
            file_stem = file_path.stem

            if file_stem in design_groups:
                existing_names = {p.name for p in design_groups[file_stem]}
                if param_name in existing_names:
                    continue

            param_source = ParameterSource(
                name=param_name,
                source_type="design",
                source_file=file_stem,
                default_value=literal_value,
                calc_def="",
                sysml_type="Real",
                description=f"Literal binding: {param_name} = {literal_value}",
            )

            if file_stem not in design_groups:
                design_groups[file_stem] = []
            design_groups[file_stem].append(param_source)

        return self._build_groups(design_groups, {})

    def _build_groups(
        self,
        design_groups: dict[str, list[ParameterSource]],
        library_groups: dict[str, list[ParameterSource]],
    ) -> list[DerivedParameterGroup]:
        """Build DerivedParameterGroup objects from grouped parameters."""
        groups: list[DerivedParameterGroup] = []

        for file_stem, params in design_groups.items():
            group_name, class_name = self._generate_group_names(file_stem)
            groups.append(
                DerivedParameterGroup(
                    name=group_name,
                    class_name=class_name,
                    source_type="design",
                    source_identifier=f"{file_stem}.sysml",
                    parameters=params,
                )
            )

        for package_name, params in library_groups.items():
            group_name, class_name = self._generate_group_names(package_name)
            groups.append(
                DerivedParameterGroup(
                    name=group_name,
                    class_name=class_name,
                    source_type="library",
                    source_identifier=package_name,
                    parameters=params,
                )
            )

        logger.info(
            f"Derived {len(groups)} parameter groups: "
            f"{len(design_groups)} design, {len(library_groups)} library"
        )

        return groups

    def _parse_default_value(self, value_str: str | None) -> float | None:
        """Parse a default value string to float if possible."""
        if value_str is None:
            return None

        try:
            return float(value_str)
        except (ValueError, TypeError):
            logger.debug(f"Could not parse default value '{value_str}' as float")
            return None

    def _get_file_stem(self, filename: str) -> str:
        """Get file stem from filename or path string."""
        if isinstance(filename, Path):
            return filename.stem
        if filename.endswith(".sysml"):
            return filename[:-6]
        return filename

    def _generate_group_names(self, base_name: str) -> tuple[str, str]:
        """Generate snake_case group name and TitleCase class name."""
        base = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", base_name)
        base = re.sub("([a-z0-9])([A-Z])", r"\1_\2", base).lower()
        base = base.replace("-", "_")

        if base.endswith("_params"):
            base = base[:-7]

        group_name = f"{base}_params"
        class_name = "".join(word.capitalize() for word in base.split("_")) + "Params"

        return group_name, class_name
