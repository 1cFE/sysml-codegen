"""Real SysIDE coverage for the one-owner multiplicity authority rule."""

from __future__ import annotations

import pytest
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration import (
    ElaborationCode,
    ElaborationDiagnosticError,
)
from sysml_codegen.elaboration.diagnostics import ElaborationInvariantError
from sysml_codegen.elaboration.occurrence import (
    build_feature_slot_index,
    build_occurrence_index,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license


def _occurrences(name: str):
    extractor = SysMLDataExtractor([FIXTURES_DIR / name])
    assert extractor.load_models()
    return build_occurrence_index(
        extractor.model,
        build_feature_slot_index(extractor.model),
    )


def test_root_literal_and_nested_exact_writer_expand_only_their_declared_counts() -> None:
    root = _occurrences("occurrence_calc_domain_derivation")
    assert {
        occurrence.display_path
        for occurrence in root.occurrences()
        if "__cell[" in occurrence.display_path
    } == {
        "OccurrenceCalcDomainDerivation__cell[0]",
        "OccurrenceCalcDomainDerivation__cell[1]",
    }

    nested = _occurrences("elab_finite_expression_multiplicity")
    assert {
        occurrence.display_path
        for occurrence in nested.occurrences()
        if "__cell[" in occurrence.display_path
    } == {
        f"ElabFiniteExpressionMultiplicity__host__cell[{index}]" for index in range(4)
    }

    package_writer = _occurrences("occurrence_execution_matrix")
    assert {
        occurrence.display_path
        for occurrence in package_writer.occurrences()
        if "__root_cell[" in occurrence.display_path
    } == {
        "OccurrenceExecutionMatrix__root_cell[0]",
        "OccurrenceExecutionMatrix__root_cell[1]",
    }


def test_redefinition_uses_the_most_specific_writer_in_one_owner_domain() -> None:
    occurrences = _occurrences("elab_native_plural_scope")
    assert {
        occurrence.display_path
        for occurrence in occurrences.occurrences()
        if occurrence.display_path.endswith(tuple(f"__leaf[{index}]" for index in (0, 1)))
    } == {
        "ElabNativePluralScope__plant__selected__leaf[0]",
        "ElabNativePluralScope__plant__selected__leaf[1]",
        "ElabNativePluralScope__plant__shadow__leaf[0]",
        "ElabNativePluralScope__plant__shadow__leaf[1]",
    }


@pytest.mark.parametrize(
    ("fixture", "code", "detail", "reference", "line"),
    [
        (
            "multiplicity_writer_authority",
            ElaborationCode.SI_MULTIPLICITY_UNRESOLVED,
            "upper multiplicity on 'cell' is not a known finite integer",
            "unrelated_count",
            25,
        ),
        (
            "elab_unresolved_multiplicity",
            ElaborationCode.SI_MULTIPLICITY_UNRESOLVED,
            "upper multiplicity on 'cell' is not a known finite integer",
            "count",
            8,
        ),
        (
            "instance_index_probe",
            ElaborationCode.SI_MULTIPLICITY_UNSUPPORTED,
            "range multiplicity on 'range_member' is outside the supported occurrence model",
            "InstanceIndexProbe::BlockHost::range_member",
            94,
        ),
    ],
)
def test_unrelated_unresolved_and_unsupported_shapes_refuse_publicly(
    fixture: str,
    code: ElaborationCode,
    detail: str,
    reference: str,
    line: int,
) -> None:
    with pytest.raises(ElaborationDiagnosticError) as excinfo:
        elaborate_model_paths([FIXTURES_DIR / fixture])

    [diagnostic] = excinfo.value.diagnostics
    assert diagnostic.code is code
    assert diagnostic.reference == reference
    assert diagnostic.source_file == "root-0/model.sysml"
    assert diagnostic.source_line == line
    assert diagnostic.detail == detail
    rendered = str(excinfo.value)
    assert reference in rendered
    assert f"root-0/model.sysml:{line}" in rendered
    assert rendered.count(code.value) == 1


def test_incomparable_definition_writers_refuse_without_electing_one() -> None:
    with pytest.raises(ElaborationInvariantError) as caught:
        _occurrences("occurrence_multiplicity_incomparable")

    assert caught.value.code is ElaborationCode.SI_REDEFINITION_INVALID
    # The refusal names every writer it could not order, so the modeller is told
    # which declarations to compare rather than only that a comparison failed.
    assert caught.value.detail == (
        "applicable definition writers have no unique most-specific owner: "
        "OccurrenceMultiplicityIncomparable::Left, "
        "OccurrenceMultiplicityIncomparable::Right, "
        "OccurrenceMultiplicityIncomparable::Root"
    )

    with pytest.raises(ElaborationDiagnosticError) as public:
        elaborate_model_paths(
            [FIXTURES_DIR / "occurrence_multiplicity_incomparable"]
        )
    [diagnostic] = public.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_REDEFINITION_INVALID
    assert diagnostic.detail == caught.value.detail
    assert diagnostic.reference == "count"
    assert diagnostic.source_file == "root-0/runtime.sysml"
    assert diagnostic.source_line == 8
    assert str(public.value).count("SI_REDEFINITION_INVALID") == 1


def test_multiple_exact_writers_in_one_owner_domain_refuse(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    extractor = SysMLDataExtractor(
        [FIXTURES_DIR / "elab_finite_expression_multiplicity"]
    )
    assert extractor.load_models()
    original = SysideAdapter.elements_of_type

    def duplicate_count(cls, model, type_name, **kwargs):
        del cls
        elements = list(original(model, type_name, **kwargs))
        if type_name == "AttributeUsage":
            count = next(
                item
                for item in elements
                if str(getattr(item, "qualified_name", None)).endswith("::host::count")
            )
            elements.append(count)
        return iter(elements)

    monkeypatch.setattr(
        SysideAdapter,
        "elements_of_type",
        classmethod(duplicate_count),
    )
    with pytest.raises(ElaborationInvariantError) as caught:
        build_occurrence_index(
            extractor.model,
            build_feature_slot_index(extractor.model),
        )

    assert caught.value.code is ElaborationCode.SI_MULTIPLICITY_UNRESOLVED
    assert caught.value.detail == (
        "upper multiplicity on 'cell' is not a known finite integer"
    )
