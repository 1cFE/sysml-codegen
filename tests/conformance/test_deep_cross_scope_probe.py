"""deep_cross_scope_probe drift pin (D1-F6): a committed snapshot at last.

This fixture had no committed snapshot (permanent drift). Item 1 commits one and pins
its CURRENT observed shape — the deep cross-scope reference patterns resolve/drop as
recorded here — so future silent drift fails loudly. Property pins (not byte-equality).

Note: the fixture was un-broken for capture by renaming a calc usage `derived` ->
`derived_calc` (`derived` is a reserved KerML feature modifier; the fixture never
parsed). The pattern shapes below are otherwise unchanged.
"""

from __future__ import annotations

from sysml_codegen.resolution.graph_builder import collect_uncovered_params
from sysml_codegen.snapshot import build_full_graph_from_snapshot
from tests.conftest import snapshot_fixture

_ANALYZER = "deepcrossscopedesign__measurement_system__analyzer"
_DERIVED = "deepcrossscopedesign__measurement_system__station__array__derived_calc"

# Item 2 channel-identity pins (R1). Each QN is derived from the fixture's instance
# path, independently of the resolution code under test: `data_point` wires to the
# `derived_calc` calc's `derived_value` output (instance QN snapshot `:389`/`:402`),
# `base_metric` to the `core` calc's `metric_value` output (instance QN snapshot
# `:359`/`:383`). Casing confirmed against those snapshot instance QNs.
_DATA_POINT_CHANNEL = (
    "DeepCrossScopeDesign__measurement_system__station__array__derived_calc__derived_value"
)
_BASE_METRIC_CHANNEL = (
    "DeepCrossScopeDesign__measurement_system__station__array__sensor__core__metric_value"
)


def _graph():
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("deep_cross_scope_probe"))
    return graph


def _input_source_qn(graph, module_name, param):
    for m in graph.modules:
        if m.name == module_name:
            for inp in m.inputs:
                if inp.param_name == param:
                    return inp.source.qualified_name
    raise AssertionError(f"{module_name}.{param} not found")


def test_full_graph_builds_five_modules():
    """The fixture builds a full graph (full-pipeline capture, Open Question resolved)."""
    assert len(_graph().modules) == 5


def test_offender_set_pinned():
    """Item 2: the two former V11 offenders — the Pattern-A deep CHAIN
    `chain_analysis.data_point` and the mid-level `derived_calc.base_metric` — are
    3+-segment chains that now **resolve to their upstream channels** (the climb +
    Step-1 direct hit). The uncovered-offender set stays empty, but now because both
    are *wired* to a module output, not rejected-to-clean-EP. Pinned so drift that
    re-introduces a silent wire — or drops one back to a fallback — fails."""
    actual = {(u.module, u.input) for u in collect_uncovered_params(_graph())}
    assert actual == set()


def test_pattern_a_deep_chain_resolves_to_derived_value_channel():
    """Pattern A (4-level dot CHAIN `station.array.derived_calc.derived_value`):
    the consumer scope is `measurement_system.analyzer` (a *sibling* of `station`),
    so Step 1 misses and the ancestor-scope climb drops `analyzer`, hits
    `measurement_system.station.array.derived_calc.derived_value`, and wires to the
    `derived_calc` calc's `derived_value` output. Channel-identity pin (R1, INV-1)."""
    qn = _input_source_qn(_graph(), f"{_ANALYZER}__chain_analysis", "data_point")
    assert qn == _DATA_POINT_CHANNEL


def test_base_metric_deep_chain_resolves_to_metric_value_channel():
    """Mid-level chain (`sensor.core.metric_value`) on `derived_calc`: the consumer
    scope `measurement_system.station.array` already prefixes the target, so Step 1
    hits directly (no climb) and wires to the `core` calc's `metric_value` output.
    Channel-identity pin (R1, INV-1) — its own always-on guard so the flip is not
    unpinned."""
    qn = _input_source_qn(_graph(), _DERIVED, "base_metric")
    assert qn == _BASE_METRIC_CHANNEL


def test_pattern_a_deep_chain_full_path_chain_binding():
    """Item 2 (D1): extraction now emits a full-path CHAIN binding for the Pattern-A
    deep chain — the whole dotted `station.array.derived_calc.derived_value`, not a
    root-truncated `station` and not a dropped/unbound param. Guards against a
    regression to either the old truncation or the old hard-reject."""
    import json

    from tests.conftest import snapshot_fixture

    snap = json.loads(snapshot_fixture("deep_cross_scope_probe").read_text())
    matches = [
        b
        for usage in snap["calc_usages"]
        if "chain_analysis" in (usage.get("qualified_name") or "")
        for b in usage["bindings"]
        if b["param_name"] == "data_point"
    ]
    assert len(matches) == 1, f"expected one data_point binding, got: {matches}"
    b = matches[0]
    assert b["binding_type"] == "chain", b
    assert b["source_path"] == "station.array.derived_calc.derived_value", b


# NOTE (Item 2): `test_pattern_a_deep_chain_warns_on_extraction` was removed here.
# Extraction no longer warns on a 3+-segment chain (D1) — it emits a full-path CHAIN.
# The loud diagnostic for a genuinely unresolvable chain moved to the backtracker
# Step-4 fallback (D3), covered by the fires-on-shape unit test
# (tests/unit/test_dependency_backtracker.py). Live/offline parity for the resolved
# chains is re-added below in Phase 5 as an @requires_license leg.


def test_pattern_b_deep_reference_resolves_to_cross_package_producer_ep():
    """Pattern B (6-segment `::` REFERENCE to `core.metric_value`): resolves cross-package
    to the Core Metric producer's entry point QN (distinct from Pattern A's local EP)."""
    qn = _input_source_qn(_graph(), f"{_ANALYZER}__ref_analysis", "data_point")
    assert qn == "DeepCrossScopeProducer__Core_Metric__metric_value"
