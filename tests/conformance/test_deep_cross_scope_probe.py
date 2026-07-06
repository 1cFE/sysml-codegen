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
    """Two cross-scope inputs stay valueless-and-wired today (V11 offenders): the
    Pattern-A deep CHAIN `chain_analysis.data_point` and the mid-level `derived_calc.
    base_metric`. Pinned so drift that silently wires or drops them fails."""
    actual = {(u.module, u.input) for u in collect_uncovered_params(_graph())}
    assert actual == {
        (f"{_ANALYZER}__chain_analysis", "data_point"),
        (_DERIVED, "base_metric"),
    }


def test_pattern_a_deep_chain_falls_to_valueless_ep():
    """Pattern A (4-level dot CHAIN `station.array.derived_calc.derived_value`): does NOT
    resolve to the producer; the consumer input lands on its own design-params EP."""
    qn = _input_source_qn(_graph(), f"{_ANALYZER}__chain_analysis", "data_point")
    assert qn == "DeepCrossScopeDesign__measurement_system__analyzer__chain_analysis__data_point"


def test_pattern_a_deep_chain_source_path_truncates_degradation():
    """DEGRADATION the probe exposes: the extractor truncates the Pattern-A deep CHAIN
    `station.array.derived_calc.derived_value` source_path to its FIRST segment
    (`station`) — losing the rest of the path. Pinned as observed so a fix (or further
    drift) is caught. This is why the probe is kept out of the global CHAIN-source_path
    invariant (it would fail the dotted-source_path assertion)."""
    import json

    from tests.conftest import snapshot_fixture

    snap = json.loads(snapshot_fixture("deep_cross_scope_probe").read_text())
    for usage in snap["calc_usages"]:
        for b in usage["bindings"]:
            if b["param_name"] == "data_point" and "chain_analysis" in (
                usage.get("qualified_name") or ""
            ):
                assert b["source_path"] == "station"  # truncated (should be 4 segments)
                return
    raise AssertionError("chain_analysis.data_point binding not found")


def test_pattern_b_deep_reference_resolves_to_cross_package_producer_ep():
    """Pattern B (6-segment `::` REFERENCE to `core.metric_value`): resolves cross-package
    to the Core Metric producer's entry point QN (distinct from Pattern A's local EP)."""
    qn = _input_source_qn(_graph(), f"{_ANALYZER}__ref_analysis", "data_point")
    assert qn == "DeepCrossScopeProducer__Core_Metric__metric_value"
