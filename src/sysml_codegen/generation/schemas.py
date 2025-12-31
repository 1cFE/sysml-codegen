"""MultiOutput model generator for multi-output calculation definitions.

Generates Pydantic MultiOutput models for SysML calc defs with 2+ output
attributes. Follows the pattern validated in Phase 0 golden reference.

Enhanced to include:
- Comprehensive docstrings from SysML doc comments
- Default values from SysML attributes
- Field descriptions with unit annotations

Usage:
    from sysml_codegen.generation.schemas import should_use_multioutput, generate_multioutput_model

    if should_use_multioutput(calc_def):
        code = generate_multioutput_model(calc_def, template_env, output_path)
"""

from pathlib import Path
from typing import Any

import jinja2

# UPDATED: Import from sysml_codegen package
from sysml_codegen.extraction.constraint_extractor import ConstraintData
from sysml_codegen.extraction.constraints import generate_field_constraints
from sysml_codegen.extraction.data_models import AttributeInfo, CalculationDefinitionData
from sysml_codegen.generation.constraint_comments import generate_field_constraint_comments


def _build_field_description(
    attr: AttributeInfo,
    constraint_comment: str | None = None,
) -> str:
    """Build comprehensive field description with units and constraints.

    Args:
        attr: Attribute info with description and optional unit
        constraint_comment: Optional constraint comment from generator

    Returns:
        Formatted description string (e.g., "Alpha particle power [MW]. Constraint: p > 0")
    """
    desc = attr.description.strip() if attr.description else ""

    # If no description, use generic
    if not desc:
        desc = f"{attr.name} output"

    # Append unit if available and not already in description
    if attr.unit:
        unit_pattern = f"[{attr.unit}]"
        if unit_pattern not in desc:
            desc = f"{desc} [{attr.unit}]"

    # Append constraint comment if available
    if constraint_comment:
        desc = f"{desc}. {constraint_comment}"

    return desc


def _build_schema_docstring(calc_def: CalculationDefinitionData) -> str:
    """Build comprehensive schema docstring.

    Args:
        calc_def: Calculation definition with doc comment

    Returns:
        Formatted docstring with source reference
    """
    lines = []

    # Add short description
    lines.append(f"Multi-output container for {calc_def.name}.")

    # Add detailed doc comment if available
    if calc_def.doc_comment and calc_def.doc_comment.strip():
        lines.append("")
        lines.append(calc_def.doc_comment.strip())

    # Add source reference
    lines.append("")
    lines.append(f"SysML Source: {calc_def.source_file}:{calc_def.source_line}")

    return "\n".join(lines)


def _format_default_value(attr: AttributeInfo) -> str | None:
    """Format default value for Field() definition.

    Args:
        attr: Attribute with optional default_value

    Returns:
        Python literal string (e.g., "0.06", "'hello'", "True") or None if no default
    """
    if attr.default_value is None:
        return None

    return attr.default_value


def should_use_multioutput(calc_def: CalculationDefinitionData) -> bool:
    """Determine if calc def needs MultiOutput pattern.

    Args:
        calc_def: Extracted calculation definition data

    Returns:
        True if calc def has 2+ output attributes
    """
    output_attrs = calc_def.output_attributes
    return len(output_attrs) >= 2


