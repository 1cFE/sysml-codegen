"""Two-level cross-part aggregation — per-child redefinition follow (Item 10, A7 + WI-015 #4).

`grand_total = a.capital + b.capital` where each child `a`/`b` redefines `capital` to its own
`cost_calc.cost` with DIFFERENT bases (3.0 / 5.0). The fix must resolve each `X.capital` term
to X's OWN per-instance channel — structurally (by following the child part usage's `:>>`
redefinition), never by dropping the `X.` qualifier and leaf-matching (which collapsed all
children to one producer before the fix).

The assertion is STRUCTURAL (channel identity), not just value: a value check alone can pass on
a defaulted or collapsed entry point (the F2 lesson). The distinct bases 3 != 5 additionally
mean a collapse could never be masked by a value coincidence.
"""

from __future__ import annotations

from sysml_codegen.orchestration.snapshot_context import (
    build_pipeline_context_from_snapshot,
)
from sysml_codegen.resolution.producer_completeness import check_producer_completeness
from sysml_codegen.resolution.producer_resolution import capturing_resolutions
from tests.conftest import snapshot_fixture

MODEL = "crosspart_rollup_twolevel"
A_CHANNEL = "CrossPartRollupDesign__rollup_plant__a__cost_calc__cost"
B_CHANNEL = "CrossPartRollupDesign__rollup_plant__b__cost_calc__cost"


def _grand_total_module():
    ctx = build_pipeline_context_from_snapshot(snapshot_fixture(MODEL))
    for m in ctx.computation_graph.modules:
        if "grand_total" in m.name:
            return m
    raise AssertionError("grand_total module not found")


def test_grand_total_is_an_aggregation_module() -> None:
    """The cross-part FORMULA sum was routed into the aggregation path (Step 4.7)."""
    assert _grand_total_module().module_kind.value == "aggregation"


def test_each_child_term_wires_to_its_own_instance_channel() -> None:
    """A7 / WI-015 #4 root: a.capital -> a's channel, b.capital -> b's channel — distinct
    per-instance module_output producers, never a qualifier-dropped collapse."""
    m = _grand_total_module()
    by_param = {i.param_name: getattr(i, "source", i) for i in m.inputs}
    assert "a_capital" in by_param and "b_capital" in by_param, by_param

    a_src, b_src = by_param["a_capital"], by_param["b_capital"]
    assert a_src.source_type == "module_output", a_src
    assert b_src.source_type == "module_output", b_src
    # Distinct channels, each scoped to its own child instance — the structural proof.
    assert a_src.producer_channel == A_CHANNEL, a_src.producer_channel
    assert b_src.producer_channel == B_CHANNEL, b_src.producer_channel
    assert a_src.producer_channel != b_src.producer_channel


def test_no_producer_completeness_violation() -> None:
    """The cross-part terms resolve to intended producers under exact identity — the
    completeness check (which flagged the 13-term stellarator collapse) is clean here."""
    with capturing_resolutions() as sink:
        build_pipeline_context_from_snapshot(snapshot_fixture(MODEL))
    violations = check_producer_completeness(sink)
    assert violations == [], [v.message() for v in violations]
