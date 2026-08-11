"""EXPRESSION-redefinition aggregations through the elaborator (Item 5 Phase 2, leg 5).

Design D6, second half: a ``:>>`` redefinition whose value is an expression
(``:>> station_total = rig.gain_setting + 100.0``, ``sum(cell.cell_cost)``)
converts the attribute into a computed calc node whose term edges come from the
shared neutral aggregation decomposition — every term carries its Item-2
resolved facts and resolves by the same referent rules as bindings. A
``sum(part.attr)`` term expands to one edge per concrete instance under the
node's anchor (occurrence enumeration, never QN string surgery), following
per-instance chain redefinitions through their aliases — which is exactly the
Item-10 cross-part collapse family, now impossible by construction. Findings:
``.project/research/20260807-173125_elaborator-aggregations.md``.

All tests require a live SysIDE license.
"""

from __future__ import annotations

import pytest

from sysml_codegen.elaboration import (
    InstanceGraph,
    elaborate,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.elaboration_graph import attr, calc, node_ref, producer_ref

pytestmark = requires_license

MIXED = "source_identity_mixed_consumers"


@pytest.fixture(scope="module")
def graph_cache():
    cache: dict[str, InstanceGraph] = {}

    def get(name: str, *, strict: bool = True) -> InstanceGraph:
        key = f"{name}:{strict}"
        if key not in cache:
            extractor = SysMLDataExtractor([FIXTURES_DIR / name])
            assert extractor.load_models(), f"fixture {name} failed to load"
            cache[key] = elaborate(
                extractor.model,
                extractor.extract_calculation_definitions(),
                validation_diagnostics=extractor.diagnostics.validation,
                strict=strict,
            )
        return cache[key]

    return get


def test_expression_redefinition_becomes_a_computed_node(graph_cache) -> None:
    """``:>> station_total = rig.gain_setting + 100.0`` — a computed node at
    the occurrence, its chain term wired to the rig node; the attribute node is
    replaced, and elaboration stays strict-clean."""
    graph = graph_cache(MIXED)
    node = calc(graph, f"{MIXED}__station__station_total")
    assert node.is_computed
    assert set(node.inputs.values()) == {node_ref(graph, f"{MIXED}__station__rig__gain_setting")}
    with pytest.raises(KeyError):
        attr(graph, f"{MIXED}__station__station_total")
    assert graph.diagnostics == []


def test_sum_expands_to_one_edge_per_instance(graph_cache) -> None:
    """``:>> bank_total = sum(cell.cell_cost)`` — three edges, one per
    ``cell[i]`` occurrence node (multiplicity by occurrence enumeration)."""
    graph = graph_cache(MIXED)
    node = calc(graph, f"{MIXED}__bank__bank_total")
    assert set(node.inputs.values()) == {
        node_ref(graph, f"{MIXED}__bank__cell[{i}]__cell_cost") for i in range(3)
    }


def test_qualified_aggregation_term_reaches_the_contained_occurrence(
    graph_cache,
) -> None:
    """``:>> qual_total = 'Qual Plant'::level + 1.0`` on the CONTAINING station:
    the def-level referent is declared by no enclosing occurrence — the
    off-ancestor fallback anchors at the unique contained occurrence."""
    graph = graph_cache(MIXED)
    node = calc(graph, f"{MIXED}__qual_station__qual_total")
    assert set(node.inputs.values()) == {
        node_ref(graph, f"{MIXED}__qual_station__qual_plant__level")
    }


def test_aggregation_chain_to_producer_output(graph_cache) -> None:
    """``:>> computed_total = source_identity_computed.producer_calc.result + 1.0``
    — the aggregation term is a producer edge, no minted input (C24's agg leg)."""
    graph = graph_cache(MIXED)
    node = calc(graph, f"{MIXED}__computed_station__computed_total")
    assert set(node.inputs.values()) == {
        producer_ref(
            graph,
            f"{MIXED}__computed_station__source_identity_computed__producer_calc",
            "result",
        )
    }


def test_crosspart_rollup_keeps_per_child_channels_distinct(graph_cache) -> None:
    """The Item-10 collapse family (crosspart_rollup_twolevel): the rollup's
    two terms follow each child's OWN ``:>> capital = cost_calc.cost`` alias —
    distinct producers, a qualifier-drop collapse cannot occur."""
    graph = graph_cache("crosspart_rollup_twolevel", strict=False)
    plant = "CrossPartRollupDesign__rollup_plant"
    node = calc(graph, f"{plant}__grand_total")
    assert node.is_computed
    assert set(node.inputs.values()) == {
        producer_ref(graph, f"{plant}__a__cost_calc", "cost"),
        producer_ref(graph, f"{plant}__b__cost_calc", "cost"),
    }
    consumer = calc(graph, f"{plant}__final")
    assert consumer.input_by_name("t") == producer_ref(
        graph, f"{plant}__grand_total", "grand_total"
    )


def test_local_term_and_per_instance_producers_mix(graph_cache) -> None:
    """agg_localterm_probe: ``sum(cell.capital_cost) * markup`` — three
    per-instance producer edges (each through the cell's chain redefinition)
    plus the plain local attribute node."""
    graph = graph_cache("agg_localterm_probe", strict=False)
    bank = "AggLocalTermProbe__the_bank"
    node = calc(graph, f"{bank}__capital_cost")
    expected = {producer_ref(graph, f"{bank}__cell[{i}]__cost_model", "cost") for i in range(3)}
    expected.add(node_ref(graph, f"{bank}__markup"))
    assert set(node.inputs.values()) == expected


def test_modeled_finite_multiplicity_expands_the_aggregation() -> None:
    """``cell[count]`` has four occurrences when ``count`` is modeled as 4."""
    extractor = SysMLDataExtractor([FIXTURES_DIR / "d38_caret"])
    assert extractor.load_models()
    graph = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
    )

    pack = "D38Design__plant__pack"
    total = calc(graph, f"{pack}__total_cost")
    assert {
        occurrence.display_path
        for occurrence in graph.attrs.values()
        if occurrence.display_name == "base_cost"
    } == {f"{pack}__cell[{index}]__base_cost" for index in range(4)}
    assert set(total.inputs.values()) == {
        node_ref(graph, f"{pack}__cell[{index}]__base_cost") for index in range(4)
    } | {node_ref(graph, f"{pack}__exponent")}


