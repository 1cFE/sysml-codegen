"""A modelled aggregation reaches the public surface with its literal intact.

This is the B37-01 ruling made public (recovery plan, Phase 2): modelled
aggregation is executable, so ``:>> total_cost = sum(module.cost) + 5.0;`` must
project to something a caller can run — not be swallowed by a pre-elaboration
``calc def`` gate, and not lose the ``5.0`` operand on the way through.

Every number here is read off the fixture by hand, never off the projection:
``tests/fixtures/agg_literal_probe/library.sysml:24`` declares
``sum(module.cost) + 5.0`` over ``part module : 'Module' [3]``, and
``design.sysml:7`` binds ``:>> module.cost = 10.0``. So the model says
3 x 10.0 + 5.0 = 35.0, and the test asserts that.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from sysml_codegen.orchestration.exact_pipeline_context import (
    build_exact_pipeline_context,
    build_exact_pipeline_context_from_snapshot,
)
from sysml_codegen.resolution.models import EntryPointType, ModuleKind
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "agg_literal_probe"

#: Read off library.sysml:24 and design.sysml:7 by hand.
MEMBER_COST = 10.0
MEMBER_COUNT = 3
LITERAL_TERM = 5.0
EXPECTED_TOTAL = MEMBER_COST * MEMBER_COUNT + LITERAL_TERM


def _aggregation(graph):
    (module,) = [
        item for item in graph.modules if item.module_kind is ModuleKind.AGGREGATION
    ]
    return module


def test_the_modelled_aggregation_is_public_and_carries_its_literal() -> None:
    graph = build_exact_pipeline_context([FIXTURE]).computation_graph
    module = _aggregation(graph)

    assert len(module.inputs) == MEMBER_COUNT
    assert str(LITERAL_TERM) in module.compiled_expression, (
        "the literal operand was swallowed; B37-01 exists because it used to be"
    )

    defaults = {
        parameter.qualified_name: parameter.default_value
        for group in graph.entry_point_groups
        for parameter in group.parameters
    }
    assert sorted(defaults.values()) == [MEMBER_COST] * MEMBER_COUNT
    assert {
        parameter.entry_type
        for group in graph.entry_point_groups
        for parameter in group.parameters
    } == {EntryPointType.DESIGN_ATTRIBUTE}

    # Evaluate the generated expression against the modelled defaults and check
    # it against the hand arithmetic above.
    values = type("Inputs", (), {})()
    for ordinal, module_input in enumerate(module.inputs):
        setattr(values, module_input.param_name, defaults[module_input.source.qualified_name])
        assert module_input.param_name == f"cost_{ordinal}"
    assert eval(module.compiled_expression, {}, {"inputs": values}) == EXPECTED_TOTAL  # noqa: S307


def test_every_member_occurrence_is_its_own_entry_point() -> None:
    """Three modelled members must not collapse into one shared parameter."""
    graph = build_exact_pipeline_context([FIXTURE]).computation_graph
    qualified = sorted(
        parameter.qualified_name
        for group in graph.entry_point_groups
        for parameter in group.parameters
    )

    assert qualified == [
        f"AggLiteralProbeDesign__plant__assembly__module[{index}]__cost"
        for index in range(MEMBER_COUNT)
    ]


def test_the_aggregation_projects_identically_on_all_three_routes(tmp_path: Path) -> None:
    live = build_exact_pipeline_context([FIXTURE])
    captured = capture_instance_graph_snapshot([FIXTURE], tmp_path / "case.json")
    relocated_path = tmp_path / "moved" / "case.json"
    relocated_path.parent.mkdir()
    shutil.copyfile(captured, relocated_path)

    in_place = build_exact_pipeline_context_from_snapshot(captured)
    relocated = build_exact_pipeline_context_from_snapshot(relocated_path)

    assert in_place.receipt.computation_digest == relocated.receipt.computation_digest

    def surface(context):
        graph = context.computation_graph
        return (
            _aggregation(graph).compiled_expression,
            [group.model_dump(mode="json") for group in graph.entry_point_groups],
            graph.execution_order,
        )

    assert surface(live) == surface(in_place) == surface(relocated)
