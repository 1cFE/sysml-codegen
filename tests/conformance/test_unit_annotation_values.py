"""A unit annotation contributes its value, in both spellings, and never a reference.

The exact route used to accept `default 40.0 [W]` on a calc-def formal and refuse
`= 0.5 [m]` on an attribute value, with `SI_OCCURRENCE_MISSING` naming `SI::metre`. The unit
reached the reference walk, and `FeatureSlotIndex` indexes only the user model's features, so
a standard-library element had no slot. That asymmetry was a defect, not a policy: it is the
same category error Slice 3D fixed for enumeration members, where a reference that names
something other than a data source has no occurrence to resolve against.

These pin the cure from both ends — the annotated spelling resolves, and the two spellings
resolve *identically* — so the asymmetry cannot come back silently. Before the fix the first
test here was red against the same fixture.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

ANNOTATED = FIXTURES_DIR / "unit_annotation_lanes"
BARE = FIXTURES_DIR / "unit_annotation_lanes_bare"


def _entry_point_values(fixture: Path) -> dict[str, float]:
    graph = build_elaborated_pipeline([fixture])
    return {
        parameter.qualified_name.rsplit("__", 1)[-1]: parameter.default_value
        for group in graph.entry_point_groups
        for parameter in group.parameters
    }


def test_an_attribute_value_carrying_a_unit_annotation_resolves() -> None:
    """`attribute thickness : Real = 0.5 [m];` — the spelling that used to refuse."""
    assert _entry_point_values(ANNOTATED)["thickness"] == 0.5


def test_a_calc_def_default_carrying_a_unit_annotation_still_resolves() -> None:
    """`in attribute rated_power : Real default 40.0 [W];` — the spelling that always did."""
    assert _entry_point_values(ANNOTATED)["rated_power"] == 40.0


def test_both_spellings_resolve_to_the_same_values_as_the_unannotated_model() -> None:
    """The asymmetry pin. One rule, so annotated and bare must agree everywhere."""
    assert _entry_point_values(ANNOTATED) == _entry_point_values(BARE)


def test_the_unit_is_not_resolved_as_a_reference() -> None:
    """The defect's signature: no SI library element may appear as a graph dependency."""
    graph = build_elaborated_pipeline([ANNOTATED])
    for module in graph.modules:
        for module_input in module.inputs:
            assert "SI::" not in (module_input.source.qualified_name or "")
            assert "SI::" not in (module_input.source.producer_channel or "")


@pytest.mark.parametrize("fixture", [ANNOTATED, BARE])
def test_the_model_still_computes_what_it_says(fixture: Path) -> None:
    """0.5 × 40.0 = 20.0, read off the model by hand rather than from a route."""
    graph = build_elaborated_pipeline([fixture])
    values = _entry_point_values(fixture)
    assert values["thickness"] * values["rated_power"] == 20.0
    figure = [
        expression
        for module in graph.modules
        for expression in module.calc_expressions
        if expression.startswith("figure =")
    ]
    assert figure == ["figure = thickness * rated_power"]
