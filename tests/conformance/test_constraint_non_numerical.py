"""End-to-end numerical-profile v3 warning, exclusion, and halt families."""

from __future__ import annotations

import json
import logging

import pytest

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from sysml_codegen.orchestration.snapshot_context import build_pipeline_context_from_snapshot
from tests.conftest import FIXTURES_DIR, requires_license

LOWERING_LOGGER = "sysml_codegen.analysis.constraint_lowering"
EXPECTED_WARNING = (
    "Constraint constraint_non_numerical::MixedPurposeHost::status_annotation at "
    "root-0/model.sysml:13:9 is not numerical and will not execute: "
    "warn_non_numerical_equality: equality is a valid non-numerical statement and is not executed"
)
EXPECTED_EXCLUDED_BYTES = (
    b'{"constraint_id":"constraint_non_numerical__MixedPurposeHost__status_annotation__'
    b'status_annotation__cefe17cf7fc6a392","exclusion":{"kind":"non_numerical",'
    b'"location":"root-0/model.sysml:13:9","reasons":["warn_non_numerical_equality"]},'
    b'"membership_kind":null,"source_form":"inline","usage_qualified_name":'
    b'"constraint_non_numerical::MixedPurposeHost::status_annotation"}'
)


def _profile_warnings(caplog: pytest.LogCaptureFixture) -> list[str]:
    return [
        record.getMessage()
        for record in caplog.records
        if record.levelno == logging.WARNING and record.name == LOWERING_LOGGER
    ]


def _excluded_bytes(context) -> bytes:
    catalog = context.computation_graph.constraint_catalog
    assert catalog is not None
    [excluded] = catalog.excluded_records
    return json.dumps(
        excluded.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
    ).encode("ascii")


@requires_license
def test_non_numerical_fixture_generates_warns_and_catalogs(caplog):
    with caplog.at_level(logging.WARNING, logger=LOWERING_LOGGER):
        context = build_pipeline_context(
            [FIXTURES_DIR / "constraint_non_numerical"],
            lower_constraints_enabled=True,
        )

    warnings = _profile_warnings(caplog)
    assert warnings == [EXPECTED_WARNING]

    catalog = context.computation_graph.constraint_catalog
    assert catalog is not None
    assert len(catalog.concrete_entries) == 1
    [excluded] = catalog.excluded_records
    assert excluded.usage_qualified_name.endswith("status_annotation")
    assert excluded.exclusion.kind == "non_numerical"
    assert excluded.exclusion.reasons == ["warn_non_numerical_equality"]
    assert excluded.exclusion.location == "root-0/model.sysml:13:9"
    assert _excluded_bytes(context) == EXPECTED_EXCLUDED_BYTES


@requires_license
def test_non_numerical_live_snapshot_warning_and_record_parity(caplog):
    fixture = FIXTURES_DIR / "constraint_non_numerical"
    snapshot = fixture / "extraction_snapshot.json"

    with caplog.at_level(logging.WARNING, logger=LOWERING_LOGGER):
        live = build_pipeline_context([fixture], lower_constraints_enabled=True)
    live_warnings = _profile_warnings(caplog)
    caplog.clear()

    with caplog.at_level(logging.WARNING, logger=LOWERING_LOGGER):
        offline = build_pipeline_context_from_snapshot(snapshot)
    offline_warnings = _profile_warnings(caplog)

    assert live_warnings == [EXPECTED_WARNING]
    assert offline_warnings == [EXPECTED_WARNING]
    assert offline.computation_graph.model_dump(mode="json") == live.computation_graph.model_dump(
        mode="json"
    )
    live_catalog = live.computation_graph.constraint_catalog
    offline_catalog = offline.computation_graph.constraint_catalog
    assert live_catalog is not None
    assert offline_catalog is not None
    assert offline_catalog.model_dump(mode="json") == live_catalog.model_dump(mode="json")
    assert _excluded_bytes(live) == EXPECTED_EXCLUDED_BYTES
    assert _excluded_bytes(offline) == EXPECTED_EXCLUDED_BYTES


def test_non_numerical_snapshot_warning_and_record_are_exact(caplog):
    snapshot = FIXTURES_DIR / "constraint_non_numerical/extraction_snapshot.json"
    with caplog.at_level(logging.WARNING, logger=LOWERING_LOGGER):
        context = build_pipeline_context_from_snapshot(snapshot)
    assert _profile_warnings(caplog) == [EXPECTED_WARNING]
    assert _excluded_bytes(context) == EXPECTED_EXCLUDED_BYTES


@requires_license
def test_malformed_numerical_fixture_halts_naming_fix():
    with pytest.raises(CodeGenerationError) as exc_info:
        build_pipeline_context(
            [FIXTURES_DIR / "constraint_malformed_mixed"],
            lower_constraints_enabled=True,
        )

    message = str(exc_info.value)
    assert "mixed_claim" in message
    assert "model.sysml:" in message
    assert "feature_ref" in message
    assert "block_non_numerical_containment" in message
    assert "generation stops" in message
    assert "separate it into its own assertion" in message
    assert "rewrite it as a numerical comparison" in message
    assert "is not executed" not in message
