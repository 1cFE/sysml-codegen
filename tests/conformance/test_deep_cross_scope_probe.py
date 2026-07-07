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
from tests.conftest import requires_license, snapshot_fixture

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
    """D3-2 loud-reject (Item 5): the two former V11 offenders — the Pattern-A deep
    CHAIN `chain_analysis.data_point` and the mid-level `derived_calc.base_metric` —
    are 3+-segment chains the extractor can no longer truncate. They are now
    hard-rejected at extraction (warned) and surface as clean entry points, NOT
    valueless-and-wired fallbacks. So the uncovered-offender set is empty: silent
    degradation was replaced by a loud, user-fillable EP. Pinned so drift that
    re-introduces a silent wire fails."""
    actual = {(u.module, u.input) for u in collect_uncovered_params(_graph())}
    assert actual == set()


def test_pattern_a_deep_chain_falls_to_own_entry_point():
    """Pattern A (4-level dot CHAIN `station.array.derived_calc.derived_value`): the
    3+-segment chain is loud-rejected (D3-2), so the consumer input is unbound and
    lands on its own design-params EP (its own QN), rather than a truncated wire."""
    qn = _input_source_qn(_graph(), f"{_ANALYZER}__chain_analysis", "data_point")
    assert qn == "DeepCrossScopeDesign__measurement_system__analyzer__chain_analysis__data_point"


def test_pattern_a_deep_chain_no_truncated_binding():
    """D3-2 (Item 5): the extractor no longer truncates the Pattern-A deep CHAIN
    `station.array.derived_calc.derived_value` source_path to its root (`station`).
    A 3+-segment chain is hard-rejected: there is NO CHAIN binding carrying a
    truncated `station` source_path — the param is unbound instead (see the
    fires-on-shape warning test below)."""
    import json

    from tests.conftest import snapshot_fixture

    snap = json.loads(snapshot_fixture("deep_cross_scope_probe").read_text())
    for usage in snap["calc_usages"]:
        for b in usage["bindings"]:
            if b["param_name"] == "data_point" and "chain_analysis" in (
                usage.get("qualified_name") or ""
            ):
                raise AssertionError(
                    f"Expected no truncated CHAIN binding for data_point, got: {b}"
                )
    # No data_point binding survives — correct (it is now an unbound entry point).


@requires_license
def test_pattern_a_deep_chain_warns_on_extraction():
    """D3-2 fires-on-shape (LOUD-REJECT): extracting the fixture live emits a warning
    naming the multi-hop chain the extractor cannot resolve. Expectation anchored to
    the fixture source (`station.array.derived_calc.derived_value`), not computed by
    the code under test (R1)."""
    from sysml_codegen.extraction.extractor import SysMLDataExtractor
    from sysml_codegen.extraction.usage_extractor import extract_calculation_usages

    fixture_dir = snapshot_fixture("deep_cross_scope_probe").parent
    extractor = SysMLDataExtractor([fixture_dir])
    assert extractor.load_models()
    calc_defs = extractor.extract_calculation_definitions()
    _usages, report = extract_calculation_usages(extractor.model, calc_defs=calc_defs)
    assert any(
        "station.array.derived_calc.derived_value" in w for w in report.warnings
    ), report.warnings


def test_pattern_b_deep_reference_resolves_to_cross_package_producer_ep():
    """Pattern B (6-segment `::` REFERENCE to `core.metric_value`): resolves cross-package
    to the Core Metric producer's entry point QN (distinct from Pattern A's local EP)."""
    qn = _input_source_qn(_graph(), f"{_ANALYZER}__ref_analysis", "data_point")
    assert qn == "DeepCrossScopeProducer__Core_Metric__metric_value"
