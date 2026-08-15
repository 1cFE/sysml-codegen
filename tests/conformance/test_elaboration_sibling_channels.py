"""Sibling same-name channels through the elaborator (Item 5 Phase 2, leg 2).

The SC-3 shape (``sibling_channel_ambiguity``): two same-type sibling chambers
each own a ``power_calc`` and each expose ``power = power_calc.power``, so the
flat name collides twice; the consumer binds ``chamber_b.power`` specifically.
The legacy pipeline needs instance-scoped channel machinery to disambiguate —
in the instance graph the disambiguation holds by construction, because every
occurrence is its own node. No leg-specific implementation was needed; these
tests pin that the leg-1 mechanics already carry the shape. Findings:
``.project/research/20260807-165502_elaborator-sibling-channels.md``.

The fixture also authors the degenerate ``in fuel = fuel`` idiom on the shared
``Chamber`` producer — a real SRC-01 in the fixture, rejected strict and
reported lenient exactly like catf_mfe's.

All tests require a live SysIDE license.
"""

from __future__ import annotations

import pytest

from sysml_codegen.elaboration import (
    ElaborationError,
    InstanceGraph,
    elaborate,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.source_evidence import ReadinessCode
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.elaboration_graph import attr, calc, producer_ref

pytestmark = requires_license

PKG = "SiblingDesign"
PLANT = f"{PKG}__twin_plant"


@pytest.fixture(scope="module")
def loaded() -> SysMLDataExtractor:
    extractor = SysMLDataExtractor([FIXTURES_DIR / "sibling_channel_ambiguity"])
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
    """``in fuel = fuel`` on the shared Chamber producer is a real SRC-01 the
    fixture authors; strict elaboration rejects it at the declaration."""
    with pytest.raises(ElaborationError) as excinfo:
        elaborate(
            loaded.model,
            loaded.extract_calculation_definitions(),
            validation_diagnostics=loaded.diagnostics.validation,
        )
    (finding,) = excinfo.value.findings
    assert finding.code is ReadinessCode.SI_SELF_BINDING
    assert finding.usage_qualified_name == "SiblingLib__Chamber__power_calc"
    assert finding.param_name == "fuel"


def test_lenient_reports_one_declaration_level_finding(
    graph: InstanceGraph,
) -> None:
    """Lenient records the self-binding ONCE (declaration-level, not per
    occurrence) and skips only that binding."""
    self_bindings = [
        diagnostic
        for diagnostic in graph.diagnostics
        if diagnostic.code is ReadinessCode.SI_SELF_BINDING
    ]
    assert len(self_bindings) == 1
    for chamber in ("chamber_a", "chamber_b"):
        node = calc(graph, f"{PLANT}__{chamber}__power_calc")
        assert not any(
            name == "fuel" and port in node.inputs for port, name in node.input_names.items()
        )


def test_sibling_producers_are_distinct_nodes(graph: InstanceGraph) -> None:
    """Two same-type siblings expand to two producer calc nodes — distinct by
    occurrence-path identity, no collision to disambiguate later."""
    first = calc(graph, f"{PLANT}__chamber_a__power_calc")
    second = calc(graph, f"{PLANT}__chamber_b__power_calc")
    assert first.node_id != second.node_id


def test_sibling_exposes_alias_their_own_producer(graph: InstanceGraph) -> None:
    """Each sibling's exposed ``power`` aliases ITS OWN producer instance —
    the def-declared expose resolves per occurrence."""
    for chamber in ("chamber_a", "chamber_b"):
        node = attr(graph, f"{PLANT}__{chamber}__power")
        assert node.alias_target == producer_ref(graph, f"{PLANT}__{chamber}__power_calc", "power")


def test_consumer_reaches_exactly_chamber_b(graph: InstanceGraph) -> None:
    """The SC-3 check: ``in chamber_power = chamber_b.power`` wires to
    chamber_b's instance channel — never first-wins to chamber_a."""
    total = calc(graph, f"{PLANT}__total_calc")
    assert total.input_by_name("chamber_power") == producer_ref(
        graph, f"{PLANT}__chamber_b__power_calc", "power"
    )
