"""Immutable instance authority and complete projection-receipt checks."""

from __future__ import annotations

import copy
import pickle
from dataclasses import replace

import pytest

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.orchestration.pipeline_context import (
    CodeGenerationError,
    _computation_digest,
)
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "source_identity_mixed_consumers"


@pytest.fixture(scope="module")
def context():
    return build_pipeline_context(
        [FIXTURE],
        targets=["z", "a", "z"],
        include_all=True,
    )


def test_context_reprojects_from_bound_immutable_authority(context) -> None:
    first = context.computation_graph
    expected = first.model_copy(deep=True)
    first.modules.clear()
    first.entry_point_groups.clear()
    first.execution_order.clear()
    first.fallback_entry_points.add("invented")
    first.output_aliases.clear()
    first.constraint_catalog = None

    second = context.computation_graph
    assert second == expected
    assert second is not first
    assert second.modules is not expected.modules


@pytest.mark.parametrize("operation", [copy.copy, copy.deepcopy, pickle.dumps])
def test_context_copy_and_pickle_refuse(context, operation) -> None:
    with pytest.raises(TypeError, match="PipelineContext"):
        operation(context)


def test_context_normal_attribute_mutation_refuses(context) -> None:
    with pytest.raises(TypeError, match="immutable"):
        context._receipt = context._receipt
    with pytest.raises(TypeError, match="immutable"):
        del context._receipt


def test_receipt_binds_every_private_authority_field(context) -> None:
    original_bytes = context._instance_bytes
    original_selection = context._selection
    original_receipt = context._receipt

    assert original_selection.targets == ("a", "z")
    assert original_receipt.instance_fingerprint
    assert original_receipt.targets == ("a", "z")
    assert original_receipt.include_all is True
    assert original_receipt.projector_semantic_marker == "instance-projector/v1"
    assert original_receipt.computation_digest

    tamper_cases = [
        ("_instance_bytes", original_bytes[:-1] + b"!"),
        ("_selection", replace(original_selection, include_all=False)),
        (
            "_receipt",
            replace(original_receipt, projector_semantic_marker="instance-projector/v0"),
        ),
        (
            "_receipt",
            replace(original_receipt, computation_digest="0" * 64),
        ),
    ]
    for attribute, tampered in tamper_cases:
        object.__setattr__(context, attribute, tampered)
        with pytest.raises(CodeGenerationError, match="PipelineContext"):
            _ = context.computation_graph
        object.__setattr__(
            context,
            attribute,
            {
                "_instance_bytes": original_bytes,
                "_selection": original_selection,
                "_receipt": original_receipt,
            }[attribute],
        )


def test_computation_digest_covers_excluded_fields_and_rejects_nonfinite(context) -> None:
    graph = context.computation_graph
    baseline = _computation_digest(graph)

    graph.fallback_entry_points.add("excluded-by-pydantic")
    assert _computation_digest(graph) != baseline

    graph = context.computation_graph
    assert graph.constraint_catalog is not None
    graph.constraint_catalog.fingerprint = "changed-excluded-catalog"
    assert _computation_digest(graph) != baseline

    graph = context.computation_graph
    graph.modules[0].inputs[0].default_value = float("nan")
    with pytest.raises(CodeGenerationError, match="non-finite"):
        _computation_digest(graph)


def test_projection_lease_rechecks_receipt_before_seal(context) -> None:
    lease = context._verified_projection_lease()
    assert lease.computation_graph == context.computation_graph
    original = context._receipt
    object.__setattr__(
        context,
        "_receipt",
        replace(original, computation_digest="f" * 64),
    )
    try:
        with pytest.raises(CodeGenerationError, match="PipelineContext"):
            lease.verify_before_seal()
    finally:
        object.__setattr__(context, "_receipt", original)
