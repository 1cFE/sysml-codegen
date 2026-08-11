"""Exact occurrence authority reached through every public builder route."""

from __future__ import annotations

import shutil

import pytest

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.orchestration.snapshot_context import (
    build_pipeline_context_from_snapshot,
)
from sysml_codegen.snapshot import capture_snapshot
from sysml_codegen.snapshot.instance_graph import decode_instance_graph
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "source_identity_mixed_consumers"


@pytest.fixture(scope="module")
def route_graphs(tmp_path_factory):
    output = tmp_path_factory.mktemp("cut-occ")
    captured = capture_snapshot([FIXTURE], output / "in-place.json")
    relocated = output / "relocated" / "case.json"
    relocated.parent.mkdir()
    shutil.copyfile(captured, relocated)
    contexts = {
        "live": build_pipeline_context([FIXTURE]),
        "in_place_v6": build_pipeline_context_from_snapshot(captured),
        "relocated_v6": build_pipeline_context_from_snapshot(relocated),
    }
    return {
        route: decode_instance_graph(context._instance_bytes)
        for route, context in contexts.items()
    }


def test_public_routes_preserve_exact_occurrence_records(route_graphs) -> None:
    inventories = {
        route: {
            occurrence.occurrence_id.to_wire(): (
                occurrence.parent_id.to_wire() if occurrence.parent_id is not None else None,
                occurrence.containment_slot.root_declaration.to_wire(),
                occurrence.occurrence_index,
                occurrence.effective_usage_id.to_wire(),
                tuple(item.to_wire() for item in occurrence.effective_type_ids),
                occurrence.display_segment,
            )
            for occurrence in graph.occurrences.values()
        }
        for route, graph in route_graphs.items()
    }
    assert inventories["live"]
    assert inventories["in_place_v6"] == inventories["live"]
    assert inventories["relocated_v6"] == inventories["live"]


def test_plural_occurrences_use_one_slot_and_exact_indices(route_graphs) -> None:
    for graph in route_graphs.values():
        cells = [
            occurrence
            for occurrence in graph.occurrences.values()
            if occurrence.display_segment.startswith("cell[")
        ]
        assert {item.display_segment for item in cells} == {"cell[0]", "cell[1]", "cell[2]"}
        assert {item.occurrence_index for item in cells} == {0, 1, 2}
        assert len({item.containment_slot for item in cells}) == 1
        assert len({item.parent_id for item in cells}) == 1
        assert len({item.effective_usage_id for item in cells}) == 1
        assert len({item.effective_type_ids for item in cells}) == 1


def test_every_occurrence_scoped_node_has_a_public_route_record(route_graphs) -> None:
    for graph in route_graphs.values():
        assert all(
            node.scope in graph.occurrences
            for population in (graph.attrs, graph.calcs, graph.constraints)
            for node in population.values()
            if node.scope.__class__.__name__ == "OccurrenceId"
        )
