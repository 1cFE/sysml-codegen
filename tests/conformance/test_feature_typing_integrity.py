"""Exact primitive typing and exact document-origin contracts."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.core.type_mapping import QUALIFIED_SYSML_TO_PYTHON, SYSML_TO_PYTHON
from sysml_codegen.elaboration import ElaborationCode, ElaborationDiagnosticError
from sysml_codegen.elaboration.expression_evidence import ExpressionEvidenceInventory
from sysml_codegen.extraction.errors import ExactTypeError
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.feature_metadata import _source_file, extract_feature_unit
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_loaded_extractor
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

TYPING_FIXTURE = FIXTURES_DIR / "feature_typing_integrity"
METADATA_FIXTURE = FIXTURES_DIR / "feature_metadata_multifile"


def _loaded_extractor(fixture: Path = TYPING_FIXTURE) -> SysMLDataExtractor:
    extractor = SysMLDataExtractor([fixture])
    assert extractor.load_models()
    return extractor


def _attribute(extractor: SysMLDataExtractor, qualified_name: str) -> Any:
    return next(
        attribute
        for attribute in SysideAdapter.elements_of_type(extractor.model, "AttributeUsage")
        if str(getattr(attribute, "qualified_name", None)) == qualified_name
    )


@pytest.mark.parametrize(
    ("member", "expected"),
    [
        ("real_value", ("Real", "float")),
        ("integer_value", ("Integer", "int")),
        ("boolean_value", ("Boolean", "bool")),
        ("string_value", ("String", "str")),
    ],
)
def test_only_exact_scalarvalues_primitive_typings_are_accepted(
    member: str, expected: tuple[str, str]
) -> None:
    extractor = _loaded_extractor()
    attribute = _attribute(
        extractor,
        f"FeatureTypingIntegrity::SupportedTypes::{member}",
    )

    extracted = extractor._extract_attribute(attribute)

    assert extracted is not None
    assert (extracted.sysml_type, extracted.python_type) == expected


@pytest.mark.parametrize(
    ("member", "reason", "line"),
    [
        ("MissingType::value", "exactly one qualified typing", 18),
        ("UserDefinedLookalike::value", "FeatureTypingUserTypes::Real", 23),
        ("MultipleTypes::value", "exactly one qualified typing", 28),
        ("UnsupportedType::value", "FeatureTypingUserTypes::Vector", 33),
    ],
)
def test_invalid_real_typing_shapes_refuse_with_identity_and_location(
    member: str, reason: str, line: int
) -> None:
    extractor = _loaded_extractor()
    qualified_name = f"FeatureTypingIntegrity::{member}"
    attribute = _attribute(extractor, qualified_name)

    with pytest.raises(ExactTypeError) as caught:
        extractor._extract_attribute(attribute)

    error = caught.value
    assert error.code is ElaborationCode.SI_TYPE_INVALID
    assert error.reference == qualified_name
    assert error.location is not None
    assert Path(error.location[0]).name == "model.sysml"
    assert error.location[1] == line
    assert reason in error.detail


def test_corpus_user_defined_enumeration_is_a_named_type_refusal() -> None:
    extractor = _loaded_extractor(FIXTURES_DIR / "plant_value_shapes")

    with pytest.raises(ExactTypeError) as caught:
        extractor.extract_calculation_definitions()

    error = caught.value
    assert error.code is ElaborationCode.SI_TYPE_INVALID
    assert error.reference == "PlantValueShapesLib::ChamberSelectCalc::wall"
    assert "PlantValueShapesLib::'Wall Kind'" in error.detail
    assert error.location is not None
    assert Path(error.location[0]).name == "library.sysml"
    assert error.location[1] == 92


@pytest.mark.parametrize("strict", [True, False])
def test_exact_type_refusal_uses_the_one_public_bridge(
    strict: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw_source = str((TYPING_FIXTURE / "model.sysml").resolve())
    error = ExactTypeError(
        "typing target 'FeatureTypingUserTypes::Real' is unsupported",
        reference="FeatureTypingIntegrity::UserDefinedLookalike::value",
        location=(raw_source, 23),
    )

    class Extractor:
        model = object()
        diagnostics = SimpleNamespace(validation=())

        @staticmethod
        def extract_calculation_definitions() -> list[Any]:
            raise error

    monkeypatch.setattr(
        "sysml_codegen.orchestration.elaborated_pipeline.build_expression_evidence_inventory",
        lambda _model: ExpressionEvidenceInventory({}),
    )

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborate_loaded_extractor(
            Extractor(),
            model_paths=(Path(raw_source),),
            source_referents={raw_source: "root-0/model.sysml"},
            strict=strict,
        )

    public = caught.value
    assert len(public.diagnostics) == 1
    diagnostic = public.diagnostics[0]
    assert diagnostic.code is ElaborationCode.SI_TYPE_INVALID
    assert diagnostic.consumer_display == error.reference
    assert diagnostic.detail == (
        "extract_type: typing target 'FeatureTypingUserTypes::Real' is unsupported"
    )
    assert diagnostic.reference == error.reference
    assert diagnostic.source_file == "root-0/model.sysml"
    assert diagnostic.source_line == 23
    assert "root-0/model.sysml:23" in str(public)
    assert str(public).count("SI_TYPE_INVALID") == 1
    assert public.__cause__ is error


def test_document_origin_is_exact_for_each_file_without_path_election() -> None:
    extractor = _loaded_extractor(METADATA_FIXTURE)
    expected_files = {path.resolve() for path in METADATA_FIXTURE.glob("*.sysml")}
    witnessed: set[Path] = set()
    for feature in SysideAdapter.elements_of_type(
        extractor.model, "AttributeUsage", include_subtypes=True
    ):
        source = _source_file(feature)
        if source is None or source.resolve() not in expected_files:
            continue
        if extract_feature_unit(feature) is not None:
            witnessed.add(source.resolve())

    assert witnessed == expected_files


def test_document_origin_has_no_glob_or_model_path_fallback() -> None:
    import sysml_codegen.extraction.feature_metadata as feature_metadata

    source = Path(feature_metadata.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    source_function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_source_file"
    )
    calls = {
        node.func.attr
        for node in ast.walk(source_function)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    names = {node.id for node in ast.walk(source_function) if isinstance(node, ast.Name)}
    assert calls.isdisjoint({"glob", "rglob", "is_file", "is_dir"})
    assert "model_paths" not in names
    assert "model_paths" not in inspect.signature(extract_feature_unit).parameters
    assert "model_paths" not in inspect.signature(_source_file).parameters


def test_exact_scalar_view_is_the_canonical_qualified_only_mapping() -> None:
    assert dict(QUALIFIED_SYSML_TO_PYTHON) == {
        name: python_type
        for name, python_type in SYSML_TO_PYTHON.items()
        if name.startswith("ScalarValues::")
    }
    assert all("::" in name for name in QUALIFIED_SYSML_TO_PYTHON)


def test_exact_elaborator_does_not_own_a_second_scalar_mapping() -> None:
    import sysml_codegen.elaboration.elaborate as elaborate_module

    source = inspect.getsource(elaborate_module._ExactElaborator._feature_python_type)
    assert "QUALIFIED_SYSML_TO_PYTHON" in source
    assert "ScalarValues::Real" not in source


def test_root_namespace_scalar_lookalike_is_not_a_primitive(tmp_path: Path) -> None:
    """B6: even the exact bare spelling ``Real`` is user-owned outside ScalarValues."""
    source = tmp_path / "model.sysml"
    source.write_text(
        """attribute def Real;

package RootTypeLookalike {
    calc def Probe {
        in attribute value : Real;
        out attribute result : ScalarValues::Real = 0.0;
    }
}
""",
        encoding="utf-8",
    )
    extractor = _loaded_extractor(source)
    attribute = _attribute(extractor, "RootTypeLookalike::Probe::value")

    with pytest.raises(ExactTypeError) as caught:
        extractor._extract_attribute(attribute)

    assert caught.value.reference == "RootTypeLookalike::Probe::value"
    assert "typing target 'Real' is unsupported" in caught.value.detail


def test_extractor_reads_only_the_qualified_scalar_view() -> None:
    source = inspect.getsource(SysMLDataExtractor._extract_attribute)
    assert "QUALIFIED_SYSML_TO_PYTHON" in source
    assert "SYSML_TO_PYTHON.get" not in source


def test_public_extractor_kind_decisions_use_mapped_metatypes() -> None:
    source = inspect.getsource(SysMLDataExtractor._extract_calculation_definition)
    assert 'is_instance(owning_membership, "ReturnParameterMembership")' in source
    assert "type(owning_membership).__name__" not in source
