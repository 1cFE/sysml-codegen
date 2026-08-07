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
    NodeRef,
    ProducerRef,
    elaborate,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.source_evidence import ReadinessCode
from tests.conftest import FIXTURES_DIR, requires_license

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
        loaded.model, loaded.extract_calculation_definitions(), strict=False
    )


def test_strict_rejects_the_fixtures_own_self_binding(
    loaded: SysMLDataExtractor,
) -> None:
    """Fourth corpus member of the SRC-01 class: ``meier_cost``'s
    ``in drive_power = drive_power`` on the base driver def."""
    with pytest.raises(ElaborationError) as excinfo:
        elaborate(loaded.model, loaded.extract_calculation_definitions())
    (finding,) = excinfo.value.findings
    assert finding.code is ReadinessCode.SI_SELF_BINDING
    assert finding.usage_qualified_name == "TwoLevelLib__IFE_Driver__meier_cost"


def test_retyped_usage_carries_the_specialized_definition(
    graph: InstanceGraph,
) -> None:
    """``part :>> driver : 'HIF Driver'`` on the hif_plant USAGE: the driver
    occurrence exists once and its inherited base attributes materialize
    (base-def template calc included)."""
    assert f"{PLANT}__driver__drive_power" in graph.attrs
    assert graph.attrs[f"{PLANT}__driver__drive_power"].value == 50.0
    assert f"{PLANT}__driver__meier_cost" in graph.calcs


def test_chain_redefinition_becomes_an_alias_at_the_occurrence(
    graph: InstanceGraph,
) -> None:
    """``:>> cost_per_joule = meier_cost.gamma`` on the SPECIALIZED def aliases
    the inherited attribute to the producer at the retyped occurrence."""
    node = graph.attrs[f"{PLANT}__driver__cost_per_joule"]
    assert node.alias_target == ProducerRef(f"{PLANT}__driver__meier_cost", "gamma")


def test_inherited_consumer_reaches_the_specialized_producer(
    graph: InstanceGraph,
) -> None:
    """The WI-015 edge: lcoe_calc is declared on the BASE plant def and binds
    ``driver.cost_per_joule``; through the retype and the chain redefinition it
    wires to gamma — not to a dead library-default entry point."""
    lcoe = graph.calcs[f"{PLANT}__lcoe_calc"]
    assert lcoe.inputs["cost_per_joule"] == ProducerRef(
        f"{PLANT}__driver__meier_cost", "gamma"
    )


def test_plain_cross_part_attribute_stays_a_node_reference(
    graph: InstanceGraph,
) -> None:
    """``maint_calc.rate = driver.maintenance_rate`` — no calc output in the
    chain, so the input is the attribute node itself (the P1 acceptance shape)."""
    maint = graph.calcs[f"{PLANT}__maint_calc"]
    assert maint.inputs["rate"] == NodeRef(f"{PLANT}__driver__maintenance_rate")
    assert graph.attrs[f"{PLANT}__driver__maintenance_rate"].value == 3.0


def test_fanout_collapses_to_one_shared_node(graph: InstanceGraph) -> None:
    """Two ScaleCalc instances read the one plant ``scale`` attribute — one
    node, two consumer edges (SC-2's collapse, by construction)."""
    shared = NodeRef(f"{PLANT}__scale")
    assert graph.calcs[f"{PLANT}__scale_a"].inputs["s"] == shared
    assert graph.calcs[f"{PLANT}__scale_b"].inputs["s"] == shared


def test_fusion_tea_driver_edge_wires_end_to_end() -> None:
    """The customer's real shape (lenient — fusion_tea carries 15 SRC-01
    self-bindings): hif_plant's retyped driver aliases cost_per_joule to
    meier_cost.gamma and the usage-authored lcoe_calc consumes that channel."""
    extractor = SysMLDataExtractor([FIXTURES_DIR / "fusion_tea"])
    assert extractor.load_models()
    graph = elaborate(
        extractor.model, extractor.extract_calculation_definitions(), strict=False
    )
    driver = "hif_plant_pkg__hif_plant__driver"
    node = graph.attrs[f"{driver}__cost_per_joule"]
    assert node.alias_target == ProducerRef(f"{driver}__meier_cost", "gamma")
    lcoe = graph.calcs["hif_plant_pkg__hif_plant__lcoe_calc"]
    assert lcoe.inputs["driver_cost_constant"] == ProducerRef(
        f"{driver}__meier_cost", "gamma"
    )
