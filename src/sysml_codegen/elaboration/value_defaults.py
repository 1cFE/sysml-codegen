"""Route-neutral modeled scalar default decoding for exact elaboration."""

from __future__ import annotations

from dataclasses import dataclass

from agentic_mbse.sysml.expression_ir import (
    ExpressionIR,
    LiteralNode,
    OperatorNode,
    UnitAnnotationNode,
    parse_expression,
)


@dataclass(frozen=True)
class ModeledDefault:
    """A modeled default's value, unit, and unresolved IR kind."""

    value: float | None = None
    unit_text: str | None = None
    unresolved_node_kind: str | None = None


def _resolve_default_node(node: ExpressionIR) -> ModeledDefault:
    if isinstance(node, LiteralNode):
        try:
            return ModeledDefault(value=float(node.literal.value))
        except (TypeError, ValueError):
            return ModeledDefault(unresolved_node_kind=node.kind)

    if isinstance(node, UnitAnnotationNode):
        inner = _resolve_default_node(node.value)
        if inner.value is None:
            return inner
        return ModeledDefault(value=inner.value, unit_text=node.unit_text or inner.unit_text)

    if isinstance(node, OperatorNode) and len(node.operands) == 1 and node.operator in ("+", "-"):
        inner = _resolve_default_node(node.operands[0])
        if inner.value is None:
            return inner
        signed = -inner.value if node.operator == "-" else inner.value
        return ModeledDefault(value=signed, unit_text=inner.unit_text)

    return ModeledDefault(unresolved_node_kind=node.kind)


def resolve_modeled_default(serialized_ir: str | None) -> ModeledDefault:
    """Decode the narrow literal, unary-sign, and unit forms used by modeled defaults."""

    if serialized_ir is None:
        return ModeledDefault()
    return _resolve_default_node(parse_expression(serialized_ir))
