"""An empty attachment lookup explains itself, and an unmapped owner kind refuses.

Emptiness used to come back as one bare ``()`` for three structurally different reasons.
The disposition severity a constraint usage gets now keys on which reason it was, so the
lookup returns the cause beside the scopes and the owner-kind map refuses a kind it does
not know rather than grading it by accident.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration.diagnostics import ElaborationCode, ElaborationInvariantError
from sysml_codegen.elaboration.elaborate import _ExactElaborator
from sysml_codegen.elaboration.occurrence import semantic_owner
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import FIXTURES_DIR, requires_license


def _elaborator(fixture: str) -> _ExactElaborator:
    extractor = SysMLDataExtractor([Path(FIXTURES_DIR / fixture)])
    assert extractor.load_models()
    return _ExactElaborator(
        extractor.model, extractor.extract_calculation_definitions(), strict=True
    )


def _owner_named(model, qualified_name: str):
    for usage in SysideAdapter.elements_of_type(
        model, "ConstraintUsage", include_subtypes=True
    ):
        if str(getattr(usage, "qualified_name", None)) == qualified_name:
            return getattr(usage, "owning_type", None) or getattr(usage, "owner", None)
    raise AssertionError(f"no constraint usage named {qualified_name!r}")


class _UnmappedOwner:
    """Stands in for an owner metaclass nobody has graded yet."""

    qualified_name = "Somewhere::exotic"


class _FalseyCalculationDefinition:
    def __bool__(self) -> bool:
        return False


class _OwnedFeature:
    owning_type = _FalseyCalculationDefinition()
    owner = object()


class _DetachedFeature:
    owning_type = None
    owner = None


def test_semantic_owner_uses_presence_not_truthiness() -> None:
    feature = _OwnedFeature()
    assert semantic_owner(feature) is feature.owning_type


def test_semantic_owner_accepts_a_missing_owner() -> None:
    assert semantic_owner(_DetachedFeature()) is None


@requires_license
def test_attachment_reports_owner_absent_for_no_owner():
    assert _elaborator("constraint_domain_detached_owner")._attachment(None) == (
        (),
        "owner_absent",
    )


@requires_license
def test_attachment_reports_owner_kind_unattachable_for_a_calc_def():
    elaborator = _elaborator("constraint_domain_satisfy_calc_def")
    owner = _owner_named(
        elaborator._model, "constraint_domain_satisfy_calc_def::Sizer::budget_met"
    )
    assert elaborator._attachment(owner) == ((), "owner_kind_unattachable")


@requires_license
def test_attachment_reports_no_occurrences_for_an_uninstantiated_part_def():
    elaborator = _elaborator("constraint_domain_detached_owner")
    owner = _owner_named(
        elaborator._model, "constraint_domain_detached_owner::Detached::vacuous_gate"
    )
    assert elaborator._attachment(owner) == ((), "owner_has_no_occurrences")


@requires_license
def test_attachment_reports_no_cause_when_scopes_exist():
    elaborator = _elaborator("constraint_domain_detached_owner")
    owner = _owner_named(
        elaborator._model, "constraint_domain_detached_owner::Live::reached_gate"
    )
    scopes, cause = elaborator._attachment(owner)
    assert scopes
    assert cause is None


def test_unmapped_owner_kind_refuses_by_name():
    with pytest.raises(ElaborationInvariantError) as raised:
        _ExactElaborator._owner_kind(_UnmappedOwner())
    assert raised.value.code is ElaborationCode.SI_CONSTRAINT_UNATTACHED
    assert "_UnmappedOwner" in raised.value.detail
    assert "closed owner-kind map" in raised.value.detail


def test_mapped_owner_kinds_keep_their_graded_spellings():
    assert _ExactElaborator._owner_kind(None) == "absent"
