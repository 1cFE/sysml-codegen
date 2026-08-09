"""Spike-parity conformance for the production elaborator (ELABORATE-FIRST Item 5, Phase 1).

Ports the Item-3 spike probes 1, 2, and 4 (``.project/active/elaborator-spike/``)
as kept tests against ``sysml_codegen.elaboration``. Spike parity is the Phase-1
gate: the customer collapse (C25), twin distinctness (C8), the producer edge
(C24), contextualization per referent class (C12/C13/C15), the stamp-route and
authored-literal split, the chain + constraint convergence (C11), the deep-path
override, the C19 fixture the string pipeline cannot fix, the fusion_tea
self-binding hard failure, Bank multiplicity nodes, and node-ID stability.

Cell keys map to the ratified contract's Appendix C
(``.project/concepts/constraint-execution-authoritative-lifecycle-contract.md``);
expected values are the SysIDE oracle's answers pinned by the spike
(``.project/active/elaborator-spike/findings.md``).

All tests require a live SysIDE license.
"""

from __future__ import annotations

from typing import Any

import pytest

from sysml_codegen.elaboration import (
    ElaborationError,
    InstanceGraph,
    LiteralInput,
    ValueSite,
    elaborate,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.source_evidence import ReadinessCode
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.elaboration_graph import (
    attr,
    calc,
    constraint,
    node_ref,
    producer_ref,
)

pytestmark = requires_license

PKG = "source_identity_mixed_consumers"


def _elaborate_fixture(name: str) -> InstanceGraph:
    extractor = SysMLDataExtractor([FIXTURES_DIR / name])
    assert extractor.load_models(), f"fixture {name} failed to load"
    calc_defs = extractor.extract_calculation_definitions()
    return elaborate(
        extractor.model,
        calc_defs,
        validation_diagnostics=extractor.diagnostics.validation,
    )


@pytest.fixture(scope="module")
def graph_cache():
    """Elaborate each fixture once per module."""
    cache: dict[str, InstanceGraph] = {}

    def get(name: str) -> InstanceGraph:
        if name not in cache:
            cache[name] = _elaborate_fixture(name)
        return cache[name]

    return get


@pytest.fixture(scope="module")
def mixed(graph_cache) -> InstanceGraph:
    return graph_cache(PKG)


def _calc_input(graph: InstanceGraph, node_id: str, param: str) -> Any:
    return calc(graph, node_id).input_by_name(param)


def _constraint_input(graph: InstanceGraph, node_id: str, param: str) -> Any:
    return constraint(graph, node_id).input_by_name(param)


# ---------------------------------------------------------------------------
# Probe 1: product-behavior checks on source_identity_mixed_consumers
# ---------------------------------------------------------------------------


def test_c25_two_binding_contexts_one_node(mixed: InstanceGraph) -> None:
    """The customer shape: a def-authored and a usage-authored consumer of one
    modeled value — different binding contexts, different referent classes —
    converge on the SAME occurrence node."""
    avail_node = f"{PKG}__avail_ctx__avail_plant__availability"
    def_authored = _calc_input(
        mixed, f"{PKG}__avail_ctx__avail_plant__def_authored_calc", "value_in"
    )
    usage_authored = _calc_input(
        mixed, f"{PKG}__avail_ctx__avail_plant__usage_authored_calc", "value_in"
    )
    assert def_authored == node_ref(mixed, avail_node)
    assert usage_authored == node_ref(mixed, avail_node)

    node = attr(mixed, avail_node)
    assert node.value == 0.8
    assert node.value_site is ValueSite.OCCURRENCE_OVERRIDE


def test_c25_exactly_two_consumers_share_the_node(mixed: InstanceGraph) -> None:
    avail_node = f"{PKG}__avail_ctx__avail_plant__availability"
    consumers = [
        (calc_id, param)
        for calc_id, calc in mixed.calcs.items()
        for param, ref in calc.inputs.items()
        if ref == node_ref(mixed, avail_node)
    ]
    assert len(consumers) == 2, consumers


def test_c8_twin_occurrences_stay_distinct(mixed: InstanceGraph) -> None:
    ref_a = _calc_input(mixed, f"{PKG}__twin_bay__calc_a", "value_in")
    ref_b = _calc_input(mixed, f"{PKG}__twin_bay__calc_b", "value_in")
    assert ref_a == node_ref(mixed, f"{PKG}__twin_bay__sensor_a__reading")
    assert ref_b == node_ref(mixed, f"{PKG}__twin_bay__sensor_b__reading")
    assert attr(mixed, f"{PKG}__twin_bay__sensor_a__reading").value == 11.0
    assert attr(mixed, f"{PKG}__twin_bay__sensor_b__reading").value == 22.0


def test_c24_chain_to_computed_value_is_a_producer_edge(
    mixed: InstanceGraph,
) -> None:
    """A chain to a calc output becomes a producer-output edge — never a minted
    public input."""
    ref = _calc_input(mixed, f"{PKG}__computed_station__computed_calc", "value_in")
    assert ref == producer_ref(
        mixed,
        f"{PKG}__computed_station__source_identity_computed__producer_calc",
        "result",
    )


def test_c12_qualified_reference_contextualizes(mixed: InstanceGraph) -> None:
    ref = _calc_input(mixed, f"{PKG}__qual_station__qual_plant__qual_calc", "value_in")
    assert ref == node_ref(mixed, f"{PKG}__qual_station__qual_plant__level")
    assert attr(mixed, f"{PKG}__qual_station__qual_plant__level").value == 70.0


def test_c13_bare_renamed_reference_contextualizes(mixed: InstanceGraph) -> None:
    ref = _calc_input(mixed, f"{PKG}__bare_station__bare_rig__bare_calc", "value_in")
    assert ref == node_ref(mixed, f"{PKG}__bare_station__bare_rig__intensity")
    assert attr(mixed, f"{PKG}__bare_station__bare_rig__intensity").value == 30.0


def test_c15_cross_owner_reference_reaches_parent_node(
    mixed: InstanceGraph,
) -> None:
    ref = _calc_input(mixed, f"{PKG}__parent_unit__child__child_calc", "value_in")
    assert ref == node_ref(mixed, f"{PKG}__parent_unit__shared_rate")
    assert attr(mixed, f"{PKG}__parent_unit__shared_rate").value == 40.0


def test_stamp_route_stays_a_node_reference(mixed: InstanceGraph) -> None:
    """The binding the legacy VBR literal-stamps stays a node reference here —
    no literal identity theft."""
    ref = _calc_input(mixed, f"{PKG}__stamp_plant__stamp_calc", "value_in")
    assert ref == node_ref(mixed, f"{PKG}__stamp_plant__efficiency")
    assert attr(mixed, f"{PKG}__stamp_plant__efficiency").value == 0.75


def test_authored_literal_stays_a_literal(mixed: InstanceGraph) -> None:
    ref = _calc_input(mixed, f"{PKG}__stamp_plant__lit_calc", "value_in")
    assert ref == LiteralInput(9.5)


def test_c11_chain_calc_and_constraint_converge(mixed: InstanceGraph) -> None:
    """The calc chain and the constraint actual read the SAME rig node."""
    rig_node = f"{PKG}__station__rig__gain_setting"
    calc_ref = _calc_input(mixed, f"{PKG}__station__chain_calc", "value_in")
    guard_ref = _constraint_input(mixed, f"{PKG}__station__chain_guard", "v")
    assert calc_ref == node_ref(mixed, rig_node)
    assert guard_ref == node_ref(mixed, rig_node)
    assert attr(mixed, rig_node).value == 42.0


def test_deep_path_override_lands_on_nested_occurrence(
    mixed: InstanceGraph,
) -> None:
    node = attr(mixed, f"{PKG}__deep_design__panel_two__deep_rig__gain_setting")
    assert node.value == 43.0
    assert node.value_site is ValueSite.OCCURRENCE_OVERRIDE


def test_bank_multiplicity_yields_per_cell_nodes(mixed: InstanceGraph) -> None:
    cells = [attr(mixed, f"{PKG}__bank__cell[{i}]__cell_cost") for i in range(3)]
    assert all(cell.value == 6.0 for cell in cells), [cell.value for cell in cells]


def test_mixed_consumers_elaborates_clean(mixed: InstanceGraph) -> None:
    assert mixed.diagnostics == []


# ---------------------------------------------------------------------------
# Probe 2: C19 + fusion_tea self-binding
# ---------------------------------------------------------------------------

C19_PKG = "nested_occurrence_override_probe"


def test_c19_deep_path_override_reaches_both_consumers(graph_cache) -> None:
    """The fixture the string pipeline cannot fix: the def-relative deep-path
    ``:>> source.reading = 80.0`` lands on the occurrence node, and BOTH the
    calc and the constraint consumer read that node."""
    graph = graph_cache(C19_PKG)
    target = f"{C19_PKG}__the_design__panel__source__reading"

    node = attr(graph, target)
    assert node.value == 80.0
    assert node.value_site is ValueSite.OCCURRENCE_OVERRIDE

    calc_ref = _calc_input(graph, f"{C19_PKG}__the_design__panel__noop", "x")
    assert calc_ref == node_ref(graph, target)

    guard_ref = _constraint_input(graph, f"{C19_PKG}__the_design__panel__within", "v")
    assert guard_ref == node_ref(graph, target)

    assert graph.diagnostics == []


def test_fusion_tea_self_binding_fails_loud() -> None:
    """``in gain = gain`` is a hard elaboration error carrying SI_SELF_BINDING
    and every offending binding — never reinterpreted (contract D-3/SRC-01)."""
    with pytest.raises(ElaborationError) as excinfo:
        _elaborate_fixture("fusion_tea")
    message = str(excinfo.value)
    assert "SI_SELF_BINDING" in message
    assert "gain" in message
    self_bindings = [
        finding
        for finding in excinfo.value.findings
        if finding.code is ReadinessCode.SI_SELF_BINDING
    ]
    assert self_bindings, excinfo.value.findings
    assert any("gain" == finding.param_name for finding in self_bindings)


# ---------------------------------------------------------------------------
# Probe 4: node-ID stability across independent loads
# ---------------------------------------------------------------------------


def test_graph_identical_across_independent_loads() -> None:
    first = _elaborate_fixture(PKG)
    second = _elaborate_fixture(PKG)

    def node_ids(graph: InstanceGraph) -> list[str]:
        return sorted(
            node_id.to_wire()
            for population in (graph.attrs, graph.calcs, graph.constraints)
            for node_id in population
        )

    def edges(graph: InstanceGraph) -> list[tuple[str, str, str]]:
        return sorted(
            (node_id.to_wire(), repr(param), repr(ref))
            for nodes in (graph.calcs, graph.constraints)
            for node_id, node in nodes.items()
            for param, ref in node.inputs.items()
        )

    def values(graph: InstanceGraph) -> list[tuple[str, str, ValueSite]]:
        return sorted(
            (node.node_id.to_wire(), repr(node.value), node.value_site)
            for node in graph.attrs.values()
        )

    assert node_ids(first) == node_ids(second)
    assert edges(first) == edges(second)
    assert values(first) == values(second)
