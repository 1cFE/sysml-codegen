"""Language-validation boundary for the exact-ID elaboration route."""

from __future__ import annotations

import pytest

from sysml_codegen.elaboration import (
    ElaborationCode,
    ElaborationDiagnosticError,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.raw_elaboration import elaborate

pytestmark = requires_license


def _invalid_namespace_model() -> SysMLDataExtractor:
    extractor = SysMLDataExtractor([FIXTURES_DIR / "elab_namespace_distinguishability_probe"])
    assert extractor.load_models()
    assert extractor.diagnostics is not None
    assert [
        diagnostic.code
        for diagnostic in extractor.diagnostics.validation
        if diagnostic.code == "namespace-distinguishability"
    ] == ["namespace-distinguishability", "namespace-distinguishability"]
    return extractor


def test_namespace_conflicts_block_before_occurrence_expansion() -> None:
    extractor = _invalid_namespace_model()

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborate(
            extractor.model,
            extractor.extract_calculation_definitions(),
            validation_diagnostics=extractor.diagnostics.validation,
        )

    diagnostics = caught.value.diagnostics
    assert [diagnostic.code for diagnostic in diagnostics] == [
        ElaborationCode.SYSML_NAMESPACE_NOT_DISTINGUISHABLE,
        ElaborationCode.SYSML_NAMESPACE_NOT_DISTINGUISHABLE,
    ]
    assert "model.sysml:26:14" in diagnostics[0].detail
    assert "Member name 'array' shadows" in diagnostics[0].detail
    assert "model.sysml:27:18" in diagnostics[1].detail
    assert "Member name 'sensor' shadows" in diagnostics[1].detail
    assert all("explicit `:>>`" in diagnostic.detail for diagnostic in diagnostics)

    with pytest.raises(ElaborationDiagnosticError) as route_error:
        build_elaborated_pipeline([FIXTURES_DIR / "elab_namespace_distinguishability_probe"])
    assert [diagnostic.code for diagnostic in route_error.value.diagnostics] == [
        ElaborationCode.SYSML_NAMESPACE_NOT_DISTINGUISHABLE,
        ElaborationCode.SYSML_NAMESPACE_NOT_DISTINGUISHABLE,
    ]


def test_lenient_namespace_conflict_never_builds_the_invalid_tree() -> None:
    extractor = _invalid_namespace_model()

    graph = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
        strict=False,
    )

    assert not graph.attrs
    assert not graph.calcs
    assert not graph.constraints
    assert [diagnostic.code for diagnostic in graph.diagnostics] == [
        ElaborationCode.SYSML_NAMESPACE_NOT_DISTINGUISHABLE,
        ElaborationCode.SYSML_NAMESPACE_NOT_DISTINGUISHABLE,
    ]
