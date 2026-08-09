"""Exact containment-slot occurrence-walker contracts."""

from __future__ import annotations

from typing import Any
from uuid import UUID

import pytest
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration import ElaborationCode, ElaborationDiagnosticError, elaborate
from sysml_codegen.elaboration.identity import DeclarationId, OccurrenceId
from sysml_codegen.elaboration.occurrence import (
    FeatureSlotIndex,
    InvalidRedefinitionFamilyError,
    OccurrenceIndex,
    build_feature_slot_index,
    build_occurrence_index,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license


def _load(name: str) -> Any:
    model, diagnostics = SysideAdapter.load_model([FIXTURES_DIR / name])
    errors = [
        diagnostic for diagnostic in diagnostics.all if str(diagnostic.severity).endswith("Error")
    ]
    assert not errors, errors
    return model


def _by_qn(model: Any, type_name: str, qualified_name: str) -> Any:
    return next(
        element
        for element in SysideAdapter.elements_of_type(model, type_name)
        if str(getattr(element, "qualified_name", None)) == qualified_name
    )


def test_authored_and_implied_redefinitions_share_endpoint_root_slots() -> None:
    model = _load("spec_chain_twolevel")
    slots = build_feature_slot_index(model)
    base_driver = _by_qn(model, "PartUsage", "TwoLevelLib::'IFE Power Plant'::driver")
    retyped_driver = _by_qn(model, "PartUsage", "TwoLevelDesign::hif_plant::driver")
    base_id = DeclarationId(SysideAdapter.element_id(base_driver))
    retyped_id = DeclarationId(SysideAdapter.element_id(retyped_driver))
    assert slots.slot_of(base_id) == slots.slot_of(retyped_id)

    implied_param = _by_qn(
        model,
        "ReferenceUsage",
        "TwoLevelLib::'IFE Driver'::meier_cost::drive_power",
    )
    implied_edge = next(iter(implied_param.owned_redefinitions))
    formal_id = DeclarationId(SysideAdapter.element_id(implied_edge.redefined_feature))
    implied_id = DeclarationId(SysideAdapter.element_id(implied_param))
    assert slots.slot_of(formal_id) == slots.slot_of(implied_id)


def test_occurrence_ids_use_slots_and_indices_not_rendered_paths() -> None:
    model = _load("spec_chain_twolevel")
    slots = build_feature_slot_index(model)
    occurrences = build_occurrence_index(model, slots)
    driver = _by_qn(model, "PartUsage", "TwoLevelDesign::hif_plant::driver")
    driver_id = DeclarationId(SysideAdapter.element_id(driver))
    matches = occurrences.occurrences_for_declaration(driver_id)

    assert len(matches) == 1
    occurrence = matches[0]
    assert isinstance(occurrence.occurrence_id, OccurrenceId)
    assert all(step.containment_slot for step in occurrence.occurrence_id.steps)
    assert occurrence.display_path == "TwoLevelDesign__hif_plant__driver"


def test_occurrence_identity_is_stable_across_independent_loads() -> None:
    first_model = _load("source_identity_mixed_consumers")
    second_model = _load("source_identity_mixed_consumers")
    first = build_occurrence_index(first_model, build_feature_slot_index(first_model))
    second = build_occurrence_index(second_model, build_feature_slot_index(second_model))
    assert first.occurrence_ids() == second.occurrence_ids()


def test_definition_specificity_uses_subtype_order_not_closure_size() -> None:
    base = DeclarationId(UUID(int=1))
    short_branch = DeclarationId(UUID(int=2))
    long_parent = DeclarationId(UUID(int=3))
    long_branch = DeclarationId(UUID(int=4))
    index = OccurrenceIndex(
        {},
        FeatureSlotIndex(set(), {}),
        {
            base: frozenset({base}),
            short_branch: frozenset({short_branch, base}),
            long_parent: frozenset({long_parent, base}),
            long_branch: frozenset({long_branch, long_parent, base}),
        },
    )

    with pytest.raises(InvalidRedefinitionFamilyError):
        index.most_specific_definition({short_branch, long_branch})


def test_definition_specificity_selects_the_actual_subtype() -> None:
    base = DeclarationId(UUID(int=10))
    middle = DeclarationId(UUID(int=11))
    leaf = DeclarationId(UUID(int=12))
    index = OccurrenceIndex(
        {},
        FeatureSlotIndex(set(), {}),
        {
            base: frozenset({base}),
            middle: frozenset({middle, base}),
            leaf: frozenset({leaf, middle, base}),
        },
    )

    assert index.most_specific_definition({base, middle, leaf}) == leaf


def test_finite_constant_integer_expression_expands_occurrences() -> None:
    model = _load("elab_finite_expression_multiplicity")
    occurrences = build_occurrence_index(model, build_feature_slot_index(model))

    cells = [
        occurrence
        for occurrence in occurrences.occurrences()
        if "__cell[" in occurrence.display_path
    ]
    assert {occurrence.display_path for occurrence in cells} == {
        f"ElabFiniteExpressionMultiplicity__host__cell[{index}]" for index in range(4)
    }


@pytest.mark.parametrize(
    ("fixture", "expected_code"),
    [
        ("elab_unresolved_multiplicity", ElaborationCode.SI_MULTIPLICITY_UNRESOLVED),
        (
            "constraint_occurrence_demand/cycle",
            ElaborationCode.SI_CONTAINMENT_RECURSIVE,
        ),
    ],
)
def test_occurrence_expansion_failures_use_structured_diagnostics(
    fixture: str, expected_code: ElaborationCode
) -> None:
    extractor = SysMLDataExtractor([FIXTURES_DIR / fixture])
    assert extractor.load_models()

    with pytest.raises(ElaborationDiagnosticError) as excinfo:
        elaborate(
            extractor.model,
            extractor.extract_calculation_definitions(),
            validation_diagnostics=extractor.diagnostics.validation,
        )

    assert [diagnostic.code for diagnostic in excinfo.value.diagnostics] == [expected_code]
