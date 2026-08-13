"""The exact route's public context is receipt-bound and cannot be mutated.

The instance fingerprint is derived independently: this module elaborates and
encodes the graph again and compares. The computation digest is recomputed with
this file's own canonical-JSON code, which is a field-coverage check rather than
an independent one — the graph it hashes comes back from the context, and
production has already checked that equality before returning it. What proves
the receipt has teeth is the tamper set below, where the sealed authority is
moved out from under a built context and the read is refused.

The tamper cases reach past ``__setattr__`` with ``object.__setattr__``. That is
deliberate: the point is not that the public API refuses mutation (a separate
test covers that), it is that a context whose private authority moved anyway
refuses to hand out a graph instead of quietly serving the stale one.
"""

from __future__ import annotations

import copy
import hashlib
import json
import pickle
from pathlib import Path

import pytest

from sysml_codegen.orchestration.exact_pipeline_context import (
    ExactPipelineContext,
    build_exact_pipeline_context,
    build_exact_pipeline_context_from_snapshot,
)
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "source_identity_mixed_consumers"


def _expected_digest(graph) -> str:
    """Recompute the receipt digest here, from the graph, independently."""
    payload = {
        "projector_semantics": "instance-projector/v1",
        "modules": [module.model_dump(mode="json") for module in graph.modules],
        "entry_point_groups": [group.model_dump(mode="json") for group in graph.entry_point_groups],
        "execution_order": list(graph.execution_order),
        "fallback_entry_points": sorted(graph.fallback_entry_points),
        "output_aliases": [alias.model_dump(mode="json") for alias in graph.output_aliases],
        "constraint_catalog": (
            graph.constraint_catalog.model_dump(mode="json")
            if graph.constraint_catalog is not None
            else None
        ),
    }
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def test_the_receipt_binds_the_instance_bytes_and_the_projection() -> None:
    context = build_exact_pipeline_context([FIXTURE])
    receipt = context.receipt

    from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
    from sysml_codegen.snapshot.instance_graph import encode_instance_graph

    # Independent: the graph is elaborated and encoded again here, by this test,
    # and the fingerprint must match what the context sealed.
    independent_bytes = encode_instance_graph(elaborate_model_paths([FIXTURE]))
    assert receipt.instance_fingerprint == json.loads(independent_bytes)["fingerprint"]

    # Not independent, and not claimed to be: `computation_graph` is only
    # returned after production has already checked this same equality. What it
    # does buy is field coverage — it fails if the digest formula stops covering
    # a field this test's local copy covers. The receipt's teeth are proven by
    # the tamper cases below, not by this line.
    assert receipt.computation_digest == _expected_digest(context.computation_graph)
    assert receipt.targets is None
    assert receipt.projector_semantics == "instance-projector/v1"


def test_every_read_returns_an_isolated_graph() -> None:
    """A caller that mutates what it got cannot change what the next caller gets."""
    context = build_exact_pipeline_context([FIXTURE])
    first = context.computation_graph
    second = context.computation_graph
    assert first is not second
    assert first.modules[0] is not second.modules[0]

    first.modules.clear()
    assert context.computation_graph.modules, "a mutated read leaked back into the context"
    assert len(context.computation_graph.modules) == len(second.modules)


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda ctx: setattr(ctx, "computation_graph", None), id="set-public"),
        pytest.param(lambda ctx: setattr(ctx, "_receipt", None), id="set-private"),
        pytest.param(lambda ctx: setattr(ctx, "brand_new", 1), id="set-new"),
        pytest.param(lambda ctx: delattr(ctx, "_instance_bytes"), id="delete"),
        pytest.param(lambda ctx: copy.copy(ctx), id="copy"),
        pytest.param(lambda ctx: copy.deepcopy(ctx), id="deepcopy"),
        pytest.param(lambda ctx: pickle.dumps(ctx), id="pickle"),
    ],
)
def test_a_built_context_refuses_to_be_changed_or_duplicated(mutate) -> None:
    context = build_exact_pipeline_context([FIXTURE])
    with pytest.raises(TypeError):
        mutate(context)
    assert context.computation_graph.modules, "the refusal must leave the context usable"


def test_the_context_cannot_be_constructed_without_a_builder() -> None:
    with pytest.raises(TypeError, match="builder-created"):
        ExactPipelineContext()
    # ``object.__new__`` is the one way past that guard. The result carries no
    # sealed authority, so it must refuse to project rather than raise a bare
    # AttributeError from somewhere inside.
    unbuilt = object.__new__(ExactPipelineContext)
    with pytest.raises(CodeGenerationError, match="carries no sealed authority"):
        _ = unbuilt.computation_graph


def test_swapped_instance_bytes_are_refused_rather_than_projected() -> None:
    """Substituting a different model's sealed bytes must not silently re-project."""
    context = build_exact_pipeline_context([FIXTURE])
    other = build_exact_pipeline_context([FIXTURES_DIR / "wi014_toy"])
    object.__setattr__(context, "_instance_bytes", other._instance_bytes)

    with pytest.raises(CodeGenerationError, match="no longer match the receipt"):
        _ = context.computation_graph


def test_a_receipt_from_a_different_projector_is_refused() -> None:
    context = build_exact_pipeline_context([FIXTURE])
    stale = type(context.receipt)(
        instance_fingerprint=context.receipt.instance_fingerprint,
        targets=context.receipt.targets,
        projector_semantics="instance-projector/v0",
        computation_digest=context.receipt.computation_digest,
    )
    object.__setattr__(context, "_receipt", stale)

    with pytest.raises(CodeGenerationError, match="minted by projector"):
        _ = context.computation_graph


