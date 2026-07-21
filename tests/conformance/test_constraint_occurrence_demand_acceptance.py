"""Stable public RED/GREEN surface for lifecycle-remediation Item 1.

These tests intentionally use only public construction, capture, and replay APIs that
exist at the Item 0 predecessor and the candidate.  Same-checkout replay assertions are
regression evidence; they do not certify relocation or the composed artifact thread.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from sysml_codegen.snapshot import build_full_graph_from_snapshot, capture_snapshot
from tests.conftest import FIXTURES_DIR, requires_license


ROOT = FIXTURES_DIR / "constraint_occurrence_demand"
MATERIALIZER_LOGGER = "sysml_codegen.resolution.supplied_values"


def _entry_points(graph) -> list:
    return [parameter for group in graph.entry_point_groups for parameter in group.parameters]


def _entry_point(graph, qualified_name: str):
    return next(item for item in _entry_points(graph) if item.qualified_name == qualified_name)


def _materializer_messages(caplog: pytest.LogCaptureFixture) -> list[str]:
    return [record.getMessage() for record in caplog.records if record.name == MATERIALIZER_LOGGER]


def _warning_messages(caplog: pytest.LogCaptureFixture) -> list[str]:
    return [
        record.getMessage()
        for record in caplog.records
        if record.levelno >= logging.WARNING
    ]


@requires_license
def test_r4_live_anonymous_association(caplog: pytest.LogCaptureFixture) -> None:
    target = "OccurrenceDemandAnonymous__design__admitted__admitted_value"
    with caplog.at_level(logging.INFO):
        context = build_pipeline_context([ROOT / "anonymous"])

    assert [usage.identity.qualified_name for usage in context.constraint_facts.usages[:2]] == [
        None,
        None,
    ]
    parameter = _entry_point(context.computation_graph, target)
    assert parameter.default_value == 3.0
    assert not any("excluded_value" in item.qualified_name for item in _entry_points(context.computation_graph))
    assert list(context.part_occurrences) == ["OccurrenceDemandAnonymous__Admitted"]

    catalog = context.computation_graph.constraint_catalog
    assert catalog is not None
    assert len(catalog.concrete_entries) == 1
    assert [item.exclusion.kind for item in catalog.excluded_records] == [
        "unsupported_owner",
        "unassessed_form",
    ]
    assert _warning_messages(caplog) == []
    assert _materializer_messages(caplog) == [
        "supplied-value materializer scanned 1 referenced bindings: "
        "1 literal applied, 0 non-literal skipped."
    ]


@requires_license
def test_r4_valid_replay_not_corrupt(tmp_path: Path) -> None:
    fixture = ROOT / "anonymous"
    live = build_pipeline_context([fixture])
    snapshot_path = capture_snapshot([fixture], tmp_path / "snapshot.json")

    replay, _inputs = build_full_graph_from_snapshot(snapshot_path)
    assert replay.model_dump(mode="json") == live.computation_graph.model_dump(mode="json")
    assert replay.constraint_catalog is not None
    assert live.computation_graph.constraint_catalog is not None
    assert replay.constraint_catalog.model_dump(mode="json") == (
        live.computation_graph.constraint_catalog.model_dump(mode="json")
    )


@requires_license
def test_r5_finite_first_cycle_is_atomic() -> None:
    with pytest.raises(CodeGenerationError) as caught:
        build_pipeline_context([ROOT / "cycle"])

    cause = caught.value.__cause__
    assert type(cause).__name__ == "RecursiveContainmentError"
    assert cause.requested_owner_qn == "OccurrenceDemandCycle__Node"
    assert cause.edge_owner_qn == "OccurrenceDemandCycle__Node"
    assert cause.edge_feature_name == "recursive"
    assert cause.edge_type_qn == "OccurrenceDemandCycle__Node"
    assert cause.cycle_path == (
        "OccurrenceDemandCycle__Node",
        "OccurrenceDemandCycle__Node",
    )


@requires_license
def test_r7_shared_target_dedup_grouping_counts(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    target = "DemandShared__plant__source__value"
    fixture = ROOT / "shared"
    with caplog.at_level(logging.INFO):
        live = build_pipeline_context([fixture])
    parameter = _entry_point(live.computation_graph, target)
    assert (parameter.default_value, parameter.param_group) == (17.0, "calc_route_params")
    assert [(item.formal_name, item.design_attribute_qn) for item in live.concrete_constraints[0].inputs] == [
        ("value", target)
    ]
    assert _warning_messages(caplog) == []
    assert _materializer_messages(caplog) == [
        "supplied-value materializer scanned 1 referenced bindings: "
        "1 literal applied, 0 non-literal skipped."
    ]

    caplog.clear()
    snapshot_path = capture_snapshot([fixture], tmp_path / "snapshot.json")
    with caplog.at_level(logging.INFO):
        replay, _inputs = build_full_graph_from_snapshot(snapshot_path)
    replay_parameter = _entry_point(replay, target)
    assert (replay_parameter.default_value, replay_parameter.param_group) == (
        17.0,
        "calc_route_params",
    )


@requires_license
def test_r7_multi_target_order_permutations(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    targets = [
        "DemandOrder__plant__source__a_collision",
        "DemandOrder__plant__source__b_nonliteral",
        "DemandOrder__plant__source__c_clean",
    ]
    fixture = ROOT / "order"
    with caplog.at_level(logging.INFO):
        live = build_pipeline_context([fixture])
    parameters = [item for item in _entry_points(live.computation_graph) if item.qualified_name in targets]
    assert [item.qualified_name for item in parameters] == targets
    assert [item.default_value for item in parameters] == [11.0, 22.0, 33.0]
    assert _warning_messages(caplog) == []
    assert _materializer_messages(caplog) == [
        "supplied-value materializer scanned 3 referenced bindings: "
        "3 literal applied, 0 non-literal skipped."
    ]

    caplog.clear()
    snapshot_path = capture_snapshot([fixture], tmp_path / "snapshot.json")
    with caplog.at_level(logging.INFO):
        replay, _inputs = build_full_graph_from_snapshot(snapshot_path)
    replay_parameters = [item for item in _entry_points(replay) if item.qualified_name in targets]
    assert [item.qualified_name for item in replay_parameters] == targets
    assert [item.default_value for item in replay_parameters] == [11.0, 22.0, 33.0]


@requires_license
def test_r7_constraint_only_provenance_after_resolution(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    target = "DemandConstraintOnly__plant__source__value"
    fixture = ROOT / "constraint_only"
    with caplog.at_level(logging.INFO):
        live = build_pipeline_context([fixture])
    parameter = _entry_point(live.computation_graph, target)
    assert (parameter.default_value, parameter.param_group) == (23.0, "constraint_route_params")
    assert _materializer_messages(caplog) == [
        "supplied-value materializer scanned 1 referenced bindings: "
        "1 literal applied, 0 non-literal skipped."
    ]

    snapshot_path = capture_snapshot([fixture], tmp_path / "snapshot.json")
    replay, _inputs = build_full_graph_from_snapshot(snapshot_path)
    replay_parameter = _entry_point(replay, target)
    assert (replay_parameter.default_value, replay_parameter.param_group) == (
        23.0,
        "constraint_route_params",
    )
