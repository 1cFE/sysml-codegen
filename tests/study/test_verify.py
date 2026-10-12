"""verify re-derives a verdict from the predicate IR, evaluating every disjunct.

Moved from fusion-tea ``tests/study/test_verify.py`` at ``b06585709``: its two tests that need
no package and no teax. The tests that run verify on a store join the teax lane.
"""

import json

import pytest

from sysml_codegen.study import verify


@pytest.mark.parametrize(
    "enabled,gap,expected",
    [(0.0, -1.0, True), (1.0, 1.0, True), (1.0, 0.0, False), (1.0, -1.0, False)],
)
@pytest.mark.parametrize("negated", [False, True])
def test_exact_active_heat_direction_disjunction(enabled, gap, expected, negated):
    literal = lambda value: {"kind": "literal", "literal": {"value": value}}
    feature = lambda name: {"kind": "feature_ref", "reference": {"source_name": name}}
    ir = {
        "kind": "operator",
        "operator": "or",
        "operands": [
            {"kind": "operator", "operator": "<=", "operands": [feature("enabled"), literal(0.0)]},
            {"kind": "operator", "operator": ">", "operands": [feature("gap"), literal(0.0)]},
        ],
    }
    entry = {"predicate_ir": json.dumps(ir), "is_negated": negated}
    bindings = {
        "heat": {
            "enabled": {"kind": "input", "key": "mode"},
            "gap": {"kind": "channel", "key": "raw_gap"},
        }
    }
    result, count = verify.derive_verdict(
        "heat", entry, bindings, {"mode": enabled}, {}, {"raw_gap": gap}
    )
    assert result is (not expected if negated else expected)
    assert count == 2


@pytest.mark.parametrize("failure", ["missing", "nonfinite", "unsupported", "wrong_arity"])
def test_true_disjunction_cannot_hide_missing_or_invalid_evidence(failure):
    literal = lambda value: {"kind": "literal", "literal": {"value": value}}
    left = {"kind": "operator", "operator": "<=", "operands": [literal(0.0), literal(0.0)]}
    right = {
        "kind": "operator",
        "operator": ">",
        "operands": [{"kind": "feature_ref", "reference": {"source_name": "gap"}}, literal(0.0)],
    }
    ir = {"kind": "operator", "operator": "or", "operands": [left, right]}
    channels = {"raw_gap": 1.0}
    if failure == "missing":
        channels = {}
    elif failure == "nonfinite":
        channels = {"raw_gap": float("nan")}
    elif failure == "unsupported":
        right["operator"] = "xor"
    else:
        ir["operands"].append(left)
    with pytest.raises(verify.VerifyError):
        verify.derive_verdict(
            "heat",
            {"predicate_ir": json.dumps(ir)},
            {"heat": {"gap": {"kind": "channel", "key": "raw_gap"}}},
            {},
            {},
            channels,
        )
