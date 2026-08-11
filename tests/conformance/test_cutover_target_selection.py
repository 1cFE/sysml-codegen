"""Typed target closure shared by live and v6 snapshot builders."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from sysml_codegen.orchestration.snapshot_context import (
    build_pipeline_context_from_snapshot,
)
from sysml_codegen.snapshot import capture_snapshot
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "source_identity_mixed_consumers"
TARGET = (
    "source_identity_mixed_consumers__computed_station__computed_calc__value_out"
)
PRODUCER = (
    "source_identity_mixed_consumers__computed_station__source_identity_computed__producer_calc"
)
SELECTED_MODULES = {
    PRODUCER,
    "source_identity_mixed_consumers__computed_station__computed_calc",
    "source_identity_mixed_consumers__parent_unit__parent_guard__b413f5b14c12ad2f",
    "source_identity_mixed_consumers__qual_station__qual_plant__qual_guard__69ab4a5369f19193",
    "source_identity_mixed_consumers__station__chain_guard__501fce689a098c04",
    "source_identity_mixed_consumers__bare_station__bare_rig__bare_guard__afb0c1fde76643cb",
    "source_identity_mixed_consumers__computed_station__computed_guard__f0ea0a8e244185ef",
    "constraint_report_aggregator",
}
ALL_MODULES = SELECTED_MODULES | {
    "source_identity_mixed_consumers__bank__bank_total",
    "source_identity_mixed_consumers__parent_unit__child__child_calc",
    "source_identity_mixed_consumers__parent_unit__parent_total",
    "source_identity_mixed_consumers__stamp_plant__lit_calc",
    "source_identity_mixed_consumers__stamp_plant__stamp_calc",
    "source_identity_mixed_consumers__avail_ctx__avail_plant__def_authored_calc",
    "source_identity_mixed_consumers__avail_ctx__avail_plant__usage_authored_calc",
    "source_identity_mixed_consumers__qual_station__qual_plant__qual_calc",
    "source_identity_mixed_consumers__qual_station__qual_total",
    "source_identity_mixed_consumers__twin_bay__calc_a",
    "source_identity_mixed_consumers__twin_bay__calc_b",
    "source_identity_mixed_consumers__station__chain_calc",
    "source_identity_mixed_consumers__station__station_total",
    "source_identity_mixed_consumers__bare_station__bare_rig__bare_calc",
    "source_identity_mixed_consumers__bare_station__bare_total",
    "source_identity_mixed_consumers__computed_station__computed_total",
}


def _module_names(context) -> set[str]:
    return {module.name for module in context.computation_graph.modules}


def test_exact_edge_closure_preserves_targets_and_constraint_roots(tmp_path: Path) -> None:
    captured = capture_snapshot([FIXTURE], tmp_path / "in-place.json")
    relocated = tmp_path / "relocated" / "case.json"
    relocated.parent.mkdir()
    shutil.copyfile(captured, relocated)

    contexts = [
        build_pipeline_context(
            [FIXTURE], targets=[TARGET, TARGET], include_all=False
        ),
        build_pipeline_context_from_snapshot(
            captured, targets=[TARGET], include_all=False
        ),
        build_pipeline_context_from_snapshot(
            relocated, targets=[TARGET], include_all=False
        ),
    ]
    for context in contexts:
        graph = context.computation_graph
        assert {module.name for module in graph.modules} == SELECTED_MODULES
        assert set(graph.execution_order) == SELECTED_MODULES
        assert graph.constraint_catalog is not None
        assert len(graph.constraint_catalog.concrete_entries) == 5
        assert any(
            item.name == PRODUCER
            for item in graph.modules
        )

    assert _module_names(build_pipeline_context([FIXTURE])) == ALL_MODULES


@pytest.mark.parametrize(
    "targets, include_all, error",
    [
        ([""], False, TypeError),
        ([1], False, TypeError),
        (["missing-output"], False, CodeGenerationError),
        (None, 1, TypeError),
    ],
)
def test_target_selection_refuses_invalid_or_missing_targets(targets, include_all, error) -> None:
    with pytest.raises(error):
        build_pipeline_context([FIXTURE], targets=targets, include_all=include_all)