def generate_multioutput_model(
    calc_def: CalculationDefinitionData,
    template_env: jinja2.Environment,
    output_path: Path,
    constraints: list[ConstraintData] | None = None,
    package_name: str = "generated_code",
) -> str | None:
    """Generate MultiOutput model for multi-output calc def.

    Args:
        calc_def: Calculation definition with 2+ outputs
        template_env: Jinja2 environment with templates loaded
        output_path: Directory to write generated file (not used, for future)
        constraints: Optional list of constraints for this calc def
        package_name: Package name (parameterized)

    Returns:
        Generated Python code string or None if single-output
    """
    if not should_use_multioutput(calc_def):
        return None

    # Generate constraint comments for output fields
    constraint_comments: dict[str, str] = {}
    if constraints:
        output_field_names = [attr.name for attr in calc_def.output_attributes]
        constraint_comments = generate_field_constraint_comments(
            constraints, output_field_names
        )

    # Build fields with enhanced descriptions, defaults, and constraints
    fields = []
    for attr in calc_def.output_attributes:
        field_data = {
            "name": attr.name,
            "type": _map_output_type(attr.sysml_type),
            "description": _build_field_description(
                attr, constraint_comments.get(attr.name)
            ),
            "default": _format_default_value(attr),
        }
        fields.append(field_data)

    # Collect unique primitive types used in fields
    primitive_types = set()

    # Prepare template context with enhanced docstring
    context = {
        "class_name": f"{calc_def.name}Output",
        "doc_comment": _build_schema_docstring(calc_def),
        "package_name": package_name,
        "fields": fields,
        "primitive_types": sorted(primitive_types),
        "sysml_source": f"{calc_def.source_file}:{calc_def.source_line}",
    }

    # Render template
    template = template_env.get_template("multioutput_model.py.jinja2")
    code = template.render(**context)

    # Ensure final newline (PEP 8 compliance)
    if not code.endswith('\n'):
        code += '\n'

    return code


def _map_output_type(sysml_type: str) -> str:
    """Map SysML type to Python primitive type for multi-output fields.

    Args:
        sysml_type: SysML type reference (e.g., 'Real', 'Integer', 'String')

    Returns:
        Python primitive type (e.g., 'float', 'int', 'str', 'bool')
    """
    mapping = {
        "Real": "float",
        "ScalarValues::Real": "float",
        "Integer": "int",
        "ScalarValues::Integer": "int",
        "String": "str",
        "ScalarValues::String": "str",
        "Boolean": "bool",
        "ScalarValues::Boolean": "bool",
    }
    return mapping.get(sysml_type, "float")


def prepare_input_fields_with_constraints(calc_def: CalculationDefinitionData) -> list[dict[str, Any]]:
    """Prepare input field data with constraints for template rendering.

    Args:
        calc_def: Calculation definition with input attributes

    Returns:
        List of field dictionaries with constraint parameters
    """
    # Get constraints for input attributes
    field_constraints = generate_field_constraints(calc_def)

    # Prepare field data with constraints
    fields: list[dict[str, Any]] = []
    for attr in calc_def.input_attributes:
        # Build field dictionary
        field_data: dict[str, Any] = {
            "name": attr.name,
            "type": _map_input_type(attr.sysml_type),
            "description": attr.description or f"{attr.name} input",
        }

        # Add constraints if available
        if attr.name in field_constraints:
            constraint = field_constraints[attr.name]
            constraints_dict: dict[str, float] = {}

            if constraint.gt is not None:
                constraints_dict["gt"] = constraint.gt
            if constraint.ge is not None:
                constraints_dict["ge"] = constraint.ge
            if constraint.lt is not None:
                constraints_dict["lt"] = constraint.lt
            if constraint.le is not None:
                constraints_dict["le"] = constraint.le

            if constraints_dict:
                field_data["constraints"] = constraints_dict

        fields.append(field_data)

    return fields


def _map_input_type(sysml_type: str) -> str:
    """Map SysML type to Python input type.

    Args:
        sysml_type: SysML type reference (e.g., 'Real', 'Integer')

    Returns:
        Python type for input field (e.g., 'float', 'int')
    """
    if sysml_type in ["Real", "ScalarValues::Real"]:
        return "float"
    elif sysml_type in ["Integer", "ScalarValues::Integer"]:
        return "int"
    elif sysml_type in ["Boolean", "ScalarValues::Boolean"]:
        return "bool"
    elif sysml_type in ["String"]:
        return "str"

    return "float"


__all__ = [
    "generate_multioutput_model",
    "prepare_input_fields_with_constraints",
    "should_use_multioutput",
]
