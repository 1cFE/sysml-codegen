"""Expression compiler for SysML CalcDef output expressions.

Orchestrates CalcDef compilation: builds each CalcDef's dependency graph (including
undeclared intermediates), topologically sorts it, and compiles each output's expression via
`calc_compat_renderer` (ExpressionIR -> Python), classifying overall compilability.

This module is a leaf in the extraction layer — it does NOT import from
analysis/, resolution/, or generation/.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_mbse.sysml.constraint_extraction import extract_expression_ir
from agentic_mbse.sysml.expression import extract_feature_refs

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


@dataclass
class CompilationResult:
    """Result of compiling one output attribute's expression."""

    output_name: str
    compilability: Compilability
    python_expression: str | None = None
    input_refs: list[str] = field(default_factory=list)
    intermediate_refs: list[str] = field(default_factory=list)
    unsupported_reason: str | None = None
    is_undeclared_intermediate: bool = False


@dataclass
class CalcDefCompilationResult:
    """Aggregate compilation result for an entire CalcDef.

    Carried alongside PipelineContext from Step 6.5 to generation.
    Keyed by calc_def.name so the generator can look up expression
    strings without them living on the resolution model.
    """

    calc_def_name: str
    overall_compilability: Compilability
    output_results: list[CompilationResult]
    execution_order: list[str]


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


def _topological_sort(dep_graph: dict[str, set[str]]) -> list[str] | None:
    """Kahn's algorithm with deterministic tie-breaking via sorted().

    Args:
        dep_graph: {name: set of names it depends on}.

    Returns:
        Topologically sorted list, or None if circular dependency detected.
    """
    # in_degree[node] = number of its deps that are also in the graph
    in_degree: dict[str, int] = {node: 0 for node in dep_graph}
    for node, deps in dep_graph.items():
        for dep in deps:
            if dep in dep_graph:
                in_degree[node] += 1

    queue = sorted(node for node, deg in in_degree.items() if deg == 0)
    result: list[str] = []

    while queue:
        node = queue.pop(0)
        result.append(node)
        for other, deps in dep_graph.items():
            if node in deps and other in in_degree:
                in_degree[other] -= 1
                if in_degree[other] == 0:
                    queue.append(other)
                    queue.sort()

    if len(result) != len(dep_graph):
        return None  # circular dependency
    return result


# ---------------------------------------------------------------------------
# CalcDef orchestrator
# ---------------------------------------------------------------------------


def compile_calc_def(
    calc_def: Any,
    expression_asts: dict[str, Any],
    all_member_names: set[str] | None = None,
    member_expressions: dict[str, Any] | None = None,
) -> CalcDefCompilationResult:
    """Compile all outputs of a CalcDef into Python expressions.

    Builds a dependency graph (including undeclared intermediates),
    topologically sorts, and compiles each output in order.

    Args:
        calc_def: CalculationDefinitionData with input_attributes,
            output_attributes.
        expression_asts: Keyed by output attribute name, values are raw
            syside AST nodes (or None if no expression).
        all_member_names: All owned_member names from raw CalcDef element,
            for undeclared intermediate resolution.
        member_expressions: Mapping from member name → syside AST for
            undeclared intermediates.

    Returns:
        CalcDefCompilationResult with per-output results and overall
        compilability.
    """
    # Local import: calc_compat_renderer imports CompilationError/_sanitize_name from this
    # module, so importing it at module level here would be circular.
    from .calc_compat_renderer import collect_calc_refs, render_calc_expression

    input_names = {attr.name for attr in calc_def.input_attributes}
    output_names = {attr.name for attr in calc_def.output_attributes}

    # --- Build dependency graph ---
    dep_graph: dict[str, set[str]] = {}
    undeclared_intermediates: set[str] = set()

    def _add_node(name: str, is_declared_output: bool) -> None:
        if name in dep_graph:
            return

        if is_declared_output:
            expr = expression_asts.get(name)
        else:
            expr = (
                member_expressions.get(name) if member_expressions else None
            )

        deps: set[str] = set()
        if expr is not None:
            refs = extract_feature_refs(expr, ignore_std_lib=True)
            for ref in refs:
                ref_name = _sanitize_name(ref.name)
                if ref_name == name:
                    continue  # self-reference
                if ref_name in input_names:
                    continue  # inputs don't create dep edges
                if ref_name in output_names:
                    deps.add(ref_name)
                elif all_member_names and ref_name in all_member_names:
                    deps.add(ref_name)
                    undeclared_intermediates.add(ref_name)

        dep_graph[name] = deps

    # First pass: declared outputs
    for output_name in output_names:
        _add_node(output_name, is_declared_output=True)

    # Second pass: undeclared intermediates (iterative discovery)
    to_process = list(undeclared_intermediates)
    while to_process:
        name = to_process.pop()
        if name not in dep_graph:
            _add_node(name, is_declared_output=False)
            # Check for newly discovered intermediates
            for new_name in undeclared_intermediates - set(dep_graph.keys()):
                to_process.append(new_name)

    # --- Topological sort ---
    execution_order = _topological_sort(dep_graph)

    if execution_order is None:
        # Circular dependency
        output_results = [
            CompilationResult(
                output_name=name,
                compilability=Compilability.MANUAL_REQUIRED,
                unsupported_reason="circular dependency detected",
            )
            for name in sorted(output_names)
        ]
        return CalcDefCompilationResult(
            calc_def_name=calc_def.name,
            overall_compilability=Compilability.MANUAL_REQUIRED,
            output_results=output_results,
            execution_order=[],
        )

    # --- Compile each output in topological order ---
    output_results = []

    for name in execution_order:
        is_undeclared = name in undeclared_intermediates

        # Get AST
        if is_undeclared:
            ast_node = (
                member_expressions.get(name)
                if member_expressions
                else None
            )
        else:
            ast_node = expression_asts.get(name)

        if ast_node is None:
            output_results.append(
                CompilationResult(
                    output_name=name,
                    compilability=Compilability.MANUAL_REQUIRED,
                    unsupported_reason="no expression AST",
                    is_undeclared_intermediate=is_undeclared,
                )
            )
            continue

        # M3: member_names is the union declared-outputs + all owned members -- passing
        # only all_member_names (trusting it to contain declared outputs) would
        # under-classify a declared-output reference as unresolved.
        member_names = output_names | (all_member_names or set())
        ir = extract_expression_ir(ast_node)
        if ir is None:
            # extract_expression_ir returns None only for a None input; ast_node was just
            # checked non-None above, so this would mean the extractor's contract broke.
            raise CompilationError(f"extract_expression_ir returned None for {name!r}")

        # Compile to Python
        try:
            python_expr = render_calc_expression(ir, input_names, member_names)
        except CompilationError as e:
            output_results.append(
                CompilationResult(
                    output_name=name,
                    compilability=Compilability.MANUAL_REQUIRED,
                    unsupported_reason=str(e),
                    is_undeclared_intermediate=is_undeclared,
                )
            )
            continue

        # Collect refs
        input_refs, intermediate_refs = collect_calc_refs(ir, input_names, member_names)

        output_results.append(
            CompilationResult(
                output_name=name,
                compilability=Compilability.FULLY_COMPILABLE,
                python_expression=python_expr,
                input_refs=input_refs,
                intermediate_refs=intermediate_refs,
                is_undeclared_intermediate=is_undeclared,
            )
        )

    overall = classify_compilability(output_results)

    return CalcDefCompilationResult(
        calc_def_name=calc_def.name,
        overall_compilability=overall,
        output_results=output_results,
        execution_order=execution_order,
    )
