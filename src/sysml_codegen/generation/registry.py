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

from sysml_codegen.generation.module_paths import module_python_path

if TYPE_CHECKING:
    from sysml_codegen.resolution.models import ComputationGraph, PipelineModule
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


def _resolve_class_name_collisions(all_modules: list[dict]) -> list[dict]:
    """Give each entry whose class name another entry shares a disambiguating alias.

    The alias is derived from the entry's parent segment in its module_type path, and
    replaces ``class_name``. Only names change here: each entry's import line is rendered
    from the entry itself afterwards (``_import_lines``), so the alias always lands on the
    import of the file that defines that class.

    Args:
        all_modules: Registry entries (``_registry_class_entries``).

    Returns:
        The same entries, colliding ones renamed.
    """
    collisions = _colliding_class_names(all_modules)
    if not collisions:
        return all_modules

    # Report collisions (REQ-REG-07)
    collision_names = sorted(collisions.keys())
    logger.warning(
        "Module class name collisions detected: %s. Generating aliased imports for %d modules.",
        collision_names,
        sum(len(indices) for indices in collisions.values()),
    )

    for class_name, indices in collisions.items():
        for idx in indices:
            module = all_modules[idx]
            module["class_name"] = _parent_segment_alias(module["module_type"], class_name)

    return all_modules


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


#: The four import groups, in the order the registry renders them. Each group's lines are
#: sorted on their text before any alias is added, which keeps every package that needs
#: no alias byte-identical to the per-pass rendering this replaced.
_IMPORT_GROUPS = ("calculation", "formula", "aggregation", "constraint")


def class_owners(modules: list[PipelineModule]) -> list[PipelineModule]:
    """The modules that own a generated class, in the order given.

    Every module, except that formula and rollup (aggregation) modules are reduced to
    the first copy, by module name, of each module type. Projection has already given
    every copy under one module type the same class body (I1), so that one copy's class
    file, stencil and registry entry serve every copy's pipeline entry. Calc-def modules
    pass through: their class file is per calc def already, and the registry keys them
    by simple name (``_registry_class_entries``).
    """
    from sysml_codegen.resolution.models import ModuleKind

    computed = (ModuleKind.FORMULA, ModuleKind.AGGREGATION)
    first_name: dict[str, str] = {}
    for module in modules:
        if module.module_kind in computed:
            prior = first_name.get(module.module_type)
            if prior is None or module.name < prior:
                first_name[module.module_type] = module.name
    return [
        module
        for module in modules
        if module.module_kind not in computed or first_name[module.module_type] == module.name
    ]


def require_one_class_per_module_type(modules: list[PipelineModule]) -> None:
    """Raise if two formula or rollup modules share a module type but not a class body.

    Projection guarantees this (I1); this is the generation side's check that it held,
    over every module, not only the class owners. A failure is the generator's defect,
    not the model's, so it raises a plain error that the public route reports as an
    internal defect rather than as a class-name collision the modeller could rename away.
    """
    from sysml_codegen.resolution.models import ModuleKind, class_signature

    shapes: dict[str, dict[str, str]] = defaultdict(dict)
    for module in modules:
        if module.module_kind in (ModuleKind.FORMULA, ModuleKind.AGGREGATION):
            shapes[module.module_type].setdefault(class_signature(module), module.name)
    for module_type, by_shape in shapes.items():
        if len(by_shape) > 1:
            raise AssertionError(
                f"module type {module_type!r} names {len(by_shape)} different class bodies "
                f"(first copies {sorted(by_shape.values())}); projection settles one per type"
            )


