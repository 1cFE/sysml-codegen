"""Module registration code generator.

Generates pure auto-registration code using create_registry() for all modules.
TEAx introspection handles both single-output (RootModel[T]) and multi-output
(BaseModel with fields) correctly.

Usage:
    from sysml_codegen.generation.registry import generate_registry

    code = generate_registry(
        graph, "package_name", template_env, output_path
    )
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
    from sysml_codegen.resolution.models import ComputationGraph
    from sysml_codegen.resolution.models import ParameterGroup as ModelParameterGroup

logger = logging.getLogger(__name__)

_EXIT_POINT_WRAPPERS = {
    "float": "Float",
    "int": "Int",
    "str": "String",
    "bool": "Bool",
}


def exit_point_wrapper_type(python_type: str) -> str | None:
    """Return the supported root-output wrapper, or ``None`` for a refusal."""
    return _EXIT_POINT_WRAPPERS.get(python_type)


def required_exit_point_wrapper_types(
    graph: ComputationGraph,
) -> tuple[str, ...]:
    """Derive and validate the root-output wrappers required by one graph.

    For single-output modules (field_name="root"), returns the wrapper type
    name from primitives.py (e.g., "Float" for python_type="float").

    Multi-output modules use BaseModel schemas which are already registered
    via entry_point_groups or schema generation.
    """
    from sysml_codegen.generation.errors import unsupported_exit_point_type_error

    types: set[str] = set()
    for module in graph.modules:
        for out in module.outputs:
            if out.field_name == "root":
                wrapper = exit_point_wrapper_type(out.python_type)
                if wrapper is None:
                    raise unsupported_exit_point_type_error(module, out)
                types.add(wrapper)
    return tuple(sorted(types))


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
    collisions = _colliding_class_names(all_modules)
    if not collisions:
        return all_modules, imports

    # Report collisions (REQ-REG-07)
    collision_names = sorted(collisions.keys())
    logger.warning(
        "Module class name collisions detected: %s. Generating aliased imports for %d modules.",
        collision_names,
        sum(len(indices) for indices in collisions.values()),
    )

    # Build alias for each colliding module
    for class_name, indices in collisions.items():
        for idx in indices:
            module = all_modules[idx]
            module_type = module["module_type"]
            alias = _parent_segment_alias(module_type, class_name)
            module["class_name"] = alias

            # Update the corresponding import statement
            import_path_prefix = ".".join(module_type.split(".")[:-1])
            for j, imp in enumerate(imports):
                if (
                    f"import {class_name}" in imp
                    and import_path_prefix in imp
                    and " as " not in imp  # Don't re-alias already aliased imports
                ):
                    imports[j] = f"{imp} as {alias}"
                    break

    return all_modules, imports


def _colliding_class_names(all_modules: list[dict]) -> dict[str, list[int]]:
    """Class names shared by more than one entry, mapped to their entry indices."""
    by_name: dict[str, list[int]] = defaultdict(list)
    for i, module in enumerate(all_modules):
        by_name[module["class_name"]].append(i)
    return {name: indices for name, indices in by_name.items() if len(indices) > 1}


def _parent_segment_alias(module_type: str, class_name: str) -> str:
    """The disambiguating name one colliding module gets: PascalParent_ClassName."""
    segments = module_type.split(".")
    if len(segments) >= 2:
        parent_segment = segments[-2]
    else:
        parent_segment = segments[0] if segments else "unknown"
    pascal_parent = "".join(word.capitalize() for word in parent_segment.split("_"))
    return f"{pascal_parent}_{class_name}"


def _residual_collisions(all_modules: list[dict]) -> dict[str, list[str]]:
    """REQ-REG-08: class names still shared by two modules after aliasing.

    The alias keys on the parent segment only, so two modules with the same class
    name AND parent but different grandparents alias identically -- a residual
    SC-11 collision the aliasing cannot resolve. Pure: reports, decides nothing.
    """
    post_alias: dict[str, list[str]] = defaultdict(list)
    for module in all_modules:
        post_alias[module["class_name"]].append(module["module_type"])
    return {name: mts for name, mts in post_alias.items() if len(mts) > 1}


def _registry_class_entries(graph: ComputationGraph) -> list[dict]:
    """The ``{class_name, module_type}`` entry each module contributes, in registry order.

    One derivation, two consumers: ``generate_registry`` renders these, and
    ``residual_class_name_collisions`` checks them at the generation boundary
    before anything is written. Order matches the four import passes below,
    because the rendered registry is sorted from this list.
    """
    from sysml_codegen.resolution.models import ModuleKind

    entries: list[dict] = []

    # Keyed exactly as the import pass keys it, ``None`` included: a calculation
    # module without a calc_def_name is one entry, not one per occurrence.
    seen_names: set[str | None] = set()
    for module in graph.modules:
        if module.module_kind is not ModuleKind.CALCULATION:
            continue
        if module.calc_def_name in seen_names:
            continue
        seen_names.add(module.calc_def_name)
        entries.append(
            {"class_name": f"{module.calc_def_name}Module", "module_type": module.module_type}
        )

    for kind in (ModuleKind.FORMULA, ModuleKind.AGGREGATION):
        entries.extend(
            {"class_name": module.module_type.split(".")[-1], "module_type": module.module_type}
            for module in graph.modules
            if module.module_kind is kind
        )

    entries.extend(
        {"class_name": module.module_type.split(".")[-1], "module_type": module.module_type}
        for module in graph.modules
        if module.module_kind in (ModuleKind.CONSTRAINT, ModuleKind.REPORT_AGGREGATOR)
    )
    return entries


def residual_class_name_collisions(graph: ComputationGraph) -> dict[str, list[str]]:
    """Registry class names that survive aliasing, by name -> colliding module types.

    Pure (raises nothing, logs nothing), so the generation boundary can run it
    *before* the output tree is cleared. The Item-5 static scan proved no
    committed model hits this, but the exact route reaches module sets the legacy
    route never built, and a silent import overwrite is worse than a refusal.
    """
    entries = _registry_class_entries(graph)
    for class_name, indices in _colliding_class_names(entries).items():
        for idx in indices:
            entries[idx]["class_name"] = _parent_segment_alias(
                entries[idx]["module_type"], class_name
            )
    return _residual_collisions(entries)


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
    graph: ComputationGraph,
    package_name: str,
    template_env: jinja2.Environment,
    output_path: Path,
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
    Returns:
        Generated Python code
    """
    from sysml_codegen.generation.errors import (
        residual_class_name_collision_error,
        validate_constraint_graph_or_raise,
    )

    exit_point_types = required_exit_point_wrapper_types(graph)
    validate_constraint_graph_or_raise(graph)

    schema_imports = _generate_schema_imports_from_entry_points(
        package_name, graph.entry_point_groups
    )
    group_names = [g.class_name for g in graph.entry_point_groups]

    # One derivation of what the registry names each module, shared with the
    # boundary check the CLI runs before it touches the output tree.
    all_modules: list[dict] = _registry_class_entries(graph)
    imports: list[str] = [
        "from simkit.core.registry_builder import create_registry",
        "from simkit.core.pipeline_registry import PipelineModuleRegistry",
        "",
    ]

    from sysml_codegen.resolution.models import ModuleKind

    # Split modules by type (same processing order as original)
    calcusage_modules = [m for m in graph.modules if m.module_kind == ModuleKind.CALCULATION]
    formula_modules = [m for m in graph.modules if m.module_kind == ModuleKind.FORMULA]
    aggregation_modules = [m for m in graph.modules if m.module_kind == ModuleKind.AGGREGATION]
    constraint_modules = [
        m
        for m in graph.modules
        if m.module_kind in (ModuleKind.CONSTRAINT, ModuleKind.REPORT_AGGREGATOR)
    ]

    # 1. CalcUsage modules (sorted imports, deduplicated by calc_def_name)
    seen_names: set[str] = set()
    calcusage_imports: list[str] = []
    for module in calcusage_modules:
        assert module.calc_def_name is not None
        assert module.calc_def_qualified_name is not None
        if module.calc_def_name not in seen_names:
            class_name = f"{module.calc_def_name}Module"
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

        import_module = f"{package_name}.modules.{python_path.import_path}"
        aggregation_imports.append(f"from {import_module} import {class_name}")
    aggregation_imports.sort()
    imports.extend(aggregation_imports)

    # 4. Constraint + report-aggregator modules (Item 7 / D9). module_type is already a
    # Python-dotted path (not a SysML "::" qualified name) — derive directly, matching
    # cli._get_python_path's constraint-kind branch. Sorted for deterministic output.
    constraint_imports: list[str] = []
    for module in constraint_modules:
        module_type_full = module.module_type
        class_name = module_type_full.split(".")[-1]
        parts = module_type_full.split(".")
        directory = "/".join(parts[:-1])
        filename = parts[-1].lower()
        import_path = f"{directory}.{filename}" if directory else filename

        import_module = f"{package_name}.modules.{import_path}"
        constraint_imports.append(f"from {import_module} import {class_name}")
    constraint_imports.sort()
    imports.extend(constraint_imports)

    from sysml_codegen.resolution.models import ships_constraint_machinery

    if ships_constraint_machinery(graph):
        schema_imports.append(
            f"from {package_name}.schemas.constraint_types "
            "import ConstraintEvaluation as ConstraintEvaluation, "
            "ConstraintReport as ConstraintReport"
        )
        schema_imports.sort()
        group_names = [*group_names, "ConstraintEvaluation", "ConstraintReport"]

    # Resolve class name collisions
    all_modules, imports = _resolve_class_name_collisions(all_modules, imports)

    # REQ-REG-08: refuse rather than emit a registry whose imports overwrite each
    # other. The public route already refused at the generation boundary, before
    # clearing the output tree; this is the backstop for a direct caller.
    residual = _residual_collisions(all_modules)
    if residual:
        raise residual_class_name_collision_error(residual)

    # Sort module entries by module_type for deterministic output
    all_modules.sort(key=lambda m: m["module_type"])

    context = {
        "function_name": f"create_{package_name}_registry",
        "all_modules": all_modules,
        "imports": imports,
        "schema_imports": schema_imports,
        "parameter_groups": group_names,
        "package_name": package_name,
        "exit_point_types": exit_point_types,
    }

    template = template_env.get_template("registry_function.py.jinja2")
    code = template.render(**context)

    if not code.endswith("\n"):
        code += "\n"

    return code


# Every exported name is the same four-argument graph-derived seam.
generate_registry_from_graph = generate_registry
generate_registry_function = generate_registry


__all__ = [
    "exit_point_wrapper_type",
    "generate_registry",
    "required_exit_point_wrapper_types",
    "residual_class_name_collisions",
    "generate_registry_from_graph",
    "generate_registry_function",
]
