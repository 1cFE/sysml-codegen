"""Definition-owned qualified references: outcome by consumer position (D-6).

These three fixtures pin the surviving ``_resolve_leaf`` route for a leaf owned
by a *definition* — the owner class the exact usage-owner anchoring repair
(`98970c9`) deliberately did not change. The discriminator is the consumer's
position relative to the qualifying definition's occurrences, not the
occurrence count:

* inside the definition, two occurrences → generates, each occurrence reads its
  own value (spike row 4b);
* above the definition, two occurrences below the consumer → refused,
  ``SI_OCCURRENCE_AMBIGUOUS`` (spike row 4d);
* no local occurrence, one in a sibling subtree → generates by positional
  fallback, silently crossing a containment boundary (spike row 6 / F-4).

Every claim the published guidance makes about this owner class cites these
fixtures. All tests require a live SysIDE license.
"""

from __future__ import annotations

from collections import Counter

import pytest

from sysml_codegen.elaboration import (
    ElaborationCode,
    ElaborationDiagnosticError,
    InstanceGraph,
    elaborate,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.elaboration_graph import attr, calc, inputs_by_name, node_ref

pytestmark = requires_license


def _elaborate_fixture(name: str, strict: bool = True) -> InstanceGraph:
    extractor = SysMLDataExtractor([FIXTURES_DIR / name])
    assert extractor.load_models(), f"fixture {name} failed to load"
    return elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
        strict=strict,
    )


def test_inside_the_definition_each_occurrence_reads_its_own_value() -> None:
    """Two occurrences are not ambiguous when the consumer sits inside them:
    the consumer's own scope lineage owns the slot, so each occurrence's calc
    binds its own attribute — a wrong pick would be visible as a crossed value."""
    graph = _elaborate_fixture("def_qual_two_occ_inside")
    assert graph.diagnostics == []

    pkg = "def_qual_two_occ_inside"
    for occurrence, value in (("plant_a", 0.11), ("plant_b", 0.99)):
        consumer = calc(graph, f"{pkg}__{occurrence}__revenue_calc")
        target = f"{pkg}__{occurrence}__availability"
        assert inputs_by_name(consumer)["availability"] == node_ref(graph, target)
        assert attr(graph, target).value == value


def test_above_the_definition_two_occurrences_refuse_as_ambiguous() -> None:
    """The consumer sits outside every occurrence with two reachable below its
    anchor: strict elaboration refuses with SI_OCCURRENCE_AMBIGUOUS rather than
    guessing, and the lenient graph leaves the consumer unbound."""
    with pytest.raises(ElaborationDiagnosticError) as excinfo:
        _elaborate_fixture("def_qual_two_occ_above")
    codes = Counter(diagnostic.code for diagnostic in excinfo.value.diagnostics)
    assert codes == Counter({ElaborationCode.SI_OCCURRENCE_AMBIGUOUS: 1})

    lenient = _elaborate_fixture("def_qual_two_occ_above", strict=False)
    consumer = calc(lenient, "def_qual_two_occ_above__fleet__revenue_calc")
    assert consumer.inputs == {}


def test_sibling_scope_resolves_sideways_by_positional_fallback() -> None:
    """The single sibling occurrence is selected and 7.0 arrives. This is the
    positional fallback — lineage miss, then a descendant search from each
    lineage anchor — not checked author intent: the route cannot know the
    author meant the sibling, and the guidance must say so (F-4)."""
    graph = _elaborate_fixture("def_qual_sibling_scope")
    assert graph.diagnostics == []

    pkg = "def_qual_sibling_scope"
    consumer = calc(graph, f"{pkg}__plant__block__cost_calc")
    target = f"{pkg}__plant__bop__the_unit__cost"
    assert inputs_by_name(consumer)["unit_cost"] == node_ref(graph, target)
    assert attr(graph, target).value == 7.0