def test_the_caret_reaches_python_as_power_never_as_xor(tmp_path) -> None:
    """D3-8 on the exact route: ``^`` is SysML's power alias, and ``^`` is Python's XOR.

    A renderer that passed the character through would emit code that runs, returns a
    number, and is wrong — the worst failure class this recovery exists to close. The
    exact route maps it at ``elaboration/project.py:671``
    (``"**" if expression.operator == "^"``).

    Asserted one layer further out than the rest of this module, in the generated
    implementation stencil, because that is where a reader would meet the bug: the
    aggregation is expanded into one term per occurrence and the exponent applies to the
    sum. The old legacy pin read a transformed expression *string* off the extractor;
    this reads the Python that ships.

    Gate 4C part 7 chunk 14 authored this as the replacement for row L-174's D3-8 node.
    """
    from sysml_codegen.cli import GenerationConfig, run_codegen

    name = "d38_caret_rendering"
    package = tmp_path / name
    assert run_codegen(
        GenerationConfig(
            models_path=FIXTURES_DIR / "d38_caret",
            output_path=package,
            package_name=name,
            overwrite=True,
        )
    )

    stencil = next(package.rglob("total_cost_impl.py"))
    body = next(
        line.strip()
        for line in stencil.read_text().splitlines()
        if line.strip().startswith("return")
    )
    assert " ** " in body, body
    assert " ^ " not in body, body
    # The four occurrences are summed before the exponent applies, not after.
    assert all(f"total_cost_{index}" in body for index in range(4)), body
