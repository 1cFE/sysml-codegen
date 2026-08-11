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

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.snapshot.instance_graph import decode_instance_graph
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.elaboration_graph import attr, calc, node_ref, producer_ref

pytestmark = requires_license

MIXED = "source_identity_mixed_consumers"


@pytest.fixture(scope="module")
def graph_cache():
    cache = {}

    def get(name: str):
        if name not in cache:
            context = build_pipeline_context([FIXTURES_DIR / name])
            cache[name] = decode_instance_graph(context._instance_bytes)
        return cache[name]

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


def test_modeled_finite_multiplicity_expands_the_aggregation() -> None:
    """``cell[count]`` has four occurrences when ``count`` is modeled as 4."""
    context = build_pipeline_context([FIXTURES_DIR / "d38_caret"])
    graph = decode_instance_graph(
        context._instance_bytes
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
