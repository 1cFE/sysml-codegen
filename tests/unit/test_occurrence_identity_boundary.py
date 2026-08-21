"""Containment identity conversion catches only its declared typed boundary."""

from types import SimpleNamespace

import pytest

import sysml_codegen.elaboration.occurrence as occurrence
from sysml_codegen.elaboration.diagnostics import ElaborationCode
from sysml_codegen.elaboration.identity import IdentityBoundaryError


@pytest.fixture
def part_usage(monkeypatch: pytest.MonkeyPatch) -> object:
    element = SimpleNamespace(owner=None)
    monkeypatch.setattr(
        occurrence.SysideAdapter,
        "is_instance",
        staticmethod(lambda candidate, kind: candidate is element and kind == "PartUsage"),
    )
    return element


def test_containment_identity_boundary_preserves_typed_code_and_cause(
    monkeypatch: pytest.MonkeyPatch,
    part_usage: object,
) -> None:
    identity_error = IdentityBoundaryError("declaration identity changed")
    monkeypatch.setattr(
        occurrence,
        "declaration_id_for",
        lambda _element: (_ for _ in ()).throw(identity_error),
    )

    with pytest.raises(occurrence.OccurrenceResolutionError) as caught:
        occurrence.build_containment_address(part_usage, SimpleNamespace())

    assert caught.value.code is ElaborationCode.SI_ID_UNSTABLE
    assert caught.value.detail == identity_error.detail
    assert caught.value.__cause__ is identity_error


def test_containment_identity_boundary_does_not_hide_unrelated_defects(
    monkeypatch: pytest.MonkeyPatch,
    part_usage: object,
) -> None:
    defect = RuntimeError("adapter defect")
    monkeypatch.setattr(
        occurrence,
        "declaration_id_for",
        lambda _element: (_ for _ in ()).throw(defect),
    )

    with pytest.raises(RuntimeError, match="adapter defect") as caught:
        occurrence.build_containment_address(part_usage, SimpleNamespace())

    assert caught.value is defect
