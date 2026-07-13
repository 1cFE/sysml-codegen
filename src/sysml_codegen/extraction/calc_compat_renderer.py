"""Calc-compat renderer: ExpressionIR -> Python expression string.

Productionized form of the S2 spike's ``probe4.compat_render``. Reproduces
``expression_compiler.compile_expression``'s dialect byte-for-byte: n-ary left-fold,
``^`` -> ``**``, unit-strip, ``str()`` literals, and the ``python_ast.parse`` validation.

``ExpressionIR`` (agentic-mbse-owned) carries feature references unclassified — only a
``source_name``. Classifying a reference as ``inputs.x`` (an input) or bare ``x`` (an
intermediate) is calc-specific policy, so it happens here at render time from the caller's
name sets, not baked into the tree the way ``build_expression_ast`` used to.

Self-contained on purpose (own operator map, own copy of nothing borrowed from
``expression_compiler`` except the kept ``CompilationError`` symbol and ``_sanitize_name``):
this module is what survives when ``expression_compiler`` sheds ``ExpressionAST`` and its two
compile functions at Stage 4.
"""

from __future__ import annotations

import ast as python_ast

from agentic_mbse.sysml.expression_ir import (
    ExpressionIR,
    FeatureReferenceNode,
    InvocationNode,
    LiteralNode,
    OperatorNode,
    UnitAnnotationNode,
    UnsupportedNode,
)

from .expression_compiler import CompilationError, _sanitize_name

__all__ = ["collect_calc_refs", "render_calc_expression"]

# Mirrors expression_compiler.PYTHON_OPERATOR_MAP's arithmetic subset (the `[` unit-strip
# entry is handled structurally via UnitAnnotationNode, not through this map). Kept as a
# private copy so this module has no import that Stage 4 deletes out from under it.
_ARITHMETIC_OPERATOR_MAP: dict[str, str] = {
    "+": " + ",
    "-": " - ",
    "*": " * ",
    "/": " / ",
    "**": " ** ",
    "^": " ** ",  # SysML power alias -> Python power
}


def render_calc_expression(
    ir: ExpressionIR, input_names: set[str], member_names: set[str]
) -> str:
    """Render a calc output expression's IR to a Python expression string.

    ``input_names`` classify a reference as ``inputs.{name}``; ``member_names`` (declared
    outputs plus undeclared intermediates) classify it as bare ``{name}``. Any other
    reference, unsupported node, or unsupported operator raises CompilationError -- same
    exception the old path raised, so callers' ``except CompilationError`` fallback is
    unchanged.
    """
    result = _render(ir, input_names, member_names)
    try:
        python_ast.parse(result, mode="eval")
    except SyntaxError as e:
        raise CompilationError(
            f"Compiled expression is not valid Python: {result!r} ({e})"
        ) from e
    return result


def _render(node: ExpressionIR, input_names: set[str], member_names: set[str]) -> str:
    if isinstance(node, LiteralNode):
        return _render_literal(node)
    if isinstance(node, FeatureReferenceNode):
        return _render_reference(node, input_names, member_names)
    if isinstance(node, UnitAnnotationNode):
        return _render(node.value, input_names, member_names)
    if isinstance(node, OperatorNode):
        return _render_operator(node, input_names, member_names)
    if isinstance(node, InvocationNode):
        raise CompilationError(f"unsupported node: invocation ({node.function_qn})")
    if isinstance(node, UnsupportedNode):
        raise CompilationError(
            f"Cannot compile unsupported node: {node.source_text} "
            f"(reason: {node.diagnostic})"
        )
    raise CompilationError(f"Unknown IR node type: {type(node).__name__}")


def _render_literal(node: LiteralNode) -> str:
    # Keyed on the recovered type category, not the raw Python type -- the landed
    # extractor keeps LiteralInteger values as int and LiteralRational as float (B4), so
    # this reproduces the old path's str(raw_syside_value) exactly: `4` stays "4",
    # `4.0` stays "4.0".
    if node.operand_type.category == "integer":
        return str(int(node.literal.value))
    if node.operand_type.category == "real":
        return str(float(node.literal.value))
    raise CompilationError(
        f"unsupported literal category in calc expression: {node.operand_type.category!r}"
    )


def _render_reference(
    node: FeatureReferenceNode, input_names: set[str], member_names: set[str]
) -> str:
    if node.reference.chain_segments:
        raise CompilationError(
            "feature chain expression not supported in CalcDef output"
        )
    name = _sanitize_name(node.reference.source_name or "")
    if name in input_names:
        return f"inputs.{name}"
    if name in member_names:
        return name
    raise CompilationError(f"unresolved reference: {name}")


def _render_operator(
    node: OperatorNode, input_names: set[str], member_names: set[str]
) -> str:
    op_str = _ARITHMETIC_OPERATOR_MAP.get(node.operator)
    if op_str is None:
        raise CompilationError(f"unsupported operator: {node.operator}")
    if not node.operands:
        raise CompilationError(f"operator with no operands: {node.operator}")
    if len(node.operands) == 1:
        operand = _render(node.operands[0], input_names, member_names)
        return f"(-{operand})"
    parts = [_render(operand, input_names, member_names) for operand in node.operands]
    result = parts[0]
    for part in parts[1:]:
        result = f"({result}{op_str}{part})"
    return result


def collect_calc_refs(
    ir: ExpressionIR, input_names: set[str], member_names: set[str]
) -> tuple[list[str], list[str]]:
    """Walk an already-rendered-clean IR and collect referenced names.

    Returns ``(input_refs, intermediate_refs)``, both pre-order, first-occurrence
    deduplicated -- matching ``_collect_refs``'s traversal exactly (R3). Only called after
    ``render_calc_expression`` succeeds, so every reachable reference already classifies
    into one of the two sets; this walk does not re-validate that.
    """
    input_refs: list[str] = []
    intermediate_refs: list[str] = []
    seen_inputs: set[str] = set()
    seen_intermediates: set[str] = set()

    def _walk(node: ExpressionIR) -> None:
        if isinstance(node, FeatureReferenceNode):
            name = _sanitize_name(node.reference.source_name or "")
            if name in input_names:
                if name not in seen_inputs:
                    seen_inputs.add(name)
                    input_refs.append(name)
            elif name in member_names and name not in seen_intermediates:
                seen_intermediates.add(name)
                intermediate_refs.append(name)
            return
        if isinstance(node, UnitAnnotationNode):
            _walk(node.value)
            return
        if isinstance(node, OperatorNode):
            for operand in node.operands:
                _walk(operand)
            return
        # LiteralNode / InvocationNode / UnsupportedNode carry no classifiable references.

    _walk(ir)
    return input_refs, intermediate_refs
