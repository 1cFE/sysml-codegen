"""The predicate operand grammar both tools read: conjunctions, binary products, refusals.

``indicators`` traces the leaves of a constraint's ``predicate_ir`` and ``verify`` re-derives its
verdict from them. Both accept comparisons, two-operand conjunctions and binary products of
features and literals, and both refuse anything else by name, never by guessing.

Moved from three fusion-tea files at ``b06585709``: ``test_breeding_predicate.py`` (3 tests),
``test_indicator_operands.py`` (4) and ``test_verify_operands.py`` (all but the one that pins a
fusion package's own expression). They read a fusion package's real conjunction and product;
here each shape is built from the station's real ``pump_fit`` entry, ``capacity >=
demand_flow``, using its own generated feature nodes.
"""

from __future__ import annotations

import copy
import json
from typing import Any

import pytest

from sysml_codegen.study import indicators, verify
from tests.study.conftest import STATION_PACKAGE

P = "PumpStation__station__"
CAPACITY_KEY = P + "installed_capacity"
FLOW_CHANNEL = P + "demand__required_flow"

Entry = dict[str, Any]
Bindings = dict[str, dict[str, dict[str, str]]]


def station_entry() -> Entry:
    contract = json.loads((STATION_PACKAGE / "contracts" / "model_contract.json").read_text())
    entry: Entry = next(
        e for e in contract["constraint_catalog"]["concrete_entries"]
        if e["source_local_identity"] == "pump_fit"
    )
    return entry


def _ir(entry: Entry) -> dict[str, Any]:
    ir: dict[str, Any] = json.loads(entry["predicate_ir"])
    return ir


def _with_ir(entry: Entry, ir: dict[str, Any]) -> Entry:
    return {**entry, "predicate_ir": json.dumps(ir)}


def feature(name: str) -> dict[str, Any]:
    """The station's own generated ``feature_ref`` node for ``capacity`` or ``demand_flow``."""
    node: dict[str, Any] = next(
        operand for operand in _ir(station_entry())["operands"]
        if operand["reference"]["source_name"] == name
    )
    return copy.deepcopy(node)


def literal(value: float) -> dict[str, Any]:
    return {"kind": "literal", "literal": {"value": value}}


def operator(symbol: str, *operands: dict[str, Any]) -> dict[str, Any]:
    return {"kind": "operator", "operator": symbol, "operands": list(operands)}


def conjunction_entry() -> Entry:
    """``capacity >= 0.3 and capacity >= demand_flow``: one guard per branch, so the first
    branch can be false on evidence the second branch does not need."""
    return _with_ir(station_entry(), operator(
        "and",
        operator(">=", feature("capacity"), literal(0.3)),
        _ir(station_entry()),
    ))


def product_entry() -> Entry:
    """``capacity * 1.2 >= demand_flow``: a binary product on the left of the comparison."""
    ir = _ir(station_entry())
    ir["operands"][0] = operator("*", feature("capacity"), literal(1.2))
    return _with_ir(station_entry(), ir)


def bindings(entry: Entry) -> Bindings:
    return {
        entry["constraint_id"]: {
            "capacity": {"kind": "input", "key": CAPACITY_KEY},
            "demand_flow": {"kind": "channel", "key": FLOW_CHANNEL},
        }
    }


# ------------------------------------------------- conjunctions (test_breeding_predicate)


@pytest.mark.parametrize(
    "capacity,flow,expected",
    [(0.35, 0.24, True), (0.25, 0.24, False), (0.35, 0.40, False), (0.25, 0.40, False)],
)
def test_independent_conjunction_and_negation(capacity: float, flow: float, expected: bool) -> None:
    entry = conjunction_entry()
    cid = entry["constraint_id"]
    point, channels = {CAPACITY_KEY: capacity}, {FLOW_CHANNEL: flow}
    assert verify.derive_verdict(cid, entry, bindings(entry), point, {}, channels) == (expected, 3)
    entry["is_negated"] = True
    assert verify.derive_verdict(cid, entry, bindings(entry), point, {}, channels) == (
        not expected, 3
    )


def test_false_first_branch_does_not_hide_missing_evidence() -> None:
    """The first guard is false on the input alone, and the channel the second needs is
    missing: re-derivation refuses rather than short-circuiting past the gap."""
    entry = conjunction_entry()
    with pytest.raises(verify.VerifyError, match="oracle did not return"):
        verify.derive_verdict(
            entry["constraint_id"], entry, bindings(entry), {CAPACITY_KEY: 0.25}, {}, {}
        )


@pytest.mark.parametrize("arity", [0, 1, 3])
def test_malformed_conjunction_refused(arity: int) -> None:
    ir = _ir(conjunction_entry())
    ir["operands"] = [ir["operands"][0]] * arity
    entry = _with_ir(station_entry(), ir)
    with pytest.raises(indicators.IndicatorError, match="exactly two"):
        indicators.predicate_operands(entry)
    with pytest.raises(verify.VerifyError, match="exactly two"):
        verify.derive_verdict(entry["constraint_id"], entry, {}, {}, {}, {})


