"""The two default lanes disagree, and that disagreement is pinned (audit F4).

DD-R23 requires one typed representation without a second one. The IR lane
(`constraint_lowering.resolve_modeled_default`) and the captured-string lane
(`parameter_groups.design_attribute_float_default`) do not currently satisfy that
for one shape, and the original retention justification — "a captured string for
which no expression IR exists" — was falsified by this item's own fixture.

This test exists so the disagreement is a **known, asserted** fact rather than
something a future reader re-justifies away. If the lanes are ever made to agree
(by removing the constraint-formal double-ownership, the recorded correct fix),
this test should fail and be deleted with that change.
"""

from __future__ import annotations

import json

from sysml_codegen.analysis.constraint_lowering import resolve_modeled_default
from tests.conftest import snapshot_fixture

FORMAL_QN = "ModeledDefaultFidelity__Derived_Bound__limit"


def _captured_string_default(qualified_name: str) -> str | None:
    payload = json.loads(snapshot_fixture("modeled_default_fidelity").read_text())
    for attributes in payload["design_attributes"].values():
        for attribute in attributes:
            if attribute["qualified_name"] == qualified_name:
                return attribute["default_value"]
    return None


def test_string_lane_folded_what_the_ir_lane_refuses():
    """The same modeled default, two answers: 5.0 versus explicitly unresolved."""
    assert _captured_string_default(FORMAL_QN) == "5.0"

    payload = json.loads(snapshot_fixture("modeled_default_fidelity").read_text())
    formal = next(
        formal
        for definition in payload["constraint_facts"]["definitions"]
        for formal in definition["formals"]
        if formal["name"] == "limit"
    )
    resolved = resolve_modeled_default(json.dumps(formal["default"]))

    assert resolved.value is None
    assert resolved.unresolved_node_kind == "operator"


def test_the_disagreement_is_unobservable_because_the_ir_lane_owns_the_formal():
    """Why it is a latent contradiction rather than a live bug.

    The design-attribute route does not mint an entry point for a constraint
    formal; the IR lane does, and its answer is the one that reaches the graph.
    """
    from sysml_codegen.orchestration.snapshot_context import (
        build_pipeline_context_from_snapshot,
    )

    context = build_pipeline_context_from_snapshot(snapshot_fixture("modeled_default_fidelity"))
    minted = {
        parameter.qualified_name
        for group in context.computation_graph.entry_point_groups
        for parameter in group.parameters
    }
    assert FORMAL_QN not in minted

    limit = next(p for p in minted if p.endswith("__limit"))
    entry = next(
        parameter
        for group in context.computation_graph.entry_point_groups
        for parameter in group.parameters
        if parameter.qualified_name == limit
    )
    assert entry.default_value is None
    assert entry.unresolved_default_kind == "operator"
