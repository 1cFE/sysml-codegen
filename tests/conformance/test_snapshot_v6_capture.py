"""Capture writes one complete v6 snapshot or nothing at all."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from sysml_codegen.elaboration.elaborate import ElaborationDiagnosticError
from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from sysml_codegen.snapshot.envelope import load_instance_graph_snapshot
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

GOOD = FIXTURES_DIR / "source_identity_mixed_consumers"
BLOCKED = FIXTURES_DIR / "elab_fail_closed_probe"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _literal_values(expressions: list) -> set:
    """Every literal value reachable in a set of expression IR trees."""
    found = set()
    for expression in expressions:
        literal = getattr(expression, "literal", None)
        if literal is not None:
            found.add(getattr(literal, "value", None))
        for attribute in ("operands", "arguments"):
            children = getattr(expression, attribute, None)
            if children:
                found |= _literal_values(list(children))
        value = getattr(expression, "value", None)
        if value is not None and hasattr(value, "kind"):
            found |= _literal_values([value])
    return found


def test_capture_returns_a_loadable_destination_and_leaves_no_temporary_file(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "nested" / "case.json"
    assert capture_instance_graph_snapshot([GOOD], destination) == destination
    assert load_instance_graph_snapshot(destination)
    assert list(destination.parent.iterdir()) == [destination]


def test_a_refused_capture_leaves_an_existing_snapshot_untouched(tmp_path: Path) -> None:
    destination = tmp_path / "case.json"
    destination.write_bytes(b"sentinel-owner-work")
    before = _digest(destination)

    with pytest.raises(Exception):
        capture_instance_graph_snapshot([BLOCKED], destination)

    assert _digest(destination) == before
    assert list(tmp_path.iterdir()) == [destination]


def test_a_refused_capture_creates_no_destination(tmp_path: Path) -> None:
    destination = tmp_path / "missing.json"
    with pytest.raises(Exception):
        capture_instance_graph_snapshot([BLOCKED], destination)
    assert not destination.exists()
    assert not list(tmp_path.iterdir())


def test_capture_and_the_live_route_share_one_emptiness_gate(tmp_path: Path) -> None:
    """Capture must not seal a model the live route would refuse, or vice versa.

    The gate is graph-level emptiness — no calculation, no constraint, and no
    calculation definition — following the B37-01 ruling, which is why a model
    whose only computation is a modelled aggregation is *not* refused here even
    though the legacy pre-elaboration ``calc def`` check would reject it.
    """
    empty = tmp_path / "empty"
    empty.mkdir()
    (empty / "model.sysml").write_text(
        "package EmptyProbe {\n"
        "    private import ScalarValues::*;\n"
        "    part def Widget { attribute mass : Real = 1.0; }\n"
        "    part widget : Widget;\n"
        "}\n"
    )

    with pytest.raises(CodeGenerationError, match="nothing to generate"):
        build_elaborated_pipeline([empty])
    with pytest.raises(CodeGenerationError, match="nothing to generate"):
        capture_instance_graph_snapshot([empty], tmp_path / "empty.json")
    assert not (tmp_path / "empty.json").exists()


def test_a_model_whose_only_computation_is_an_aggregation_is_sealable(tmp_path: Path) -> None:
    """The B37-01 half of the gate: no ``calc def`` is not the same as nothing.

    ``agg_literal_probe`` models ``sum(module.cost) + 5.0`` and declares no
    calculation definition. The legacy pre-elaboration check refuses it; the
    graph-level gate does not, because the elaborated graph carries a computed
    calculation node.

    This also discharges the B37-01 obligation carried from Phase 2: assert the
    ``5.0`` operand is *observed* in the produced graph, rather than asserting the
    fixture collapses.
    """
    captured = capture_instance_graph_snapshot(
        [FIXTURES_DIR / "agg_literal_probe"], tmp_path / "agg.json"
    )
    graph = load_instance_graph_snapshot(captured)
    assert graph.calcs
    assert all(node.calculation_definition_id is None for node in graph.calcs.values())

    literals = _literal_values(
        [node.expression_ir for node in graph.calcs.values() if node.expression_ir is not None]
    )
    assert 5.0 in literals, (
        "the modelled '+ 5.0' operand must survive into the sealed graph "
        f"(found {sorted(literals)})"
    )


def test_capture_refuses_a_model_that_does_not_elaborate_cleanly(tmp_path: Path) -> None:
    """A snapshot may only seal a projectable, diagnostic-free graph.

    The probe models an alias cycle and an unsupported formula, so elaboration
    itself refuses; capture never reaches the sealing step.
    """
    with pytest.raises(ElaborationDiagnosticError):
        capture_instance_graph_snapshot([BLOCKED], tmp_path / "blocked.json")
