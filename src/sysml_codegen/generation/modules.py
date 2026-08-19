"""TEAx module wrapper generator for calculation definitions.

Generates TEAx module wrappers that integrate handwritten implementations
with the TEAx framework. Handles both single-output and multi-output patterns
using Pydantic v2 RootModel wrappers.

Usage:
    from sysml_codegen.generation.modules import generate_teax_module

    code = generate_teax_module(module, template_env, output_path)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import jinja2

from sysml_codegen.core.identifier_types import PythonModulePath, SysMLQualifiedName
from sysml_codegen.core.qualified_names import sanitize_qualified_name

if TYPE_CHECKING:
    from sysml_codegen.generation.coverage import CoverageAccountData
    from sysml_codegen.resolution.models import ConstraintCatalog, PipelineModule


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
    from sysml_codegen.generation.errors import unrenderable_module_kind_error
    from sysml_codegen.resolution.models import ModuleKind

    if module.module_kind == ModuleKind.FORMULA:
        return f"{module.calc_def_qualified_name}::{module.calc_def_name}"
    elif module.module_kind == ModuleKind.AGGREGATION:
        return module.name.replace("__", "::")
    elif module.module_kind == ModuleKind.CALCULATION:
        return module.calc_def_qualified_name
    else:
        raise unrenderable_module_kind_error(module, "module-wrapper")


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


# ---------------------------------------------------------------------------
# Constraint + report-aggregator rendering (Item 7 / D2, D3, D9).
# ---------------------------------------------------------------------------

PREDICATES_MODULE_IMPORT_PATH = "modules.constraints.predicates"


def constraint_predicate_function_name(raw_definition_key: str) -> str:
    """Return the emitted Python function name for one raw predicate definition key."""
    return f"constraint_pred_{sanitize_qualified_name(raw_definition_key).lower()}"


def assert_unique_predicate_function_names(catalog: ConstraintCatalog) -> None:
    """Reject distinct raw definition keys that map to one emitted function name."""
    from sysml_codegen.generation.constraint_catalog import predicate_definition_key

    raw_keys = {predicate_definition_key(entry) for entry in catalog.concrete_entries}
    keys_by_function_name: dict[str, list[str]] = {}
    for raw_key in raw_keys:
        function_name = constraint_predicate_function_name(raw_key)
        keys_by_function_name.setdefault(function_name, []).append(raw_key)

    collisions = [
        (function_name, sorted(keys))
        for function_name, keys in keys_by_function_name.items()
        if len(keys) > 1
    ]
    if not collisions:
        return

    function_name, keys = min(collisions, key=lambda collision: collision[0])
    raise _generation_error(
        "Predicate function-name collision: raw definition keys "
        f"{keys!r} all normalize to {function_name!r}. "
        "Rename one; generation cannot emit them safely."
    )


def compile_shared_predicates(catalog: ConstraintCatalog) -> dict[str, tuple[str, str, list[str]]]:
    """One compiled function per distinct source definition (D3, INV-1).

    Runs the same-IR guard (INV-2) first, then compiles once per
    ``predicate_definition_key`` — every concrete entry sharing that key (a part_def owner's
    N occurrences) imports the same emitted function rather than duplicating it. Returns
    ``{definition_key: (fn_name, full_source, arg_names)}``; ``full_source`` is a standalone
    ``compile_predicate`` output (runtime prelude included).
    """
    from agentic_mbse.sysml.expression_ir import parse_expression

    from sysml_codegen.generation.constraint_catalog import (
        assert_same_ir,
        predicate_definition_key,
    )
    from sysml_codegen.generation.predicate_compiler import (
        PredicateCompileError,
        compile_predicate_body,
    )

    validated_entries = [
        type(entry).model_validate(entry.model_dump(mode="python"))
        for entry in catalog.concrete_entries
    ]
    validated_catalog = catalog.model_copy(update={"concrete_entries": validated_entries})
    assert_unique_predicate_function_names(validated_catalog)
    assert_same_ir(validated_entries)
    compiled: dict[str, tuple[str, str, list[str]]] = {}
    for entry in validated_entries:
        key = predicate_definition_key(entry)
        if key in compiled:
            continue
        if entry.predicate_ir is None:  # guarded by assert_same_ir; keep invariant under -O
            raise RuntimeError(
                "CONSTRAINT_PREDICATE_MISSING: eligible catalog constraint "
                f"{entry.constraint_id!r} has no predicate_ir"
            )
        fn_name = constraint_predicate_function_name(key)
        ir = parse_expression(entry.predicate_ir)
        try:
            src, args = compile_predicate_body(ir, fn_name)
        except PredicateCompileError as error:
            from sysml_codegen.generation import CodeGenerationError

            raise CodeGenerationError(
                f"PREDICATE_COMPILE_FAILED: {error}",
                name_safety_violation=error.name_safety_violation,
            ) from error
        compiled[key] = (fn_name, src, args)
    return compiled


def render_constraint_predicates_module(
    compiled: dict[str, tuple[str, str, list[str]]],
    template_env: jinja2.Environment,
) -> str:
    """Render the shared predicates module: one Kleene runtime block + N function bodies."""
    from sysml_codegen.generation.constraint_name_safety import (
        PREDICATE_SCOPE_POLICY,
        ScopePolicyMismatchError,
        verify_emitted_scope,
    )
    from sysml_codegen.generation.predicate_compiler import (
        KLEENE_RUNTIME_SOURCE,
        function_source_only,
    )

    for _key, (fn_name, src, args) in compiled.items():
        try:
            verify_emitted_scope(
                src,
                PREDICATE_SCOPE_POLICY,
                set(args),
                function_name=fn_name,
            )
        except ScopePolicyMismatchError as error:
            raise _generation_error(str(error)) from error

    functions = [
        {"usage_qualified_name": key, "source": function_source_only(src).strip("\n")}
        for key, (_fn_name, src, _args) in compiled.items()
    ]
    template = template_env.get_template("constraint_predicates.py.jinja2")
    code = template.render(runtime_source=KLEENE_RUNTIME_SOURCE.strip("\n"), functions=functions)
    if not code.endswith("\n"):
        code += "\n"
    return code


def render_constraint_module(
    module: PipelineModule,
    catalog: ConstraintCatalog,
    compiled: dict[str, tuple[str, str, list[str]]],
    template_env: jinja2.Environment,
    package_name: str = "generated_code",
) -> str:
    """Render one class-per-assertion constraint module (D9 naming, B5 reconciliation)."""
    from sysml_codegen.generation.constraint_catalog import predicate_definition_key

    entry = next(
        (e for e in catalog.concrete_entries if e.constraint_id.lower() == module.name), None
    )
    if entry is None:
        raise _generation_error(
            f"module {module.name!r} (kind=constraint) has no matching catalog entry — "
            "the catalog and the graph's constraint modules have diverged"
        )
    fn_name, _src, args = compiled[predicate_definition_key(entry)]

    from agentic_mbse.sysml.expression_ir import parse_expression

    from sysml_codegen.generation.constraint_name_safety import (
        PREDICATE_SCOPE_POLICY,
        WRAPPER_SCOPE_POLICY,
        ConstraintBinding,
        ScopePolicyMismatchError,
        predicate_bindings,
        select_name_safety_violation,
        validate_binding_correspondence,
        validate_scope_bindings,
        verify_emitted_scope,
    )
    from sysml_codegen.generation.errors import constraint_name_safety_error

    predicate_scope_bindings = predicate_bindings(parse_expression(entry.predicate_ir))
    wrapper_scope_bindings = []
    missing_provenance = []
    for module_input in module.inputs:
        if module_input.formal_identity is None:
            missing_provenance.append(module_input.param_name)
        else:
            wrapper_scope_bindings.append(
                ConstraintBinding("wrapper", module_input.param_name, module_input.formal_identity)
            )
    violations = validate_scope_bindings(predicate_scope_bindings, PREDICATE_SCOPE_POLICY)
    violations.extend(validate_scope_bindings(wrapper_scope_bindings, WRAPPER_SCOPE_POLICY))
    if missing_provenance:
        from sysml_codegen.generation.constraint_name_safety import ConstraintNameViolation

        violations.extend(
            ConstraintNameViolation(
                scope="wrapper",
                kind="missing_provenance",
                final_binding=name,
                identities=(),
                constraint_id=entry.constraint_id,
                usage_qualified_name=entry.usage_qualified_name,
            )
            for name in missing_provenance
        )
    from dataclasses import replace

    violations = [
        replace(
            violation,
            constraint_id=entry.constraint_id,
            usage_qualified_name=entry.usage_qualified_name,
        )
        for violation in violations
    ]
    violation = select_name_safety_violation(violations)
    if not missing_provenance:
        violations.extend(
            replace(
                candidate,
                constraint_id=entry.constraint_id,
                usage_qualified_name=entry.usage_qualified_name,
            )
            for candidate in validate_binding_correspondence(
                predicate_scope_bindings, wrapper_scope_bindings
            )
        )
        violation = select_name_safety_violation(violations)
    if violation is not None:
        raise constraint_name_safety_error(violation)

    input_names = [inp.param_name for inp in module.inputs]
    missing = [a for a in args if a not in input_names]
    if missing:
        raise _generation_error(
            f"{entry.constraint_id}: predicate leaf(s) {missing} have no matching module "
            f"input among {input_names} — leaf-name/input-name reconciliation failed (B5)"
        )

    class_name = module.module_type.split(".")[-1]
    base_name = class_name.removesuffix("ConstraintModule")
    observed_dict = "{" + ", ".join(f'"{a}": float({a})' for a in args) + "}"

    context = {
        "constraint_id": entry.constraint_id,
        "usage_qualified_name": entry.usage_qualified_name,
        "owner_instance_path": entry.owner_instance_path,
        "package_name": package_name,
        "predicates_import_path": f"{package_name}.{PREDICATES_MODULE_IMPORT_PATH}",
        "predicate_fn_name": fn_name,
        "is_negated": entry.is_negated,
        "expected_value": entry.expected_value,
        "input_class_name": f"{base_name}ConstraintInput",
        "output_class_name": f"{base_name}ConstraintOutput",
        "class_name": class_name,
        "module_name": module.name,
        "input_names": input_names,
        "run_signature": ", ".join(f"{n}: float" for n in input_names),
        "run_call": ", ".join(f"{n}={n}" for n in input_names),
        "predicate_call": ", ".join(f"{a}={a}" for a in args),
        "observed_dict": observed_dict,
    }
    template = template_env.get_template("constraint_module.py.jinja2")
    code = template.render(**context)
    if not code.endswith("\n"):
        code += "\n"
    try:
        verify_emitted_scope(
            code,
            WRAPPER_SCOPE_POLICY,
            set(input_names),
            function_name="run",
            class_name=class_name,
        )
    except ScopePolicyMismatchError as error:
        raise _generation_error(str(error)) from error
    return code


def render_report_aggregator(
    module: PipelineModule,
    catalog: ConstraintCatalog,
    coverage: CoverageAccountData,
    template_env: jinja2.Environment,
    package_name: str = "generated_code",
) -> str:
    """Render the exact-schema report aggregator (D5, D11) with its baked coverage account.

    Field names come from ``module.inputs`` (already-sanitized ``param_name``s, the same
    identifiers the pipeline YAML wires evaluations to), not ``catalog.concrete_entries``'
    raw ``constraint_id``s directly — see the sanitization note in
    ``extend_graph_with_constraints``'s aggregator-input construction (Item 5/7 boundary).

    The account is passed in rather than derived here so exactly one derivation exists per
    generation run, shared with the coverage preflight (Item 3, invariant 5).
    """
    constraint_ids = [inp.param_name for inp in module.inputs]
    class_name = module.module_type.split(".")[-1]
    context = {
        "package_name": package_name,
        "expected_ids": repr(tuple(constraint_ids)),
        "constraint_ids": constraint_ids,
        "class_name": class_name,
        "module_name": module.name,
        "catalog_fingerprint": catalog.fingerprint,
        "coverage": repr(coverage.as_mapping()),
    }
    template = template_env.get_template("report_aggregator.py.jinja2")
    code = template.render(**context)
    if not code.endswith("\n"):
        code += "\n"
    return code


def _generation_error(message: str) -> Exception:
    from sysml_codegen.generation import CodeGenerationError

    return CodeGenerationError(message)


def generate_teax_module(
    module,
    template_env: jinja2.Environment,
    output_path: Path,
    package_name: str = "generated_code",
    *,
    catalog: ConstraintCatalog | None = None,
    compiled_predicates: dict[str, tuple[str, str, list[str]]] | None = None,
) -> str:
    """Generate TEAx module wrapper from PipelineModule.

    Handles all module types: CalcUsage, FORMULA, aggregation, constraint, and
    report-aggregator. Derives class names, import paths, and template context from
    PipelineModule fields.

    Args:
        module: PipelineModule with metadata fields populated
        template_env: Jinja2 environment with templates loaded
        output_path: Path where module will be written (for reference)
        package_name: Python package name
        catalog: The graph's ConstraintCatalog — required when ``module.module_kind`` is
            ``CONSTRAINT`` or ``REPORT_AGGREGATOR`` (Item 7 / D6); ``None`` otherwise.
        compiled_predicates: The compile-once map from :func:`compile_shared_predicates` —
            required alongside ``catalog`` when ``module.module_kind`` is ``CONSTRAINT``.

    Returns:
        Generated Python code string
    """
    from sysml_codegen.resolution.models import ModuleKind

    if module.module_kind is ModuleKind.CONSTRAINT:
        if catalog is None or compiled_predicates is None:
            raise _generation_error(
                f"module {module.name!r} (kind=constraint) needs the graph's "
                "ConstraintCatalog and its compiled predicates to render"
            )
        return render_constraint_module(
            module, catalog, compiled_predicates, template_env, package_name
        )
    if module.module_kind is ModuleKind.REPORT_AGGREGATOR:
        raise _generation_error(
            f"module {module.name!r} (kind=report_aggregator) cannot be rendered here: the "
            "aggregator bakes a coverage account derived once per run from the sealed "
            "catalog, and this function has no access to it. Render it through "
            "build_constraint_generation_plan, which is what the CLI does."
        )

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
        output_attributes.append(
            {
                "name": out_name,
                "description": out.description or f"{out_name} output",
            }
        )

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

    if not code.endswith("\n"):
        code += "\n"

    return code


# Keep old name as alias for backward compatibility during transition
generate_teax_module_from_graph = generate_teax_module


__all__ = [
    "generate_teax_module",
    "generate_teax_module_from_graph",
]
