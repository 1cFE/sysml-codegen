"""Pure name-safety policy for generated constraint Python scopes."""

from __future__ import annotations

import symtable
from collections.abc import Iterable
from dataclasses import dataclass, replace
from typing import Literal

from agentic_mbse.sysml.expression_ir import (
    ExpressionIR,
    FeatureReferenceNode,
    InvocationNode,
    OperatorNode,
    UnitAnnotationNode,
    parse_expression,
)

from sysml_codegen.resolution.models import (
    ComputationGraph,
    ConstraintFormalIdentity,
    ModuleKind,
    PipelineModule,
)

ScopeName = Literal["predicate", "wrapper"]


@dataclass(frozen=True)
class ConstraintScopePolicy:
    scope: ScopeName
    generated_parameters: frozenset[str]
    generated_locals: frozenset[str]


PREDICATE_SCOPE_POLICY = ConstraintScopePolicy(
    scope="predicate",
    generated_parameters=frozenset(),
    generated_locals=frozenset({"value"}),
)
WRAPPER_SCOPE_POLICY = ConstraintScopePolicy(
    scope="wrapper",
    generated_parameters=frozenset({"self"}),
    generated_locals=frozenset({"body", "verdict"}),
)


@dataclass(frozen=True)
class ConstraintBinding:
    scope: ScopeName
    final_binding: str
    identity: ConstraintFormalIdentity


@dataclass(frozen=True)
class ConstraintNameViolation:
    scope: ScopeName
    kind: str
    final_binding: str
    identities: tuple[ConstraintFormalIdentity, ...]
    generated_binding: str | None = None
    predicate_function_name: str | None = None
    constraint_id: str | None = None
    usage_qualified_name: str | None = None


class ScopePolicyMismatchError(RuntimeError):
    """Emitted function bindings no longer match the reviewed scope policy."""


def _identity_sort_key(identity: ConstraintFormalIdentity) -> tuple[str, str]:
    return (identity.qualified_name or "", identity.raw_name)


def _identity_key(identity: ConstraintFormalIdentity) -> tuple[str, str]:
    if identity.qualified_name is not None:
        return ("qualified", identity.qualified_name)
    return ("raw", identity.raw_name)


def _violation_sort_key(violation: ConstraintNameViolation) -> tuple[object, ...]:
    return (
        0 if violation.scope == "predicate" else 1,
        violation.final_binding,
        tuple(_identity_sort_key(identity) for identity in violation.identities),
        violation.constraint_id or "",
        violation.usage_qualified_name or "",
        violation.kind,
    )


def select_name_safety_violation(
    violations: Iterable[ConstraintNameViolation],
) -> ConstraintNameViolation | None:
    ordered = sorted(violations, key=_violation_sort_key)
    return ordered[0] if ordered else None


def format_name_safety_violation(violation: ConstraintNameViolation) -> str:
    identities = ", ".join(
        f"raw_name={identity.raw_name!r}, qualified_name={identity.qualified_name!r}"
        for identity in violation.identities
    )
    context = []
    if violation.constraint_id is not None:
        context.append(f"constraint_id={violation.constraint_id!r}")
    if violation.usage_qualified_name is not None:
        context.append(f"usage_qualified_name={violation.usage_qualified_name!r}")
    if violation.predicate_function_name is not None:
        context.append(f"predicate_function={violation.predicate_function_name!r}")
    prefix = ", ".join(context)
    prefix = f"{prefix}: " if prefix else ""
    generated = (
        f" collides with generated binding {violation.generated_binding!r};"
        if violation.generated_binding is not None
        else ";"
    )
    return (
        f"Constraint name-safety violation: {prefix}scope={violation.scope!r}, "
        f"kind={violation.kind!r}, final_binding={violation.final_binding!r}{generated} "
        f"identities=[{identities}]"
    )


def predicate_bindings(ir: ExpressionIR) -> list[ConstraintBinding]:
    bindings: list[ConstraintBinding] = []

    def visit(node: ExpressionIR) -> None:
        if isinstance(node, FeatureReferenceNode):
            name = node.reference.source_name
            if name is None:
                return
            target = node.reference.target
            bindings.append(
                ConstraintBinding(
                    scope="predicate",
                    final_binding=name,
                    identity=ConstraintFormalIdentity(
                        raw_name=name,
                        qualified_name=(target.qualified_name if target is not None else None),
                    ),
                )
            )
            return
        if isinstance(node, OperatorNode):
            for operand in node.operands:
                visit(operand)
        elif isinstance(node, UnitAnnotationNode):
            visit(node.value)
        elif isinstance(node, InvocationNode):
            for argument in node.arguments:
                visit(argument)

    visit(ir)
    return bindings


