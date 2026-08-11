"""Selecting named outputs cuts the pipeline to their exact typed closure.

Expectations are derived from the model, not from the selection under test: the
closure a target needs is read off the *complete* graph's wiring, and the
selected graph is then required to be exactly that set. A test that asked the
selector what it selected and agreed with itself would pass on any closure.
"""

from __future__ import annotations

import pytest

from sysml_codegen.orchestration.exact_pipeline_context import build_exact_pipeline_context
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from sysml_codegen.resolution.models import ModuleKind
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "source_identity_mixed_consumers"


@pytest.fixture(scope="module")
def complete():
    return build_exact_pipeline_context([FIXTURE]).computation_graph


def _upstream_closure(graph, module_name: str) -> set[str]:
    """Every module ``module_name`` transitively needs, read off the wiring."""
    producer_of = {
        output.channel_name: module.name for module in graph.modules for output in module.outputs
    }
    by_name = {module.name: module for module in graph.modules}
    needed: set[str] = set()
    pending = [module_name]
    while pending:
        name = pending.pop()
        if name in needed:
            continue
        needed.add(name)
        for module_input in by_name[name].inputs:
            source = module_input.source
            if source.source_type == "module_output":
                pending.append(producer_of[source.producer_channel])
    return needed


def test_selecting_one_output_keeps_exactly_its_closure(complete) -> None:
    target_module = next(
        module
        for module in complete.modules
        if module.module_kind is ModuleKind.CALCULATION
        and any(
            module_input.source.source_type == "module_output" for module_input in module.inputs
        )
    )
    channel = target_module.outputs[0].channel_name
    expected = _upstream_closure(complete, target_module.name)

    selected = build_exact_pipeline_context([FIXTURE], targets=[channel]).computation_graph
    calculations = {
        module.name for module in selected.modules if module.module_kind is ModuleKind.CALCULATION
    }

    assert calculations == expected
    assert len(selected.modules) < len(complete.modules), (
        "the selection must actually cut something"
    )


def test_selection_renumbers_execution_order_without_gaps(complete) -> None:
    channel = complete.modules[0].outputs[0].channel_name
    selected = build_exact_pipeline_context([FIXTURE], targets=[channel]).computation_graph

    assert [module.execution_order for module in selected.modules] == list(
        range(len(selected.modules))
    )
    assert selected.execution_order == [module.name for module in selected.modules]


def test_selection_drops_the_entry_points_no_selected_module_reads(complete) -> None:
    target_module = next(
        module for module in complete.modules if module.module_kind is ModuleKind.CALCULATION
    )
    channel = target_module.outputs[0].channel_name
    selected = build_exact_pipeline_context([FIXTURE], targets=[channel]).computation_graph

    kept = {
        parameter.qualified_name
        for group in selected.entry_point_groups
        for parameter in group.parameters
    }
    every = {
        parameter.qualified_name
        for group in complete.entry_point_groups
        for parameter in group.parameters
    }
    read_by_selected = {
        module_input.source.qualified_name
        for module in selected.modules
        for module_input in module.inputs
        if module_input.source.source_type == "entry_point"
    }

    assert read_by_selected <= kept, "a selected module reads an entry point that was dropped"
    assert kept < every, "the selection must actually prune the entry points"
    assert all(group.parameters for group in selected.entry_point_groups), "empty group survived"


def test_every_admitted_constraint_survives_any_selection(complete) -> None:
    """A constraint report that covered only the selected subtree would lie."""
    channel = next(
        module.outputs[0].channel_name
        for module in complete.modules
        if module.module_kind is ModuleKind.CALCULATION
    )
    selected = build_exact_pipeline_context([FIXTURE], targets=[channel]).computation_graph

    def constraints(graph):
        return {
            module.name for module in graph.modules if module.module_kind is ModuleKind.CONSTRAINT
        }

    assert constraints(selected) == constraints(complete)
    assert constraints(complete), "the fixture must model constraints for this to mean anything"
    assert any(
        module.module_kind is ModuleKind.REPORT_AGGREGATOR for module in selected.modules
    )


def test_no_targets_means_the_whole_model(complete) -> None:
    assert build_exact_pipeline_context([FIXTURE], targets=None).receipt.targets is None
    assert len(complete.modules) > 1


def test_selecting_by_module_and_field_name_finds_the_same_output(complete) -> None:
    module = next(
        item for item in complete.modules if item.module_kind is ModuleKind.CALCULATION
    )
    output = module.outputs[0]

    by_channel = build_exact_pipeline_context(
        [FIXTURE], targets=[output.channel_name]
    ).receipt.computation_digest
    by_field = build_exact_pipeline_context(
        [FIXTURE], targets=[f"{module.name}.{output.field_name}"]
    ).receipt.computation_digest

    assert by_channel == by_field


def test_an_unknown_target_is_refused(complete) -> None:
    with pytest.raises(CodeGenerationError, match="not a distinct output"):
        build_exact_pipeline_context([FIXTURE], targets=["no_such_output"])


@pytest.mark.parametrize(
    ("targets", "error"),
    [
        pytest.param([], ValueError, id="empty"),
        pytest.param("a_channel", TypeError, id="bare-string"),
        pytest.param([""], TypeError, id="empty-string"),
        pytest.param([None], TypeError, id="non-string"),
    ],
)
def test_a_malformed_target_list_is_refused_before_projection(targets, error) -> None:
    with pytest.raises(error):
        build_exact_pipeline_context([FIXTURE], targets=targets)


def test_duplicate_targets_collapse_to_one_selection(complete) -> None:
    channel = next(
        module.outputs[0].channel_name
        for module in complete.modules
        if module.module_kind is ModuleKind.CALCULATION
    )
    once = build_exact_pipeline_context([FIXTURE], targets=[channel])
    twice = build_exact_pipeline_context([FIXTURE], targets=[channel, channel])

    assert once.receipt == twice.receipt
