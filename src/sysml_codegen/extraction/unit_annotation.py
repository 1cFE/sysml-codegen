"""The one rule for a unit annotation, and the two spellings that apply it.

**A unit annotation contributes its value and never a reference.** `= 0.2 [m]`
means the number `0.2`; `[m]` says how to read it. The unit is not a data
dependency, so it is unwrapped once, up front, and it is never converted
(DD-R25: general constant folding and unit conversion both stay out).

Getting that wrong is not a cosmetic loss. Left wrapped, the annotation reaches
the reference walk, whose second operand is a standard-library element
(`SI::metre`), and the elaborator's feature-slot index carries only the user
model's features — so the walk fails with `SI_OCCURRENCE_MISSING` against a
unit. That is the same category error Slice 3D fixed for enumeration members: a
reference naming something other than a data source has no occurrence to
resolve against.

This module owns the **parsed `ExpressionIR`** spelling, which modeled defaults
and the predicate compiler read — the `default 40.0 [W]` lane.

The raw-AST spelling is gone from here. It read the parser's operand sequence
directly, which is Agentic's to own after this item: the reference walk applies
the rule inside `inspect_reference_uses`, and the one place that still needs the
structural unwrap for a value-shape decision gets it from
`elaboration/expression_evidence.py`, over Agentic's owned operand materializer.
This function decides nothing about a malformed annotation — that policy belongs
to the caller, which knows how it refuses.
"""

from __future__ import annotations

from agentic_mbse.sysml.expression_ir import ExpressionIR, UnitAnnotationNode

__all__ = ["UNIT_ANNOTATION_OPERATOR", "annotated_ir_value"]

#: A unit annotation parses as an ``OperatorExpression`` whose operator is ``[``,
#: with the annotated value first and the unit second. Structural throughout: no
#: name is read.
UNIT_ANNOTATION_OPERATOR = "["


def annotated_ir_value(node: ExpressionIR) -> tuple[ExpressionIR, str | None]:
    """Return what an IR unit-annotation node annotates, plus its unit text.

    Other nodes pass through with no unit text. The unit is carried, never
    applied: nothing here converts a value.
    """
    if isinstance(node, UnitAnnotationNode):
        return node.value, node.unit_text
    return node, None
