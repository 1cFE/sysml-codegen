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
from sysml_codegen.elaboration.elaborate import (
    _ExactElaborator,
    _UnsupportedExpressionError,
)
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

    Shape rather than name, and that limit is measured rather than assumed. Putting the leaf
    param name back into the row fails on these twins: the constraint module's identity
    parameter is `<package>_the_host_gap_guard_<hash>`, which embeds the package name with no
    `__` separator, so no leaf-split can normalize it across two differently-named packages.
    The edges themselves are identical — `(0, entry_point)`, `(1, module_output)`.
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
    """The asymmetry pin: twin wiring shape agrees, and the annotated value survives.

    What this observes, exactly: the two twins produce the same module-input wiring shape,
    and `gap_width [m] = 0.5` still reaches the entry point as `0.5`. The value half is the
    already-cured `_create_value_node` lane, not the lane D1 opened.

    What it does **not** observe, stated so nobody reads more into it: invariant 7 — that a
    `[` annotation's second operand is never a user-model feature. Both annotated sites in
    this fixture are inside `gap_guard`, and a constraint contributes no `PipelineModule`
    input, so an edge lost there would not change these rows. Invariant 7 holds
    *structurally*, not because this test would catch its violation: the second operand of
    `[` is a unit by construction, and no supported authoring shape produces anything else
    (design M6b). This test is the twin-agreement guard; the structural argument is the
    invariant's evidence.
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


def test_the_walk_refuses_a_malformed_annotation_and_the_refusal_is_not_downgradable() -> None:
    """M7, decided deliberately: one rule, one refusal — pinned in its two checkable halves.

    Half one, driven: the walk itself refuses. `_without_unit_annotation` turns a malformed
    annotation's `ValueError` into `ElaborationInvariantError(SI_EDGE_DANGLING)`, the same
    way `_create_value_node` already refuses it.

    Half two, typed: that error is not an `_UnsupportedExpressionError`, which is the only
    thing the computed/predicate caller catches (`_resolve_computed_expressions`), so the
    refusal escapes and becomes a hard elaboration failure rather than a readiness finding.

    The name says "the walk" rather than "a predicate" because no predicate is loaded here.
    An end-to-end fixture is not available: a `[` node carrying no annotated value is not
    authorable SysML — the parser will not produce one — so the malformed shape can only be
    reached by handing the walk a synthetic node. The route from the walk to a hard refusal
    is the type relationship asserted below, not a third thing left unchecked.
    """
    elaborator = _ExactElaborator.__new__(_ExactElaborator)
    with pytest.raises(ElaborationInvariantError) as refusal:
        elaborator._expression_references(_MalformedUnitAnnotation(), plural=False)
    assert refusal.value.code is ElaborationCode.SI_EDGE_DANGLING
    assert not isinstance(refusal.value, _UnsupportedExpressionError)
