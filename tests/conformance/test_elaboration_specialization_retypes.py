"""Specialization + usage-level retypes through the elaborator (Item 5 Phase 2, leg 3).

The two-level shape (``spec_chain_twolevel``, mirroring fusion-tea's hif_plant):
a part usage typed by the BASE plant def with an inline ``part :>> driver :
'HIF Driver'`` retype, where the specialized driver def re-sources an inherited
attribute with a chain redefinition (``:>> cost_per_joule = meier_cost.gamma``).
The legacy pipeline loses this edge (the WI-015 unwired pin: usage-level retypes
are not in the def-keyed type map). In the instance graph the occurrence carries
its most-specific type, so the leg's implementation is the redefinition-borne
EXPOSE alias: chain-valued ``:>>`` members enqueue alias facts in tier order.
Findings: ``.project/research/20260807-170356_elaborator-specialization-retypes.md``.

Also pinned here: the def-context remap rule accepts a whole path that IS a
definition key (a ``:>>`` owned directly by a specialized def) — the expansion
previously checked only proper prefixes, so def-owned redefinitions never
anchored (latent for literal def-level ``:>>`` too).

All tests require a live SysIDE license.
"""

from __future__ import annotations

import pytest

from sysml_codegen.elaboration import (
    ElaborationError,
    InstanceGraph,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.source_evidence import ReadinessCode
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.elaboration_graph import attr, calc, node_ref, producer_ref
from tests.helpers.raw_elaboration import elaborate

pytestmark = requires_license

PLANT = "TwoLevelDesign__hif_plant"


@pytest.fixture(scope="module")
def loaded() -> SysMLDataExtractor:
    extractor = SysMLDataExtractor([FIXTURES_DIR / "spec_chain_twolevel"])
    assert extractor.load_models()
    return extractor


@pytest.fixture(scope="module")
def graph(loaded: SysMLDataExtractor) -> InstanceGraph:
    return elaborate(
        loaded.model,
        loaded.extract_calculation_definitions(),
        validation_diagnostics=loaded.diagnostics.validation,
        strict=False,
    )


def test_strict_rejects_the_fixtures_own_self_binding(
    loaded: SysMLDataExtractor,
) -> None:
    """Fourth corpus member of the SRC-01 class: ``meier_cost``'s
    ``in drive_power = drive_power`` on the base driver def."""
    with pytest.raises(ElaborationError) as excinfo:
        elaborate(
            loaded.model,
            loaded.extract_calculation_definitions(),
            validation_diagnostics=loaded.diagnostics.validation,
        )
    (finding,) = excinfo.value.findings
    assert finding.code is ReadinessCode.SI_SELF_BINDING
    assert finding.usage_qualified_name == "TwoLevelLib__IFE_Driver__meier_cost"


def test_retyped_usage_carries_the_specialized_definition(
    graph: InstanceGraph,
) -> None:
    """``part :>> driver : 'HIF Driver'`` on the hif_plant USAGE: the driver
    occurrence exists once and its inherited base attributes materialize
    (base-def template calc included)."""
    assert attr(graph, f"{PLANT}__driver__drive_power").value == 50.0
    calc(graph, f"{PLANT}__driver__meier_cost")


def test_chain_redefinition_becomes_an_alias_at_the_occurrence(
    graph: InstanceGraph,
) -> None:
    """``:>> cost_per_joule = meier_cost.gamma`` on the SPECIALIZED def aliases
    the inherited attribute to the producer at the retyped occurrence."""
    node = attr(graph, f"{PLANT}__driver__cost_per_joule")
    assert node.alias_target == producer_ref(graph, f"{PLANT}__driver__meier_cost", "gamma")


def test_inherited_consumer_reaches_the_specialized_producer(
    graph: InstanceGraph,
) -> None:
    """The WI-015 edge: lcoe_calc is declared on the BASE plant def and binds
    ``driver.cost_per_joule``; through the retype and the chain redefinition it
    wires to gamma — not to a dead library-default entry point."""
    lcoe = calc(graph, f"{PLANT}__lcoe_calc")
    assert lcoe.input_by_name("cost_per_joule") == producer_ref(
        graph, f"{PLANT}__driver__meier_cost", "gamma"
    )


def test_plain_cross_part_attribute_stays_a_node_reference(
    graph: InstanceGraph,
) -> None:
    """``maint_calc.rate = driver.maintenance_rate`` — no calc output in the
    chain, so the input is the attribute node itself (the P1 acceptance shape)."""
    maint = calc(graph, f"{PLANT}__maint_calc")
    assert maint.input_by_name("rate") == node_ref(graph, f"{PLANT}__driver__maintenance_rate")
    assert attr(graph, f"{PLANT}__driver__maintenance_rate").value == 3.0


def test_fanout_collapses_to_one_shared_node(graph: InstanceGraph) -> None:
    """Two ScaleCalc instances read the one plant ``scale`` attribute — one
    node, two consumer edges (SC-2's collapse, by construction)."""
    shared = node_ref(graph, f"{PLANT}__scale")
    assert calc(graph, f"{PLANT}__scale_a").input_by_name("s") == shared
    assert calc(graph, f"{PLANT}__scale_b").input_by_name("s") == shared


def test_fusion_tea_driver_edge_wires_end_to_end() -> None:
    """The customer's real shape (lenient — fusion_tea carries 15 SRC-01
    self-bindings): hif_plant's retyped driver aliases cost_per_joule to
    meier_cost.gamma and the usage-authored lcoe_calc consumes that channel."""
    extractor = SysMLDataExtractor([FIXTURES_DIR / "fusion_tea"])
    assert extractor.load_models()
    graph = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
        strict=False,
    )
    driver = "hif_plant_pkg__hif_plant__driver"
    node = attr(graph, f"{driver}__cost_per_joule")
    assert node.alias_target == producer_ref(graph, f"{driver}__meier_cost", "gamma")
    lcoe = calc(graph, "hif_plant_pkg__hif_plant__lcoe_calc")
    assert lcoe.input_by_name("driver_cost_constant") == producer_ref(
        graph, f"{driver}__meier_cost", "gamma"
    )


# ---------------------------------------------------------------------------
# The single-level shape — Gate 4C part 7 chunk 13, replacing row L-183
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def single_level_graph() -> InstanceGraph:
    """``spec_chain_channel``: consumer and retype on ONE def, elaborated lenient."""
    extractor = SysMLDataExtractor([FIXTURES_DIR / "spec_chain_channel"])
    assert extractor.load_models()
    return elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
        strict=False,
    )


def test_the_single_level_chain_reaches_gamma_too(single_level_graph: InstanceGraph) -> None:
    """The same gamma edge where the retype and the consumer live on one def.

    The two-level fixture above is the harder shape — the retype on a part usage, the
    consumer inherited from the base def — and it is the one that mirrors fusion-tea. The
    single-level shape is not merely its easy case: it takes a different path through the
    resolver, because ``usage_type_map`` picks the specialized definition from the *def*
    rather than from an inline usage-level retype. So it gets its own assertion rather than
    an argument that it must follow.

    The specialized plant def retypes ``driver`` to ``'HIF Driver'``, which redefines
    ``cost_per_joule :>> meier_cost.gamma``, and ``lcoe_calc`` on that same def binds
    ``cost_per_joule = driver.cost_per_joule``.
    """
    plant = "SpecChainDesign__spec_chain_plant"
    lcoe = calc(single_level_graph, f"{plant}__lcoe_calc")
    assert lcoe.input_by_name("cost_per_joule") == producer_ref(
        single_level_graph, f"{plant}__driver__meier_cost", "gamma"
    )