def validate_scope_bindings(
    bindings: Iterable[ConstraintBinding], policy: ConstraintScopePolicy
) -> list[ConstraintNameViolation]:
    materialized = list(bindings)
    violations: list[ConstraintNameViolation] = []
    generated = policy.generated_parameters | policy.generated_locals
    by_name: dict[str, dict[tuple[str, str], ConstraintFormalIdentity]] = {}
    by_identity: dict[tuple[str, str], set[str]] = {}
    identity_values: dict[tuple[str, str], ConstraintFormalIdentity] = {}
    for binding in materialized:
        key = _identity_key(binding.identity)
        by_name.setdefault(binding.final_binding, {})[key] = binding.identity
        by_identity.setdefault(key, set()).add(binding.final_binding)
        identity_values[key] = binding.identity
    for final_binding, identities_by_key in by_name.items():
        identities = tuple(sorted(identities_by_key.values(), key=_identity_sort_key))
        if final_binding in generated:
            violations.append(
                ConstraintNameViolation(
                    scope=policy.scope,
                    kind="generated_binding_overlap",
                    final_binding=final_binding,
                    generated_binding=final_binding,
                    identities=identities,
                )
            )
        if len(identities_by_key) > 1:
            violations.append(
                ConstraintNameViolation(
                    scope=policy.scope,
                    kind="binding_identity_collision",
                    final_binding=final_binding,
                    identities=identities,
                )
            )
    for identity_key, names in by_identity.items():
        if len(names) > 1:
            violations.append(
                ConstraintNameViolation(
                    scope=policy.scope,
                    kind="identity_binding_disagreement",
                    final_binding=min(names),
                    identities=(identity_values[identity_key],),
                )
            )
    return violations


def validate_binding_correspondence(
    predicate: Iterable[ConstraintBinding], wrapper: Iterable[ConstraintBinding]
) -> list[ConstraintNameViolation]:
    """Require the two scope inventories to describe the same identities and names."""
    predicate_bindings_list = list(predicate)
    wrapper_bindings_list = list(wrapper)
    violations: list[ConstraintNameViolation] = []
    matched_wrapper: set[int] = set()
    for predicate_binding in predicate_bindings_list:
        identity = predicate_binding.identity
        exact = [
            (index, candidate)
            for index, candidate in enumerate(wrapper_bindings_list)
            if (
                identity.qualified_name is not None
                and candidate.identity.qualified_name == identity.qualified_name
            )
            or (
                identity.qualified_name is None
                and candidate.identity.qualified_name is None
                and candidate.identity.raw_name == identity.raw_name
            )
        ]
        if len(exact) == 1:
            index, candidate = exact[0]
            matched_wrapper.add(index)
            if candidate.final_binding != predicate_binding.final_binding:
                violations.append(
                    ConstraintNameViolation(
                        scope="predicate",
                        kind="cross_scope_binding_disagreement",
                        final_binding=predicate_binding.final_binding,
                        identities=(identity,),
                    )
                )
            continue
        one_sided = [
            candidate
            for candidate in wrapper_bindings_list
            if candidate.identity.raw_name == identity.raw_name
            and (candidate.identity.qualified_name is None) != (identity.qualified_name is None)
        ]
        violations.append(
            ConstraintNameViolation(
                scope="predicate",
                kind="missing_provenance" if one_sided else "identity_set_disagreement",
                final_binding=predicate_binding.final_binding,
                identities=tuple(
                    sorted(
                        [identity, *(candidate.identity for candidate in one_sided)],
                        key=_identity_sort_key,
                    )
                ),
            )
        )
    for index, wrapper_binding in enumerate(wrapper_bindings_list):
        if index not in matched_wrapper:
            violations.append(
                ConstraintNameViolation(
                    scope="wrapper",
                    kind="identity_set_disagreement",
                    final_binding=wrapper_binding.final_binding,
                    identities=(wrapper_binding.identity,),
                )
            )
    return violations


