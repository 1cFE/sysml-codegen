"""Shadowing + equal-valued literal identity through the elaborator (Item 5 Phase 2, leg 7).

The capability survey's evidence gap: no shadowing/specialization *referent*
fixtures existed. ``elab_shadowing_probe`` (authored this leg) closes it with
two shapes; ``shadowed_reference`` (audit F2's fixture) pins the scope-shadow
case. Authoring note baked into the fixture: an overridable default chain needs
``default`` at every level — SysIDE rejects ``:>>`` over a bound (``=``) value
(``feature-value-overriding``).

Findings: ``.project/research/20260807-174301_elaborator-shadowing-literals.md``.
All tests require a live SysIDE license.
"""

from __future__ import annotations

import pytest

from sysml_codegen.elaboration import (
    InstanceGraph,
    ValueSite,
    elaborate,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.elaboration_graph import attr, calc, node_ref

pytestmark = requires_license

PKG = "ElabShadowingProbe"


@pytest.fixture(scope="module")
def graph_cache():
    cache: dict[str, InstanceGraph] = {}

    def get(name: str) -> InstanceGraph:
        if name not in cache:
            extractor = SysMLDataExtractor([FIXTURES_DIR / name])
            assert extractor.load_models(), f"fixture {name} failed to load"
            cache[name] = elaborate(
                extractor.model,
                extractor.extract_calculation_definitions(),
                validation_diagnostics=extractor.diagnostics.validation,
            )
        return cache[name]

    return get


def test_innermost_definition_wins_per_occurrence(graph_cache) -> None:
    """Two-level specialized-def shadowing: Leaf's ``:>> rate = 9.0`` outranks
    Mid's ``default 5.0`` at a Leaf occurrence, while a Mid occurrence keeps
    5.0 — specificity ordering, never redefinition list order."""
    graph = graph_cache("elab_shadowing_probe")
    leaf = attr(graph, f"{PKG}__the_leaf__rate")
    assert (leaf.value, leaf.value_site) == (9.0, ValueSite.SPECIALIZED_DEF)
    mid = attr(graph, f"{PKG}__the_mid__rate")
    assert (mid.value, mid.value_site) == (5.0, ValueSite.SPECIALIZED_DEF)
    assert graph.diagnostics == []


def test_base_authored_consumer_reads_the_occurrence_value(graph_cache) -> None:
    """The consumer declared on BASE reads each occurrence's own node — the
    Leaf occurrence's 9.0, the Mid occurrence's 5.0, one node each."""
    graph = graph_cache("elab_shadowing_probe")
    leaf_calc = calc(graph, f"{PKG}__the_leaf__base_calc")
    assert leaf_calc.input_by_name("v") == node_ref(graph, f"{PKG}__the_leaf__rate")
    mid_calc = calc(graph, f"{PKG}__the_mid__base_calc")
    assert mid_calc.input_by_name("v") == node_ref(graph, f"{PKG}__the_mid__rate")


def test_equal_valued_independent_literals_stay_distinct(graph_cache) -> None:
    """The ratified 2026-08-05 rule: distinct occurrences are distinct sources
    even when the overridden values coincide (both 4.0) — two nodes, each
    consumer wired to its own."""
    graph = graph_cache("elab_shadowing_probe")
    t1 = attr(graph, f"{PKG}__t1__x")
    t2 = attr(graph, f"{PKG}__t2__x")
    assert t1.node_id != t2.node_id
    assert (t1.value, t2.value) == (4.0, 4.0)
    assert t1.value_site is ValueSite.OCCURRENCE_OVERRIDE
    assert t2.value_site is ValueSite.OCCURRENCE_OVERRIDE
    assert calc(graph, f"{PKG}__t1__thing_calc").input_by_name("v") == node_ref(
        graph, f"{PKG}__t1__x"
    )
    assert calc(graph, f"{PKG}__t2__thing_calc").input_by_name("v") == node_ref(
        graph, f"{PKG}__t2__x"
    )


def test_qualified_reference_never_selects_the_scope_shadow(graph_cache) -> None:
    """shadowed_reference (audit F2): the ``::``-qualified reference to the
    outer 2.0 attribute resolves to the OUTER node — the same-named 7.0 shadow
    on the consumer's own owner is never selected."""
    graph = graph_cache("shadowed_reference")
    calculation = calc(graph, "ShadowedReference__the_outer__inner__shadowed_calc")
    assert calculation.input_by_name("factor") == node_ref(
        graph, "ShadowedReference__the_outer__scale"
    )
    assert attr(graph, "ShadowedReference__the_outer__scale").value == 2.0
    assert attr(graph, "ShadowedReference__the_outer__inner__scale").value == 7.0
    assert graph.diagnostics == []
