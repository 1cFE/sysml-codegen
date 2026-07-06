"""Secondary fusion-tea syntactic shapes: one property pin per shape (SC-3).

Each pin asserts a specific OBSERVED property of the committed snapshot/graph — not a
whole-snapshot byte-equality (the epic-R1 banned REQ-EXT-09 anti-pattern). The observed
label (correct / degraded / diagnostic) was measured at capture, following the ife_plant
precedent. No shape crashed the extractor, so none was filed under the L2-2 escape hatch.
"""

from __future__ import annotations

import json

from sysml_codegen.snapshot import build_full_graph_from_snapshot
from tests.conftest import snapshot_fixture


def _snap():
    return json.loads(snapshot_fixture("plant_value_shapes").read_text())


def _design_attr(snap, name):
    for v in snap["design_attributes"].values():
        for a in v:
            if a["name"] == name:
                return a
    raise AssertionError(f"design attribute {name} not found")


def _calc_def_outputs(snap, qn):
    for c in snap["calc_defs"]:
        if c["qualified_name"] == qn:
            return {o["name"] for o in c["output_attributes"]}
    raise AssertionError(f"calc def {qn} not found")


def _ep_default(name):
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("plant_value_shapes"))
    qn = f"PlantValueShapesDesign__shapes_design__{name}"
    for group in graph.entry_point_groups:
        for ep in group.parameters:
            if ep.qualified_name == qn:
                return ep.default_value
    raise AssertionError(f"entry point {qn} not found")


# --- CORRECT shapes ------------------------------------------------------------

def test_shape2_bare_default_captured():
    """Shape 2 (bare `default 10.0`, no `:=`): captured as a design attribute value 10.0."""
    assert _design_attr(_snap(), "rate_default")["default_value"] == "10.0"


def test_shape5_five_deep_chain_inherits_abstract_end_attr():
    """Shape 5 (5-deep chain, abstract ends): the abstract L1's `depth_marker = 1.0`
    inherits through L2..L4 to the instantiated `chain_unit : 'Chain L4'` (value 1.0)."""
    assert _design_attr(_snap(), "depth_marker")["default_value"] == "1.0"


def test_shape7_quoted_output_param_captured():
    """Shape 7 (`out attribute 'net cost'`): the quoted output param loads and its name
    de-quotes to `net_cost` — CORRECT (no extractor crash, no escape-hatch filing)."""
    assert _calc_def_outputs(_snap(), "PlantValueShapesLib::NetCostCalc") == {"net_cost"}


def test_shape8_style_e_mixed_out_and_return():
    """Shape 8 (Style-E, quoted def mixing `out attribute` + `return`): BOTH outputs are
    captured — `doubled` (out attribute) and `tripled` (return)."""
    assert _calc_def_outputs(
        _snap(), "PlantValueShapesLib::'Mixed Output Style'"
    ) == {"doubled", "tripled"}


def test_shape8b_return_in_quoted_def():
    """Shape 8b (a `return` inside a quoted calc def): the return output `scaled` captured."""
    assert _calc_def_outputs(
        _snap(), "PlantValueShapesLib::'Quoted Return Calc'"
    ) == {"scaled"}


# --- DEGRADED shapes -----------------------------------------------------------

def test_shape1_econ_param_nested_redef_does_not_reach_cross_part_input():
    """Shape 1 (attribute-def-typed attr with nested `:>>`, the 14-econ-params shape):
    DEGRADED — the nested `:>> value = 0.70` does not propagate to the cross-part calc
    input `rated_cost.rate`, which lands on a valueless entry point (default None)."""
    assert _ep_default("rated_cost__rate") is None


def test_shape4_inherited_attr_redefined_below_does_not_propagate():
    """Shape 4 (in-binding reading an inherited attr the same def redefines below it):
    DEGRADED — `:>> throughput = 8.0` does not reach `flow_calc.flow_rate`, which lands
    on a valueless entry point (default None)."""
    assert _ep_default("flow_unit__flow_calc__flow_rate") is None


# --- DIAGNOSTIC / Item 5 substrate --------------------------------------------

def test_shape9_non_float_enum_ep_is_valueless_item5_substrate():
    """Shape 9 (non-float EP, the `wall_type` idiom): the enum-valued `wall` one hop from
    the calc input yields a valueless entry point (default None) — the silent None-omission
    Item 5 hardens. Its float sibling `footprint` is captured normally (12.0)."""
    assert _ep_default("chamber_unit__select__wall") is None
    assert _ep_default("chamber_unit__select__footprint") == 12.0
