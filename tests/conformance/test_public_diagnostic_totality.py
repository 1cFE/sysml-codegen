"""Every failure crossing the exact public boundary keeps useful provenance.

The governing rule for these proofs: **a diagnostic field is either measured or
absent, never defaulted.** A refusal that cites a file and line has read them off
the failure; a refusal that cannot name a site omits reference and location
entirely rather than filling them with a plausible guess. Totality means a formed
diagnostic always crosses the boundary, not that all four fields are always
non-empty.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest

import sysml_codegen.snapshot.capture as snapshot_capture
from sysml_codegen.cli import GenerationConfig, cmd_snapshot, run_codegen
from sysml_codegen.elaboration import ElaborationCode, ElaborationDiagnosticError
from sysml_codegen.elaboration.elaborate import ElaborationError
from sysml_codegen.orchestration import elaborated_pipeline, exact_pipeline_context
from tests.conftest import FIXTURES_DIR, requires_license

#: A rendered refusal ends in ``[file:line]`` only when both were measured.
_RENDERED_LOCATION = re.compile(r"\[[^\[\]]+:\d+\]")


def assert_no_location_is_invented(diagnostic: object, rendered: str) -> None:
    """A diagnostic that knows no site names none, in fields and in rendering."""
    assert getattr(diagnostic, "reference") is None
    assert getattr(diagnostic, "source_file") is None
    assert getattr(diagnostic, "source_line") is None
    assert _RENDERED_LOCATION.search(rendered) is None


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


@requires_license
def test_a_syntax_error_reports_as_a_parse_failure_at_its_own_line(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A user's syntax error is a parse failure, not an internal defect.

    The regression this pins: ``SysMLParsingError`` fell out of one passthrough
    tuple, so a plain syntax error surfaced as ``unexpected internal failure``
    cited at line 1 of whichever file sorted first.
    """
    model = tmp_path / "model"
    model.mkdir()
    (model / "model.sysml").write_text(
        "package SyntaxProbe;\n"
        + "".join(f"// filler line {index}\n" for index in range(2, 17))
        + "part def Broken { attribute\n"
    )

    with caplog.at_level(logging.ERROR):
        assert (
            run_codegen(
                GenerationConfig(
                    models_path=model,
                    output_path=tmp_path / "generated",
                    package_name="syntax_probe",
                )
            )
            is False
        )

    assert "SysML parsing failed" in caplog.text
    assert "model.sysml:17" in caplog.text
    assert "unexpected internal failure" not in caplog.text
    assert ElaborationCode.SI_INTERNAL_DEFECT.value not in caplog.text
    assert "Traceback" not in caplog.text


@requires_license
@pytest.mark.skipif(os.geteuid() == 0, reason="root reads an unreadable file anyway")
def test_an_unreadable_source_is_never_cited_against_an_innocent_file(
    tmp_path: Path,
) -> None:
    """The file that caused the failure is named; the valid file beside it is not."""
    model = tmp_path / "model"
    model.mkdir()
    (model / "aaa_fine.sysml").write_text("package FineProbe;\npart def Widget;\n")
    broken = model / "zzz_broken.sysml"
    broken.write_text("package Broken;\n")
    broken.chmod(stat.S_IMODE(0o000))

    try:
        with pytest.raises(ElaborationDiagnosticError) as caught:
            elaborated_pipeline.elaborate_model_paths([model])
    finally:
        broken.chmod(stat.S_IMODE(0o644))

    [diagnostic] = caught.value.diagnostics
    rendered = str(caught.value)
    assert diagnostic.code is ElaborationCode.SI_INTERNAL_DEFECT
    assert "zzz_broken.sysml" in rendered
    assert "aaa_fine" not in rendered
    assert_no_location_is_invented(diagnostic, rendered)


def test_the_internal_defect_code_is_not_the_model_facing_code() -> None:
    """"Your model" and "our bug" are different answers and carry different codes."""
    assert (
        ElaborationCode.SI_INTERNAL_DEFECT.value
        != ElaborationCode.SI_EVIDENCE_INCOMPLETE.value
    )


@pytest.mark.parametrize(
    "planted",
    [
        RuntimeError("planted runtime failure"),
        AttributeError("'NoneType' object has no attribute 'qualified_name'"),
        KeyError("missing declaration"),
        TypeError("unsupported operand"),
    ],
    ids=["runtime", "attribute", "key", "type"],
)
def test_unexpected_internal_failure_is_contained_at_the_total_seam(
    monkeypatch: pytest.MonkeyPatch,
    planted: Exception,
) -> None:
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
    rendered = str(caught.value)
    assert diagnostic.code is ElaborationCode.SI_INTERNAL_DEFECT
    assert f"{type(planted).__name__}: {planted}" in diagnostic.detail
    assert caught.value.__cause__ is planted
    assert_no_location_is_invented(diagnostic, rendered)


