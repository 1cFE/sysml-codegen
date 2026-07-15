"""Committed, probe3-style Kleene semantics suite for the predicate compiler (Item 7 / D2).

Asserts directly on `compile_predicate`'s emitted-function output — one case per rendered
semantic cell — because end-to-end tests only exercise happy paths and would miss a wrong
propagation cell, which reads as a *confident wrong verdict* (the exact failure this feature
exists to prevent). Builds `expression_ir.ExpressionIR` trees directly (`parse_expression`
reconstructs canonical JSON, not SysML source text, so hand-built trees are the fixture form).
"""

from __future__ import annotations

import pytest
from agentic_mbse.sysml.expression_facts import FeatureReferenceFact, LiteralFact, OperandTypeFact
from agentic_mbse.sysml.expression_ir import FeatureReferenceNode, LiteralNode, OperatorNode

from sysml_codegen.generation.predicate_compiler import (
    PredicateCompileError,
    compile_predicate,
    load_predicate,
    margin_expression,
)


def _ref(name: str) -> FeatureReferenceNode:
    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name=name, target=None, target_types=[], chain_segments=[]
        ),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )

def _chain_ref(name: str) -> FeatureReferenceNode:
    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name=name, target=None, target_types=[], chain_segments=["a", "b"]
        ),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _lit_real(value: float) -> LiteralNode:
    return LiteralNode(
        literal=LiteralFact(kind="LiteralRational", value=value, result_type="real"),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _lit_bool(value: bool) -> LiteralNode:
    return LiteralNode(
        literal=LiteralFact(kind="LiteralBoolean", value=value, result_type="boolean"),
        operand_type=OperandTypeFact(category="boolean", enumeration=None, unit=None),
    )


def _cmp_node(op: str, a, b) -> OperatorNode:
    return OperatorNode(operator=op, operands=[a, b], operand_type=None)


def _bool_op(op: str, *operands) -> OperatorNode:
    return OperatorNode(operator=op, operands=list(operands), operand_type=None)


def _compile_and_load(ir, fn_name: str, negated: bool = False):
    src, args = compile_predicate(ir, fn_name, negated=negated)
    return load_predicate(src, fn_name), args


def test_nonfinite_leaf_is_indeterminate():
    ir = _cmp_node(">", _ref("a"), _ref("b"))
    fn, _ = _compile_and_load(ir, "p", negated=False)
    r = fn(a=float("inf"), b=1.0)
    assert r.status == "indeterminate"
    assert r.actual_value is None and r.margin is None


def test_true_or_unknown_is_true():
    ir = _bool_op("or", _cmp_node(">", _ref("x"), _ref("y")), _lit_bool(True))
    fn, _ = _compile_and_load(ir, "p", negated=False)
    r = fn(x=float("inf"), y=1.0)
    assert r.actual_value is True
    assert r.status == "satisfied"


def test_false_and_unknown_is_false():
    ir = _bool_op("and", _cmp_node(">", _ref("x"), _ref("y")), _lit_bool(False))
    fn, _ = _compile_and_load(ir, "p", negated=False)
    r = fn(x=float("inf"), y=1.0)
    assert r.actual_value is False
    assert r.status == "violated"


def test_not_unknown_is_unknown():
    ir = _bool_op("not", _cmp_node(">", _ref("x"), _ref("y")))
    fn, _ = _compile_and_load(ir, "p", negated=False)
    r = fn(x=float("inf"), y=1.0)
    assert r.actual_value is None
    assert r.status == "indeterminate"


def test_negated_polarity_false_predicate_is_satisfied():
    ir = _cmp_node(">", _ref("a"), _ref("b"))
    fn, _ = _compile_and_load(ir, "p", negated=True)
    r = fn(a=1.0, b=2.0)  # 1 > 2 is False
    assert r.actual_value is False
    assert r.status == "satisfied"


def test_negated_inequality_margin_sign_flip():
    ir = _cmp_node(">", _ref("a"), _ref("b"))
    fn_pos, _ = _compile_and_load(ir, "p_pos", negated=False)
    fn_neg, _ = _compile_and_load(ir, "p_neg", negated=True)
    r_pos = fn_pos(a=5.0, b=2.0)
    r_neg = fn_neg(a=5.0, b=2.0)
    assert r_pos.margin == 3.0
    assert r_neg.margin == -3.0


def test_boundary_margin_normalizes_signed_zero():
    # negated inequality at exact boundary yields -0.0; must read 0.0 (`[HARD]`).
    ir = _cmp_node(">", _ref("a"), _ref("b"))
    fn, _ = _compile_and_load(ir, "p", negated=True)
    r = fn(a=1.0, b=1.0)
    assert repr(r.margin) == "0.0"


def test_compound_predicate_has_no_margin():
    ir = _bool_op("and", _cmp_node(">", _ref("a"), _ref("b")), _lit_bool(True))
    assert margin_expression(ir, negated=False) is None
    fn, _ = _compile_and_load(ir, "p", negated=False)
    r = fn(a=5.0, b=2.0)
    assert r.margin is None


def test_leaf_ref_names_dedup_first_occurrence_order():
    ir = _bool_op(
        "and",
        _cmp_node(">", _ref("a"), _ref("b")),
        _cmp_node("<", _ref("b"), _ref("c")),
    )
    _, args = compile_predicate(ir, "p", negated=False)
    assert args == ["a", "b", "c"]


def test_equality_blocked():
    ir = _cmp_node("==", _ref("a"), _ref("b"))
    try:
        compile_predicate(ir, "p", negated=False)
    except PredicateCompileError as e:
        assert "equality blocked" in str(e)
    else:
        raise AssertionError("expected PredicateCompileError for equality operator")


def test_feature_chain_unsupported():
    ir = _cmp_node(">", _chain_ref("x"), _ref("y"))
    try:
        compile_predicate(ir, "p", negated=False)
    except PredicateCompileError as e:
        assert "feature chain" in str(e)
    else:
        raise AssertionError("expected PredicateCompileError for feature-chain leaf")


# --- IR shape validation (code-quality remediation, 2026-07-14) --------------------
# Finding 12: malformed arity raised raw IndexError, a one-operand `+` silently
# rendered as negation, and leaf names were interpolated into the generated
# signature unvalidated. All now raise PredicateCompileError.


def _unary(op: str, operand) -> OperatorNode:
    return OperatorNode(operator=op, operands=[operand], operand_type=None)


def test_unary_minus_still_compiles_and_negates():
    ir = _cmp_node(">=", _unary("-", _ref("x")), _lit_real(0.0))
    fn, args = _compile_and_load(ir, "p", negated=False)
    assert args == ["x"]
    assert fn(x=-3.0).status == "satisfied"  # -(-3) = 3 >= 0
    assert fn(x=3.0).status == "violated"


def test_unary_plus_raises_not_silent_negation():
    ir = _cmp_node(">=", _unary("+", _ref("x")), _lit_real(0.0))
    with pytest.raises(PredicateCompileError, match="unsupported unary operator"):
        compile_predicate(ir, "p", negated=False)


def test_comparison_wrong_arity_raises_typed_error():
    ir = OperatorNode(operator=">", operands=[_ref("a")], operand_type=None)
    with pytest.raises(PredicateCompileError, match="needs 2 operands"):
        compile_predicate(ir, "p", negated=False)


def test_margin_expression_wrong_arity_raises_typed_error():
    ir = OperatorNode(operator="<", operands=[_ref("a")], operand_type=None)
    with pytest.raises(PredicateCompileError, match="needs 2 operands"):
        margin_expression(ir, negated=False)


def test_not_wrong_arity_raises_typed_error():
    inner = _cmp_node(">", _ref("a"), _ref("b"))
    ir = OperatorNode(operator="not", operands=[inner, inner], operand_type=None)
    with pytest.raises(PredicateCompileError, match="exactly 1 operand"):
        compile_predicate(ir, "p", negated=False)


def test_connective_zero_operands_raises_typed_error():
    ir = OperatorNode(operator="and", operands=[], operand_type=None)
    with pytest.raises(PredicateCompileError, match="at least 2 operands"):
        compile_predicate(ir, "p", negated=False)


def test_zero_operand_arithmetic_raises_typed_error():
    bad = OperatorNode(operator="+", operands=[], operand_type=None)
    ir = _cmp_node(">", bad, _lit_real(0.0))
    with pytest.raises(PredicateCompileError, match="no operands"):
        compile_predicate(ir, "p", negated=False)


def test_unsafe_leaf_identifier_raises():
    ir = _cmp_node(">", _ref("net cost"), _lit_real(0.0))
    with pytest.raises(PredicateCompileError, match="not a safe Python identifier"):
        compile_predicate(ir, "p", negated=False)


def test_keyword_leaf_identifier_raises():
    ir = _cmp_node(">", _ref("lambda"), _lit_real(0.0))
    with pytest.raises(PredicateCompileError, match="not a safe Python identifier"):
        compile_predicate(ir, "p", negated=False)


def test_unsafe_fn_name_raises():
    ir = _cmp_node(">", _ref("a"), _ref("b"))
    with pytest.raises(PredicateCompileError, match="not a Python identifier"):
        compile_predicate(ir, "bad name", negated=False)


def test_nameless_reference_raises():
    ref = FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name=None, target=None, target_types=[], chain_segments=[]
        ),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )
    ir = _cmp_node(">", ref, _lit_real(0.0))
    with pytest.raises(PredicateCompileError, match="nameless feature reference"):
        compile_predicate(ir, "p", negated=False)
