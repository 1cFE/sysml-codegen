"""Expression compiler for SysML CalcDef output expressions.

Converts raw SysIDE AST nodes into a clean ExpressionAST intermediate
representation, compiles to Python expression strings, classifies CalcDef
compilability, and handles undeclared intermediates.

This module is a leaf in the extraction layer — it does NOT import from
analysis/, resolution/, or generation/.
"""

from __future__ import annotations

import ast as python_ast
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_mbse.sysml.expression import extract_feature_refs
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from .expression_utils import extract_feature_reference_name


class Compilability(str, Enum):
    """Compilability verdict for a CalcDef or individual output expression.

    Determined by the expression compiler at Step 6.5 of the pipeline.
    UNKNOWN is the sentinel for modules that have not yet been compiled.
    """

    FULLY_COMPILABLE = "fully_compilable"
    PARTIALLY_COMPILABLE = "partially_compilable"
    MANUAL_REQUIRED = "manual_required"
    UNKNOWN = "unknown"


class ExpressionNodeType(str, Enum):
    """Node types in the compiler's intermediate representation."""

    BINARY_OP = "binary_op"
    UNARY_OP = "unary_op"
    LITERAL = "literal"
    INPUT_REF = "input_ref"
    INTERMEDIATE_REF = "intermediate_ref"
    UNSUPPORTED = "unsupported"


class CompilationError(Exception):
    """Raised when an ExpressionAST contains UNSUPPORTED nodes."""

    pass


@dataclass
class ExpressionAST:
    """Compiler's intermediate representation of a SysML expression.

    Constructed during compilation from syside AST nodes, used to produce
    a Python expression string, then discarded. Not stored long-term.

    Binary tree structure: n-ary syside OperatorExpressions are left-folded
    into nested binary nodes at construction time (build_expression_ast).
    """

    node_type: ExpressionNodeType
    operator: str | None = None
    left: ExpressionAST | None = None
    right: ExpressionAST | None = None
    value: float | int | None = None
    input_name: str | None = None
    intermediate_name: str | None = None
    raw_text: str | None = None
    reason: str | None = None

    @classmethod
    def binary(
        cls, operator: str, left: ExpressionAST, right: ExpressionAST
    ) -> ExpressionAST:
        return cls(
            node_type=ExpressionNodeType.BINARY_OP,
            operator=operator,
            left=left,
            right=right,
        )

    @classmethod
    def unary(cls, operator: str, operand: ExpressionAST) -> ExpressionAST:
        return cls(
            node_type=ExpressionNodeType.UNARY_OP,
            operator=operator,
            left=operand,
        )

    @classmethod
    def literal(cls, value: float | int) -> ExpressionAST:
        return cls(node_type=ExpressionNodeType.LITERAL, value=value)

    @classmethod
    def input_ref(cls, name: str) -> ExpressionAST:
        return cls(node_type=ExpressionNodeType.INPUT_REF, input_name=name)

    @classmethod
    def intermediate_ref(cls, name: str) -> ExpressionAST:
        return cls(
            node_type=ExpressionNodeType.INTERMEDIATE_REF,
            intermediate_name=name,
        )

    @classmethod
    def unsupported(cls, raw_text: str, reason: str) -> ExpressionAST:
        return cls(
            node_type=ExpressionNodeType.UNSUPPORTED,
            raw_text=raw_text,
            reason=reason,
        )


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
# Python-specific operator mapping (distinct from expression_utils.OPERATOR_MAP
# which produces SysML text). Used by build_expression_ast (Phase 3).
# ---------------------------------------------------------------------------
PYTHON_OPERATOR_MAP: dict[str, str | None] = {
    "+": " + ",
    "-": " - ",
    "*": " * ",
    "/": " / ",
    "**": " ** ",
    "^": " ** ",   # SysML power alias → Python power
    "[": None,     # unit annotation → strip, use value operand
}


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


def compile_expression(ast: ExpressionAST) -> str:
    """Convert an ExpressionAST to a Python expression string.

    Pure recursive descent on the IR — no syside dependency.

    Raises:
        CompilationError: If the AST contains UNSUPPORTED nodes.
    """
    if ast.node_type == ExpressionNodeType.BINARY_OP:
        left = compile_expression(ast.left)  # type: ignore[arg-type]
        right = compile_expression(ast.right)  # type: ignore[arg-type]
        op_str = PYTHON_OPERATOR_MAP.get(ast.operator, f" {ast.operator} ")  # type: ignore[arg-type]
        result = f"({left}{op_str}{right})"
    elif ast.node_type == ExpressionNodeType.UNARY_OP:
        operand = compile_expression(ast.left)  # type: ignore[arg-type]
        result = f"(-{operand})"
    elif ast.node_type == ExpressionNodeType.LITERAL:
        result = str(ast.value)
    elif ast.node_type == ExpressionNodeType.INPUT_REF:
        result = f"inputs.{ast.input_name}"
    elif ast.node_type == ExpressionNodeType.INTERMEDIATE_REF:
        result = str(ast.intermediate_name)
    elif ast.node_type == ExpressionNodeType.UNSUPPORTED:
        raise CompilationError(
            f"Cannot compile unsupported node: {ast.raw_text} "
            f"(reason: {ast.reason})"
        )
    else:
        raise CompilationError(f"Unknown node type: {ast.node_type}")

    # Validate output is parseable Python
    try:
        python_ast.parse(result, mode="eval")
    except SyntaxError as e:
        raise CompilationError(
            f"Compiled expression is not valid Python: {result!r} ({e})"
        ) from e

    return result


