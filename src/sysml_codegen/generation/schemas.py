"""MultiOutput model generator for multi-output calculation definitions.

Generates Pydantic MultiOutput models for PipelineModules with 2+ output
attributes. Uses PipelineModule fields exclusively (no extraction imports).

Usage:
    from sysml_codegen.generation.schemas import generate_multioutput_model

    code = generate_multioutput_model(module, template_env, output_path)
"""

from pathlib import Path

import jinja2


def _build_field_description(output) -> str:
    """Build field description from ModuleOutput fields."""
    desc = output.description.strip() if output.description else ""

    if not desc:
        desc = f"{output.field_name} output"

    if output.unit:
        unit_pattern = f"[{output.unit}]"
        if unit_pattern not in desc:
            desc = f"{desc} [{output.unit}]"

    return desc


def _build_schema_docstring(module) -> str:
    """Build schema docstring from PipelineModule fields."""
    lines = []

    lines.append(f"Multi-output container for {module.calc_def_name}.")

    if module.doc_comment and module.doc_comment.strip():
        lines.append("")
        lines.append(module.doc_comment.strip())

    lines.append("")
    lines.append(f"SysML Source: {module.source_file}:{module.source_line}")

    return "\n".join(lines)


def generate_multioutput_model(
    module,
    template_env: jinja2.Environment,
    output_path: Path,
    package_name: str = "generated_code",
) -> str | None:
    """Generate MultiOutput model from PipelineModule.

    Args:
        module: PipelineModule with metadata fields populated
        template_env: Jinja2 environment with templates loaded
        output_path: Directory to write generated file
        package_name: Package name

    Returns:
        Generated Python code string or None if single-output
    """
    if len(module.outputs) < 2:
        return None

    fields = []
    for out in module.outputs:
        field_data = {
            "name": out.field_name,
            "type": out.python_type,
            "description": _build_field_description(out),
            "default": None,  # REQ-OSR-05: output fields must never have defaults
        }
        fields.append(field_data)

    primitive_types: set[str] = set()

    context = {
        "class_name": f"{module.calc_def_name}Output",
        "doc_comment": _build_schema_docstring(module),
        "package_name": package_name,
        "fields": fields,
        "primitive_types": sorted(primitive_types),
        "sysml_source": f"{module.source_file}:{module.source_line}",
    }

    template = template_env.get_template("multioutput_model.py.jinja2")
    code = template.render(**context)

    if not code.endswith('\n'):
        code += '\n'

    return code


# Keep old name as alias for backward compatibility during transition
generate_multioutput_model_from_graph = generate_multioutput_model


__all__ = [
    "generate_multioutput_model",
    "generate_multioutput_model_from_graph",
]