def test_the_whole_cause_chain_crosses_the_seam(monkeypatch: pytest.MonkeyPatch) -> None:
    """What the catch-all does know — the chain of causes — it reports in full."""
    root = PermissionError(13, "Permission denied", "zzz_broken.sysml")
    planted = RuntimeError("source acquisition failed")
    planted.__cause__ = root
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

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborated_pipeline.elaborate_loaded_extractor(
            extractor,
            model_paths=(Path("/stage/model.sysml"),),
            source_referents={},
            strict=True,
        )

    [diagnostic] = caught.value.diagnostics
    assert "RuntimeError: source acquisition failed" in diagnostic.detail
    assert "PermissionError" in diagnostic.detail
    assert "zzz_broken.sysml" in diagnostic.detail


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
    assert diagnostic.code is ElaborationCode.SI_INTERNAL_DEFECT
    assert "RuntimeError: planted model load failure" in diagnostic.detail
    assert caught.value.__cause__ is planted
    assert_no_location_is_invented(diagnostic, str(caught.value))


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
    assert diagnostic.code is ElaborationCode.SI_INTERNAL_DEFECT
    assert caught.value.__cause__ is planted
    assert_no_location_is_invented(diagnostic, str(caught.value))


def test_constraint_owner_classification_uses_mapped_metatypes() -> None:
    import inspect

    from sysml_codegen.elaboration.elaborate import _ExactElaborator

    source = inspect.getsource(_ExactElaborator._owner_kind)
    assert "SysideAdapter.is_instance" in source
    assert "type(owner).__name__" not in source


@pytest.mark.parametrize("source_kind", ["models", "snapshot"])
def test_context_builders_contain_unexpected_failures_without_inventing_a_site(
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
    assert diagnostic.code is ElaborationCode.SI_INTERNAL_DEFECT
    assert f"RuntimeError: planted {source_kind} context failure" in diagnostic.detail
    assert caught.value.__cause__ is planted
    assert_no_location_is_invented(diagnostic, str(caught.value))


def test_a_parse_failure_crosses_the_context_builder_as_itself(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The passthrough tuple keeps a formed parse refusal from being reclassified."""
    from sysml_codegen.generation import SysMLParsingError

    planted = SysMLParsingError("Failed to load SysML models from: ['probe']")
    monkeypatch.setattr(
        elaborated_pipeline,
        "elaborate_model_paths",
        lambda _paths: (_ for _ in ()).throw(planted),
    )

    with pytest.raises(SysMLParsingError) as caught:
        exact_pipeline_context.build_exact_pipeline_context([tmp_path])

    assert caught.value is planted


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

    assert ElaborationCode.SI_INTERNAL_DEFECT.value in caplog.text
    assert ElaborationCode.SI_EVIDENCE_INCOMPLETE.value not in caplog.text
    assert f"RuntimeError: planted {source_kind} generation failure" in caplog.text
    assert _RENDERED_LOCATION.search(caplog.text) is None
    assert "Traceback" not in caplog.text


def test_a_formed_generation_refusal_is_not_relabelled_an_internal_defect(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A refusal the generator already formed keeps its own code and vocabulary."""
    import sysml_codegen.cli as cli_module
    from sysml_codegen.generation import CodeGenerationError

    monkeypatch.setattr(
        exact_pipeline_context,
        "build_exact_pipeline_context",
        lambda _source: SimpleNamespace(computation_graph=SimpleNamespace(modules=())),
    )
    monkeypatch.setattr(
        cli_module,
        "_generate_package_from_graph",
        lambda _graph, _config: (_ for _ in ()).throw(
            CodeGenerationError("EXIT_POINT_TYPE_UNSUPPORTED: module='m' output='root'")
        ),
    )
    config = GenerationConfig(
        models_path=tmp_path / "models",
        output_path=tmp_path / "generated",
        package_name="totality_probe",
    )

    with caplog.at_level(logging.ERROR):
        assert run_codegen(config) is False

    assert "EXIT_POINT_TYPE_UNSUPPORTED" in caplog.text
    assert ElaborationCode.SI_INTERNAL_DEFECT.value not in caplog.text
    assert "unexpected internal failure" not in caplog.text


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

    assert ElaborationCode.SI_INTERNAL_DEFECT.value in caplog.text
    assert "RuntimeError: planted capture failure" in caplog.text
    assert _RENDERED_LOCATION.search(caplog.text) is None
    assert "Traceback" not in caplog.text
