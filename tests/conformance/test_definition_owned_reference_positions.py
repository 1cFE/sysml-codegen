"""Definition-owned qualified references resolve only on the consumer lineage (D-6).

These four fixtures pin the surviving ``_resolve_leaf`` route for a leaf owned
by a *definition* — the owner class the exact usage-owner anchoring repair
(`98970c9`) deliberately did not change:

* inside the definition, two occurrences → generates, each occurrence reads its
  own value (spike row 4b);
* above the definition, one or two occurrences below the consumer → refused,
  ``SI_OCCURRENCE_MISSING``;
* no local occurrence, one in a sibling subtree → refused,
  ``SI_OCCURRENCE_MISSING`` (spike row 6 / F-4).

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
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.elaboration_graph import attr, calc, inputs_by_name, node_ref
from tests.helpers.raw_elaboration import elaborate

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


@pytest.mark.parametrize(
    ("fixture", "consumer_qn"),
    [
        ("def_qual_one_occ_above", "def_qual_one_occ_above__fleet__revenue_calc"),
        ("def_qual_two_occ_above", "def_qual_two_occ_above__fleet__revenue_calc"),
        ("def_qual_sibling_scope", "def_qual_sibling_scope__plant__block__cost_calc"),
    ],
)
def test_definition_owned_lineage_miss_refuses_without_descendant_search(
    fixture: str, consumer_qn: str
) -> None:
    """Descendant count and position cannot invent an occurrence for the leaf."""
    with pytest.raises(ElaborationDiagnosticError) as excinfo:
        _elaborate_fixture(fixture)
    codes = Counter(diagnostic.code for diagnostic in excinfo.value.diagnostics)
    assert codes == Counter({ElaborationCode.SI_OCCURRENCE_MISSING: 1})
    [diagnostic] = excinfo.value.diagnostics
    assert diagnostic.detail.startswith(
        "consumer lineage has no occurrence of definition-owned leaf slot"
    )

    lenient = _elaborate_fixture(fixture, strict=False)
    consumer = calc(lenient, consumer_qn)
    assert consumer.inputs == {}
