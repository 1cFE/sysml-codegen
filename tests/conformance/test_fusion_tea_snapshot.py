"""SC-4: the committed fusion-tea snapshot resolves to TRUE ZERO V11 offenders.

The vendored canonical fusion-tea models (`~/1cfe/fusion-tea/models`) are the license-free
stand-in for Item 3's live acceptance run. All ten cross-part/in-part plain-value
references — the residual plant gap RN-10 left — clear under the supplied-value
materializer (a/b/c cross-part + d in-part). `generate --from-snapshot` on this snapshot
emits the full YAML package; V11 sees zero offenders.
"""

from __future__ import annotations

from sysml_codegen.resolution.graph_builder import collect_uncovered_params
from sysml_codegen.snapshot import build_full_graph_from_snapshot
from tests.conftest import snapshot_fixture


def test_fusion_tea_snapshot_zero_offenders():
    """SC-4 / epic CSF: zero V11 offenders on the committed fusion-tea snapshot."""
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("fusion_tea"))
    offenders = collect_uncovered_params(graph)
    assert offenders == [], [(u.module, u.input) for u in offenders]


def test_fusion_tea_emits_full_pipeline():
    """The full YAML package emits (modules + pipeline), not a partial graph."""
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("fusion_tea"))
    assert len(graph.modules) > 0
    # Every module output has a channel; every wired input resolves (no valueless V11).
    assert all(m.name for m in graph.modules)


def _consumers_of(graph, ep_suffix: str):
    eps = {
        ep.qualified_name
        for gr in graph.entry_point_groups
        for ep in gr.parameters
        if ep.qualified_name.endswith(ep_suffix)
    }
    consumers = [
        (m.name, inp.param_name)
        for m in graph.modules
        for inp in m.inputs
        if inp.source and getattr(inp.source, "qualified_name", "") in eps
    ]
    return eps, consumers


def test_renamed_consumers_collapse_to_one_source_ep():
    """INV-2 / EP-keys-by-source-QN [HARD]: fusion-tea's real fan-out renames per
    consumer — `driver.efficiency` feeds `lcoe_calc.driver_efficiency` AND
    `recirc_calc.eta`. Both differently-named inputs collapse onto ONE source-QN entry
    point (not N per-consumer keys), the property that distinguishes this mechanism from
    per-consumer VBR-03."""
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("fusion_tea"))
    eps, consumers = _consumers_of(graph, "__driver__efficiency")
    assert len(eps) == 1, eps  # one source EP, not two
    consumer_names = {c[1] for c in consumers}
    assert {"eta", "driver_efficiency"} <= consumer_names, consumers  # both renamed readers

    # The second renamed source: chamber.blanket_energy_multiple -> two differing names.
    bem_eps, _ = _consumers_of(graph, "__chamber__blanket_energy_multiple")
    assert len(bem_eps) == 1, bem_eps
