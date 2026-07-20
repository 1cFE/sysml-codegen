"""Modeled-default fidelity: signed and unit-annotated defaults survive (DD-A11, DD-A12).

`:= -0.1` parses as an `OperatorNode` over a literal and `= 40.0 [W]` as a
`UnitAnnotationNode`. The pre-Item-4 default lane returned a value only for a bare
`LiteralNode`, so both became `None`, the MODELED_DEFAULT formal minted an entry point
with no default, and the generated JSON omitted the key (DD-R20, DD-R21).

Both public routes. The snapshot leg was the declared Phase 5 licence dependency:
before this fixture was captured, there were zero `unit` IR nodes across every
committed snapshot, so the unit-annotation path could not be exercised offline.
"""

from __future__ import annotations

import json
import logging

import pytest

from sysml_codegen.generation.entry_point import generate_all_derived_jsons
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from tests.conftest import FIXTURES_DIR, requires_license, snapshot_fixture

ROOT = FIXTURES_DIR / "modeled_default_fidelity"
LOWERING_LOGGER = "sysml_codegen.analysis.constraint_lowering"


def _entry_point(graph, suffix: str):
    matches = [
        parameter
        for group in graph.entry_point_groups
        for parameter in group.parameters
        if parameter.qualified_name.endswith(suffix)
    ]
    assert len(matches) == 1, f"expected exactly one entry point ending {suffix!r}, got {matches}"
    return matches[0]


@pytest.fixture(scope="module")
def fidelity_context():
    return build_pipeline_context([ROOT])


@requires_license
def test_signed_modeled_default_survives(fidelity_context) -> None:
    """DD-A11: `default -0.1` reaches the typed entry point with its sign intact."""
    drift = _entry_point(fidelity_context.computation_graph, "__drift")
    assert drift.default_value == -0.1
    assert drift.unresolved_default_kind is None


@requires_license
def test_unit_annotated_modeled_default_survives_with_unit_carried(fidelity_context) -> None:
    """DD-A11 / DD-R25: the value survives and the unit is carried, never converted."""
    rated = _entry_point(fidelity_context.computation_graph, "__rated_power")
    assert rated.default_value == 40.0
    assert rated.unit_text == "W"
    assert rated.unresolved_default_kind is None


@requires_license
def test_unsupported_default_ir_is_explicitly_unresolved_and_diagnosed(caplog) -> None:
    """DD-A12: no value invented, and the entry point is named with its node kind."""
    with caplog.at_level(logging.WARNING, logger=LOWERING_LOGGER):
        context = build_pipeline_context([ROOT])

    limit = _entry_point(context.computation_graph, "__limit")
    assert limit.default_value is None
    assert limit.unresolved_default_kind == "operator"

    messages = [r.getMessage() for r in caplog.records if r.name == LOWERING_LOGGER]
    diagnosed = [m for m in messages if limit.qualified_name in m]
    assert diagnosed, f"unresolved default must be diagnosed by QN; saw {messages}"
    assert "operator" in diagnosed[0]


@requires_license
def test_generated_json_carries_every_key_including_unresolved(fidelity_context, tmp_path) -> None:
    """DD-A12 / I7: the key is always present. Absence of a value is `null`, not absence."""
    generate_all_derived_jsons(fidelity_context.computation_graph.entry_point_groups, tmp_path)

    payloads = {
        path.name: json.loads(path.read_text()) for path in (tmp_path / "inputs").glob("*.json")
    }
    merged = {key: value for payload in payloads.values() for key, value in payload.items()}

    drift = _entry_point(fidelity_context.computation_graph, "__drift")
    rated = _entry_point(fidelity_context.computation_graph, "__rated_power")
    limit = _entry_point(fidelity_context.computation_graph, "__limit")

    assert merged[drift.qualified_name] == -0.1
    assert merged[rated.qualified_name] == 40.0
    # Present and null — never silently omitted (DD-R21).
    assert limit.qualified_name in merged
    assert merged[limit.qualified_name] is None


# --- DD-A11 snapshot route (Phase 5, the declared licence dependency) --------


@pytest.fixture(scope="module")
def fidelity_snapshot_context():
    from sysml_codegen.orchestration.snapshot_context import (
        build_pipeline_context_from_snapshot,
    )

    return build_pipeline_context_from_snapshot(snapshot_fixture("modeled_default_fidelity"))


def test_signed_modeled_default_survives_from_snapshot(fidelity_snapshot_context) -> None:
    drift = _entry_point(fidelity_snapshot_context.computation_graph, "__drift")
    assert drift.default_value == -0.1
    assert drift.unresolved_default_kind is None


def test_unit_annotated_modeled_default_survives_from_snapshot(fidelity_snapshot_context) -> None:
    """The `unit` IR node reaches the offline lane, which no prior snapshot exercised."""
    rated = _entry_point(fidelity_snapshot_context.computation_graph, "__rated_power")
    assert rated.default_value == 40.0
    assert rated.unit_text == "W"


def test_unsupported_default_ir_is_unresolved_from_snapshot(fidelity_snapshot_context) -> None:
    limit = _entry_point(fidelity_snapshot_context.computation_graph, "__limit")
    assert limit.default_value is None
    assert limit.unresolved_default_kind == "operator"


def test_live_and_snapshot_routes_agree(fidelity_context, fidelity_snapshot_context) -> None:
    """Both routes reach the same values, units, and unresolved dispositions."""

    def summary(context):
        return sorted(
            (p.qualified_name, p.default_value, p.unit_text, p.unresolved_default_kind)
            for group in context.computation_graph.entry_point_groups
            for p in group.parameters
        )

    assert summary(fidelity_context) == summary(fidelity_snapshot_context)