# -------------------------------------------- products, traced (test_indicator_operands)


def test_nested_products_preserve_literals_and_repeated_features() -> None:
    ir = _ir(product_entry())
    ir["operands"][0] = operator(
        "*", operator("*", feature("capacity"), feature("capacity")), literal(2.0)
    )
    assert indicators.predicate_operands(_with_ir(station_entry(), ir)) == (">=", [
        {"kind": "feature_ref", "name": "capacity"},
        {"kind": "feature_ref", "name": "capacity"},
        {"kind": "literal", "value": 2.0},
        {"kind": "feature_ref", "name": "demand_flow"},
    ])


@pytest.mark.parametrize("symbol", ["+", "/", "**"])
def test_other_nested_operators_are_refused(symbol: str) -> None:
    ir = _ir(product_entry())
    ir["operands"][0]["operator"] = symbol
    with pytest.raises(indicators.IndicatorError, match="unsupported nested"):
        indicators.predicate_operands(_with_ir(station_entry(), ir))


@pytest.mark.parametrize("arity", [0, 1, 3])
def test_malformed_product_arity_is_refused(arity: int) -> None:
    ir = _ir(product_entry())
    product = ir["operands"][0]
    product["operands"] = [product["operands"][0]] * arity
    with pytest.raises(indicators.IndicatorError, match="exactly two"):
        indicators.predicate_operands(_with_ir(station_entry(), ir))


def test_unknown_nested_kind_is_refused() -> None:
    ir = _ir(product_entry())
    ir["operands"][0]["operands"][0] = {"kind": "invocation"}
    with pytest.raises(indicators.IndicatorError, match="unknown predicate operand kind"):
        indicators.predicate_operands(_with_ir(station_entry(), ir))


# --------------------------------------------- products, re-derived (test_verify_operands)


def test_nested_multiplication_counts_feature_occurrences_and_preserves_negation() -> None:
    ir = _ir(product_entry())
    ir["operands"][0] = operator("*", ir["operands"][0], feature("capacity"))
    entry = {**_with_ir(station_entry(), ir), "is_negated": True}
    # (0.25 * 1.2) * 0.25 = 0.075 < 0.24, then negated. capacity occurs twice.
    assert verify.derive_verdict(
        entry["constraint_id"], entry, bindings(entry), {CAPACITY_KEY: 0.25}, {},
        {FLOW_CHANNEL: 0.24},
    ) == (True, 3)


def test_multiplication_accepts_literal_operands_without_counting_them() -> None:
    ir = _ir(product_entry())
    ir["operands"][0]["operands"][0] = literal(0.25)
    entry = _with_ir(station_entry(), ir)
    # 0.25 * 1.2 = 0.3 >= 0.24; only demand_flow is a feature.
    assert verify.derive_verdict(
        entry["constraint_id"], entry, bindings(entry), {}, {}, {FLOW_CHANNEL: 0.24}
    ) == (True, 1)


@pytest.mark.parametrize("symbol", ["+", "/", "**", "unknown"])
def test_unsupported_arithmetic_is_named_and_refused(symbol: str) -> None:
    ir = _ir(product_entry())
    ir["operands"][0]["operator"] = symbol
    entry = _with_ir(station_entry(), ir)
    with pytest.raises(verify.VerifyError, match="unsupported arithmetic operator") as error:
        verify.derive_verdict(entry["constraint_id"], entry, bindings(entry), {}, {}, {})
    assert entry["constraint_id"] in str(error.value)
    assert repr(symbol) in str(error.value)


@pytest.mark.parametrize("arity", [0, 1, 3])
def test_multiplication_arity_is_checked(arity: int) -> None:
    ir = _ir(product_entry())
    product = ir["operands"][0]
    product["operands"] = [product["operands"][0]] * arity
    entry = _with_ir(station_entry(), ir)
    with pytest.raises(verify.VerifyError, match="two multiplication operands"):
        verify.derive_verdict(entry["constraint_id"], entry, bindings(entry), {}, {}, {})


def test_nested_missing_binding_is_not_guessed() -> None:
    entry = product_entry()
    table = bindings(entry)
    del table[entry["constraint_id"]]["capacity"]
    with pytest.raises(verify.VerifyError, match="capacity.*no published binding"):
        verify.derive_verdict(entry["constraint_id"], entry, table, {}, {}, {})


def test_unsupported_operand_kind_is_refused() -> None:
    ir = _ir(product_entry())
    ir["operands"][0] = {"kind": "invocation"}
    entry = _with_ir(station_entry(), ir)
    with pytest.raises(verify.VerifyError, match="operand kind 'invocation'"):
        verify.derive_verdict(entry["constraint_id"], entry, bindings(entry), {}, {}, {})
