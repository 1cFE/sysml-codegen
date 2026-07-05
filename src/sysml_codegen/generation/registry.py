"""Module registration code generator.

Generates pure auto-registration code using create_registry() for all modules.
TEAx introspection handles both single-output (RootModel[T]) and multi-output
(BaseModel with fields) correctly.

Usage:
    from sysml_codegen.generation.registry import generate_registry

    code = generate_registry(graph, "package_name", template_env, output_path)
"""

from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

import jinja2

from sysml_codegen.core.identifier_types import (
    PythonModulePath,
    SysMLQualifiedName,
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
            import_path_prefix = ".".join(segments[:-1]).replace(".", ".")
            for j, imp in enumerate(imports):
                if (
                    f"import {class_name}" in imp
                    and import_path_prefix in imp
                    and " as " not in imp  # Don't re-alias already aliased imports
                ):
                    imports[j] = f"{imp} as {alias}"
                    break

    # REQ-REG-08: post-alias uniqueness re-check. The alias keys on the parent
    # segment only (above), so two modules with the same class name AND parent
    # but different grandparents alias identically -- a residual SC-11 collision
    # the aliasing cannot resolve. The Item-5 static scan proved no committed
    # model hits this, so it lands as a hard fail-fast (a silent import
    # overwrite is worse than a clear error).
    post_alias: dict[str, list[str]] = defaultdict(list)
    for module in all_modules:
        post_alias[module["class_name"]].append(module["module_type"])
    residual = {name: mts for name, mts in post_alias.items() if len(mts) > 1}
    if residual:
        raise ValueError(
            "Module class name collision survives aliasing (grandparent collision): "
            + "; ".join(f"{name!r} <- {sorted(mts)}" for name, mts in sorted(residual.items()))
            + ". The parent-segment alias cannot disambiguate these; rename one scope."
        )

    return all_modules, imports


def _generate_schema_imports_from_entry_points(
    package_name: str,
    entry_point_groups: list[ModelParameterGroup],
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


def generate_registry(
    graph,
    package_name: str,
    template_env: jinja2.Environment,
    output_path: Path,
    exit_point_primitive_types: list[str] | None = None,
) -> str:
    """Generate registry from ComputationGraph.

    Derives all module data, import paths, and schema imports from
    ComputationGraph fields. Processes modules in order: CalcUsage first
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

    # Split modules by type (same processing order as original)
    calcusage_modules = [
        m for m in graph.modules
        if not m.is_computed_attribute and not m.is_aggregation
    ]
    formula_modules = [m for m in graph.modules if m.is_computed_attribute]
    aggregation_modules = [m for m in graph.modules if m.is_aggregation]

    # 1. CalcUsage modules (sorted imports, deduplicated by calc_def_name)
    seen_names: set[str] = set()
    calcusage_imports: list[str] = []
    for module in calcusage_modules:
        if module.calc_def_name not in seen_names:
            class_name = f"{module.calc_def_name}Module"
            all_modules.append({
                "class_name": class_name,
                "module_type": module.module_type,
            })
            sqn = SysMLQualifiedName(module.calc_def_qualified_name)
            python_path = PythonModulePath.from_sysml(sqn)
            import_module = f"{package_name}.modules.{python_path.import_path}"
            calcusage_imports.append(f"from {import_module} import {class_name}")
            seen_names.add(module.calc_def_name)

    calcusage_imports.sort()
    imports.extend(calcusage_imports)

    # 2. FORMULA modules (sorted for deterministic output)
    formula_imports: list[str] = []
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
        formula_imports.append(f"from {import_module} import {class_name}")
    formula_imports.sort()
    imports.extend(formula_imports)

    # 3. Aggregation modules (sorted for deterministic output)
    aggregation_imports: list[str] = []
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
        aggregation_imports.append(f"from {import_module} import {class_name}")
    aggregation_imports.sort()
    imports.extend(aggregation_imports)

    # Resolve class name collisions
    all_modules, imports = _resolve_class_name_collisions(all_modules, imports)

    # Sort module entries by module_type for deterministic output
    all_modules.sort(key=lambda m: m["module_type"])

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


# Keep old names as aliases for backward compatibility during transition
generate_registry_from_graph = generate_registry
generate_registry_function = generate_registry


__all__ = [
    "_collect_exit_point_primitive_types",
    "generate_registry",
    "generate_registry_from_graph",
    "generate_registry_function",
]
