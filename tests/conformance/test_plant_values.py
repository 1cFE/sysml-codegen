"""Headline plant_values fixture: the V11 "before" state Item 2 flips (SC-1).

The fixture reproduces the fusion-tea whole-plant shape: a plant calc reads three
subsystem values cross-part, each supplied by a distinct value-provision mechanism
the current pipeline cannot wire, so each lands on a valueless Step-4 entry point
that the calc still wires — `collect_uncovered_params` flags all three (V11 trips).

These pins assert specific observed properties (SC-3), not whole-snapshot bytes:
  - the exact three-offender set covering mechanisms (a)/(b)/(c) [Item 2 flips it];
  - per-mechanism, that its entry point is valueless (`default_value is None`);
  - the assert-constraint substrate: the constraint is invisible to extraction today
    (the CONSTRAINT-SILENCE bug — Item 4 flips it).
"""

from __future__ import annotations

import json

from sysml_codegen.resolution.graph_builder import collect_uncovered_params
from sysml_codegen.snapshot import build_full_graph_from_snapshot
from tests.conftest import snapshot_fixture

_MODULE = "plantvaluesdesign__plant__cost_calc"

# The exact offender tuples read from the committed snapshot (Phase 2 D6 gate). One
# per value-provision mechanism; the missing_key is the params key the JSON never mints.
EXPECTED_UNCOVERED = {
    # (a) subtype-def literal `:>> efficiency = 0.35` via usage-level retype
    (_MODULE, "driver_efficiency",
     "library_params.PlantValuesDesign__plant__cost_calc__driver_efficiency"),
    # (b) bare no-retype override block `part :>> target_factory { :>> cost_per_target = 10.0; }`
    (_MODULE, "target_cost",
     "library_params.PlantValuesDesign__plant__cost_calc__target_cost"),
    # (c) plain cross-part chain `chamber.cost_per_unit` (no calc output; the P1 shape)
    (_MODULE, "chamber_cost",
     "library_params.PlantValuesDesign__plant__cost_calc__chamber_cost"),
}

# The entry-point QN each mechanism's cross-part input falls through to (valueless).
_EP_BY_MECHANISM = {
    "a": "PlantValuesDesign__plant__cost_calc__driver_efficiency",
    "b": "PlantValuesDesign__plant__cost_calc__target_cost",
    "c": "PlantValuesDesign__plant__cost_calc__chamber_cost",
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


def test_plant_values_trips_v11_all_three_mechanisms():
    """SC-1 before-state pin: exactly the three-mechanism offender set.

    Item 2 flips this as it wires the cross-part values. The structure fails loudly
    if the set later goes empty (a regression that silently re-drops the trip) OR if
    the offenders change, so the pin stays meaningful either direction.
    """
    actual = {(u.module, u.input, u.missing_key) for u in collect_uncovered_params(_graph())}
    assert actual == EXPECTED_UNCOVERED, actual
    assert len(actual) == 3  # non-empty, one per mechanism (a)/(b)/(c)


def test_mechanism_a_subtype_def_literal_valueless_ep():
    """(a): the subtype-def `:>> efficiency = 0.35` (via usage-level retype) feeds a
    valueless plant-calc EP — the current pipeline does not propagate it, so it trips."""
    assert _ep_default(_graph(), _EP_BY_MECHANISM["a"]) is None


def test_mechanism_b_override_block_literal_valueless_ep():
    """(b): the bare no-retype `part :>>` override-block literal (10.0) feeds a
    valueless plant-calc EP — it is NOT pre-filled, so the collector flags it."""
    assert _ep_default(_graph(), _EP_BY_MECHANISM["b"]) is None


def test_mechanism_c_plain_cross_part_chain_valueless_ep():
    """(c): the plain cross-part chain `chamber.cost_per_unit` (no calc output — the P1
    shape) feeds a valueless plant-calc EP — the pipeline leaves it a user-fill EP the
    inherited calc still wires, so it trips (the headline's (c) V11-trip role)."""
    assert _ep_default(_graph(), _EP_BY_MECHANISM["c"]) is None


def test_assert_constraint_is_invisible_today():
    """Item 4 substrate (CONSTRAINT-SILENCE): the `assert constraint viability` usage and
    its three binding sub-shapes (cross-part `in eta = driver.efficiency`, self-named
    `in gain = gain`, unbound-defaulted `threshold`) are authored in the source but are
    INVISIBLE to extraction today — the snapshot carries no constraint usage and no
    binding tokens. Pinned as the observed absence; Item 4 flips it (makes the constraint
    and its bindings visible to the drop report)."""
    snap = json.loads(snapshot_fixture("plant_values").read_text())
    usage_names = {cu.get("qualified_name") for cu in snap["calc_usages"]}
    assert "PlantValuesDesign__plant__viability" not in usage_names
    # The only extracted usage is the plant cost calc — the assert constraint is dropped.
    assert usage_names == {"PlantValuesDesign__plant__cost_calc"}
    blob = json.dumps(snap)
    assert blob.count("eta") == 0          # the cross-part binding is invisible
    assert blob.count("viability") == 0    # the constraint usage is invisible


def test_constraint_defaulted_param_leaks_to_design_attrs():
    """Observed diagnostic (Item 4 substrate): while the assert constraint usage is
    invisible, the constraint def's unbound-defaulted param `threshold` leaks into
    `design_attributes` (parent 'Viability Threshold'). Recorded so Item 4's fix — which
    should surface the constraint properly, not via this leak — has a before-state."""
    snap = json.loads(snapshot_fixture("plant_values").read_text())
    design_names = {a["name"] for v in snap["design_attributes"].values() for a in v}
    assert "threshold" in design_names
