"""Cross-package / multi-hop EXPOSE shapes through the elaborator (Item 5 Phase 2, leg 1).

Learning-test leg for the first Phase-2 shape
(``.project/active/elaborator-breadth/plan.md``): the EXPOSE idiom the plant models
author — derived attributes exposing calc outputs, consumers in other packages
chaining to them, sibling-calc chaining, package-level calcs/attributes, and untyped
part usages carrying all of it. Findings:
``.project/research/20260807-163643_elaborator-crosspackage-expose-shapes.md``.

Two test families:

- **Fact pins** — the SysIDE evidence each shape yields (chain-root kinds, untyped
  enumeration, EXPOSE expression facts). These hold regardless of elaborator
  implementation; the implementation builds on exactly these facts.
- **Shape behavior** — the elaborated outcome per shape (written test-first for the
  leg's implementation).

All tests require a live SysIDE license.
"""

from __future__ import annotations

import pytest
from agentic_mbse.sysml.expression import feature_chain_facts
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration import (
    ElaborationError,
    InstanceGraph,
    ValueSite,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.source_evidence import ReadinessCode
from sysml_codegen.extraction.usage_extractor import (
    extract_calculation_usages,
    owned_feature_typing_targets,
    user_partdef_lookup,
)
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.elaboration_graph import (
    attr,
    calc,
    constraint,
    node_ref,
    producer_ref,
)
from tests.helpers.raw_elaboration import elaborate

pytestmark = requires_license


@pytest.fixture(scope="module")
def loaded_cache():
    """Load each fixture model once per module (extractor + calc defs)."""
    cache: dict[str, SysMLDataExtractor] = {}

    def get(name: str) -> SysMLDataExtractor:
        if name not in cache:
            extractor = SysMLDataExtractor([FIXTURES_DIR / name])
            assert extractor.load_models(), f"fixture {name} failed to load"
            cache[name] = extractor
        return cache[name]

    return get


@pytest.fixture(scope="module")
def graph_cache(loaded_cache):
    """Elaborate each fixture once per module.

    catf_mfe elaborates lenient: the fixture carries a real SRC-01 self-binding
    (``pump_load.pumping_speed_total``), which strict mode rejects — pinned by
    ``test_catf_strict_elaboration_rejects_its_real_self_binding``. Lenient
    records the finding and skips ONLY that binding (halt-vs-report, D9).
    """
    cache: dict[str, InstanceGraph] = {}

    def get(name: str, *, strict: bool = True) -> InstanceGraph:
        key = f"{name}:{strict}"
        if key not in cache:
            extractor = loaded_cache(name)
            cache[key] = elaborate(
                extractor.model,
                extractor.extract_calculation_definitions(),
                validation_diagnostics=extractor.diagnostics.validation,
                strict=strict,
            )
        return cache[key]

    return get


def _declarations(extractor: SysMLDataExtractor):
    usages, _report = extract_calculation_usages(
        extractor.model,
        calc_defs=extractor.extract_calculation_definitions(),
        expand_templates=False,
    )
    return usages


def _binding_evidence(usages, qn: str, param: str):
    (usage,) = [u for u in usages if u.qualified_name == qn]
    (binding,) = [b for b in usage.bindings if b.param_name == param]
    assert binding.reference_evidence is not None
    return binding.reference_evidence


# ---------------------------------------------------------------------------
# Fact pins: what SysIDE provides for each shape
# ---------------------------------------------------------------------------


def test_fact_sibling_calc_chain_root_is_a_calculation_usage(loaded_cache) -> None:
    """wi014: ``in area = area_calc.area`` roots at the sibling CalculationUsage
    itself (owner = the part def) — not at any part occurrence."""
    evidence = _binding_evidence(
        _declarations(loaded_cache("wi014_toy")),
        "toy_plant__Toy_Plant__cost_calc",
        "area",
    )
    assert evidence.chain_root is not None
    assert evidence.chain_root.element_kind == "CalculationUsage"
    assert evidence.chain_root.qualified_name == "toy_plant::'Toy Plant'::area_calc"
    assert evidence.chain_root.owner_is_definition
    assert evidence.resolved_member_names == ("area",)


def test_fact_cross_package_chain_root_is_a_package_level_part_usage(
    loaded_cache,
) -> None:
    """catf: ``in p_pumps = catf_blanket.pump_power`` roots at a PartUsage in a
    DIFFERENT package — never on the consumer's ancestor chain, with no owner QN."""
    evidence = _binding_evidence(
        _declarations(loaded_cache("catf_mfe_model")),
        "CATFMFEPhysics__catf_physics__net_electric",
        "p_pumps",
    )
    assert evidence.chain_root is not None
    assert evidence.chain_root.element_kind == "PartUsage"
    assert evidence.chain_root.qualified_name == "CATFMFEBlanket::catf_blanket"
    assert not evidence.chain_root.owner_is_definition
    assert evidence.chain_root.owner_qualified_name == ""
    assert evidence.resolved_member_names == ("pump_power",)


def test_fact_untyped_part_usages_are_invisible_to_the_typed_index(
    loaded_cache,
) -> None:
    """d316: the model has zero user part defs, so the untyped ``consumer`` part carries
    no owned feature typing — the shape the elaborator must supplement.

    The typed index this node was named for (``analysis/part_instance_index.py``, L-004)
    retired with the v5 family (retirement step 2), per the per-node disposition on ledger
    L-129. Its assertion — that ``consumer`` has no occurrence in that index — was a
    consequence of the two model facts below, which are what the elaborator actually reads,
    so they stay and the index read goes.
    """
    model = loaded_cache("d316_crosspart_expose").model
    assert user_partdef_lookup(model) == {}
    (consumer,) = [
        part
        for part in SysideAdapter.elements_of_type(model, "PartUsage")
        if str(getattr(part, "qualified_name", "")).endswith("consumer")
    ]
    assert owned_feature_typing_targets(consumer) == []


def test_fact_package_level_attribute_referent_has_no_owner_qn(loaded_cache) -> None:
    """d316: ``in seed = seed_src`` resolves to the package-owned attribute with an
    empty owner QN — a third referent-owner kind beside def and part usage."""
    evidence = _binding_evidence(
        _declarations(loaded_cache("d316_crosspart_expose")),
        "D316Design__gen",
        "seed",
    )
    assert evidence.referent is not None
    assert evidence.referent.qualified_name == "D316Design::seed_src"
    assert not evidence.referent.owner_is_definition
    assert evidence.referent.owner_qualified_name == ""


def test_fact_expose_attribute_carries_complete_chain_facts(loaded_cache) -> None:
    """catf: the exposed attr's own value expression is a FeatureChainExpression to
    the sibling producer — everything an alias edge needs is at the declaration."""
    model = loaded_cache("catf_mfe_model").model
    (blanket,) = [
        part
        for part in SysideAdapter.elements_of_type(model, "PartUsage")
        if str(getattr(part, "qualified_name", "")) == "CATFMFEBlanket::catf_blanket"
    ]
    (pump_power,) = [
        member
        for member in blanket.owned_members
        if SysideAdapter.is_instance(member, "AttributeUsage")
        and getattr(member, "name", "") == "pump_power"
    ]
    expr = pump_power.feature_value_expression
    assert SysideAdapter.is_instance(expr, "FeatureChainExpression")
    facts = feature_chain_facts(expr)
    assert facts.root is not None
    assert facts.root.element_kind == "CalculationUsage"
    assert facts.root.qualified_name == "CATFMFEBlanket::catf_blanket::pump_load"
    assert facts.resolved_member_names == ("pump_power",)
    assert not facts.has_index_segment


# ---------------------------------------------------------------------------
# Shape behavior: the elaborated outcomes (test-first for the leg implementation)
# ---------------------------------------------------------------------------

WI = "wi014_toy"
D316 = "d316_crosspart_expose"
CATF = "catf_mfe_model"


def test_sibling_calc_chain_becomes_a_producer_edge(graph_cache) -> None:
    """wi014: ``in area = area_calc.area`` wires the calc-to-calc chain."""
    graph = graph_cache(WI)
    node = calc(graph, "toy_plant__demo_plant__cost_calc")
    assert node.input_by_name("area") == producer_ref(
        graph, "toy_plant__demo_plant__area_calc", "area"
    )


def test_constraint_reads_producer_and_attr_nodes(graph_cache) -> None:
    """wi014: the asserted constraint reads the calc output and the budget attr."""
    graph = graph_cache(WI)
    node = constraint(graph, "toy_plant__demo_plant__affordable")
    assert node.input_by_name("cost") == producer_ref(
        graph, "toy_plant__demo_plant__cost_calc", "cost"
    )
    assert node.input_by_name("budget") == node_ref(graph, "toy_plant__demo_plant__plant_budget")
    assert attr(graph, "toy_plant__demo_plant__plant_budget").value == 5000.0


def test_partdef_expose_attr_aliases_the_producer(graph_cache) -> None:
    """wi014: ``attribute total_cost = cost_calc.cost`` on the part def becomes an
    alias edge at the occurrence — not a minted input, not a dead node."""
    graph = graph_cache(WI)
    node = attr(graph, "toy_plant__demo_plant__total_cost")
    assert node.alias_target == producer_ref(graph, "toy_plant__demo_plant__cost_calc", "cost")
    assert graph.diagnostics == []


def test_package_level_calc_and_attribute_elaborate(graph_cache) -> None:
    """d316: the package-level calc places, reading the package-level attribute."""
    graph = graph_cache(D316)
    gen = calc(graph, "D316Design__gen")
    assert gen.input_by_name("seed") == node_ref(graph, "D316Design__seed_src")
    seed = attr(graph, "D316Design__seed_src")
    assert seed.value == 3.0
    assert seed.value_site is ValueSite.DEFINITION_DEFAULT


def test_untyped_part_expose_follows_through_to_the_producer(graph_cache) -> None:
    """d316: ``sink.inp = exposed`` where ``exposed = gen.gval`` — the consumer's
    identity is the PRODUCER channel, through the alias, across the part boundary."""
    graph = graph_cache(D316)
    exposed = attr(graph, "D316Design__consumer__exposed")
    assert exposed.alias_target == producer_ref(graph, "D316Design__gen", "gval")
    sink = calc(graph, "D316Design__consumer__sink")
    assert sink.input_by_name("inp") == producer_ref(graph, "D316Design__gen", "gval")
    assert graph.diagnostics == []


def test_catf_strict_elaboration_rejects_its_real_self_binding(
    loaded_cache,
) -> None:
    """Leg discovery: catf_mfe itself authors the degenerate idiom
    (``in pumping_speed_total = pumping_speed_total`` on the vacuum pump load,
    ``vacuum.sysml:176``). Strict elaboration rejects the fixture — the same
    contract ruling fusion_tea pins."""
    extractor = loaded_cache(CATF)
    with pytest.raises(ElaborationError) as excinfo:
        elaborate(
            extractor.model,
            extractor.extract_calculation_definitions(),
            validation_diagnostics=extractor.diagnostics.validation,
        )
    codes = {finding.code for finding in excinfo.value.findings}
    assert codes == {ReadinessCode.SI_SELF_BINDING}
    assert any(finding.param_name == "pumping_speed_total" for finding in excinfo.value.findings)


def test_catf_lenient_records_the_finding_and_skips_only_that_binding(
    graph_cache,
) -> None:
    """Lenient (report-not-halt, D9): the SI_SELF_BINDING finding lands in the
    graph diagnostics; the offending param gets NO input (never reinterpreted);
    the pump_load node's other bindings still resolve."""
    graph = graph_cache(CATF, strict=False)
    self_bindings = [
        diagnostic
        for diagnostic in graph.diagnostics
        if diagnostic.code is ReadinessCode.SI_SELF_BINDING
    ]
    assert len(self_bindings) == 1
    pump_load = calc(graph, "CATFMFEVacuum__catf_vacuum_pumping__pump_load")
    assert not any(
        name == "pumping_speed_total" and port in pump_load.inputs
        for port, name in pump_load.input_names.items()
    )
    assert pump_load.input_by_name("base_pressure") == node_ref(
        graph, "CATFMFEVacuum__catf_vacuum_pumping__base_pressure_achievable"
    )


def test_catf_all_calc_usages_place_under_untyped_parts(graph_cache) -> None:
    """catf: all 42 calc usages sit under untyped parts; every one elaborates.

    Counted over non-computed nodes: the D6 leg additionally lifts catf's
    computed attributes into computed calc nodes.
    """
    graph = graph_cache(CATF, strict=False)
    usage_calcs = [c for c in graph.calcs.values() if not c.is_computed]
    assert len(usage_calcs) == 42, sorted(c.display_path for c in usage_calcs)


def test_catf_multi_hop_expose_reaches_the_producer_cross_package(
    graph_cache,
) -> None:
    """catf: ``net_electric.p_pumps = catf_blanket.pump_power`` — two hops (consumer
    -> exposed attr in another package -> producer) collapse to ONE producer edge."""
    graph = graph_cache(CATF, strict=False)
    exposed = attr(graph, "CATFMFEBlanket__catf_blanket__pump_power")
    assert exposed.alias_target == producer_ref(
        graph, "CATFMFEBlanket__catf_blanket__pump_load", "pump_power"
    )
    net = calc(graph, "CATFMFEPhysics__catf_physics__net_electric")
    assert net.input_by_name("p_pumps") == producer_ref(
        graph, "CATFMFEBlanket__catf_blanket__pump_load", "pump_power"
    )


def test_catf_sibling_concrete_calc_chain_wires(graph_cache) -> None:
    """catf: ``p_electric_gross = gross_electric.p_electric_gross`` — a concrete
    sibling calc under an untyped part."""
    graph = graph_cache(CATF, strict=False)
    net = calc(graph, "CATFMFEPhysics__catf_physics__net_electric")
    assert net.input_by_name("p_electric_gross") == producer_ref(
        graph, "CATFMFEPhysics__catf_physics__gross_electric", "p_electric_gross"
    )