def test_a_receipt_whose_digest_moved_is_refused() -> None:
    context = build_exact_pipeline_context([FIXTURE])
    wrong = type(context.receipt)(
        instance_fingerprint=context.receipt.instance_fingerprint,
        targets=context.receipt.targets,
        projector_semantics=context.receipt.projector_semantics,
        computation_digest="0" * 64,
    )
    object.__setattr__(context, "_receipt", wrong)

    with pytest.raises(CodeGenerationError, match="disagrees with the receipt"):
        _ = context.computation_graph


def test_a_receipt_whose_selection_moved_reprojects_and_is_refused() -> None:
    """The receipt carries the selection, so a swapped selection cannot pass."""
    context = build_exact_pipeline_context([FIXTURE])
    channel = next(
        output.channel_name for module in context.computation_graph.modules for output in
        module.outputs
    )
    narrowed = type(context.receipt)(
        instance_fingerprint=context.receipt.instance_fingerprint,
        targets=(channel,),
        projector_semantics=context.receipt.projector_semantics,
        computation_digest=context.receipt.computation_digest,
    )
    object.__setattr__(context, "_receipt", narrowed)

    with pytest.raises(CodeGenerationError, match="disagrees with the receipt"):
        _ = context.computation_graph


def test_the_live_and_v6_contexts_agree_on_the_public_entry_point_surface(tmp_path: Path) -> None:
    """The two builders differ in provenance only, never in modelled identity."""
    live = build_exact_pipeline_context([FIXTURE]).computation_graph
    captured = capture_instance_graph_snapshot([FIXTURE], tmp_path / "case.json")
    from_snapshot = build_exact_pipeline_context_from_snapshot(captured).computation_graph

    assert [group.model_dump(mode="json") for group in live.entry_point_groups] == [
        group.model_dump(mode="json") for group in from_snapshot.entry_point_groups
    ]
    assert live.execution_order == from_snapshot.execution_order
    assert [alias.model_dump(mode="json") for alias in live.output_aliases] == [
        alias.model_dump(mode="json") for alias in from_snapshot.output_aliases
    ]


# --- Design invariant 4, where both sides are in scope (audit A1) -----------------------


def _with_projection(monkeypatch, mutate) -> None:
    """Route every projection — the seal's and every later read's — through `mutate`.

    Patching before the context is built is what makes this a *projection defect* rather
    than tampering: the receipt's own digest is minted from the defective output, so it
    agrees with itself, and the catalog it produces is internally consistent. Nothing
    downstream of projection can see it. Only a check that still holds the domain can.
    """
    from sysml_codegen.orchestration import exact_pipeline_context as module

    real = module._project_or_fail

    def defective(graph, targets):
        projected = real(graph, targets)
        mutate(projected.constraint_catalog)
        return projected

    monkeypatch.setattr(module, "_project_or_fail", defective)


def test_a_catalog_missing_a_non_reaching_member_is_refused_by_name(monkeypatch) -> None:
    """The 56-of-65 shape: no occurrence to orphan, no count to contradict, still caught."""
    dropped: dict[str, object] = {}

    def drop_a_non_reaching_row(catalog):
        # Deterministic across every call: the seal and each later read must drop the SAME
        # row, or the receipt's digest check fires first and this proves nothing.
        if catalog is None:
            return
        candidates = sorted(
            (row for row in catalog.usage_records if row.occurrence_count == 0),
            key=lambda row: row.declaration_id,
        )
        if not candidates:
            return
        victim = candidates[0]
        dropped["row"] = victim
        catalog.usage_records.remove(victim)
        object.__setattr__(catalog, "fingerprint", catalog.recomputed_fingerprint())

    _with_projection(monkeypatch, drop_a_non_reaching_row)
    context = build_exact_pipeline_context([FIXTURES_DIR / "catf_mfe_d5"])

    with pytest.raises(CodeGenerationError) as raised:
        _ = context.computation_graph

    message = str(raised.value)
    assert "missing 1 of 65 constraint usage domain members" in message
    assert dropped["row"].usage_qualified_name in message
    assert dropped["row"].declaration_id in message


def test_a_catalog_row_that_joins_no_domain_member_is_refused(monkeypatch) -> None:
    """The other direction: a row the domain never minted."""

    def append_a_ghost_row(catalog):
        if catalog is None or any(
            row.declaration_id == "ghost" for row in catalog.usage_records
        ):
            return
        ghost = catalog.usage_records[0].model_copy(update={"declaration_id": "ghost"})
        catalog.usage_records.append(ghost)
        object.__setattr__(catalog, "fingerprint", catalog.recomputed_fingerprint())

    _with_projection(monkeypatch, append_a_ghost_row)
    context = build_exact_pipeline_context([FIXTURE])

    with pytest.raises(CodeGenerationError, match="join no domain member"):
        _ = context.computation_graph


def test_an_intact_catalog_passes_the_population_check() -> None:
    """The guard is not vacuous: the unmutated public route still reads clean."""
    graph = build_exact_pipeline_context([FIXTURES_DIR / "catf_mfe_d5"]).computation_graph
    assert len(graph.constraint_catalog.usage_records) == 65
