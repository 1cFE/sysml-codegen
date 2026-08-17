"""One public bridge preserves agentic semantic-evidence failures."""

from __future__ import annotations

import ast
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from agentic_mbse import SemanticEvidenceCode, SemanticEvidenceError

from sysml_codegen.elaboration import ElaborationCode, ElaborationDiagnosticError
from sysml_codegen.orchestration import elaborated_pipeline
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from tests.conftest import FIXTURES_DIR, requires_license

RAW_SOURCE = str(Path("/stage/model.sysml").resolve())
REFERENT = "root-0/model.sysml"


class _EvidenceFailingExtractor:
    def __init__(self, _model_paths: list[Path] | None = None) -> None:
        self.model = object()
        self.diagnostics = SimpleNamespace(validation=())

    def load_models(self) -> bool:
        return True

    def extract_calculation_definitions(self) -> list[Any]:
        parser_cause = RuntimeError("installed parser metatype failure")
        semantic_error = SemanticEvidenceError(
            SemanticEvidenceCode.METATYPE_CHECK_FAILED,
            "is_instance",
            "the installed parser rejected the metatype query",
            location=(RAW_SOURCE, 7),
            reference="plant::source",
            cause=parser_cause,
        )
        raise semantic_error from parser_cause


@pytest.mark.parametrize("strict", [True, False])
def test_loaded_extractor_converts_semantic_evidence_once(strict: bool) -> None:
    extractor = _EvidenceFailingExtractor()

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborated_pipeline.elaborate_loaded_extractor(
            extractor,
            model_paths=(Path(RAW_SOURCE),),
            source_referents={RAW_SOURCE: REFERENT},
            strict=strict,
        )

    public_error = caught.value
    assert len(public_error.diagnostics) == 1
    diagnostic = public_error.diagnostics[0]
    assert diagnostic.code is ElaborationCode.SI_EVIDENCE_INCOMPLETE
    assert diagnostic.consumer_display == "plant::source"
    assert diagnostic.detail == (
        "is_instance: the installed parser rejected the metatype query "
        "[root-0/model.sysml:7]"
    )
    assert str(public_error).count("SI_EVIDENCE_INCOMPLETE") == 1
    assert isinstance(public_error.__cause__, SemanticEvidenceError)
    semantic_error = public_error.__cause__
    assert semantic_error.cause is semantic_error.__cause__
    assert isinstance(semantic_error.cause, RuntimeError)


def test_live_and_admitted_routes_delegate_to_one_boundary(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[tuple[Path, ...], dict[str, str], bool]] = []
    marker = object()

    monkeypatch.setattr(elaborated_pipeline, "SysMLDataExtractor", _EvidenceFailingExtractor)
    monkeypatch.setattr(
        elaborated_pipeline,
        "_live_source_referents",
        lambda _model, _paths: {RAW_SOURCE: REFERENT},
    )

    def fake_boundary(
        _extractor: object,
        *,
        model_paths: tuple[Path, ...],
        source_referents: dict[str, str],
        strict: bool,
    ) -> object:
        calls.append((model_paths, source_referents, strict))
        return marker

    monkeypatch.setattr(elaborated_pipeline, "elaborate_loaded_extractor", fake_boundary)

    assert elaborated_pipeline.elaborate_model_paths([Path(RAW_SOURCE)], strict=False) is marker

    admitted = SimpleNamespace(
        staged_files=(Path(RAW_SOURCE),),
        staged_to_referent={RAW_SOURCE: REFERENT},
        files=(SimpleNamespace(referent=REFERENT),),
        verify_after_parse=lambda _model: None,
    )
    assert elaborated_pipeline.elaborate_admitted_sources(admitted, strict=True) is marker
    assert calls == [
        ((Path(RAW_SOURCE),), {RAW_SOURCE: REFERENT}, False),
        ((Path(RAW_SOURCE),), {RAW_SOURCE: REFERENT}, True),
    ]


