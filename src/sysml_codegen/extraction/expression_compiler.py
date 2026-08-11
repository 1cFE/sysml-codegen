"""Expression compiler for SysML CalcDef output expressions.

Orchestrates CalcDef compilation: builds each CalcDef's dependency graph (including
undeclared intermediates), topologically sorts it, and compiles each output's expression via
`calc_compat_renderer` (ExpressionIR -> Python), classifying overall compilability.

This module is a leaf in the extraction layer — it does NOT import from
analysis/, resolution/, or generation/.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any
from uuid import UUID

from agentic_mbse.sysml.constraint_extraction import extract_expression_ir
from agentic_mbse.sysml.expression import extract_feature_refs
from agentic_mbse.sysml.syside_adapter import SysideAdapter

# NOTE: calc_compat_renderer imports CompilationError/_sanitize_name from this module, so
# render_calc_expression/collect_calc_refs are imported inside compile_calc_def (not at
# module level) to avoid a circular import.


class Compilability(str, Enum):
    """Compilability verdict for a CalcDef or individual output expression.

    Determined by the expression compiler at Step 6.5 of the pipeline.
    UNKNOWN is the sentinel for modules that have not yet been compiled.
    """

    FULLY_COMPILABLE = "fully_compilable"
    PARTIALLY_COMPILABLE = "partially_compilable"
    MANUAL_REQUIRED = "manual_required"
    UNKNOWN = "unknown"


class CompilationError(Exception):
    """Raised when the renderer cannot produce a Python expression (unresolved reference,
    unsupported operator, or unparseable output)."""

    pass


@dataclass(frozen=True)
class CompilationResult:
    """Compilation result attached to one exact calculation member UUID."""

    output_id: UUID
    output_name: str
    compilability: Compilability
    python_expression: str | None = None
    input_ids: tuple[UUID, ...] = ()
    dependency_ids: tuple[UUID, ...] = ()
    unsupported_reason: str | None = None
    is_undeclared_intermediate: bool = False


@dataclass(frozen=True)
class CalcDefCompilationResult:
    """Exact-ID compilation result for one live calculation definition."""

    definition_id: UUID
    overall_compilability: Compilability
    output_results: tuple[CompilationResult, ...]
    execution_order: tuple[UUID, ...]
    declared_output_ids: tuple[UUID, ...]


# ---------------------------------------------------------------------------
# Pure compiler functions (no syside dependency)
# ---------------------------------------------------------------------------


# INTENTIONAL DIVERGENCE from agentic_mbse.sysml.qualified_names.sanitize_name:
# omits reserved-word suffixing on purpose. Do NOT "deduplicate" these two
# sanitizers — replacing this with the shared version breaks expression
# compilation (push-down design R8/Q6).
def _sanitize_name(name: str) -> str:
    """Normalize a syside referent name to match extractor conventions.

    Mirrors core.qualified_names.sanitize_name() to ensure feature reference
    names from syside AST nodes match the sanitized attribute names stored in
    CalculationDefinitionData.input_attributes / output_attributes.

    Note: does NOT apply reserved-word suffixing (unlike sanitize_name)
    because expression context (e.g. ``inputs.class``) is safe.
    """
    if not name:
        return ""
    name = name.strip("'\"")
    name = name.replace(" ", "_")
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name)
    name = name.strip("_") or "unnamed"
    return name


def classify_compilability(
    output_results: list[CompilationResult],
) -> Compilability:
    """Return worst-case Compilability across a list of CompilationResults."""
    if not output_results:
        return Compilability.MANUAL_REQUIRED
    assert all(
        r.compilability != Compilability.UNKNOWN for r in output_results
    ), "UNKNOWN is a PipelineModule sentinel, not a valid compilation result"
    if all(
        r.compilability == Compilability.FULLY_COMPILABLE
        for r in output_results
    ):
        return Compilability.FULLY_COMPILABLE
    if any(
        r.compilability == Compilability.MANUAL_REQUIRED
        for r in output_results
    ):
        return Compilability.MANUAL_REQUIRED
    return Compilability.PARTIALLY_COMPILABLE


# ---------------------------------------------------------------------------
# Topological sort (Kahn's algorithm)
# ---------------------------------------------------------------------------


def _topological_sort_ids(
    dep_graph: dict[UUID, set[UUID]],
) -> list[UUID] | None:
    """Topologically sort exact member UUIDs with stable UUID ordering."""
    in_degree = {
        node: sum(dependency in dep_graph for dependency in dependencies)
        for node, dependencies in dep_graph.items()
    }
    queue = sorted(node for node, degree in in_degree.items() if degree == 0)
    result: list[UUID] = []
    while queue:
        node = queue.pop(0)
        result.append(node)
        for other, dependencies in dep_graph.items():
            if node not in dependencies:
                continue
            in_degree[other] -= 1
            if in_degree[other] == 0:
                queue.append(other)
                queue.sort()
    return result if len(result) == len(dep_graph) else None


def _required_attribute_ids(attributes: list[Any], role: str) -> tuple[UUID, ...]:
    result: list[UUID] = []
    for attribute in attributes:
        element_id = getattr(attribute, "element_id", None)
        if not isinstance(element_id, UUID):
            raise ValueError(f"{role} {attribute.name!r} has no exact declaration UUID")
        result.append(element_id)
    if len(result) != len(set(result)):
        raise ValueError(f"duplicate exact {role} declaration UUID")
    return tuple(result)


def _exact_reference_ids(expression: Any) -> tuple[UUID, ...]:
    """Return exact referenced declaration UUIDs in expression order."""
    result: list[UUID] = []
    for reference in extract_feature_refs(expression, ignore_std_lib=True):
        if reference.element is None:
            raise CompilationError(
                f"reference {reference.name!r} has no resolved declaration element"
            )
        element_id = SysideAdapter.element_id(reference.element)
        if element_id not in result:
            result.append(element_id)
    return tuple(result)


def compile_calc_def(calc_def: Any) -> CalcDefCompilationResult:
    """Compile one live calculation definition using only exact member UUIDs.

    Names remain renderer metadata. They never classify a reference, select an
    AST, form a dependency edge, or attach the result to a graph node.
    """
    from .calc_compat_renderer import render_calc_expression

    definition_id = getattr(calc_def, "element_id", None)
    if not isinstance(definition_id, UUID):
        raise ValueError("calculation definition has no exact declaration UUID")

    input_ids = _required_attribute_ids(calc_def.input_attributes, "input")
    declared_output_ids = _required_attribute_ids(calc_def.output_attributes, "output")
    input_id_set = set(input_ids)
    output_id_set = set(declared_output_ids)
    all_member_ids = set(calc_def.all_member_ids)
    member_names = dict(calc_def.member_names)
    if not input_id_set | output_id_set <= all_member_ids:
        raise ValueError("calculation member UUID inventory omits a declared port")
    if set(member_names) != all_member_ids:
        raise ValueError("calculation member UUID/name inventory is not total")

    dep_graph: dict[UUID, set[UUID]] = {}
    undeclared_intermediates: set[UUID] = set()

    def expression_for(member_id: UUID, declared_output: bool) -> Any:
        if declared_output:
            return calc_def.output_expression_asts.get(member_id)
        return calc_def.member_expressions.get(member_id)

    def add_node(member_id: UUID, declared_output: bool) -> None:
        if member_id in dep_graph:
            return
        dependencies: set[UUID] = set()
        expression = expression_for(member_id, declared_output)
        if expression is not None:
            for reference_id in _exact_reference_ids(expression):
                if reference_id == member_id or reference_id in input_id_set:
                    continue
                if reference_id not in all_member_ids:
                    raise CompilationError(
                        f"expression member {member_names[member_id]!r} references "
                        f"undeclared exact member {reference_id}"
                    )
                dependencies.add(reference_id)
                if reference_id not in output_id_set:
                    undeclared_intermediates.add(reference_id)
        dep_graph[member_id] = dependencies

    for output_id in declared_output_ids:
        add_node(output_id, True)
    to_process = list(undeclared_intermediates)
    while to_process:
        member_id = to_process.pop()
        if member_id in dep_graph:
            continue
        add_node(member_id, False)
        to_process.extend(undeclared_intermediates - set(dep_graph))

    execution_order = _topological_sort_ids(dep_graph)
    if execution_order is None:
        failures = tuple(
            CompilationResult(
                output_id=output_id,
                output_name=member_names[output_id],
                compilability=Compilability.MANUAL_REQUIRED,
                unsupported_reason="circular dependency detected",
            )
            for output_id in sorted(declared_output_ids)
        )
        return CalcDefCompilationResult(
            definition_id=definition_id,
            overall_compilability=Compilability.MANUAL_REQUIRED,
            output_results=failures,
            execution_order=(),
            declared_output_ids=declared_output_ids,
        )

    rendered_input_names = {member_names[member_id] for member_id in input_ids}
    rendered_member_names = set(member_names.values())
    results: list[CompilationResult] = []
    for member_id in execution_order:
        is_intermediate = member_id in undeclared_intermediates
        expression = expression_for(member_id, not is_intermediate)
        if expression is None:
            results.append(
                CompilationResult(
                    output_id=member_id,
                    output_name=member_names[member_id],
                    compilability=Compilability.MANUAL_REQUIRED,
                    unsupported_reason="no expression AST",
                    is_undeclared_intermediate=is_intermediate,
                )
            )
            continue

        ir = extract_expression_ir(expression)
        if ir is None:
            raise CompilationError(
                f"extract_expression_ir returned None for exact member {member_id}"
            )
        referenced_ids = _exact_reference_ids(expression)
        exact_inputs = tuple(item for item in referenced_ids if item in input_id_set)
        dependencies = tuple(item for item in referenced_ids if item in dep_graph)
        try:
            python_expression = render_calc_expression(
                ir,
                rendered_input_names,
                rendered_member_names,
            )
        except CompilationError as error:
            results.append(
                CompilationResult(
                    output_id=member_id,
                    output_name=member_names[member_id],
                    compilability=Compilability.MANUAL_REQUIRED,
                    input_ids=exact_inputs,
                    dependency_ids=dependencies,
                    unsupported_reason=str(error),
                    is_undeclared_intermediate=is_intermediate,
                )
            )
            continue
        results.append(
            CompilationResult(
                output_id=member_id,
                output_name=member_names[member_id],
                compilability=Compilability.FULLY_COMPILABLE,
                python_expression=python_expression,
                input_ids=exact_inputs,
                dependency_ids=dependencies,
                is_undeclared_intermediate=is_intermediate,
            )
        )

    overall = classify_compilability(
        [
            CompilationResult(
                output_id=result.output_id,
                output_name=result.output_name,
                compilability=result.compilability,
            )
            for result in results
        ]
    )
    return CalcDefCompilationResult(
        definition_id=definition_id,
        overall_compilability=overall,
        output_results=tuple(results),
        execution_order=tuple(execution_order),
        declared_output_ids=declared_output_ids,
    )
