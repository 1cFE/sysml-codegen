"""Conformance test for the sibling_channel_ambiguity companion fixture (Item 10 stage (b)).

``sibling_channel_ambiguity`` isolates ONE mechanism: two same-type sibling parts, where
a consumer binding must disambiguate to the correct instance-scoped channel (SC-3).
Layout:

- ``Chamber`` owns ``power_calc`` and exposes ``power = power_calc.power``.
- ``'Twin Plant'`` owns two same-type siblings ``chamber_a`` / ``chamber_b`` — so the
  flat alias ``power`` collides across instances.
- ``total_calc`` binds ``chamber_power = chamber_b.power`` — it must reach chamber_b's
  instance-scoped channel, not first-wins to chamber_a.

## Resolved wiring (Phase 7, amendment D-D)

The #1 consumer-scoped ``_scoped_alias`` lookup (``_resolve_chain_dispatch`` Step 1c)
prepends the consumer's instance scope, so ``total_calc.chamber_power`` (bound
``chamber_b.power``) reaches the registered ``('twin_plant.chamber_b','power')`` alias
and wires to ``chamber_b``'s power channel as a ``module_output`` — never first-wins
colliding on the def-level ``power`` name (chamber_a). Captured current-incomplete FIRST
(Item 8 pattern); this test now asserts the flipped, wired state.
"""

from __future__ import annotations

from pathlib import Path

from tests.conformance.conftest import offline_input_sources
from tests.conftest import requires_license

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"

MODEL = "sibling_channel_ambiguity"
CONSUMER = "siblingdesign__twin_plant__total_calc"
CHAMBER_A = "SiblingDesign__twin_plant__chamber_a__power_calc__power"
CHAMBER_B = "SiblingDesign__twin_plant__chamber_b__power_calc__power"


def test_both_sibling_channels_exist() -> None:
    """Both siblings produce a distinct instance-scoped power channel — the ambiguity is
    real (two candidates), and the correct target (chamber_b) exists."""
    from sysml_codegen.orchestration.snapshot_context import (
        build_pipeline_context_from_snapshot,
    )
    from tests.conftest import snapshot_fixture

    ctx = build_pipeline_context_from_snapshot(snapshot_fixture(MODEL))
    channels = {
        o.channel_name for m in ctx.computation_graph.modules for o in m.outputs
    }
    assert CHAMBER_A in channels, channels
    assert CHAMBER_B in channels, channels


def test_chamber_power_disambiguated_to_chamber_b() -> None:
    """SC-3 FLIP (Phase 7, D-D): the consumer's ``chamber_power`` wires to chamber_b's
    instance channel — never chamber_a. The #1 consumer-scoped ``_scoped_alias`` lookup
    prepends the consumer's instance scope so ``chamber_b.power`` reaches the registered
    ``('twin_plant.chamber_b','power')`` alias instead of first-wins colliding on the
    def-level ``power`` name."""
    sources = offline_input_sources(MODEL)
    src = sources[(CONSUMER, "chamber_power")]
    assert src.source_type == "module_output", src
    assert src.producer_channel == CHAMBER_B, src
    assert src.producer_channel != CHAMBER_A, src


@requires_license
def test_sibling_channel_ambiguity_loads_live() -> None:
    """Guard against fixture rot: the committed model still parses through the live
    extractor (the snapshot above is only as trustworthy as a parseable source)."""
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    ex = SysMLDataExtractor([FIXTURES_DIR / "sibling_channel_ambiguity"])
    assert ex.load_models()
    calc_defs = ex.extract_calculation_definitions()
    assert {c.qualified_name for c in calc_defs} == {
        "SiblingLib::PowerCalc",
        "SiblingLib::TotalCalc",
    }