def _collect_refs(
    ast: ExpressionAST,
) -> tuple[list[str], list[str]]:
    """Walk an ExpressionAST and collect all referenced names.

    Returns:
        (input_refs, intermediate_refs) — both deduplicated, order-preserving.
        Order follows left-to-right tree traversal (pre-order).
    """
    input_refs: list[str] = []
    intermediate_refs: list[str] = []
    seen_inputs: set[str] = set()
    seen_intermediates: set[str] = set()

    def _walk(node: ExpressionAST) -> None:
        if node.node_type == ExpressionNodeType.INPUT_REF:
            if node.input_name and node.input_name not in seen_inputs:
                seen_inputs.add(node.input_name)
                input_refs.append(node.input_name)
        elif node.node_type == ExpressionNodeType.INTERMEDIATE_REF:
            if (
                node.intermediate_name
                and node.intermediate_name not in seen_intermediates
            ):
                seen_intermediates.add(node.intermediate_name)
                intermediate_refs.append(node.intermediate_name)
        if node.left:
            _walk(node.left)
        if node.right:
            _walk(node.right)

    _walk(ast)
    return input_refs, intermediate_refs


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
# Syside AST → ExpressionAST IR conversion
# ---------------------------------------------------------------------------


def build_expression_ast(
    syside_node: Any,
    input_names: set[str],
    output_names: set[str],
    all_member_names: set[str] | None = None,
) -> ExpressionAST:
    """Convert a raw syside AST node into the clean ExpressionAST IR.

    Handles n-ary to binary left-fold conversion, reference resolution
    (input vs intermediate vs undeclared vs unsupported), literal extraction,
    and unit annotation stripping.

    Args:
        syside_node: Raw syside AST node (duck-typed).
        input_names: Declared input attribute names for this CalcDef.
        output_names: Declared output attribute names for this CalcDef.
        all_member_names: All owned_member names from raw CalcDef element,
            for undeclared intermediate resolution.

    Returns:
        ExpressionAST tree ready for compile_expression().
    """
    # --- FeatureChainExpression ---
    # MUST be before OperatorExpression — FCE is a subtype of OE in SysIDE's
    # type system. Without this, FCE nodes enter the OE handler and produce
    # "unsupported operator: ." instead of the correct diagnostic.
    if SysideAdapter.is_instance(syside_node, "FeatureChainExpression"):
        return ExpressionAST.unsupported(
            type(syside_node).__name__,
            "feature chain expression not supported in CalcDef output",
        )

    # --- OperatorExpression ---
    if SysideAdapter.is_instance(syside_node, "OperatorExpression"):
        operator = ""
        if hasattr(syside_node, "operator") and syside_node.operator:
            operator = str(syside_node.operator)

        operands: list[Any] = []
        if hasattr(syside_node, "operands"):
            operands = list(syside_node.operands)

        # Unit annotation: strip, recurse on value operand (first)
        if operator == "[":
            if operands:
                return build_expression_ast(
                    operands[0], input_names, output_names, all_member_names
                )
            return ExpressionAST.unsupported(
                "[]", "unit annotation with no operands"
            )

        # Check if operator is supported
        if operator not in PYTHON_OPERATOR_MAP:
            return ExpressionAST.unsupported(
                operator, f"unsupported operator: {operator}"
            )

        if len(operands) == 1:
            # Unary
            operand_ast = build_expression_ast(
                operands[0], input_names, output_names, all_member_names
            )
            return ExpressionAST.unary(operator, operand_ast)

        if len(operands) == 2:
            left = build_expression_ast(
                operands[0], input_names, output_names, all_member_names
            )
            right = build_expression_ast(
                operands[1], input_names, output_names, all_member_names
            )
            return ExpressionAST.binary(operator, left, right)

        if len(operands) > 2:
            # N-ary: left-fold ((a op b) op c)
            result = build_expression_ast(
                operands[0], input_names, output_names, all_member_names
            )
            for i in range(1, len(operands)):
                right = build_expression_ast(
                    operands[i], input_names, output_names, all_member_names
                )
                result = ExpressionAST.binary(operator, result, right)
            return result

        return ExpressionAST.unsupported(
            operator, "operator with no operands"
        )

    # --- FeatureReferenceExpression ---
    if SysideAdapter.is_instance(syside_node, "FeatureReferenceExpression"):
        raw_name = extract_feature_reference_name(syside_node)
        name = _sanitize_name(raw_name)
        if name in input_names:
            return ExpressionAST.input_ref(name)
        if name in output_names:
            return ExpressionAST.intermediate_ref(name)
        if all_member_names and name in all_member_names:
            return ExpressionAST.intermediate_ref(name)
        return ExpressionAST.unsupported(
            name, f"unresolved reference: {name}"
        )

    # --- LiteralRational / LiteralInteger ---
    if (
        SysideAdapter.is_instance(syside_node, "LiteralRational")
        or SysideAdapter.is_instance(syside_node, "LiteralInteger")
    ):
        if hasattr(syside_node, "value"):
            return ExpressionAST.literal(syside_node.value)
        return ExpressionAST.unsupported("literal", "literal with no value")

    # --- Unknown ---
    type_name = type(syside_node).__name__
    return ExpressionAST.unsupported(
        type_name, f"unknown node type: {type_name}"
    )


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

        # Build IR
        ir = build_expression_ast(
            ast_node,
            input_names,
            output_names,
            all_member_names=all_member_names,
        )

        # Compile to Python
        try:
            python_expr = compile_expression(ir)
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
        input_refs, intermediate_refs = _collect_refs(ir)

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
