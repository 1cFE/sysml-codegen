"""FORMULA computed attributes through the elaborator (Item 5 Phase 2, leg 4).

Design D6: an attribute whose declared value is an expression
(``attribute area = length * width``) elaborates to a COMPUTED calc node at the
attribute's own occurrence path — its single output is the attribute's name, its
inputs are the expression's feature terms resolved by the same referent rules as
calc bindings. Consumers referencing the attribute get a producer edge, so
FORMULA→FORMULA chains (previously unsupported by the legacy front end) follow
naturally. Fixture: ``attr_expr_probe`` (patterns A–D). Findings:
``.project/research/20260807-171548_elaborator-computed-attributes.md``.

All tests require a live SysIDE license.
"""

from __future__ import annotations

import pytest

from sysml_codegen.elaboration import (
    InstanceGraph,
    NodeRef,
    ProducerRef,
    elaborate,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

P = "AttrExprProbeDesign__probe_design"


@pytest.fixture(scope="module")
def graph() -> InstanceGraph:
    extractor = SysMLDataExtractor([FIXTURES_DIR / "attr_expr_probe"])
    assert extractor.load_models()
    return elaborate(extractor.model, extractor.extract_calculation_definitions())


def test_probe_elaborates_strict_and_clean(graph: InstanceGraph) -> None:
    assert graph.diagnostics == []


def test_simple_expression_becomes_a_computed_node(graph: InstanceGraph) -> None:
    """A1: ``area = length * width`` — a computed node whose terms are the two
    entry attribute nodes; no attribute node competes with it."""
    node = graph.calcs[f"{P}__area"]
    assert node.is_computed
    assert node.calc_name == "area"
    assert node.inputs == {
        "length": NodeRef(f"{P}__length"),
        "width": NodeRef(f"{P}__width"),
    }
    assert f"{P}__area" not in graph.attrs


def test_duplicate_terms_collapse_to_one_edge(graph: InstanceGraph) -> None:
    """B6: ``(m_neutron * p_fusion)`` appears twice in the blanket formula —
    one term edge per distinct feature, never one per mention."""
    node = graph.calcs[f"{P}__p_blanket_thermal"]
    assert node.is_computed
    assert set(node.inputs) == {
        "m_neutron",
        "p_fusion",
        "p_input",
        "eta_thermal",
        "f_pump",
        "eta_pump",
        "f_subsystem",
    }


def test_formula_to_formula_chain(graph: InstanceGraph) -> None:
    """C1/C2: ``cost = area * rate`` and ``marked_up_cost = cost * markup`` —
    computed-to-computed edges, the previously unsupported shape."""
    cost = graph.calcs[f"{P}__cost"]
    assert cost.inputs["area"] == ProducerRef(f"{P}__area", "area")
    marked = graph.calcs[f"{P}__marked_up_cost"]
    assert marked.inputs["cost"] == ProducerRef(f"{P}__cost", "cost")


def test_formula_fan_in_from_two_computed(graph: InstanceGraph) -> None:
    """C3: ``cost_density = cost / volume`` reads two computed producers."""
    node = graph.calcs[f"{P}__cost_density"]
    assert node.inputs == {
        "cost": ProducerRef(f"{P}__cost", "cost"),
        "volume": ProducerRef(f"{P}__volume", "volume"),
    }


def test_computed_attribute_feeds_a_calc_usage(graph: InstanceGraph) -> None:
    """D1: ``scale_calc.value = area`` — a calc-usage binding whose referent is
    a computed attribute resolves to the computed producer."""
    scale = graph.calcs[f"{P}__scale_calc"]
    assert not scale.is_computed
    assert scale.inputs["value"] == ProducerRef(f"{P}__area", "area")


def test_calc_output_inside_an_expression(graph: InstanceGraph) -> None:
    """D2: ``scaled_area = scale_calc.result * 2.0`` — a chain term to a real
    calc usage's output inside a computed attribute's expression."""
    node = graph.calcs[f"{P}__scaled_area"]
    assert node.is_computed
    assert node.inputs == {
        "scale_calc__result": ProducerRef(f"{P}__scale_calc", "result")
    }


def test_pure_expose_stays_an_alias_not_a_computed_node(
    graph: InstanceGraph,
) -> None:
    """D3/D4: a pure chain value (``scale_result = scale_calc.result``,
    multi-output ``half_vol``/``quarter_vol``) is an alias edge, NOT a computed
    node — the expose never mints a module of its own."""
    for attr_name, output in (
        ("scale_result", ("scale_calc", "result")),
        ("half_vol", ("split", "half")),
        ("quarter_vol", ("split", "quarter")),
    ):
        assert f"{P}__{attr_name}" not in graph.calcs
        node = graph.attrs[f"{P}__{attr_name}"]
        assert node.alias_target == ProducerRef(f"{P}__{output[0]}", output[1])


def test_all_fifteen_computed_attributes_lift(graph: InstanceGraph) -> None:
    computed = sorted(
        calc.calc_name for calc in graph.calcs.values() if calc.is_computed
    )
    assert computed == [
        "area",
        "cost",
        "cost_density",
        "gross_electric_simple",
        "marked_up_cost",
        "minor_radius",
        "net_length",
        "p_alpha",
        "p_blanket_thermal",
        "p_neutron",
        "perimeter",
        "q_scientific",
        "scaled_area",
        "total_dim",
        "volume",
    ]
