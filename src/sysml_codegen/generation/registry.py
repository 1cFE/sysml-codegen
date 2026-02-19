"""Module registration code generator.

Generates pure auto-registration code using create_registry() for all modules.
TEAx introspection handles both single-output (RootModel[T]) and multi-output
(BaseModel with fields) correctly.

Usage:
    from sysml_codegen.generation.registry import generate_registry_function

    code = generate_registry_function(calc_defs, "package_name", template_env, output_path)
"""

from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

import jinja2

# UPDATED: Import from sysml_codegen package
from sysml_codegen.extraction.data_models import (
    CalculationDefinitionData,
    ComputedAttributeClassification,
    ComputedAttributeData,
    ScopedAggregationData,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.generation.type_mapping import map_sysml_type_to_rootmodel_wrapper
from sysml_codegen.resolution.identifier_types import (
    PythonModulePath,
    SysMLQualifiedName,
    derive_module_type,
)

if TYPE_CHECKING:
    from sysml_codegen.resolution.models import ParameterGroup as ModelParameterGroup

logger = logging.getLogger(__name__)


def _collect_exit_point_primitive_types(
    modules: list,
) -> list[str]:
    """Collect unique primitive wrapper type names needed for exit points.

    For single-output modules (field_name="root"), returns the wrapper type
    name from primitives.py (e.g., "Float" for python_type="float").

    Multi-output modules use BaseModel schemas which are already registered
    via entry_point_groups or schema generation.
    """
    type_map = {
        "float": "Float",
        "int": "Int",
        "str": "String",
        "bool": "Bool",
    }
    types = set()
    for module in modules:
        for out in module.outputs:
            if out.field_name == "root":
                wrapper = type_map.get(out.python_type)
                if wrapper:
                    types.add(wrapper)
    return sorted(types)


def generate_registry_function(
    calc_defs: list[CalculationDefinitionData],
    package_name: str,
    template_env: jinja2.Environment,
    output_path: Path,
    entry_point_groups: list[ModelParameterGroup],
    exit_point_primitive_types: list[str] | None = None,
    computed_attributes: list[ComputedAttributeData] | None = None,
    aggregation_data: list[ScopedAggregationData] | None = None,
) -> str:
    """Generate registry creation function.

    Args:
        calc_defs: All calculation definitions to register
        package_name: Package name (parameterized)
        template_env: Jinja2 environment
        output_path: Where to write __init__.py or registry.py (future use)
        entry_point_groups: List of ParameterGroup from ComputationGraph.entry_point_groups.
        exit_point_primitive_types: Primitive types needed for exit point registration.
        computed_attributes: Computed attributes to include in registry.

    Returns:
        Generated Python code
    """
    # Use entry_point_groups from ComputationGraph (single source of truth)
    schema_imports = _generate_schema_imports_from_entry_points(package_name, entry_point_groups)
    group_names = [g.class_name for g in entry_point_groups]

    all_modules = [
        {
            "class_name": f"{calc.name}Module",  # Python class name (unchanged)
            "module_type": derive_module_type(calc.qualified_name),  # Namespaced registry key
        }
        for calc in calc_defs
    ]

    imports = _generate_import_statements(calc_defs, package_name)

    # Add computed attribute modules
    if computed_attributes:
        for ca in computed_attributes:
            if (
                ca.classification == ComputedAttributeClassification.FORMULA
                and ca.compilability == Compilability.FULLY_COMPILABLE
            ):
                sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
                sqn = SysMLQualifiedName(sysml_qn)
                python_path = PythonModulePath.from_sysml(sqn)
                module_type_full = derive_module_type(sysml_qn)
                class_name = module_type_full.split(".")[-1]

                all_modules.append({
                    "class_name": class_name,
                    "module_type": module_type_full,
                })
                import_module = f"{package_name}.modules.{python_path.import_path}"
                imports.append(f"from {import_module} import {class_name}")

    # Add aggregation modules
    if aggregation_data:
        for agg in aggregation_data:
            sysml_qn = agg.module_eqn.replace("__", "::")
            sqn = SysMLQualifiedName(sysml_qn)
            python_path = PythonModulePath.from_sysml(sqn)
            module_type_full = derive_module_type(sysml_qn)
            class_name = module_type_full.split(".")[-1]

            all_modules.append({
                "class_name": class_name,
                "module_type": module_type_full,
            })
            import_module = f"{package_name}.modules.{python_path.import_path}"
            imports.append(f"from {import_module} import {class_name}")

    # Detect name collisions and generate aliases (REQ-REG-03, REQ-REG-04, REQ-REG-07)
    all_modules, imports = _resolve_class_name_collisions(all_modules, imports)

    context = {
        "function_name": f"create_{package_name}_registry",
        "all_modules": all_modules,
        "imports": imports,
        "schema_imports": schema_imports,
        "parameter_groups": group_names,
        "package_name": package_name,
        "exit_point_types": exit_point_primitive_types or [],
    }

    template = template_env.get_template("registry_function.py.jinja2")
    code = template.render(**context)

    # Ensure final newline (PEP 8 compliance)
    if not code.endswith('\n'):
        code += '\n'

    return code


def _resolve_class_name_collisions(
    all_modules: list[dict],
    imports: list[str],
) -> tuple[list[dict], list[str]]:
    """Detect and resolve class name collisions via aliased imports.

    When multiple modules share the same class_name, each is given a unique
    alias derived from its parent segment in the module_type path. The import
    statement is updated to use 'import X as Alias' format.

    Args:
        all_modules: List of {"class_name": str, "module_type": str} dicts.
        imports: List of import statement strings.

    Returns:
        Updated (all_modules, imports) with aliased class names.
    """
    # Group modules by class_name to find collisions
    by_name: dict[str, list[int]] = defaultdict(list)
    for i, module in enumerate(all_modules):
        by_name[module["class_name"]].append(i)

    # Find colliding names (more than one module with the same class_name)
    collisions = {name: indices for name, indices in by_name.items() if len(indices) > 1}

    if not collisions:
        return all_modules, imports

    # Report collisions (REQ-REG-07)
    collision_names = sorted(collisions.keys())
    logger.warning(
        "Module class name collisions detected: %s. "
        "Generating aliased imports for %d modules.",
        collision_names,
        sum(len(indices) for indices in collisions.values()),
    )

    # Build alias for each colliding module
    for class_name, indices in collisions.items():
        for idx in indices:
            module = all_modules[idx]
            module_type = module["module_type"]

            # Extract parent segment: second-to-last segment of module_type
            # e.g., "solarbatterydesign.solar_battery_plant.solar_array.capital_costModule"
            #        → parent_segment = "solar_array"
            segments = module_type.split(".")
            if len(segments) >= 2:
                parent_segment = segments[-2]
            else:
                parent_segment = segments[0] if segments else "unknown"

            # PascalCase the parent segment
            pascal_parent = "".join(
                word.capitalize() for word in parent_segment.split("_")
            )

            alias = f"{pascal_parent}_{class_name}"
            module["class_name"] = alias

            # Update the corresponding import statement
            # Find the import that imports this class_name from the matching path
            import_path_prefix = ".".join(segments[:-1]).replace(".", ".")
            for j, imp in enumerate(imports):
                if (
                    f"import {class_name}" in imp
                    and import_path_prefix in imp
                    and " as " not in imp  # Don't re-alias already aliased imports
                ):
                    imports[j] = f"{imp} as {alias}"
                    break

    return all_modules, imports


def _extract_input_fields(calc_def: CalculationDefinitionData) -> dict[str, str]:
    """Extract input field names and types for registration.

    Args:
        calc_def: Calculation definition

    Returns:
        Dict mapping field name to type (e.g., {'p_neutron': 'Float'})
    """
    inputs = {}
    for attr in calc_def.input_attributes:
        inputs[attr.name] = map_sysml_type_to_rootmodel_wrapper(attr.sysml_type)
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
    return {attr.name: map_sysml_type_to_rootmodel_wrapper(attr.sysml_type)}


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


def generate_registry_from_graph(
    graph,
    package_name: str,
    template_env: jinja2.Environment,
    output_path: Path,
    exit_point_primitive_types: list[str] | None = None,
) -> str:
    """Generate registry from ComputationGraph (graph-only variant).

    Produces byte-identical output to generate_registry_function() by deriving
    all module data, import paths, and schema imports from ComputationGraph.

    Processes modules in the same order as the original: CalcUsage modules first
    (sorted imports), then FORMULA modules, then aggregation modules.

    Args:
        graph: ComputationGraph with modules and entry_point_groups
        package_name: Package name
        template_env: Jinja2 environment
        output_path: Where to write __init__.py
        exit_point_primitive_types: Primitive types for exit point registration.

    Returns:
        Generated Python code
    """
    schema_imports = _generate_schema_imports_from_entry_points(
        package_name, graph.entry_point_groups
    )
    group_names = [g.class_name for g in graph.entry_point_groups]

    all_modules: list[dict] = []
    imports: list[str] = [
        "from simkit.core.registry_builder import create_registry",
        "from simkit.core.pipeline_registry import PipelineModuleRegistry",
        "",
    ]

    # Split modules by type (same processing order as generate_registry_function)
    calcusage_modules = [m for m in graph.modules if not m.is_computed_attribute and not m.is_aggregation]
    formula_modules = [m for m in graph.modules if m.is_computed_attribute]
    aggregation_modules = [m for m in graph.modules if m.is_aggregation]

    # 1. CalcUsage modules (sorted imports, deduplicated by calc_def_name)
    seen_names: set[str] = set()
    calcusage_imports: list[str] = []
    for module in calcusage_modules:
        class_name = f"{module.calc_def_name}Module"
        all_modules.append({
            "class_name": class_name,
            "module_type": module.module_type,
        })
        if module.calc_def_name not in seen_names:
            sqn = SysMLQualifiedName(module.calc_def_qualified_name)
            python_path = PythonModulePath.from_sysml(sqn)
            import_module = f"{package_name}.modules.{python_path.import_path}"
            calcusage_imports.append(f"from {import_module} import {class_name}")
            seen_names.add(module.calc_def_name)

    calcusage_imports.sort()
    imports.extend(calcusage_imports)

    # 2. FORMULA modules (appended unsorted)
    for module in formula_modules:
        sysml_qn = f"{module.calc_def_qualified_name}::{module.calc_def_name}"
        sqn = SysMLQualifiedName(sysml_qn)
        python_path = PythonModulePath.from_sysml(sqn)
        module_type_full = module.module_type
        class_name = module_type_full.split(".")[-1]

        all_modules.append({
            "class_name": class_name,
            "module_type": module_type_full,
        })
        import_module = f"{package_name}.modules.{python_path.import_path}"
        imports.append(f"from {import_module} import {class_name}")

    # 3. Aggregation modules (appended unsorted)
    for module in aggregation_modules:
        sysml_qn = module.name.replace("__", "::")
        sqn = SysMLQualifiedName(sysml_qn)
        python_path = PythonModulePath.from_sysml(sqn)
        module_type_full = module.module_type
        class_name = module_type_full.split(".")[-1]

        all_modules.append({
            "class_name": class_name,
            "module_type": module_type_full,
        })
        import_module = f"{package_name}.modules.{python_path.import_path}"
        imports.append(f"from {import_module} import {class_name}")

    # Resolve class name collisions
    all_modules, imports = _resolve_class_name_collisions(all_modules, imports)

    context = {
        "function_name": f"create_{package_name}_registry",
        "all_modules": all_modules,
        "imports": imports,
        "schema_imports": schema_imports,
        "parameter_groups": group_names,
        "package_name": package_name,
        "exit_point_types": exit_point_primitive_types or [],
    }

    template = template_env.get_template("registry_function.py.jinja2")
    code = template.render(**context)

    if not code.endswith('\n'):
        code += '\n'

    return code


__all__ = [
    "_collect_exit_point_primitive_types",
    "generate_registry_from_graph",
    "generate_registry_function",
]
