"""TEAx module wrapper generator for calculation definitions.

Generates TEAx module wrappers that integrate handwritten implementations
with the TEAx framework. Handles both single-output and multi-output patterns
using Pydantic v2 RootModel wrappers.

Usage:
    from sysml_codegen.generation.modules import generate_teax_module

    code = generate_teax_module(module, template_env, output_path)
"""

from pathlib import Path

import jinja2

from sysml_codegen.core.identifier_types import PythonModulePath, SysMLQualifiedName

from sysml_codegen.generation.type_mapping import map_sysml_type_to_python


def _output_attr_name(out) -> str:
    """Get original output attribute name from ModuleOutput.

    For multi-output modules, field_name IS the attribute name.
    For single-output modules, field_name is "root" -- extract from channel_name.
    Channel name format: {usage_eqn}__{attr_name} (PQN format).
    """
    if out.field_name != "root":
        return out.field_name
    return out.channel_name.split("__")[-1]


def _get_module_sysml_qn(module) -> str:
    """Get the full SysML qualified name for path/import derivation.

    Module types store calc_def_qualified_name differently:
    - CalcUsage: full calc def QN (e.g., "Package::CalcDef")
    - FORMULA: owning part QN only → append "::calc_def_name"
    - Aggregation: owning part QN with __ separator → use module.name with :: separator
    """
    if module.is_computed_attribute:
        return f"{module.calc_def_qualified_name}::{module.calc_def_name}"
    elif module.is_aggregation:
        return module.name.replace("__", "::")
    else:
        return module.calc_def_qualified_name


def _build_module_docstring_from_graph(module) -> str:
    """Build module docstring from PipelineModule fields."""
    lines = []

    lines.append(f"TEAx module for {module.calc_def_name} calculation.")

    if module.doc_comment:
        lines.append("")
        lines.append(module.doc_comment.strip())

    if module.inputs:
        lines.append("")
        lines.append("Inputs:")
        for inp in module.inputs:
            desc = inp.description or f"{inp.param_name} parameter"
            lines.append(f"    - {inp.param_name}: {desc}")

    if module.outputs:
        lines.append("")
        lines.append("Outputs:")
        for out in module.outputs:
            out_name = _output_attr_name(out)
            desc = out.description or f"{out_name} result"
            if out.unit and f"[{out.unit}]" not in desc:
                desc = f"{desc} [{out.unit}]"
            lines.append(f"    - {out_name}: {desc}")

    lines.append("")
    lines.append(f"SysML Source: {module.source_file}:{module.source_line}")

    return "\n".join(lines)


def generate_teax_module(
    module,
    template_env: jinja2.Environment,
    output_path: Path,
    package_name: str = "generated_code",
) -> str:
    """Generate TEAx module wrapper from PipelineModule.

    Handles all module types: CalcUsage, FORMULA, and aggregation.
    Derives class names, import paths, and template context from
    PipelineModule fields.

    Args:
        module: PipelineModule with metadata fields populated
        template_env: Jinja2 environment with templates loaded
        output_path: Path where module will be written (for reference)
        package_name: Python package name

    Returns:
        Generated Python code string
    """
    multi_output = len(module.outputs) > 1

    input_attributes = [
        {
            "name": inp.param_name,
            "type_hint": inp.python_type,
            "description": inp.description or f"{inp.param_name} input",
        }
        for inp in module.inputs
    ]

    output_attributes = []
    for out in module.outputs:
        out_name = _output_attr_name(out)
        output_attributes.append({
            "name": out_name,
            "description": out.description or f"{out_name} output",
        })

    primitive_types = set()
    for attr in input_attributes:
        type_hint = attr["type_hint"]
        if type_hint in ["Float", "Int", "String", "Bool"]:
            primitive_types.add(type_hint)
    primitive_types.add("Float")
    primitive_imports = sorted(primitive_types)

    # Derive path from full SysML QN (module-type-aware)
    sysml_qn = _get_module_sysml_qn(module)
    sqn = SysMLQualifiedName(sysml_qn)
    python_path = PythonModulePath.from_sysml(sqn)
    impl_import_path = python_path.impl_import_path

    # Class name from module_type (correct PascalCase for all module types)
    class_name = module.module_type.split(".")[-1]
    base_name = class_name.removesuffix("Module")

    context = {
        "class_name": class_name,
        "input_class_name": f"{base_name}Input",
        "output_class_name": f"{base_name}Output",
        "schema_name": base_name.lower() + "_output",
        "handler_name": module.calc_def_name.lower(),
        "impl_import_path": impl_import_path,
        "doc_comment": _build_module_docstring_from_graph(module),
        "package_name": package_name,
        "is_multioutput": multi_output,
        "input_attributes": input_attributes,
        "output_attributes": output_attributes,
        "calc_expressions": module.calc_expressions or [],
        "sysml_source": f"{module.source_file}:{module.source_line}",
        "primitive_imports": primitive_imports,
    }

    template = template_env.get_template("teax_module.py.jinja2")
    code = template.render(**context)

    if not code.endswith('\n'):
        code += '\n'

    return code


# Keep old name as alias for backward compatibility during transition
generate_teax_module_from_graph = generate_teax_module


__all__ = [
    "generate_teax_module",
    "generate_teax_module_from_graph",
]