def verify_emitted_scope(
    source: str,
    policy: ConstraintScopePolicy,
    model_parameters: set[str],
    *,
    function_name: str,
    class_name: str | None = None,
) -> None:
    root = symtable.symtable(source, "<generated-constraint>", "exec")
    tables = root.get_children()
    if class_name is not None:
        classes = [
            table
            for table in tables
            if table.get_name() == class_name and table.get_type() == "class"
        ]
        if len(classes) != 1:
            raise ScopePolicyMismatchError(
                f"expected one generated class {class_name!r}, found {len(classes)}"
            )
        tables = classes[0].get_children()
    functions = [
        table
        for table in tables
        if table.get_name() == function_name and table.get_type() == "function"
    ]
    if len(functions) != 1:
        raise ScopePolicyMismatchError(
            f"expected one generated function {function_name!r}, found {len(functions)}"
        )
    table = functions[0]
    if table.get_children():
        names = sorted(child.get_name() for child in table.get_children())
        raise ScopePolicyMismatchError(f"unsupported child scopes in generated function: {names}")
    parameters: set[str] = set()
    locals_: set[str] = set()
    for symbol in table.get_symbols():
        if symbol.is_nonlocal() or symbol.is_declared_global():
            raise ScopePolicyMismatchError(
                f"unsupported declaration for binding {symbol.get_name()!r}"
            )
        if symbol.is_parameter():
            parameters.add(symbol.get_name())
        elif symbol.is_local():
            locals_.add(symbol.get_name())
    actual_parameters = parameters - model_parameters
    if actual_parameters != set(policy.generated_parameters) or locals_ != set(
        policy.generated_locals
    ):
        raise ScopePolicyMismatchError(
            f"{policy.scope} scope policy mismatch: parameters={sorted(actual_parameters)!r}, "
            f"locals={sorted(locals_)!r}; expected "
            f"parameters={sorted(policy.generated_parameters)!r}, "
            f"locals={sorted(policy.generated_locals)!r}"
        )


def _with_context(
    violation: ConstraintNameViolation, *, constraint_id: str, usage_qualified_name: str
) -> ConstraintNameViolation:
    return replace(
        violation,
        constraint_id=constraint_id,
        usage_qualified_name=usage_qualified_name,
    )


def graph_name_safety_violations(graph: ComputationGraph) -> list[ConstraintNameViolation]:
    catalog = graph.constraint_catalog
    constraint_modules = [
        module for module in graph.modules if module.module_kind == ModuleKind.CONSTRAINT
    ]
    if catalog is None:
        return [
            ConstraintNameViolation(
                scope="wrapper",
                kind="catalog_module_join",
                final_binding=module.name,
                identities=(),
            )
            for module in constraint_modules
        ]
    violations: list[ConstraintNameViolation] = []
    entries_by_module: dict[str, list[object]] = {}
    for entry in catalog.concrete_entries:
        entries_by_module.setdefault(entry.constraint_id.lower(), []).append(entry)
    modules_by_name: dict[str, list[PipelineModule]] = {}
    for module in constraint_modules:
        modules_by_name.setdefault(module.name, []).append(module)
    for entry in catalog.concrete_entries:
        modules = modules_by_name.get(entry.constraint_id.lower(), [])
        entries = entries_by_module[entry.constraint_id.lower()]
        if len(modules) != 1 or len(entries) != 1:
            violations.append(
                ConstraintNameViolation(
                    scope="wrapper",
                    kind="catalog_module_join",
                    final_binding=entry.constraint_id.lower(),
                    identities=(),
                    constraint_id=entry.constraint_id,
                    usage_qualified_name=entry.usage_qualified_name,
                )
            )
            continue
        if entry.predicate_ir is None:
            continue
        module = modules[0]
        pred = predicate_bindings(parse_expression(entry.predicate_ir))
        wrapper: list[ConstraintBinding] = []
        missing = False
        for module_input in module.inputs:
            if module_input.formal_identity is None:
                missing = True
                violations.append(
                    ConstraintNameViolation(
                        scope="wrapper",
                        kind="missing_provenance",
                        final_binding=module_input.param_name,
                        identities=(),
                        constraint_id=entry.constraint_id,
                        usage_qualified_name=entry.usage_qualified_name,
                    )
                )
                continue
            wrapper.append(
                ConstraintBinding("wrapper", module_input.param_name, module_input.formal_identity)
            )
        violations.extend(
            _with_context(
                v,
                constraint_id=entry.constraint_id,
                usage_qualified_name=entry.usage_qualified_name,
            )
            for v in validate_scope_bindings(pred, PREDICATE_SCOPE_POLICY)
        )
        violations.extend(
            _with_context(
                v,
                constraint_id=entry.constraint_id,
                usage_qualified_name=entry.usage_qualified_name,
            )
            for v in validate_scope_bindings(wrapper, WRAPPER_SCOPE_POLICY)
        )
        if missing:
            continue
        violations.extend(
            _with_context(
                violation,
                constraint_id=entry.constraint_id,
                usage_qualified_name=entry.usage_qualified_name,
            )
            for violation in validate_binding_correspondence(pred, wrapper)
        )
    for module in constraint_modules:
        if len(entries_by_module.get(module.name, [])) != 1:
            violations.append(
                ConstraintNameViolation(
                    scope="wrapper",
                    kind="catalog_module_join",
                    final_binding=module.name,
                    identities=(),
                )
            )
    return violations


def select_graph_name_safety_violation(graph: ComputationGraph) -> ConstraintNameViolation | None:
    return select_name_safety_violation(graph_name_safety_violations(graph))
