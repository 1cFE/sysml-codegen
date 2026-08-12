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

The rule has to be applied to two different representations, and they cannot
share one implementation because they are not the same data:

- **the syside AST** (`annotated_ast_value`), which the elaborator walks before
  anything is parsed into IR — the `= 0.2 [m]` lane;
- **a parsed `ExpressionIR`** (`annotated_ir_value`), which modeled defaults and
  the predicate compiler read — the `default 40.0 [W]` lane.

Both spellings live here so the rule has one owner: changing what a unit
annotation means is an edit to this file, not to two files that have to be kept
saying the same thing. Neither function decides what to do about a malformed
annotation — that policy belongs to the caller, which knows how it refuses.
"""

from __future__ import annotations

from typing import Any

from agentic_mbse.sysml.expression_ir import ExpressionIR, UnitAnnotationNode
from agentic_mbse.sysml.syside_adapter import SysideAdapter

__all__ = ["UNIT_ANNOTATION_OPERATOR", "annotated_ast_value", "annotated_ir_value"]

#: A unit annotation parses as an ``OperatorExpression`` whose operator is ``[``,
#: with the annotated value first and the unit second. Structural throughout: no
#: name is read.
UNIT_ANNOTATION_OPERATOR = "["


def annotated_ast_value(expression: Any) -> Any:
    """Return what a syside unit-annotation node annotates; other expressions pass through.

    Raises ``ValueError`` when the annotation carries no annotated value at all.
    The caller decides how that refuses.
    """
    if expression is None or not SysideAdapter.is_instance(expression, "OperatorExpression"):
        return expression
    if str(getattr(expression, "operator", "")) != UNIT_ANNOTATION_OPERATOR:
        return expression
    operands = list(getattr(expression, "operands", ()) or ())
    if not operands:
        raise ValueError("unit annotation carries no annotated value")
    return operands[0]


def annotated_ir_value(node: ExpressionIR) -> tuple[ExpressionIR, str | None]:
    """Return what an IR unit-annotation node annotates, plus its unit text.

    Other nodes pass through with no unit text. The unit is carried, never
    applied: nothing here converts a value.
    """
    if isinstance(node, UnitAnnotationNode):
        return node.value, node.unit_text
    return node, None
