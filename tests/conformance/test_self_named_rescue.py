"""Conformance test for the self_named_rescue companion fixture (Item 10 stage (b)).

``self_named_rescue`` is the POSITIVE companion to ``self_named_binding_trap``: a
self-named binding ``in throughput = throughput`` that DOES have a resolvable upstream, so
the Phase-7 rewrite has a real channel to rescue it to (SC-4, mechanism D). Layout:

- ``source_calc : SourceCalc`` produces ``throughput`` — a real upstream channel.
- ``attribute throughput = source_calc.throughput`` exposes it on the part.
- ``sink_calc : SinkCalc { in throughput = throughput }`` — the RHS ``throughput`` shares
  the calc param's name AND the exposed attribute's name (the trap shape).

Where ``self_named_binding_trap`` dead-ends on the calc's own parameter (no upstream), this
fixture's identical binding has ``source_calc.throughput`` in scope to rescue to.

## Resolved wiring (Phase 7, mechanism D / amendment D-E)

The self-named binding does NOT reach the rewrite as a bare name: extraction resolves it
to a full REFERENCE QN pointing at sink_calc's OWN parameter
(``RescueLib::'Rescue Plant'::sink_calc::throughput``). The mechanism-D rescue detects that
self-reference and, because an outer same-named EXPOSE (``throughput = source_calc.throughput``)
resolves to a real channel, rewrites the binding to the upstream ``source_calc`` channel —
wiring it as a ``module_output``. Captured current-incomplete FIRST (Item 8 pattern); this
test now asserts the flipped, rescued state. The negative companion
``self_named_binding_trap`` has no resolvable upstream, so it is correctly left as-is.
"""

from __future__ import annotations

from pathlib import Path

from tests.conformance.conftest import offline_input_sources
from tests.conftest import requires_license

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"

MODEL = "self_named_rescue"
CONSUMER = "rescuedesign__rescue_plant__sink_calc"
UPSTREAM_CHANNEL = "RescueDesign__rescue_plant__source_calc__throughput"


def test_upstream_channel_exists() -> None:
    """The upstream producer that the rescue wires TO is a real channel — unlike the
    trap, this self-named binding has somewhere resolvable to go."""
    from sysml_codegen.orchestration.snapshot_context import (
        build_pipeline_context_from_snapshot,
    )
    from tests.conftest import snapshot_fixture

    ctx = build_pipeline_context_from_snapshot(snapshot_fixture(MODEL))
    channels = {
        o.channel_name for m in ctx.computation_graph.modules for o in m.outputs
    }
    assert UPSTREAM_CHANNEL in channels, channels


def test_self_named_binding_rescued_to_upstream() -> None:
    """SC-4 FLIP (Phase 7, mechanism D / D-E): the self-named ``throughput`` no longer
    dead-ends on sink_calc's own parameter — the full-QN self-reference is detected and,
    because an outer same-named EXPOSE (``throughput = source_calc.throughput``) resolves
    to a real channel, the binding is rewritten to the upstream ``source_calc`` channel as
    a wired ``module_output``. (The negative companion ``self_named_binding_trap`` has no
    such upstream and is correctly left as-is.)"""
    sources = offline_input_sources(MODEL)
    src = sources[(CONSUMER, "throughput")]
    assert src.source_type == "module_output", src
    assert src.producer_channel == UPSTREAM_CHANNEL, src


@requires_license
def test_self_named_rescue_loads_live() -> None:
    """Guard against fixture rot: the committed model still parses through the live
    extractor (the snapshot above is only as trustworthy as a parseable source)."""
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    ex = SysMLDataExtractor([FIXTURES_DIR / "self_named_rescue"])
    assert ex.load_models()
    calc_defs = ex.extract_calculation_definitions()
    assert {c.qualified_name for c in calc_defs} == {
        "RescueLib::SourceCalc",
        "RescueLib::SinkCalc",
    }
