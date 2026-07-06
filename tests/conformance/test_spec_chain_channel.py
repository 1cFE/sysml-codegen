"""Conformance test for the spec_chain_channel companion fixture (Item 10 stage (b)).

``spec_chain_channel`` isolates ONE mechanism: a specialized nested part whose calc
**output** must wire into a cross-part consumer through the redefinition chain — the
gamma -> lcoe analog (SC-2). Layout:

- ``MeierCost`` is a nested calc inside the driver; its output ``gamma`` is the head of
  the edge.
- ``'IFE Driver'`` (base) declares ``cost_per_joule`` with no value.
- ``'HIF Driver' :> 'IFE Driver'`` redefines ``cost_per_joule :>> meier_cost.gamma``
  (the specialized-def ``:>>`` tier).
- ``Variant :> Facility`` retypes ``driver`` to ``'HIF Driver'`` and owns the consumer
  ``lcoe_calc`` binding ``cost_per_joule = driver.cost_per_joule``.

## Current-incomplete pin (captured FIRST, Item 8 pattern)

The Phase-7 precedence resolver does not yet follow the specialized-def ``:>>`` through
the retyped instance, so ``lcoe_calc.cost_per_joule`` resolves to a library-default
entry point (``SpecChainLib__HIF_Driver__cost_per_joule``) instead of wiring to the
``meier_cost.gamma`` producer channel. This is the pin Phase 7 flips: the entry point
becomes a ``module_output`` wired to the gamma channel (the gamma -> lcoe edge, SC-2).
"""

from __future__ import annotations

from pathlib import Path

from tests.conformance.conftest import offline_input_sources
from tests.conftest import requires_license

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"

MODEL = "spec_chain_channel"
CONSUMER = "specchaindesign__spec_chain_plant__lcoe_calc"
GAMMA_CHANNEL = "SpecChainDesign__spec_chain_plant__driver__meier_cost__gamma"


def test_gamma_producer_channel_exists() -> None:
    """The nested calc output that the edge wires FROM is a real producer channel —
    the fixture is well-formed; only the consumer side is unwired."""
    from sysml_codegen.orchestration.snapshot_context import (
        build_pipeline_context_from_snapshot,
    )
    from tests.conftest import snapshot_fixture

    ctx = build_pipeline_context_from_snapshot(snapshot_fixture(MODEL))
    channels = {
        o.channel_name for m in ctx.computation_graph.modules for o in m.outputs
    }
    assert GAMMA_CHANNEL in channels, channels


def test_cost_per_joule_pinned_as_entry_point() -> None:
    """CURRENT-INCOMPLETE (SC-2 pin): the cross-part consumer's ``cost_per_joule`` is an
    entry point, NOT wired to the gamma channel. Phase 7 flips this to a wired
    ``module_output`` -> the gamma -> lcoe edge appears in the graph."""
    sources = offline_input_sources(MODEL)
    src = sources[(CONSUMER, "cost_per_joule")]
    # Incomplete: falls to the consumer's own valueless parameter entry point (the
    # specialized-def :>> chain to meier_cost.gamma is not yet followed).
    assert src.source_type == "entry_point", src
    assert (
        src.qualified_name
        == "SpecChainDesign__spec_chain_plant__lcoe_calc__cost_per_joule"
    ), src
    # And specifically NOT yet wired to the gamma producer channel.
    assert src.producer_channel is None, src


@requires_license
def test_spec_chain_channel_loads_live() -> None:
    """Guard against fixture rot: the committed model still parses through the live
    extractor (the snapshot above is only as trustworthy as a parseable source)."""
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    ex = SysMLDataExtractor([FIXTURES_DIR / "spec_chain_channel"])
    assert ex.load_models()
    calc_defs = ex.extract_calculation_definitions()
    assert {c.qualified_name for c in calc_defs} == {
        "SpecChainLib::MeierCost",
        "SpecChainLib::LcoeCalc",
    }
