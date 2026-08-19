"""Every failure crossing the exact public boundary keeps useful provenance."""

from __future__ import annotations

import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.elaboration import ElaborationCode, ElaborationDiagnosticError
from sysml_codegen.elaboration.elaborate import ElaborationError
from sysml_codegen.elaboration.expression_evidence import ExpressionEvidenceInventory
from sysml_codegen.orchestration import elaborated_pipeline
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
        assert run_codegen(
            GenerationConfig(
                models_path=model,
                output_path=tmp_path / fixture,
                package_name=fixture,
            )
        ) is False
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
            item for item in graph.diagnostics if item.code is ElaborationCode.SI_CONSTRAINT_UNATTACHED
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


def test_constraint_owner_classification_uses_mapped_metatypes() -> None:
    import inspect

    from sysml_codegen.elaboration.elaborate import _ExactElaborator

    source = inspect.getsource(_ExactElaborator._owner_kind)
    assert "SysideAdapter.is_instance" in source
    assert "type(owner).__name__" not in source
