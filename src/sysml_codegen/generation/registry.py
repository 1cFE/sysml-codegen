"""Module registration code generator.

Generates pure auto-registration code using create_registry() for all modules.
TEAx introspection handles both single-output (RootModel[T]) and multi-output
(BaseModel with fields) correctly.

Usage:
    from sysml_codegen.generation.registry import generate_registry_function

    code = generate_registry_function(calc_defs, "package_name", template_env, output_path)
"""

from pathlib import Path
from typing import TYPE_CHECKING

import jinja2

# UPDATED: Import from sysml_codegen package
from sysml_codegen.extraction.data_models import CalculationDefinitionData
from sysml_codegen.resolution.identifier_types import (
    PythonModulePath,
    SysMLQualifiedName,
    derive_module_type,
)

if TYPE_CHECKING:
    from sysml_codegen.resolution.models import ParameterGroup as ModelParameterGroup


def generate_registry_function(
    calc_defs: list[CalculationDefinitionData],
    package_name: str,
    template_env: jinja2.Environment,
    output_path: Path,
    entry_point_groups: "list[ModelParameterGroup]",
) -> str:
    """Generate registry creation function.

    Args:
        calc_defs: All calculation definitions to register
        package_name: Package name (parameterized)
        template_env: Jinja2 environment
        output_path: Where to write __init__.py or registry.py (future use)
        entry_point_groups: List of ParameterGroup from ComputationGraph.entry_point_groups.

    Returns:
        Generated Python code
    """
    # Use entry_point_groups from ComputationGraph (single source of truth)
    schema_imports = _generate_schema_imports_from_entry_points(package_name, entry_point_groups)
    group_names = [g.class_name for g in entry_point_groups]

    context = {
        "function_name": f"create_{package_name}_registry",
        "all_modules": [
            {
                "class_name": f"{calc.name}Module",  # Python class name (unchanged)
                "module_type": derive_module_type(calc.qualified_name),  # Namespaced registry key
            }
            for calc in calc_defs
        ],
        "imports": _generate_import_statements(calc_defs, package_name),
        "schema_imports": schema_imports,
        "parameter_groups": group_names,
    }

    template = template_env.get_template("registry_function.py.jinja2")
    code = template.render(**context)

    # Ensure final newline (PEP 8 compliance)
    if not code.endswith('\n'):
        code += '\n'

    return code


def _extract_input_fields(calc_def: CalculationDefinitionData) -> dict[str, str]:
    """Extract input field names and types for registration.

    Args:
        calc_def: Calculation definition

    Returns:
        Dict mapping field name to type (e.g., {'p_neutron': 'Float'})
    """
    inputs = {}
    for attr in calc_def.input_attributes:
        inputs[attr.name] = _map_output_type(attr.sysml_type)
    return inputs


def _extract_output_field(calc_def: CalculationDefinitionData) -> dict[str, str]:
    """Extract output field name and type for single-output module.

    Args:
        calc_def: Calculation definition with 1 output

    Returns:
        Dict with single output field (e.g., {'p_thermal': 'Float'})

    Raises:
        ValueError: If calc def doesn't have exactly 1 output
    """
    output_attrs = calc_def.output_attributes
    if len(output_attrs) != 1:
        raise ValueError(
            f"Expected 1 output for {calc_def.name}, got {len(output_attrs)}. "
            "Use MultiOutput for multi-output modules."
        )

    attr = output_attrs[0]
    return {attr.name: _map_output_type(attr.sysml_type)}


def _generate_import_statements(
    calc_defs: list[CalculationDefinitionData], package_name: str
) -> list[str]:
    """Generate import statements for registry function.

    ADR-003: Generates imports from nested namespace directories based on
    SysML qualified names.

    Args:
        calc_defs: All calculation definitions
        package_name: Package name for module imports

    Returns:
        List of import lines
    """
    imports = [
        "from simkit.core.registry_builder import create_registry",
        "from simkit.core.pipeline_registry import PipelineModuleRegistry",
        "",
    ]

    # Add module imports (deduplicated and sorted)
    seen_modules = set()
    module_imports = []
    for calc_def in calc_defs:
        if calc_def.name not in seen_modules:
            # ADR-003: Derive nested path from qualified name
            sqn = SysMLQualifiedName(calc_def.qualified_name)
            python_path = PythonModulePath.from_sysml(sqn)
            class_name = f"{calc_def.name}Module"

            # Build import path with namespace
            import_module = f"{package_name}.modules.{python_path.import_path}"

            module_imports.append(f"from {import_module} import {class_name}")
            seen_modules.add(calc_def.name)

    # Sort imports for consistency and I001 compliance
    module_imports.sort()
    imports.extend(module_imports)

    return imports


def _map_output_type(sysml_type: str) -> str:
    """Map SysML type to Python RootModel wrapper type.

    Args:
        sysml_type: SysML type reference

    Returns:
        Python RootModel wrapper type for output field
    """
    mapping = {
        "Real": "Float",
        "ScalarValues::Real": "Float",
        "Integer": "Int",
        "ScalarValues::Integer": "Int",
        "String": "String",
        "ScalarValues::String": "String",
        "Boolean": "Bool",
        "ScalarValues::Boolean": "Bool",
    }

    return mapping.get(sysml_type, sysml_type)


def _generate_schema_imports_from_entry_points(
    package_name: str,
    entry_point_groups: "list[ModelParameterGroup]",
) -> list[str]:
    """Generate import statements from Pydantic ParameterGroup models.

    Args:
        package_name: Package name (parameterized)
        entry_point_groups: ParameterGroup list from ComputationGraph

    Returns:
        Sorted list of import statements
    """
    if not entry_point_groups:
        return []

    imports = []
    for group in entry_point_groups:
        # Use explicit re-export syntax (Foo as Foo) to avoid ruff F401
        imports.append(
            f"from {package_name}.schemas.{group.name} "
            f"import {group.class_name} as {group.class_name}"
        )

    return sorted(imports)


__all__ = [
    "generate_registry_function",
]
