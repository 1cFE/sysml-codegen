"""Offline unit tests for the precedence-aware paren helper (REQ-AST-09).

These pin the C2 polarity convention and C3 unary handling of
`reconstruct_operator_expression` without a license. The five design
hand-traces (design.md:334-340) are the acceptance test for the helper: if a
trace fails here, the HELPER is wrong, not the test.

The stub classes carry their type in the class *name* so
`SysideAdapter.is_instance`'s name-based fallback fires (the pattern
`MockFeatureChainExpressionOperatorExpression` uses in
test_ast_dispatch_invariant.py). Atomic operands are plain strings, which
`reconstruct_expression` passes through unchanged — keeping only the precedence
branches under test, not dispatch.
"""

from __future__ import annotations

from sysml_codegen.extraction.expression_utils import (
    binary_op_of,
    reconstruct_operator_expression,
)


class StubOperatorExpression:
    """Name carries the type → is_instance name fallback treats it as an OE."""

    def __init__(self, operator: str, operands: list) -> None:
        self.operator = operator
        self.operands = operands


def op(operator: str, *operands: object) -> StubOperatorExpression:
    return StubOperatorExpression(operator, list(operands))


# ---------------------------------------------------------------------------
# Component-5 stub residual: the stub actually drives binary_op_of (design-
# review.md:421-428). If this returns None, the other traces pass vacuously.
# ---------------------------------------------------------------------------


def test_residual_stub_drives_binary_op_check() -> None:
    """A name-fallback stub with 2 operands and a ranked operator is seen."""
    child = op("/", "b", "c")
    assert binary_op_of(child) == "/"
    # ...and end to end: a * (b / c) must wrap (equal-prec, unfavored right).
    node = op("*", "a", child)
    assert reconstruct_operator_expression(node) == "a * (b / c)"


# ---------------------------------------------------------------------------
# The five design hand-traces (design.md:334-340) — each must render exactly.
# ---------------------------------------------------------------------------


def test_trace_equal_prec_left_assoc_minus() -> None:
    # a - (b - c): equal-prec, left-assoc unfavored=right → wrap
    node = op("-", "a", op("-", "b", "c"))
    assert reconstruct_operator_expression(node) == "a - (b - c)"


def test_trace_equal_prec_left_assoc_div() -> None:
    # a / (b * c): equal-prec, left-assoc unfavored=right → wrap
    node = op("/", "a", op("*", "b", "c"))
    assert reconstruct_operator_expression(node) == "a / (b * c)"


def test_trace_unary_over_binary() -> None:
    # -(a + b): unary(2) over binary(5), looser → wrap
    node = op("-", op("+", "a", "b"))
    assert reconstruct_operator_expression(node) == "-(a + b)"


def test_trace_power_right_assoc_flat() -> None:
    # a ** (b ** c): right-assoc, natural nesting → flat
    node = op("**", "a", op("**", "b", "c"))
    assert reconstruct_operator_expression(node) == "a ** b ** c"


def test_trace_power_right_assoc_forced_left() -> None:
    # (a ** b) ** c: right-assoc, forced left nesting → wrap
    node = op("**", op("**", "a", "b"), "c")
    assert reconstruct_operator_expression(node) == "(a ** b) ** c"


# ---------------------------------------------------------------------------
# C3: both unary operators wrap a binary operand.
# ---------------------------------------------------------------------------


def test_unary_not_over_binary() -> None:
    node = op("not", op("and", "a", "b"))
    assert reconstruct_operator_expression(node) == "not (a and b)"


def test_nested_unary_stays_flat() -> None:
    # - -a: the nested unary operand is atomic (binary_op_of → None) → no parens
    node = op("-", op("-", "a"))
    assert reconstruct_operator_expression(node) == "--a"


# ---------------------------------------------------------------------------
# C2: a looser child on each side wraps; a tighter one does not.
# ---------------------------------------------------------------------------


def test_looser_child_left_wraps() -> None:
    node = op("*", op("+", "a", "b"), "c")
    assert reconstruct_operator_expression(node) == "(a + b) * c"


def test_looser_child_right_wraps() -> None:
    node = op("*", "a", op("+", "b", "c"))
    assert reconstruct_operator_expression(node) == "a * (b + c)"


def test_tighter_child_stays_flat() -> None:
    # a + (b * c): child binds tighter → no parens needed on either side
    node = op("+", "a", op("*", "b", "c"))
    assert reconstruct_operator_expression(node) == "a + b * c"
