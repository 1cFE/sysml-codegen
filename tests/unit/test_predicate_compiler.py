"""Committed, probe3-style Kleene semantics suite for the predicate compiler (Item 7 / D2).

Asserts directly on `compile_predicate`'s emitted-function output — one case per rendered
semantic cell — because end-to-end tests only exercise happy paths and would miss a wrong
propagation cell, which reads as a *confident wrong verdict* (the exact failure this feature
exists to prevent). Builds `expression_ir.ExpressionIR` trees directly (`parse_expression`
reconstructs canonical JSON, not SysML source text, so hand-built trees are the fixture form).
"""

from __future__ import annotations

import pytest
from agentic_mbse.sysml.expression_facts import (
    FeatureReferenceFact,
    LiteralFact,
    OperandTypeFact,
    UnitFact,
)
from agentic_mbse.sysml.expression_ir import (
    FeatureReferenceNode,
    LiteralNode,
    OperatorNode,
    UnitAnnotationNode,
)

from sysml_codegen.generation.predicate_compiler import (
    PredicateCompileError,
    compile_predicate,
    compile_predicate_body,
    finalize_assertion,
    load_predicate,
    margin_expression,
)


@pytest.mark.parametrize(
    ("raw", "margin", "is_negated", "expected", "status", "final_margin"),
    [
        (True, 2.0, False, True, "satisfied", 2.0),
        (True, 2.0, True, False, "violated", -2.0),
        (False, -2.0, False, True, "violated", -2.0),
        (False, -2.0, True, False, "satisfied", 2.0),
        (False, -0.0, True, False, "satisfied", 0.0),
        (None, None, False, True, "indeterminate", None),
        (None, None, True, False, "indeterminate", None),
    ],
)
def test_finalizer_applies_polarity_exactly_once(
    raw: object,
    margin: float | None,
    is_negated: bool,
    expected: bool,
    status: str,
    final_margin: float | None,
) -> None:
    actual, got_status, got_margin = finalize_assertion(
        raw, margin, is_negated=is_negated, expected_value=expected
    )
    assert actual is raw
    assert got_status == status
    assert got_margin == final_margin
    if got_margin == 0.0:
        assert str(got_margin) == "0.0"


def test_neutral_body_compiler_has_no_usage_polarity() -> None:
    ir = OperatorNode(operator="<", operands=[_ref("a"), _ref("b")], operand_type=None)
    source, args = compile_predicate_body(ir, "neutral")
    body = load_predicate(source, "neutral")
    result = body(a=1.0, b=3.0)
    assert args == ["a", "b"]
    assert result.actual_value is True
    assert result.source_margin == 2.0
    assert "expected_value" not in source.split("def neutral", maxsplit=1)[1]


def _ref(name: str, category: str = "real", enumeration: str | None = None) -> FeatureReferenceNode:
    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name=name, target=None, target_types=[], chain_segments=[]
        ),
        operand_type=OperandTypeFact(category=category, enumeration=enumeration, unit=None),
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


_METRE = UnitFact(unit="SI::metre", dimension="ISQBase::LengthUnit")


def _quantity_ref(name: str) -> FeatureReferenceNode:
    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name=name, target=None, target_types=[], chain_segments=[]
        ),
        operand_type=OperandTypeFact(category="quantity", enumeration=None, unit=_METRE),
    )


def _quantity_literal(value: int) -> UnitAnnotationNode:
    return UnitAnnotationNode(
        value=_lit_value(value, "integer"),
        unit_text="m",
        operand_type=OperandTypeFact(category="quantity", enumeration=None, unit=_METRE),
    )


def _lit_bool(value: bool) -> LiteralNode:
    return LiteralNode(
        literal=LiteralFact(kind="LiteralBoolean", value=value, result_type="boolean"),
        operand_type=OperandTypeFact(category="boolean", enumeration=None, unit=None),
    )


def _lit_value(value: object, category: str, enumeration: str | None = None) -> LiteralNode:
    kind = {
        "boolean": "LiteralBoolean",
        "integer": "LiteralInteger",
        "string": "LiteralString",
        "enum": "LiteralString",
    }[category]
    return LiteralNode(
        literal=LiteralFact(kind=kind, value=value, result_type=category),
        operand_type=OperandTypeFact(category=category, enumeration=enumeration, unit=None),
    )


def _cmp_node(op: str, a, b) -> OperatorNode:
    return OperatorNode(operator=op, operands=[a, b], operand_type=None)


def _bool_op(op: str, *operands) -> OperatorNode:
    return OperatorNode(operator=op, operands=list(operands), operand_type=None)


def _unary(op: str, operand) -> OperatorNode:
    return OperatorNode(operator=op, operands=[operand], operand_type=None)


def _compile_and_load(ir, fn_name: str, negated: bool = False):
    src, args = compile_predicate(ir, fn_name, negated=negated)
    return load_predicate(src, fn_name), args


def _raising_arithmetic_cases():
    division = OperatorNode(operator="/", operands=[_ref("a"), _ref("b")], operand_type=None)
    power = OperatorNode(operator="**", operands=[_ref("a"), _ref("b")], operand_type=None)
    direct = (
        (
            "division-by-zero",
            _cmp_node(">", division, _lit_real(0.0)),
            {"a": 1.0, "b": 0.0},
            ZeroDivisionError,
            "float division by zero",
        ),
        (
            "zero-negative-power",
            _cmp_node(">", power, _lit_real(0.0)),
            {"a": 0.0, "b": -1.0},
            ZeroDivisionError,
            "0.0 cannot be raised to a negative power",
        ),
        (
            "exponent-overflow",
            _cmp_node(">", power, _lit_real(0.0)),
            {"a": 10.0, "b": 400.0},
            OverflowError,
            "(34, 'Numerical result out of range')",
        ),
    )
    nested = _bool_op("and", direct[0][1], _cmp_node(">", _ref("a"), _lit_real(-1.0)))
    return (
        *direct,
        (
            "nested-connective",
            nested,
            {"a": 1.0, "b": 0.0},
            ZeroDivisionError,
            "float division by zero",
        ),
    )


