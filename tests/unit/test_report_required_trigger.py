"""No constraint-bearing model is silent, and a constraint-free one is untouched (D5).

The trigger widened from "one concrete entry" to "one authored usage". The risk in a widening
is that it widens too far, so the two directions are pinned separately: a descriptive-only
model gains a zero-input aggregator, and a model with no constraints at all still projects no
catalog, no aggregator, and no report channel.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.elaboration import project
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
from sysml_codegen.resolution.models import (
    ComputationGraph,
    ModuleKind,
    ships_constraint_machinery,
)
from tests.conftest import FIXTURES_DIR, exact_graph_from_fixture, requires_license


def _aggregators(graph: ComputationGraph):
    return [m for m in graph.modules if m.module_kind is ModuleKind.REPORT_AGGREGATOR]


def _exit_channels(graph: ComputationGraph) -> set[str]:
    """Every channel the generated pipeline publishes, through the real exit-point builder.

    Narrowed to nothing so the only survivors are the structurally pinned report channels —
    which is the property invariant 32 asserts, rather than incidental capture-everything.
    """
    from sysml_codegen.generation.pipeline import _build_exit_points

    return {
        point["name"]
        for point in _build_exit_points(graph.modules, {}, selected_channels=set())
    }


def test_a_descriptive_only_model_ships_a_zero_input_aggregator():
    """`catf_mfe_d5`: 65 bare constraints, zero concrete entries, and until now no report.

    This is the shape the item exists for. Read license-free off the committed v6 snapshot.
    """
    graph = exact_graph_from_fixture("catf_mfe_d5")
    (aggregator,) = _aggregators(graph)
    assert not aggregator.inputs
    assert ships_constraint_machinery(graph)
    # Invariant 32: the report channel is an exit point whenever the module exists, so the
    # report is not stranded inside the pipeline where nothing publishes it.
    assert aggregator.outputs[0].channel_name in _exit_channels(graph)


@pytest.mark.parametrize(
    "fixture",
    ["constraint_coverage_zero_eligible", "constraint_domain_plain_forms"],
)
@requires_license
def test_both_zero_input_branches_ship_an_aggregator(fixture: str):
    """Asserted-with-zero-eligible and non-asserted-only. Different headlines, same trigger."""
    graph = project(elaborate_model_paths([Path(FIXTURES_DIR / fixture)]))
    (aggregator,) = _aggregators(graph)
    assert not aggregator.inputs
    assert aggregator.outputs[0].channel_name in _exit_channels(graph)


def test_a_constraint_free_model_stays_inert():
    """LC-E12: the trigger widened, it did not become universal.

    If this fails, every constraint-free package in the tree just gained a report schema and a
    registry import it can never populate, and the baseline byte-identity gate is meaningless.
    """
    graph = exact_graph_from_fixture("sample_model")
    assert graph.constraint_catalog is None
    assert not _aggregators(graph)
    assert not ships_constraint_machinery(graph)


def test_has_executable_content_is_gone():
    """DR-8: a property with no reader, kept for a hypothetical future one, is the shim the
    epic's bar rejects. `ships_constraint_machinery` was its only caller."""
    from sysml_codegen.resolution.models import ConstraintCatalog

    assert not hasattr(ConstraintCatalog, "has_executable_content")


@requires_license
def test_the_rule_is_read_the_same_way_on_both_sides_of_projection():
    """D5's two readings — the graph's `constraint_usages`, the catalog's `usage_records` —
    agree on every constraint-bearing fixture in the ledger. Two readings of one rule is the
    drift Item 2's A4 cure exists to stop; the coverage preflight refuses a disagreement, and
    this states the property that refusal protects."""
    for fixture in ("catf_mfe_d5", "constraint_coverage_zero_eligible", "fusion_tea"):
        instance_graph = elaborate_model_paths([Path(FIXTURES_DIR / fixture)])
        graph = project(instance_graph)
        assert bool(instance_graph.constraint_usages) == ships_constraint_machinery(graph)
        assert bool(_aggregators(graph)) == ships_constraint_machinery(graph)
