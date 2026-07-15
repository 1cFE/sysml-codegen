"""Calc-compat renderer: ExpressionIR -> Python expression string.

Productionized form of the S2 spike's ``probe4.compat_render``. Reproduces the retired
calc compiler's dialect byte-for-byte (frozen in
``tests/fixtures/golden/calc_compat_parity_golden.json``): n-ary left-fold, ``^`` -> ``**``,
unit-strip, ``str()`` literals, and ``python_ast.parse`` validation.

``ExpressionIR`` (agentic-mbse-owned) carries feature references unclassified — only a
``source_name``. Classifying a reference as ``inputs.x`` (an input) or bare ``x`` (an
intermediate) is calc-specific policy, so it happens here at render time from the caller's
name sets, not baked into the tree the way the retired syside-dispatch build step used to.

Self-contained on purpose (own operator map, own copy of nothing borrowed from
``expression_compiler`` except the kept ``CompilationError`` symbol and ``_sanitize_name``):
this module is what survived ``expression_compiler``'s retired private syntax tree and its
two compile functions.
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

# Mirrors the retired expression_compiler dialect's arithmetic operator spacing (the `[`
# unit-strip entry is handled structurally via UnitAnnotationNode, not through this map).
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
    # Keyed on literal.kind (the syside class name -- "LiteralInteger"/"LiteralRational"),
    # not operand_type.category: category depends on cached_result_type resolution, a
    # separate step that can be "unresolved" even when the literal's own value is already
    # correctly typed. kind is the same substring-fallback convention
    # SysideAdapter.is_instance itself uses for mocks (`type_name in type(elem).__name__`).
    # The landed extractor keeps LiteralInteger values as int and LiteralRational as float
    # (B4), so str() alone reproduces the old path's str(raw_syside_value) exactly: `4`
    # stays "4", `4.0` stays "4.0" -- no numeric coercion needed or wanted.
    kind = node.literal.kind
    if "LiteralInteger" in kind or "LiteralRational" in kind:
        return str(node.literal.value)
    raise CompilationError(
        f"unsupported literal kind in calc expression: {kind!r}"
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
        if node.operator != "-":
            raise CompilationError(f"unsupported unary operator: {node.operator}")
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
    deduplicated -- matching the retired ``_collect_refs``'s traversal exactly (R3). Only
    called after ``render_calc_expression`` succeeds, so every reachable reference already
    classifies into one of the two sets; this walk does not re-validate that.
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