@pytest.mark.parametrize(
    ("case_name", "expression", "values", "error_type", "message"),
    _raising_arithmetic_cases(),
    ids=lambda value: value if isinstance(value, str) else None,
)
def test_arithmetic_exception_propagates_unchanged(
    case_name, expression, values, error_type, message
):
    del case_name
    predicate, _ = _compile_and_load(expression, "raising_predicate")
    with pytest.raises(error_type) as error:
        predicate(**values)
    assert str(error.value) == message


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


@pytest.mark.parametrize("name", ["value", "status"])
def test_generated_predicate_binding_collision_is_structured(name):
    ir = _cmp_node(">", _ref(name), _lit_real(0.0))
    with pytest.raises(PredicateCompileError) as error:
        compile_predicate(ir, "p")
    violation = error.value.name_safety_violation
    assert violation is not None
    assert (violation.scope, violation.kind, violation.final_binding) == (
        "predicate",
        "generated_binding_overlap",
        name,
    )


@pytest.mark.parametrize(
    ("category", "enumeration", "left", "right"),
    [
        ("boolean", None, True, True),
        ("string", None, "tea", "coffee"),
        ("integer", None, 7, 7),
        ("enum", "Synthetic::Color", "red", "blue"),
    ],
)
def test_profile_v3_rejects_all_equality_categories(category, enumeration, left, right):
    ir = _cmp_node(
        "==",
        _lit_value(left, category, enumeration),
        _lit_value(right, category, enumeration),
    )
    with pytest.raises(PredicateCompileError, match="profile preflight must exclude"):
        compile_predicate(ir, "p")


def test_equality_rejected_before_observation_handling():
    ir = _cmp_node("==", _ref("a", "integer"), _ref("b", "integer"))
    with pytest.raises(PredicateCompileError, match="profile preflight must exclude"):
        compile_predicate(ir, "p")


@pytest.mark.parametrize(
    ("ir", "values", "expected"),
    [
        (_cmp_node("<=", _quantity_ref("a"), _quantity_ref("b")), {"a": 1, "b": 2}, True),
        (_cmp_node("<=", _quantity_ref("a"), _quantity_literal(2)), {"a": 3}, False),
        (
            _cmp_node("<=", _unary("+", _quantity_ref("a")), _quantity_literal(2)),
            {"a": 2},
            True,
        ),
        (
            _cmp_node(
                "<=",
                OperatorNode(
                    operator="*",
                    operands=[_lit_value(2, "integer"), _quantity_ref("a")],
                    operand_type=None,
                ),
                _quantity_literal(3),
            ),
            {"a": 2},
            False,
        ),
        (
            _cmp_node(
                "<=",
                OperatorNode(
                    operator="/",
                    operands=[_quantity_ref("a"), _quantity_ref("b")],
                    operand_type=None,
                ),
                _lit_value(2, "integer"),
            ),
            {"a": 6, "b": 3},
            True,
        ),
    ],
    ids=["quantity-refs", "quantity-literal", "quantity-unary", "scalar-product", "ratio"],
)
def test_profile_v3_quantity_numeric_cases_compile(ir, values, expected):
    fn, _args = _compile_and_load(ir, "p")
    assert fn(**values).actual_value is expected


def test_integer_power_is_real_for_equality_admission():
    power = OperatorNode(
        operator="**",
        operands=[_lit_value(2, "integer"), _lit_value(3, "integer")],
        operand_type=None,
    )
    with pytest.raises(PredicateCompileError, match="not admitted"):
        compile_predicate(_cmp_node("==", power, _lit_value(8, "integer")), "p")


def test_not_equal_remains_profile_blocked():
    ir = _cmp_node("!=", _ref("a", "integer"), _ref("b", "integer"))
    with pytest.raises(PredicateCompileError, match=r"not admitted by executable-profile/v\d"):
        compile_predicate(ir, "p", negated=False)


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


def test_unary_minus_still_compiles_and_negates():
    ir = _cmp_node(">=", _unary("-", _ref("x")), _lit_real(0.0))
    fn, args = _compile_and_load(ir, "p", negated=False)
    assert args == ["x"]
    assert fn(x=-3.0).status == "satisfied"  # -(-3) = 3 >= 0
    assert fn(x=3.0).status == "violated"


def test_unary_plus_compiles_as_identity():
    ir = _cmp_node(">=", _unary("+", _ref("x")), _lit_real(0.0))
    fn, args = _compile_and_load(ir, "p", negated=False)
    assert args == ["x"]
    assert fn(x=3.0).status == "satisfied"
    assert fn(x=-3.0).status == "violated"


def test_optional_literal_operand_fact_fails_loudly_in_direct_compiler_api():
    malformed = LiteralNode(
        literal=LiteralFact(kind="LiteralInteger", value=1, result_type="integer"),
        operand_type=None,
    )
    ir = _cmp_node(">", malformed, _lit_real(0.0))
    with pytest.raises(PredicateCompileError, match="missing operand_type"):
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
