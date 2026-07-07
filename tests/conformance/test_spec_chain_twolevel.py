"""Conformance test for the spec_chain_twolevel fixture (Item 10 Phase 8, C-then-B ruling).

``spec_chain_twolevel`` reproduces the REAL fusion-tea ``hif_plant`` shape that the
single-level ``spec_chain_channel`` fixture does NOT — the two-level specialization the
WI-015 anchor exposed. Layout (mirrors designs/hif_ife/hif_plant.sysml +
designs/generic_ife/ife_plant.sysml):

- ``MeierCost`` is a nested calc inside the driver; its output ``gamma`` is the head of
  the gamma -> lcoe edge (SC-2).
- ``'IFE Driver'`` (base) declares ``cost_per_joule`` with no value.
- ``'HIF Driver' :> 'IFE Driver'`` redefines ``:>> cost_per_joule = meier_cost.gamma``
  (bare form, D-F — captured by hierarchy extraction).
- ``'IFE Power Plant'`` (BASE plant def) declares BOTH ``part driver : 'IFE Driver'`` AND
  the consumer ``lcoe_calc { in cost_per_joule = driver.cost_per_joule }``.
- The design instantiates ``part hif_plant : 'IFE Power Plant'`` — a part USAGE typed by
  the BASE def — with an inline ``part :>> driver : 'HIF Driver'`` retype ON THE USAGE.
  ``lcoe_calc`` is INHERITED from the base and instantiates.

## The two-level specialization, and how it is now wired (Phase 8, C-then-B ruling STEP 2)

Unlike ``spec_chain_channel`` (consumer + retype on ONE def), here the retype lives on a
part USAGE while the consumer is declared on the base def. Two changes wire it:

- **Extraction** (``hierarchy_resolver._index_usage_level_retypes``): the usage-level
  ``:>> driver : 'HIF Driver'`` retype is indexed into ``usage_type_map`` keyed by the
  CONTAINER instance QN — ``('TwoLevelDesign__hif_plant','driver') -> 'TwoLevelLib__HIF_Driver'``
  — filtered to genuine retypes (target differs from the base-declared type), so no
  non-two-level fixture gains an entry.
- **Resolver** (``pipeline_builder._rewrite_specialized_chain``): an instance-aware
  type-select tries the consumer instance's path key first
  (``('TwoLevelDesign__hif_plant','driver')`` -> ``'HIF Driver'``) before the
  declaring-def key, finds the specialized ``:>> cost_per_joule = meier_cost.gamma``, and
  rewrites ``driver.cost_per_joule`` -> ``driver.meier_cost.gamma`` (baked into the
  recaptured snapshot). The chain dispatch resolves that to the gamma producer channel.

This is the fusion-tea WI-015 shape: before, ``hif_plant__lcoe_calc`` input
``driver_cost_constant`` was UNRESOLVED (gamma -> lcoe edge ABSENT); now it wires.
Captured current-incomplete FIRST (Item 8 pattern); these tests assert the wired state.
"""

from __future__ import annotations

from pathlib import Path

from tests.conformance.conftest import offline_input_sources
from tests.conftest import requires_license, snapshot_fixture

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"

MODEL = "spec_chain_twolevel"
CONSUMER = "twoleveldesign__hif_plant__lcoe_calc"
GAMMA_CHANNEL = "TwoLevelDesign__hif_plant__driver__meier_cost__gamma"


def test_gamma_producer_channel_exists() -> None:
    """The nested calc output the edge wires FROM is a real producer channel — the
    fixture is well-formed; only the consumer side is unwired (the two-level gap)."""
    from sysml_codegen.orchestration.snapshot_context import (
        build_pipeline_context_from_snapshot,
    )

    ctx = build_pipeline_context_from_snapshot(snapshot_fixture(MODEL))
    channels = {
        o.channel_name for m in ctx.computation_graph.modules for o in m.outputs
    }
    assert GAMMA_CHANNEL in channels, channels


def test_lcoe_calc_instantiated() -> None:
    """lcoe_calc is inherited from the base 'IFE Power Plant' and instantiates for the
    ``hif_plant`` usage (it is NOT dropped) — distinguishing this shape from a def-level
    specialization, which would drop the inherited template calc."""
    sources = offline_input_sources(MODEL)
    assert (CONSUMER, "cost_per_joule") in sources, sorted(sources)


