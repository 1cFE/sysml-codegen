"""TEAx module wrapper generator for calculation definitions.

Generates TEAx module wrappers that integrate handwritten implementations
with the TEAx framework. Handles both single-output and multi-output patterns
using Pydantic v2 RootModel wrappers.

Usage:
    from sysml_codegen.generation.modules import generate_teax_module

    code = generate_teax_module(calc_def, template_env, output_path)
"""

from pathlib import Path

import jinja2

# UPDATED: Import from sysml_codegen package
from sysml_codegen.extraction.data_models import CalculationDefinitionData
from sysml_codegen.generation.type_mapping import map_sysml_type_to_python
from sysml_codegen.resolution.identifier_types import PythonModulePath, SysMLQualifiedName


def is_multioutput(calc_def: CalculationDefinitionData) -> bool:
    """Determine if calc def has multiple outputs.

    Args:
        calc_def: Extracted calculation definition data

    Returns:
        True if calc def has 2+ output attributes
    """
    return len(calc_def.output_attributes) >= 2


def _build_module_docstring(calc_def: CalculationDefinitionData) -> str:
    """Build comprehensive module docstring with I/O sections.

    Args:
        calc_def: Calculation definition with metadata

    Returns:
        Formatted module docstring with purpose, I/O, source
    """
    lines = []

    # Add purpose
    lines.append(f"TEAx module for {calc_def.name} calculation.")

    # Add detailed description from doc comment
    if calc_def.doc_comment:
        lines.append("")
        lines.append(calc_def.doc_comment.strip())

    # Add inputs section
    if calc_def.input_attributes:
        lines.append("")
        lines.append("Inputs:")
        for attr in calc_def.input_attributes:
            desc = attr.description or f"{attr.name} parameter"
            # Add unit if available
            if attr.unit and f"[{attr.unit}]" not in desc:
                desc = f"{desc} [{attr.unit}]"
            lines.append(f"    - {attr.name}: {desc}")

    # Add outputs section
    if calc_def.output_attributes:
        lines.append("")
        lines.append("Outputs:")
        for attr in calc_def.output_attributes:
            desc = attr.description or f"{attr.name} result"
            # Add unit if available
            if attr.unit and f"[{attr.unit}]" not in desc:
                desc = f"{desc} [{attr.unit}]"
            lines.append(f"    - {attr.name}: {desc}")

    # Add source reference
    lines.append("")
    lines.append(f"SysML Source: {calc_def.source_file}:{calc_def.source_line}")

    return "\n".join(lines)


def generate_teax_module(
    calc_def: CalculationDefinitionData,
    template_env: jinja2.Environment,
    output_path: Path,
    package_name: str = "generated_code",
) -> str:
    """Generate TEAx module wrapper for calculation definition.

    ADR-003: Generates imports from namespaced handwritten files based on
    the SysML qualified name.

    Args:
        calc_def: Calculation definition data
        template_env: Jinja2 environment with templates loaded
        output_path: Path where module will be written (for reference)
        package_name: Python package name (parameterized, no hardcoded default)

    Returns:
        Generated Python code string
    """
    # Determine output pattern
    multi_output = is_multioutput(calc_def)

    # Prepare input attributes with type hints
    input_attributes = [
        {
            "name": attr.name,
            "type_hint": map_sysml_type_to_python(attr.sysml_type),
            "description": attr.description or f"{attr.name} input",
        }
        for attr in calc_def.input_attributes
    ]

    # Prepare output attributes
    output_attributes = [
        {
            "name": attr.name,
            "description": attr.description or f"{attr.name} output",
        }
        for attr in calc_def.output_attributes
    ]

    # Collect primitive types used in inputs (for imports)
    primitive_types = set()
    for attr in input_attributes:
        type_hint = attr["type_hint"]
        if type_hint in ["Float", "Int", "String", "Bool"]:
            primitive_types.add(type_hint)

    # Always include Float (used for outputs in single-output modules)
    primitive_types.add("Float")

    # Sort for consistent imports
    primitive_imports = sorted(primitive_types)

    # ADR-003: Derive namespaced import path for handwritten implementation
    sqn = SysMLQualifiedName(calc_def.qualified_name)
    python_path = PythonModulePath.from_sysml(sqn)
    impl_import_path = python_path.impl_import_path

    # Build template context
    context = {
        "class_name": f"{calc_def.name}Module",
        "input_class_name": f"{calc_def.name}Input",
        "output_class_name": f"{calc_def.name}Output",
        "schema_name": calc_def.name.lower() + "_output",
        "handler_name": calc_def.name.lower(),
        "impl_import_path": impl_import_path,  # ADR-003: Namespaced handwritten import
        "doc_comment": _build_module_docstring(calc_def),
        "package_name": package_name,
        "is_multioutput": multi_output,
        "input_attributes": input_attributes,
        "output_attributes": output_attributes,
        "calc_expressions": calc_def.calc_expressions or [],
        "sysml_source": f"{calc_def.source_file}:{calc_def.source_line}",
        "primitive_imports": primitive_imports,
    }

    # Render template
    template = template_env.get_template("teax_module.py.jinja2")
    code = template.render(**context)

    # Ensure final newline (PEP 8 compliance)
    if not code.endswith('\n'):
        code += '\n'

    return code


__all__ = [
    "generate_teax_module",
    "is_multioutput",
]
