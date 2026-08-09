"""Isolation and comparison gates for the internal exact-ID dual-run route."""

from __future__ import annotations

import inspect
from pathlib import Path

from sysml_codegen.elaboration.diff import compare_computation_graphs
from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license


def test_internal_exact_route_is_complete_and_deterministic() -> None:
    fixture = FIXTURES_DIR / "source_identity_mixed_consumers"

    first = build_elaborated_pipeline([fixture])
    second = build_elaborated_pipeline([fixture])

    assert first == second
    assert first.modules
    assert first.entry_point_groups
    assert first.constraint_catalog is not None
    assert compare_computation_graphs(first, second) == ()


def test_internal_route_is_not_a_shipped_builder_flag_or_legacy_adapter() -> None:
    signature = inspect.signature(build_pipeline_context)
    assert "elaborated" not in signature.parameters
    assert "exact" not in signature.parameters

    source = Path(inspect.getsourcefile(build_elaborated_pipeline) or "").read_text()
    assert "pipeline_builder" not in source
    assert "part_instance_index" not in source
    assert "build_pipeline_context" not in source
    assert "snapshot" not in source


def test_diff_reports_generation_sections_without_mutating_either_graph() -> None:
    fixture = FIXTURES_DIR / "source_identity_mixed_consumers"
    graph = build_elaborated_pipeline([fixture])
    changed = graph.model_copy(
        update={"execution_order": [*graph.execution_order, "foreign"]}, deep=True
    )

    differences = compare_computation_graphs(graph, changed)

    assert [difference.section for difference in differences] == ["execution_order"]
    assert graph.execution_order != changed.execution_order