# REQ-VBR-11: instance-aware _rewrite_specialized_chain type-select follows the
# hif_plant usage-level retype to the specialized def, wiring cost_per_joule to gamma.
def test_cost_per_joule_wired_to_gamma() -> None:
    """SC-2 FLIP (Phase 8 STEP 2, two-level specialization). ``lcoe_calc.cost_per_joule``
    wires to the gamma channel — the gamma -> lcoe edge — because the instance-aware
    type-select follows the ``hif_plant`` usage-level retype to ``'HIF Driver'`` and its
    ``:>> cost_per_joule = meier_cost.gamma``, rewriting ``driver.cost_per_joule`` ->
    ``driver.meier_cost.gamma`` (baked into the recaptured snapshot)."""
    sources = offline_input_sources(MODEL)
    src = sources[(CONSUMER, "cost_per_joule")]
    assert src.source_type == "module_output", src
    assert src.producer_channel == GAMMA_CHANNEL, src


# REQ-LVP-09: _index_usage_level_retypes indexes usage-level retypes keyed by the
# container instance QN (genuine retypes only).
def test_usage_type_map_indexes_usage_level_retype() -> None:
    """The EXTRACTION change (``_index_usage_level_retypes``): the ``hif_plant``
    usage-level ``:>> driver : 'HIF Driver'`` retype is indexed keyed by the CONTAINER
    instance QN — alongside the base declaring-def entry. This is the data the
    instance-aware type-select reads."""
    from sysml_codegen.orchestration.snapshot_context import (
        build_pipeline_context_from_snapshot,
    )

    ctx = build_pipeline_context_from_snapshot(snapshot_fixture(MODEL))
    utm = ctx.hierarchy_data.usage_type_map
    driver_entries = {k: v for k, v in utm.items() if k[1] == "driver"}
    assert driver_entries == {
        ("TwoLevelLib__IFE_Power_Plant", "driver"): "TwoLevelLib__IFE_Driver",
        ("TwoLevelDesign__hif_plant", "driver"): "TwoLevelLib__HIF_Driver",
    }, driver_entries


def test_hif_driver_redefinition_extracted() -> None:
    """The specialized-def ``:>> cost_per_joule = meier_cost.gamma`` redefinition IS
    extracted (bare form, D-F) — the resolver's INPUT is present; the missing piece is
    only the usage-level retype linking ``driver`` to ``'HIF Driver'``."""
    from sysml_codegen.orchestration.snapshot_context import (
        build_pipeline_context_from_snapshot,
    )

    ctx = build_pipeline_context_from_snapshot(snapshot_fixture(MODEL))
    redefs = {
        (r.owning_part_qn, r.attribute_name, r.source_path)
        for r in ctx.hierarchy_data.redefinitions
    }
    assert (
        "TwoLevelLib__HIF_Driver",
        "cost_per_joule",
        "meier_cost.gamma",
    ) in redefs, redefs


def test_fanout_collapses_to_one_producer_channel() -> None:
    """SC-2 fan-out: the one plant attribute ``scale`` is consumed by TWO modules
    (``scale_a`` and ``scale_b``). Both inputs collapse onto the SAME entry point —
    one producer channel wired to both consumers, not two separate EPs."""
    sources = offline_input_sources(MODEL)
    a = sources[("twoleveldesign__hif_plant__scale_a", "s")]
    b = sources[("twoleveldesign__hif_plant__scale_b", "s")]
    assert a.source_type == "entry_point" and b.source_type == "entry_point"
    assert a.qualified_name == b.qualified_name == "TwoLevelLib__IFE_Power_Plant__scale"


def test_plain_cross_part_attr_shape() -> None:
    """SC-2 plain cross-part-attribute shape (the P1 note, no calc output in the chain):
    ``maint_calc.rate`` reads the driver's plain ``maintenance_rate`` attribute — distinct
    from the calc-output-valued ``cost_per_joule = gamma`` chain above it."""
    sources = offline_input_sources(MODEL)
    src = sources[("twoleveldesign__hif_plant__maint_calc", "rate")]
    assert src.source_type == "entry_point"
    assert src.qualified_name == "TwoLevelLib__IFE_Driver__maintenance_rate"


@requires_license
def test_spec_chain_twolevel_loads_live() -> None:
    """Guard against fixture rot: the committed model still parses through the live
    extractor (the snapshot above is only as trustworthy as a parseable source)."""
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    ex = SysMLDataExtractor([FIXTURES_DIR / "spec_chain_twolevel"])
    assert ex.load_models()
    calc_defs = ex.extract_calculation_definitions()
    assert {c.qualified_name for c in calc_defs} == {
        "TwoLevelLib::MeierCost",
        "TwoLevelLib::LcoeCalc",
        # Item-1 SC-2 additions: plain cross-part attr consumer + fan-out consumer.
        "TwoLevelLib::MaintCalc",
        "TwoLevelLib::ScaleCalc",
    }
