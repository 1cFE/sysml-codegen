"""Every failure crossing the exact public boundary keeps useful provenance."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

import sysml_codegen.snapshot.capture as snapshot_capture
from sysml_codegen.cli import GenerationConfig, cmd_snapshot, run_codegen
from sysml_codegen.elaboration import ElaborationCode, ElaborationDiagnosticError
from sysml_codegen.elaboration.elaborate import ElaborationError
from sysml_codegen.orchestration import elaborated_pipeline, exact_pipeline_context
from tests.conftest import FIXTURES_DIR, requires_license


@requires_license
@pytest.mark.parametrize(
    ("fixture", "reference", "line", "detail"),
    [
        ("anonymous_return", "AnonymousReturnLibrary::AnonReturn", 10, "anonymous `return`"),
        ("zero_output_calc", "ZeroOutputLibrary::NoOutputCalc", 7, "zero output attributes"),
    ],
)
def test_committed_extraction_refusals_are_typed_and_located(
    fixture: str,
    reference: str,
    line: int,
    detail: str,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    model = FIXTURES_DIR / fixture
    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborated_pipeline.elaborate_model_paths([model])

    [diagnostic] = caught.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_EVIDENCE_INCOMPLETE
    assert diagnostic.reference == reference
    assert diagnostic.source_file == "root-0/library.sysml"
    assert diagnostic.source_line == line
    assert detail in diagnostic.detail
    assert caught.value.__cause__ is not None

    with caplog.at_level(logging.ERROR):
        assert (
            run_codegen(
                GenerationConfig(
                    models_path=model,
                    output_path=tmp_path / fixture,
                    package_name=fixture,
                )
            )
            is False
        )
    assert "SI_EVIDENCE_INCOMPLETE" in caplog.text
    assert reference in caplog.text
    assert f"root-0/library.sysml:{line}" in caplog.text
    assert "Traceback" not in caplog.text


@requires_license
def test_readiness_findings_keep_authored_text_and_location() -> None:
    model = FIXTURES_DIR / "expression_binding_probe"
    with pytest.raises(ElaborationError) as caught:
        elaborated_pipeline.elaborate_model_paths([model], strict=True)

    assert caught.value.findings
    for finding in caught.value.findings:
        assert finding.reference
        assert finding.source_file == "root-0/design.sysml"
        assert finding.source_line > 0
        assert finding.reference in finding.detail
        assert f"root-0/design.sysml:{finding.source_line}" in str(caught.value)


@requires_license
@pytest.mark.parametrize("strict", [True, False])
def test_unattached_constraint_keeps_owner_context_without_parser_repr(strict: bool) -> None:
    model = FIXTURES_DIR / "constraint_domain_calc_def_owner"
    if strict:
        with pytest.raises(ElaborationDiagnosticError) as caught:
            elaborated_pipeline.elaborate_model_paths([model], strict=True)
        [diagnostic] = caught.value.diagnostics
    else:
        graph = elaborated_pipeline.elaborate_model_paths([model], strict=False)
        [diagnostic] = [
            item
            for item in graph.diagnostics
            if item.code is ElaborationCode.SI_CONSTRAINT_UNATTACHED
        ]
    assert diagnostic.reference == "constraint_domain_calc_def_owner::Sizer::demand_positive"
    assert diagnostic.source_file == "root-0/model.sysml"
    assert diagnostic.source_line == 12
    assert "syside.core.QualifiedName" not in diagnostic.detail
    assert "tests/fixtures" not in diagnostic.detail


def test_unexpected_internal_failure_is_contained_at_the_total_seam(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    planted = RuntimeError("planted internal failure")
    monkeypatch.setattr(
        elaborated_pipeline,
        "build_expression_evidence_inventory",
        lambda _model: (_ for _ in ()).throw(planted),
    )
    extractor = SimpleNamespace(
        model=object(),
        diagnostics=SimpleNamespace(validation=()),
        extract_calculation_definitions=lambda: [],
    )
    raw = str(Path("/stage/model.sysml").resolve())

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborated_pipeline.elaborate_loaded_extractor(
            extractor,
            model_paths=(Path(raw),),
            source_referents={raw: "root-0/model.sysml"},
            strict=True,
        )

    [diagnostic] = caught.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_EVIDENCE_INCOMPLETE
    assert diagnostic.reference == "<model>"
    assert diagnostic.source_file == "root-0/model.sysml"
    assert diagnostic.source_line == 1
    assert "RuntimeError: planted internal failure" in diagnostic.detail
    assert caught.value.__cause__ is planted


def test_live_api_contains_an_unexpected_model_load_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    model = tmp_path / "model"
    model.mkdir()
    (model / "design.sysml").write_text("package TotalityProbe;\n")
    planted = RuntimeError("planted model load failure")
    monkeypatch.setattr(
        elaborated_pipeline,
        "SysMLDataExtractor",
        lambda _paths: (_ for _ in ()).throw(planted),
    )

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborated_pipeline.elaborate_model_paths([model])

    [diagnostic] = caught.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_EVIDENCE_INCOMPLETE
    assert diagnostic.reference == "root-0/design.sysml"
    assert diagnostic.source_file == "root-0/design.sysml"
    assert diagnostic.source_line == 1
    assert "RuntimeError: planted model load failure" in diagnostic.detail
    assert caught.value.__cause__ is planted


def test_admitted_api_contains_an_unexpected_model_load_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = str(Path("/stage/model.sysml").resolve())
    admitted = SimpleNamespace(
        staged_files=(Path(raw),),
        staged_to_referent={raw: "root-0/model.sysml"},
    )
    planted = RuntimeError("planted admitted load failure")
    monkeypatch.setattr(
        elaborated_pipeline,
        "SysMLDataExtractor",
        lambda _paths: (_ for _ in ()).throw(planted),
    )

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborated_pipeline.elaborate_admitted_sources(admitted)

    [diagnostic] = caught.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_EVIDENCE_INCOMPLETE
    assert diagnostic.source_file == "root-0/model.sysml"
    assert diagnostic.source_line == 1
    assert caught.value.__cause__ is planted


def test_constraint_owner_classification_uses_mapped_metatypes() -> None:
    import inspect

    from sysml_codegen.elaboration.elaborate import _ExactElaborator

    source = inspect.getsource(_ExactElaborator._owner_kind)
    assert "SysideAdapter.is_instance" in source
    assert "type(owner).__name__" not in source


@pytest.mark.parametrize("source_kind", ["models", "snapshot"])
def test_context_builders_contain_unexpected_failures_with_nearest_source(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    source_kind: str,
) -> None:
    planted = RuntimeError(f"planted {source_kind} context failure")
    model_root = tmp_path / "model"
    model_root.mkdir()
    (model_root / "design.sysml").write_text("package TotalityProbe;\n")
    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text(
        json.dumps(
            {
                "sources": {
                    "files": [{"referent": "root-0/design.sysml"}],
                }
            }
        )
    )
    monkeypatch.setattr(
        elaborated_pipeline,
        "elaborate_model_paths",
        lambda _paths: object(),
    )
    import sysml_codegen.snapshot.envelope as snapshot_envelope

    monkeypatch.setattr(
        snapshot_envelope,
        "load_instance_graph_snapshot",
        lambda _path, source_roots=None: object(),
    )
    monkeypatch.setattr(
        exact_pipeline_context,
        "_seal",
        lambda _graph, _targets: (_ for _ in ()).throw(planted),
    )

    with pytest.raises(ElaborationDiagnosticError) as caught:
        if source_kind == "models":
            exact_pipeline_context.build_exact_pipeline_context([model_root])
        else:
            exact_pipeline_context.build_exact_pipeline_context_from_snapshot(snapshot)

    [diagnostic] = caught.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_EVIDENCE_INCOMPLETE
    assert diagnostic.reference == "root-0/design.sysml"
    assert diagnostic.source_file == "root-0/design.sysml"
    assert diagnostic.source_line == 1
    assert f"RuntimeError: planted {source_kind} context failure" in diagnostic.detail
    assert caught.value.__cause__ is planted


@pytest.mark.parametrize("source_kind", ["models", "snapshot"])
def test_generation_entry_point_never_leaks_an_unexpected_traceback(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    source_kind: str,
) -> None:
    planted = RuntimeError(f"planted {source_kind} generation failure")
    builder_name = (
        "build_exact_pipeline_context_from_snapshot"
        if source_kind == "snapshot"
        else "build_exact_pipeline_context"
    )
    monkeypatch.setattr(
        exact_pipeline_context,
        builder_name,
        lambda _source: (_ for _ in ()).throw(planted),
    )
    config = GenerationConfig(
        models_path=tmp_path / "models" if source_kind == "models" else None,
        from_snapshot=tmp_path / "snapshot.json" if source_kind == "snapshot" else None,
        output_path=tmp_path / "generated",
        package_name="totality_probe",
    )

    with caplog.at_level(logging.ERROR):
        assert run_codegen(config) is False

    assert "SI_EVIDENCE_INCOMPLETE" in caplog.text
    assert f"RuntimeError: planted {source_kind} generation failure" in caplog.text
    assert "Traceback" not in caplog.text


def test_snapshot_command_never_leaks_an_unexpected_traceback(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    planted = RuntimeError("planted capture failure")
    monkeypatch.setattr(
        snapshot_capture,
        "capture_instance_graph_snapshot",
        lambda _paths, _output: (_ for _ in ()).throw(planted),
    )
    args = argparse.Namespace(
        models=tmp_path / "models",
        output=tmp_path / "snapshot.json",
        verbose=False,
    )

    with caplog.at_level(logging.ERROR):
        assert cmd_snapshot(args) == 1

    assert "SI_EVIDENCE_INCOMPLETE" in caplog.text
    assert "RuntimeError: planted capture failure" in caplog.text
    assert "Traceback" not in caplog.text
