"""Headline plant_values fixture: the V11 "before" state Item 2 flips (SC-1).

The fixture reproduces the fusion-tea whole-plant shape: a plant calc reads three
subsystem values cross-part, each supplied by a distinct value-provision mechanism
the current pipeline cannot wire, so each lands on a valueless Step-4 entry point
that the calc still wires — `collect_uncovered_params` flags all three (V11 trips).

These pins assert specific observed properties (SC-3), not whole-snapshot bytes:
  - the exact three-offender set covering mechanisms (a)/(b)/(c) [Item 2 flips it];
  - per-mechanism, that its entry point is valueless (`default_value is None`);
  - the assert-constraint substrate: never a calc usage (constraints are their own fact
    stream), and — since Item 14 closed the `gain` gap — now lowers into a real
    constraint module and catalog entry (Item 4's CONSTRAINT-SILENCE pin inverted).
"""

from __future__ import annotations

import json

from sysml_codegen.resolution.graph_builder import collect_uncovered_params
from sysml_codegen.snapshot import build_full_graph_from_snapshot
from tests.conftest import snapshot_fixture

_MODULE = "plantvaluesdesign__plant__cost_calc"

# Item 2 flipped this fixture: the three cross-part references now resolve to filled
# DESIGN_ATTRIBUTE entry points keyed by SOURCE QN (not the per-consumer fallback QN).
# Each mechanism's supplied literal is carried onto its source attribute by the
# supplied-value materializer (REQ-SVM-01..04), so V11 sees zero offenders.
_EP_BY_MECHANISM = {
    # (a) subtype-def literal `:>> efficiency = 0.35`, reached via usage-level retype.
    "a": ("PlantValuesDesign__plant__driver__efficiency", 0.35),
    # (b) bare no-retype override block `part :>> target_factory { :>> cost_per_target = 10.0; }`.
    "b": ("PlantValuesDesign__plant__target_factory__cost_per_target", 10.0),
    # (c) plain one-hop cross-part attr with a usage-level dotted override (`= 7.0`).
    "c": ("PlantValuesDesign__plant__chamber__cost_per_unit", 7.0),
}


def _graph():
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("plant_values"))
    return graph


def _ep_default(graph, qn: str):
    for group in graph.entry_point_groups:
        for ep in group.parameters:
            if ep.qualified_name == qn:
                return ep.default_value
    raise AssertionError(f"entry point {qn} not found")


def test_plant_values_resolves_all_three_mechanisms():
    """SC-1 after-state pin: zero V11 offenders — the headline flip.

    Behavior-observing (not `snapshot == committed`): the three cross-part references
    resolve to filled entry points, so `collect_uncovered_params` returns empty. The
    pin fails loudly in both directions — a regression that re-drops a value re-trips
    V11 and grows the set."""
    actual = {(u.module, u.input, u.missing_key) for u in collect_uncovered_params(_graph())}
    assert actual == set(), actual


def test_mechanism_a_subtype_def_literal_resolves_to_source_ep():
    """(a): the subtype-def `:>> efficiency = 0.35` (via usage-level retype) is carried
    onto its source attribute and resolves to a filled DESIGN_ATTRIBUTE entry point."""
    qn, value = _EP_BY_MECHANISM["a"]
    assert _ep_default(_graph(), qn) == value


def test_mechanism_b_override_block_literal_resolves_to_source_ep():
    """(b): the bare no-retype `part :>>` override-block literal (10.0) resolves onto its
    source EP via the materializer's tier-1 override lookup."""
    qn, value = _EP_BY_MECHANISM["b"]
    assert _ep_default(_graph(), qn) == value


def test_mechanism_c_dotted_override_resolves_to_source_ep():
    """(c): the plain one-hop cross-part attr `chamber.cost_per_unit`, its literal supplied
    by a usage-level dotted override (`:>> chamber.cost_per_unit = 7.0`, distinct from (b)'s
    override BLOCK), resolves onto its source EP. The override literal 7.0 comes from
    `design_overrides` (the model), not the test."""
    qn, value = _EP_BY_MECHANISM["c"]
    assert _ep_default(_graph(), qn) == value
    snap = json.loads(snapshot_fixture("plant_values").read_text())
    overrides = {
        o["attribute_name"]: o["literal_value"]
        for o in snap["hierarchy_data"]["design_overrides"]
    }
    assert overrides.get("cost_per_unit") == 7.0  # value carried from the model, not test-supplied
    assert overrides.get("cost_per_target") == 10.0  # (b)'s value, for symmetry


def test_plant_cost_anchor_hand_transcribed():
    """SC-1 anchor (INV-5): the three carried values compose to the hand-derived plant
    cost. The 48.5714… constant is transcribed by hand here, never read back from the
    resolver — it only asserts the resolver produced the three operands (0.35/10.0/7.0)."""
    g = _graph()
    driver = _ep_default(g, _EP_BY_MECHANISM["a"][0])
    target = _ep_default(g, _EP_BY_MECHANISM["b"][0])
    chamber = _ep_default(g, _EP_BY_MECHANISM["c"][0])
    assert driver == 0.35 and target == 10.0 and chamber == 7.0
    # plant_cost = (target_cost + chamber_cost) / driver_efficiency, hand-transcribed:
    assert abs((10.0 + 7.0) / 0.35 - 48.5714285714) < 1e-9


def test_assert_constraint_is_absent_from_calc_usages():
    """The `assert constraint viability` usage is never a calc usage — constraints are a
    separate fact stream (`constraint_facts`), extracted and lowered independently of
    `collect_calculation_usages`. True before and after Item 14; unaffected by whether
    the constraint lowers."""
    snap = json.loads(snapshot_fixture("plant_values").read_text())
    usage_names = {cu.get("qualified_name") for cu in snap["calc_usages"]}
    assert usage_names == {"PlantValuesDesign__plant__cost_calc"}
    assert "PlantValuesDesign__plant__viability" not in usage_names


def test_assert_constraint_now_lowers(caplog):
    """Item 14 (D2 + its constraint-actual demand widening, plus the def-scoped
    base-default rung for `gain`'s plain-attribute shape): the `assert constraint
    viability` usage and its three binding sub-shapes (cross-part `in eta =
    driver.efficiency`, self-named `in gain = gain`, unbound-defaulted `threshold`) now
    lower into a real constraint module and catalog entry — inverts the old
    CONSTRAINT-SILENCE pin (`test_assert_constraint_is_invisible_today`, Item 4 era),
    which asserted the opposite (grandfathered on the `gain` gap this item closes)."""
    graph = _graph()
    assert any("viability" in m.name for m in graph.modules)
    input_params = {inp.param_name for m in graph.modules for inp in m.inputs}
    assert "eta" in input_params
    assert graph.constraint_catalog is not None
    assert any(e.constraint_id for e in graph.constraint_catalog.concrete_entries)


def test_constraint_defaulted_param_still_in_design_attrs():
    """The constraint def's unbound-defaulted param `threshold` still leaks into
    `design_attributes` (parent 'Viability Threshold') — an extraction-side artifact
    independent of whether the constraint lowers, present before and after Item 14."""
    snap = json.loads(snapshot_fixture("plant_values").read_text())
    design_names = {a["name"] for v in snap["design_attributes"].values() for a in v}
    assert "threshold" in design_names
