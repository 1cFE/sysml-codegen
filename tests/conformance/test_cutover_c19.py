"""C19 occurrence literal reaches one exact calculation and one constraint."""

from __future__ import annotations

import shutil
from pathlib import Path

from sysml_codegen.elaboration import NodeRef, ValueSite, elaborate
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.orchestration.snapshot_context import build_pipeline_context_from_snapshot
from sysml_codegen.resolution.models import ModuleKind
from sysml_codegen.snapshot import capture_snapshot
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "nested_occurrence_override_probe"
SOURCE = "nested_occurrence_override_probe__the_design__panel__source__reading"
EXPECTED_CONSUMERS = {
    ("nested_occurrence_override_probe__the_design__panel__noop", "x"),
    ("nested_occurrence_override_probe__the_design__panel__within", "v"),
}


def _public_routes(tmp_path: Path):
    captured = capture_snapshot([FIXTURE], tmp_path / "in-place.json")
    relocated = tmp_path / "relocated" / "case.json"
    relocated.parent.mkdir()
    shutil.copyfile(captured, relocated)
    return {
        "live": build_pipeline_context([FIXTURE]).computation_graph,
        "in_place_v6": build_pipeline_context_from_snapshot(captured).computation_graph,
        "relocated_v6": build_pipeline_context_from_snapshot(relocated).computation_graph,
    }


def test_c19_literal_has_one_exact_source_and_two_typed_consumers() -> None:
    extractor = SysMLDataExtractor([FIXTURE])
    assert extractor.load_models()
    assert extractor.diagnostics is not None
    graph = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
        strict=True,
    )
    source = graph.attr_by_display_path(SOURCE)
    assert source.value == 80.0
    assert source.value_site is ValueSite.OCCURRENCE_OVERRIDE

    calc = graph.calc_by_display_path(
        "nested_occurrence_override_probe__the_design__panel__noop"
    )
    constraint = graph.constraint_by_display_path(
        "nested_occurrence_override_probe__the_design__panel__within"
    )
    source_ref = NodeRef(source.node_id)
    assert calc.input_by_name("x") == source_ref
    assert constraint.input_by_name("v") == source_ref
    assert {
        consumer.node_id
        for consumer in (*graph.calcs.values(), *graph.constraints.values())
        if source_ref in consumer.inputs.values()
    } == {calc.node_id, constraint.node_id}


def test_c19_literal_is_public_on_live_in_place_and_relocated_routes(tmp_path: Path) -> None:
    for graph in _public_routes(tmp_path).values():
        defaults = {
            parameter.qualified_name: parameter.default_value
            for group in graph.entry_point_groups
            for parameter in group.parameters
        }
        assert defaults[SOURCE] == 80.0
        assert list(defaults).count(SOURCE) == 1
        consumers = {
            (
                module.name.rsplit("__", 1)[0]
                if module.module_kind is ModuleKind.CONSTRAINT
                else module.name,
                input_.param_name,
            )
            for module in graph.modules
            for input_ in module.inputs
            if input_.source.qualified_name == SOURCE
        }
        assert consumers == EXPECTED_CONSUMERS
