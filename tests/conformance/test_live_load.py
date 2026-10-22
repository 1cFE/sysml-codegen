"""The one shared SysIDE load (EXEC-SUBSET-CONTRACT Item 2b, design D2).

``load_live_models`` never raises. A load with errors, or one that fails outright, comes back
as a ``FailedLoad`` carrying exactly the refusal ``elaborate_model_paths`` raises for it, so
the generator's message is unchanged when the load is shared. A clean load elaborates to the
same sealed context as the path-taking builder.

Licensed.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.core.errors import SysMLParsingError
from sysml_codegen.elaboration import ElaborationCode, ElaborationDiagnosticError
from sysml_codegen.orchestration import elaborated_pipeline
from sysml_codegen.orchestration.elaborated_pipeline import (
    FailedLoad,
    LiveLoad,
    LoadFailureKind,
    load_live_models,
)
from sysml_codegen.orchestration.exact_pipeline_context import (
    build_exact_pipeline_context,
    build_exact_pipeline_context_from_live_load,
)
from tests.conftest import requires_license

pytestmark = requires_license

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _syntax_error_model(tmp_path: Path) -> Path:
    model = tmp_path / "model"
    model.mkdir()
    (model / "model.sysml").write_text("package SyntaxProbe;\npart def Broken { attribute\n")
    return model


def _raised_by_elaboration(paths: list[Path]) -> Exception:
    with pytest.raises(Exception) as caught:
        elaborated_pipeline.elaborate_model_paths(paths)
    return caught.value


def test_a_load_with_errors_is_returned_with_the_parse_refusal(tmp_path):
    model = _syntax_error_model(tmp_path)
    loaded = load_live_models([model])
    assert isinstance(loaded, FailedLoad)
    assert loaded.kind is LoadFailureKind.PARSE_ERRORS
    assert isinstance(loaded.error, SysMLParsingError)
    assert "root-0/model.sysml:2" in str(loaded.error)
    raised = _raised_by_elaboration([model])
    assert type(raised) is type(loaded.error) and str(raised) == str(loaded.error)


def test_a_load_that_raises_value_error_is_a_parse_refusal_not_a_raise(monkeypatch, tmp_path):
    def refuse(*_args, **_kwargs):
        raise ValueError("probe: no model files")

    monkeypatch.setattr(SysideAdapter, "load_model", refuse)
    loaded = load_live_models([tmp_path])
    assert isinstance(loaded, FailedLoad)
    assert loaded.kind is LoadFailureKind.NOT_LOADED
    assert isinstance(loaded.error, SysMLParsingError)
    assert str(loaded.error) == "Failed to load SysML models: probe: no model files"
    assert str(_raised_by_elaboration([tmp_path])) == str(loaded.error)


def test_an_unclassified_load_failure_is_the_internal_defect_refusal(monkeypatch, tmp_path):
    def crash(*_args, **_kwargs):
        raise RuntimeError("probe: the parser crashed")

    monkeypatch.setattr(SysideAdapter, "load_model", crash)
    loaded = load_live_models([tmp_path])
    assert isinstance(loaded, FailedLoad)
    assert loaded.kind is LoadFailureKind.NOT_LOADED
    assert isinstance(loaded.error, ElaborationDiagnosticError)
    [diagnostic] = loaded.error.diagnostics
    assert diagnostic.code is ElaborationCode.SI_INTERNAL_DEFECT
    assert isinstance(loaded.error.__cause__, RuntimeError)
    assert str(_raised_by_elaboration([tmp_path])) == str(loaded.error)


@pytest.mark.parametrize("fixture", ["d38_caret", "constraint_multi_instance"])
def test_a_clean_load_seals_the_same_context_as_the_path_builder(fixture):
    paths = [FIXTURES / fixture]
    loaded = load_live_models(paths)
    assert isinstance(loaded, LiveLoad)
    shared = build_exact_pipeline_context_from_live_load(loaded)
    fresh = build_exact_pipeline_context(paths)
    assert shared.receipt == fresh.receipt
    assert shared.computation_graph.model_dump() == fresh.computation_graph.model_dump()


def test_the_loaded_builder_reaches_the_elaborator_through_its_module(monkeypatch):
    """The 2a harness spies on ``elaborate_loaded_extractor`` by rebinding the module name."""
    seen = []
    real = elaborated_pipeline.elaborate_loaded_extractor

    def spy(*args, **kwargs):
        graph = real(*args, **kwargs)
        seen.append(graph)
        return graph

    monkeypatch.setattr(elaborated_pipeline, "elaborate_loaded_extractor", spy)
    loaded = load_live_models([FIXTURES / "d38_caret"])
    assert isinstance(loaded, LiveLoad)
    build_exact_pipeline_context_from_live_load(loaded)
    assert len(seen) == 1
