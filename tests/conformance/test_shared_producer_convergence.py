"""Public acceptance surface for Item 4's written-reference carry (DD-A14).

`shared_producer` pins SR-A02: one usage-owned design attribute,
`SharedProducer::the_rig::gain`, read by both a calculation input and a
constraint actual. Contract invariant 21 requires the two consumers to converge
on one QN-keyed typed entry point.

**This surface is newly authored (Gate 4).** No test pinned the pre-carry
two-entry-point state at the predecessor — `PROVENANCE.md`'s "a test asserts it"
claim was false, and is corrected under DD-R31. The RED step is therefore built
here against the current state first, confirmed green, and then flipped to the
convergence assertion in the same shape, so DD-A14 is falsifiable rather than
merely asserted.

Both public routes: live extraction and the committed snapshot.
"""

from __future__ import annotations

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.orchestration.snapshot_context import (
    build_pipeline_context_from_snapshot,
)
from tests.conftest import FIXTURES_DIR, requires_license, snapshot_fixture

ROOT = FIXTURES_DIR / "shared_producer"

CONVERGED_QN = "SharedProducer__the_rig__gain"
MODELED_DEFAULT = 40.0


def _entry_points(graph) -> list:
    return [parameter for group in graph.entry_point_groups for parameter in group.parameters]


def _gain_entry_points(graph) -> list:
    """Every entry point minted for the shared `gain` attribute, either consumer."""
    return [item for item in _entry_points(graph) if item.qualified_name.endswith("gain")]


def _assert_converged(graph) -> None:
    """DD-A14: one entry point, one modeled default, one group assignment."""
    gain_entry_points = _gain_entry_points(graph)

    assert [item.qualified_name for item in gain_entry_points] == [CONVERGED_QN]
    assert gain_entry_points[0].default_value == MODELED_DEFAULT

    owning_groups = [
        group.name
        for group in graph.entry_point_groups
        for parameter in group.parameters
        if parameter.qualified_name == CONVERGED_QN
    ]
    assert len(owning_groups) == 1


@requires_license
def test_shared_producer_converges_live() -> None:
    context = build_pipeline_context([ROOT])
    _assert_converged(context.computation_graph)


def test_shared_producer_converges_from_snapshot() -> None:
    context = build_pipeline_context_from_snapshot(snapshot_fixture("shared_producer"))
    _assert_converged(context.computation_graph)