@pytest.mark.parametrize("strict", [True, False])
@pytest.mark.parametrize("source_arm", ["live", "admitted"])
def test_public_source_arms_preserve_the_same_evidence_refusal(
    monkeypatch: pytest.MonkeyPatch,
    source_arm: str,
    strict: bool,
) -> None:
    monkeypatch.setattr(elaborated_pipeline, "SysMLDataExtractor", _EvidenceFailingExtractor)
    monkeypatch.setattr(
        elaborated_pipeline,
        "_live_source_referents",
        lambda _model, _paths: {RAW_SOURCE: REFERENT},
    )
    verified: list[object] = []
    admitted = SimpleNamespace(
        staged_files=(Path(RAW_SOURCE),),
        staged_to_referent={RAW_SOURCE: REFERENT},
        files=(SimpleNamespace(referent=REFERENT),),
        verify_after_parse=verified.append,
    )

    with pytest.raises(ElaborationDiagnosticError) as caught:
        if source_arm == "live":
            elaborated_pipeline.elaborate_model_paths([Path(RAW_SOURCE)], strict=strict)
        else:
            elaborated_pipeline.elaborate_admitted_sources(admitted, strict=strict)

    assert [item.code for item in caught.value.diagnostics] == [
        ElaborationCode.SI_EVIDENCE_INCOMPLETE
    ]
    assert str(caught.value).count("SI_EVIDENCE_INCOMPLETE") == 1
    assert verified == []


def test_snapshot_evidence_refusal_preserves_existing_output(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from sysml_codegen.extraction import source_manifest

    admitted = SimpleNamespace(
        staged_files=(Path(RAW_SOURCE),),
        staged_to_referent={RAW_SOURCE: REFERENT},
        files=(SimpleNamespace(referent=REFERENT),),
        verify_after_parse=lambda _model: None,
    )

    @contextmanager
    def fake_admission(_model_paths: list[Path]):
        yield admitted

    monkeypatch.setattr(source_manifest, "admit_sources", fake_admission)
    monkeypatch.setattr(elaborated_pipeline, "SysMLDataExtractor", _EvidenceFailingExtractor)
    output = tmp_path / "snapshot.json"
    output.write_bytes(b"existing snapshot")

    with pytest.raises(ElaborationDiagnosticError):
        capture_instance_graph_snapshot([Path(RAW_SOURCE)], output)

    assert output.read_bytes() == b"existing snapshot"
    assert list(tmp_path.iterdir()) == [output]


def test_snapshot_capture_uses_the_admitted_route() -> None:
    capture_source = (
        Path(elaborated_pipeline.__file__).resolve().parents[1] / "snapshot" / "capture.py"
    ).read_text(encoding="utf-8")
    assert "elaborate_admitted_sources(admission)" in capture_source


def test_raw_builder_is_private_and_has_one_production_caller() -> None:
    import sysml_codegen.elaboration as elaboration

    assert "elaborate" not in elaboration.__all__
    package_root = Path(elaborated_pipeline.__file__).resolve().parents[1]
    callers = []
    for source_path in package_root.rglob("*.py"):
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        if any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_build_instance_graph"
            for node in ast.walk(tree)
        ):
            callers.append(source_path.relative_to(package_root).as_posix())
    assert callers == ["orchestration/elaborated_pipeline.py"]


@requires_license
@pytest.mark.parametrize("strict", [True, False])
def test_valid_indexed_source_refuses_before_graph_with_exact_capability_diagnostic(
    strict: bool,
) -> None:
    fixture = FIXTURES_DIR / "indexed_expression_source"

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborated_pipeline.elaborate_model_paths([fixture], strict=strict)

    [diagnostic] = caught.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_INDEXED_SOURCE_UNSUPPORTED
    assert diagnostic.consumer is None
    assert diagnostic.consumer_display == "<model>"
    assert diagnostic.param_name is None
    assert diagnostic.detail.endswith(
        "tests/fixtures/indexed_expression_source/model.sysml:17: "
        "indexed source '#(...)' is recognized but not implemented"
    )
    assert str(caught.value).count("SI_INDEXED_SOURCE_UNSUPPORTED") == 1
