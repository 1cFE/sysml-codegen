"""Defect A: a unit annotation inside an inline asserted predicate.

The unit-annotation rule — *a unit annotation contributes its value and never a
reference* (`extraction/unit_annotation.py`) — reached attribute values and calc-def
defaults and stopped there. A predicate's expression takes a different route: an inline
asserted usage pushes its `result_expression` into `_pending_expressions`
(`elaborate.py:1112-1117`) and `_expression_references` (`elaborate.py:2371`) recurses
into every operand, including the `[` annotation's second operand, which is `SI::metre`.
`FeatureSlotIndex` holds only the user model's features, so the walk raised
`SI_OCCURRENCE_MISSING` against a unit.

This is the third lane of a class already cured twice, kept pinned by
`test_unit_annotation_values.py`. The end state pinned here is a gate that *works* —
admitted, catalogued, assessed — not the absence of one error code.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from sysml_codegen.elaboration.diagnostics import ElaborationCode, ElaborationInvariantError
from sysml_codegen.elaboration.elaborate import _ExactElaborator
from sysml_codegen.generation.coverage import coverage_account
from sysml_codegen.orchestration.elaborated_pipeline import (
    build_elaborated_pipeline,
    elaborate_model_paths,
)
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

ANNOTATED = FIXTURES_DIR / "predicate_unit_annotation"
BARE = FIXTURES_DIR / "predicate_unit_annotation_bare"
INCOMPATIBLE = FIXTURES_DIR / "predicate_unit_annotation_incompatible"

def _gap_guard_row(fixture: Path) -> Any:
    catalog = build_elaborated_pipeline([fixture]).constraint_catalog
    assert catalog is not None
    [row] = [
        record
        for record in catalog.usage_records
        if record.usage_qualified_name.endswith("gap_guard")
    ]
    return row


def _entry_point_values(fixture: Path) -> dict[str, float | int | str | bool | None]:
    graph = build_elaborated_pipeline([fixture])
    return {
        parameter.qualified_name.rsplit("__", 1)[-1]: parameter.default_value
        for group in graph.entry_point_groups
        for parameter in group.parameters
    }


def _input_wiring(fixture: Path) -> list[tuple[int, str]]:
    """One row per module input: which module it feeds, and what kind of source feeds it.

    Compared across twins by shape rather than by name, because the identifiers carry the
    package name and the two fixtures are two packages.
    """
    graph = build_elaborated_pipeline([fixture])
    return [
        (index, module_input.source.source_type)
        for index, module in enumerate(graph.modules)
        for module_input in module.inputs
    ]


def test_an_asserted_predicate_carrying_a_unit_annotation_elaborates() -> None:
    """Today: `SI_OCCURRENCE_MISSING: leaf declaration <uuid> has no feature slot`."""
    graph = elaborate_model_paths([ANNOTATED])
    assert graph.constraint_usages


def test_the_cured_predicate_is_a_working_gate() -> None:
    """The positive end state: a carrier, an assessed disposition, and a coverage count."""
    row = _gap_guard_row(ANNOTATED)
    assert row.disposition_kind == "eligible"
    assert row.disposition_reason == "admitted"

    catalog = build_elaborated_pipeline([ANNOTATED]).constraint_catalog
    assert catalog is not None
    account = coverage_account(catalog)
    assert account.assessed_gate_count == 1
    assert account.unassessed_gate_count == 0


def test_the_unit_is_not_resolved_as_a_reference() -> None:
    """The defect's signature, checked the way the cured lanes check it.

    Follows `test_unit_annotation_values.py:53-60`: no SI library element may appear
    anywhere as a graph dependency.
    """
    graph = build_elaborated_pipeline([ANNOTATED])
    for module in graph.modules:
        for module_input in module.inputs:
            assert "SI::" not in (module_input.source.qualified_name or "")
            assert "SI::" not in (module_input.source.producer_channel or "")


def test_the_annotated_and_bare_twins_wire_up_identically() -> None:
    """Invariant 7: unwrapping the annotation drops no real dependency edge.

    The asymmetry pin, mirroring `test_unit_annotation_values.py`. If the `[` second
    operand ever resolved to a user-model feature rather than a library element, the
    annotated twin would come up an edge short here.
    """
    assert _input_wiring(ANNOTATED) == _input_wiring(BARE)
    assert _entry_point_values(ANNOTATED) == _entry_point_values(BARE) == {"gap_width": 0.5}


def test_an_incompatible_annotation_still_blocks_on_a_dimension_reason() -> None:
    """Invariant 2, as a regression guard on the companion path.

    Not a discriminator for the codegen fix (design review A1): the profile's verdict is
    computed at `elaborate.py:403` from the companion's own extraction, before and
    independent of the reference walk. It would pass either way — which is the point.
    Carried, never applied: the unit must still be *a unit* to the profile after codegen
    stops reading it as a reference.
    """
    with pytest.raises(Exception, match="block_incompatible_dimensions"):
        elaborate_model_paths([INCOMPATIBLE])


class _MalformedUnitAnnotation:
    """A `[` node carrying no annotated value — the shape `annotated_ast_value` refuses."""

    operator = "["
    operands: tuple[Any, ...] = ()


#: `SysideAdapter.is_instance` falls back to matching `type(elem).__name__` for an element
#: that is not a live syside object, so the class reports the type it stands in for.
_MalformedUnitAnnotation.__name__ = "OperatorExpression"


def test_a_malformed_annotation_in_a_predicate_hard_refuses() -> None:
    """M7, decided deliberately: one rule, one refusal.

    Inside the walk, `_without_unit_annotation` turns a malformed annotation's
    `ValueError` into `ElaborationInvariantError(SI_EDGE_DANGLING)`. That is *not* an
    `_UnsupportedExpressionError`, so it escapes the catch at `elaborate.py:2286-2295`
    and hard-refuses, exactly as `_create_value_node` already refuses it at `:757`.
    """
    elaborator = _ExactElaborator.__new__(_ExactElaborator)
    with pytest.raises(ElaborationInvariantError) as refusal:
        elaborator._expression_references(_MalformedUnitAnnotation(), plural=False)
    assert refusal.value.code is ElaborationCode.SI_EDGE_DANGLING