def _registry_class_entries(graph: ComputationGraph) -> list[dict]:
    """The registry entry each generated class contributes, in import-group order.

    Each entry is ``{class_name, module_type, imported_name, import_path, import_group}``:
    ``imported_name`` is the class's name in its file, ``class_name`` what the registry
    calls it (an alias when two entries share a name), and ``import_path`` the file's
    package-relative module path, from the writers' own path function.

    One derivation, two consumers: ``generate_registry`` renders these, and
    ``residual_class_name_collisions`` checks them at the generation boundary
    before anything is written.
    """
    from sysml_codegen.resolution.models import ModuleKind

    def entry(module: PipelineModule, class_name: str, import_group: str) -> dict:
        return {
            "class_name": class_name,
            "module_type": module.module_type,
            "imported_name": class_name,
            "import_path": module_python_path(module).import_path,
            "import_group": import_group,
        }

    entries: list[dict] = []

    # Calc-def pass: one entry per calc def *simple name*, keyed exactly as before,
    # ``None`` included. Deliberately not merged with the module-type pass below
    # ([REGISTRY-CALC-DEF-SIMPLE-NAME-DEDUP] is a separate backlog row).
    seen_names: set[str | None] = set()
    for module in graph.modules:
        if module.module_kind is not ModuleKind.CALCULATION:
            continue
        if module.calc_def_name in seen_names:
            continue
        seen_names.add(module.calc_def_name)
        entries.append(entry(module, f"{module.calc_def_name}Module", "calculation"))

    # Formula and rollup pass: one entry per module type, from its class owner.
    owners = class_owners(graph.modules)
    for kind, group in ((ModuleKind.FORMULA, "formula"), (ModuleKind.AGGREGATION, "aggregation")):
        entries.extend(
            entry(module, module.module_type.split(".")[-1], group)
            for module in owners
            if module.module_kind is kind
        )

    entries.extend(
        entry(module, module.module_type.split(".")[-1], "constraint")
        for module in graph.modules
        if module.module_kind in (ModuleKind.CONSTRAINT, ModuleKind.REPORT_AGGREGATOR)
    )
    return entries


def _import_lines(entries: list[dict], package_name: str) -> list[str]:
    """One import line per registry entry, aliased where the entry was renamed.

    Grouped as ``_IMPORT_GROUPS`` and sorted within a group on the line text before
    `` as Alias`` is added.
    """
    lines: list[str] = []
    for group in _IMPORT_GROUPS:
        keyed = [
            (
                f"from {package_name}.modules.{item['import_path']} import {item['imported_name']}",
                item,
            )
            for item in entries
            if item["import_group"] == group
        ]
        keyed.sort(key=lambda pair: pair[0])
        lines.extend(
            line
            if item["class_name"] == item["imported_name"]
            else f"{line} as {item['class_name']}"
            for line, item in keyed
        )
    return lines


def residual_class_name_collisions(graph: ComputationGraph) -> dict[str, list[str]]:
    """Registry class names that survive aliasing, by name -> colliding module types.

    Pure (raises nothing, logs nothing), so the generation boundary can run it
    *before* the output tree is cleared: a silent import overwrite is worse than a
    refusal. Two different module types that share a class name and a parent segment
    reach it (for example two different shapes of one feature whose first copies are
    both named ``a``, under different parents).
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
    from sysml_codegen.elaboration.diagnostics import SiteReason
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

    from sysml_codegen.resolution.models import ships_constraint_machinery

    if ships_constraint_machinery(graph):
        schema_imports.append(
            f"from {package_name}.schemas.constraint_types "
            "import ConstraintEvaluation as ConstraintEvaluation, "
            "ConstraintReport as ConstraintReport"
        )
        schema_imports.sort()
        group_names = [*group_names, "ConstraintEvaluation", "ConstraintReport"]

    # Resolve class name collisions, then render each entry's own import line
    all_modules = _resolve_class_name_collisions(all_modules)
    imports: list[str] = [
        "from simkit.core.registry_builder import create_registry",
        "from simkit.core.pipeline_registry import PipelineModuleRegistry",
        "",
        *_import_lines(all_modules, package_name),
    ]

    # REQ-REG-08: refuse rather than emit a registry whose imports overwrite each
    # other. The public route already refused at the generation boundary, before
    # clearing the output tree; this is the backstop for a direct caller.
    residual = _residual_collisions(all_modules)
    if residual:
        raise residual_class_name_collision_error(
            residual, reason=SiteReason.GENERATION_REGISTRY_RENDER_CLASS_NAME_COLLISION
        )

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
