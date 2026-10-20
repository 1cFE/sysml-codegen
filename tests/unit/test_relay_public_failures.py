"""The one relay rule the construction steps share (Item 2b audit fix 6).

``relay_public_failures`` lets a formed public refusal through as itself, and turns any other
failure into the internal-defect diagnostic, with the original failure as its cause.
"""

from __future__ import annotations

import pytest

from sysml_codegen.core.errors import CodeGenerationError, GenerationCode, SysMLParsingError
from sysml_codegen.elaboration.diagnostics import ElaborationCode
from sysml_codegen.elaboration.elaborate import (
    ElaborationDiagnosticError,
    ElaborationError,
    relay_public_failures,
    unexpected_public_failure,
)
from sysml_codegen.snapshot.envelope import InstanceGraphSnapshotError


@pytest.mark.parametrize(
    "error",
    [
        CodeGenerationError("probe", code=GenerationCode.MODULE_KIND_UNRENDERABLE),
        ElaborationError(()),
        SysMLParsingError("probe"),
        unexpected_public_failure(RuntimeError("probe")),
    ],
    ids=lambda e: type(e).__name__,
)
def test_a_public_refusal_passes_through_as_itself(error):
    with pytest.raises(type(error)) as raised, relay_public_failures():
        raise error
    assert raised.value is error


def test_any_other_failure_becomes_the_internal_defect():
    cause = KeyError("probe")
    with pytest.raises(ElaborationDiagnosticError) as raised, relay_public_failures():
        raise cause
    [diagnostic] = raised.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_INTERNAL_DEFECT
    assert raised.value.__cause__ is cause


def test_a_step_can_name_its_own_public_refusal():
    error = InstanceGraphSnapshotError("probe")
    with pytest.raises(ElaborationDiagnosticError), relay_public_failures():
        raise error
    with pytest.raises(InstanceGraphSnapshotError) as raised:
        with relay_public_failures(InstanceGraphSnapshotError):
            raise error
    assert raised.value is error


def test_nothing_raised_means_nothing_relayed():
    with relay_public_failures():
        value = 1
    assert value == 1
