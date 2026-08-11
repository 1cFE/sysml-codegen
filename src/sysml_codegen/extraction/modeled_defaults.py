"""What an explicitly modeled default's expression IR resolves to.

Shared by the legacy constraint-lowering route and the exact elaborator, so both
read one modeled default by one rule. Scope is exactly what a modeled default
needs (DD-R25): general constant folding and unit *conversion* stay out.
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_mbse.sysml.expression_ir import (
    ExpressionIR,
    LiteralNode,
    OperatorNode,
    UnitAnnotationNode,
    parse_expression,
)

__all__ = ["ModeledDefault", "resolve_modeled_default"]


@dataclass(frozen=True)
class ModeledDefault:
    """What a modeled default's IR resolves to.

    ``value is None`` means unresolved. ``unresolved_node_kind`` names the IR node
    that stopped resolution when there was one to name, and is ``None`` when there
    was simply no default IR at all — an absence is not an unsupported node.
    """

    value: float | None = None
    unit_text: str | None = None
    unresolved_node_kind: str | None = None


def _resolve_default_node(node: ExpressionIR) -> ModeledDefault:
    """Unwrap unit annotations and fold a unary sign over a modeled default.

    Scope is exactly what an explicitly modeled default needs (DD-R25): general
    constant folding and unit *conversion* stay out. A ``UnitAnnotationNode``
    contributes its numeric value and carries its unit text; it is never converted.
    This mirrors what ``generation/predicate_compiler.py`` already does structurally
    for the predicate lane — the drift this closes is that the default lane never
    got it.
    """
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
    """A modeled default's value, unit, and — when unresolved — the IR kind that stopped it.

    Replaces the former ``_literal_float``, which returned a value only for a bare
    ``LiteralNode``: `:= -0.1` parses as an ``OperatorNode`` over a literal and
    `= 40.0 [MW]` as a ``UnitAnnotationNode``, so both silently became ``None`` and
    the generated JSON simply omitted the key (DD-R20, DD-R21).
    """
    if serialized_ir is None:
        return ModeledDefault()
    return _resolve_default_node(parse_expression(serialized_ir))
