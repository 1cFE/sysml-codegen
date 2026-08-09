"""Parser-to-edge exact-ID vertical slice for every Phase-2 resolution class."""

from __future__ import annotations

from collections.abc import Collection, Iterator
from typing import Any

import pytest
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration import (
    InstanceGraph,
    NodeId,
    NodeRef,
    OutputPortId,
    ProducerRef,
    elaborate,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license


def _elaborate(name: str) -> InstanceGraph:
    extractor = SysMLDataExtractor([FIXTURES_DIR / name])
    assert extractor.load_models()
    return elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
    )


def _input(graph: InstanceGraph, calc_path: str, formal_name: str) -> Any:
    return graph.calc_by_display_path(calc_path).input_by_name(formal_name)


def test_exact_vertical_slice_ignores_nearer_same_name_and_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    shadowed = _elaborate("shadowed_reference")
    edge = _input(
        shadowed,
        "ShadowedReference__the_outer__inner__shadowed_calc",
        "factor",
    )
    outer = shadowed.attr_by_display_path("ShadowedReference__the_outer__scale")
    inner = shadowed.attr_by_display_path("ShadowedReference__the_outer__inner__scale")
    assert edge == NodeRef(outer.node_id)
    assert edge != NodeRef(inner.node_id)
    assert isinstance(edge.target, NodeId)

    original_elements_of_type = SysideAdapter.elements_of_type

    def reversed_elements_of_type(
        cls: type[SysideAdapter],
        model: Any,
        type_name: str,
        *,
        include_subtypes: bool = False,
        exclude: Collection[str] = (),
    ) -> Iterator[Any]:
        del cls
        elements = original_elements_of_type(
            model,
            type_name,
            include_subtypes=include_subtypes,
            exclude=exclude,
        )
        return iter(reversed(list(elements)))

    monkeypatch.setattr(
        SysideAdapter,
        "elements_of_type",
        classmethod(reversed_elements_of_type),
    )
    second = _elaborate("shadowed_reference")
    assert second.semantic_edges() == shadowed.semantic_edges()
    assert shadowed.rendered_names_are_metadata_only()


def test_definition_usage_chain_expression_and_sum_edges_are_typed() -> None:
    graph = _elaborate("source_identity_mixed_consumers")

    definition_edge = _input(
        graph,
        "source_identity_mixed_consumers__avail_ctx__avail_plant__def_authored_calc",
        "value_in",
    )
    usage_edge = _input(
        graph,
        "source_identity_mixed_consumers__avail_ctx__avail_plant__usage_authored_calc",
        "value_in",
    )
    availability = graph.attr_by_display_path(
        "source_identity_mixed_consumers__avail_ctx__avail_plant__availability"
    )
    assert definition_edge == usage_edge == NodeRef(availability.node_id)

    producer_edge = _input(
        graph,
        "source_identity_mixed_consumers__computed_station__computed_calc",
        "value_in",
    )
    assert isinstance(producer_edge, ProducerRef)
    assert isinstance(producer_edge.target, OutputPortId)

    formula = graph.calc_by_display_path("source_identity_mixed_consumers__station__station_total")
    assert formula.inputs
    assert all(isinstance(edge.target, NodeId | OutputPortId) for edge in formula.inputs.values())

    aggregation = graph.calc_by_display_path("source_identity_mixed_consumers__bank__bank_total")
    assert len(aggregation.inputs) == 3
    assert all(isinstance(edge.target, NodeId) for edge in aggregation.inputs.values())
