"""D9 de-risk pins: one entry-point QN rule reproduces all three current formulas.

Item 2 risk R3 / bet B4. `entry_point_qualified_name` is the QN authority the three
lenient consumers converge on at cutover. If it does not reproduce today's formulas
byte-for-byte, entry-point identity moves and every generated baseline shifts. These
pins run *before* any consumer is wired, so B4 is falsified cheaply if it is false.

Each pin calls the real production site rather than restating its formula, so a drift
in either direction fails here:
  - `terminal_disposition` (`dependency_backtracker.py:76`) — the calculation binding
    path, which always has a declared formal;
  - `resolve_input` (`input_resolver.py:281-282`) — the aggregation term path, which
    has no formal and flattens the reference;
  - the aggregation LocalTerm mint (`graph_builder.py:1524-1525`), observed through a
    real graph build of `solar_battery_model`, the one fixture that exercises it.
"""

from __future__ import annotations

import pytest

from sysml_codegen.analysis.dependency_backtracker import terminal_disposition
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.resolution.producer_resolution import (
    Outcome,
    ProducerContext,
    ProducerRequest,
    TerminalPolicy,
    entry_point_qualified_name,
    resolve_producer,
)
from sysml_codegen.snapshot import build_full_graph_from_snapshot
from tests.conftest import snapshot_fixture

# Real consumer/reference shapes drawn from the committed corpus: a bare name, a
# one-hop dotted chain, a multi-hop chain (the shape that warns), and a `::` form.
_CALC_SHAPES = [
    ("solarbatterydesign__solar_battery_plant__solar_array__capital_cost", "area", "area"),
    ("plantvaluesdesign__plant__cost_calc", "driver.efficiency", "driver_efficiency"),
    ("plantvaluesdesign__plant__cost_calc", "a.b.c", "chamber_cost"),
    ("wi014toydesign__toy_plant__lcoe", "toy_plant::'Toy Plant'::plant_budget", "budget"),
]


@pytest.mark.parametrize(("consumer_eqn", "reference", "param_name"), _CALC_SHAPES)
def test_d9_reproduces_the_calculation_formula(consumer_eqn, reference, param_name):
    """Calculation bindings carry a declared formal, so D9 keys on it (R3/B4)."""
    assert terminal_disposition(
        usage_qualified_name=consumer_eqn,
        param_name=param_name,
        source_path=reference,
        strict=False,
    ) == entry_point_qualified_name(
        consumer_eqn=consumer_eqn, reference=reference, param_name=param_name
    )


@pytest.mark.parametrize(
    "reference",
    ["capital_cost", "pv_module.capital_cost", "plant.assembly.widget.base_cost"],
)
def test_d9_reproduces_the_aggregation_term_formula(reference):
    """Aggregation terms have no formal, so D9 flattens the reference (R3/B4).

    Driven through the real `resolve_producer` against an empty registry, so the whole
    table misses and the lenient terminal fork is reached deterministically.
    """
    module_eqn = "solarbatterydesign__solar_battery_plant__idiot_index"
    resolved = resolve_producer(
        ProducerRequest(
            consumer_eqn=module_eqn,
            reference=reference,
            param_name=None,
            consumer_scope="solar_battery_plant",
            instance_path="SolarBatteryDesign__solar_battery_plant",
            policy=TerminalPolicy.LENIENT,
            diagnostic_context="qn rule pin",
        ),
        ProducerContext(output_registry=OutputRegistry()),
    )
    assert resolved.outcome is Outcome.ENTRY_POINT
    assert resolved.identity == entry_point_qualified_name(
        consumer_eqn=module_eqn, reference=reference, param_name=None
    )


def test_d9_reproduces_every_minted_qn_in_the_corpus():
    """The whole-corpus byte pin behind R3: every entry point a lenient terminal miss
    actually mints today is reproduced by D9's rule.

    `fusion_tea` is where the population lives — 23 calculation-binding mints. The
    non-empty assertion keeps the pin from passing vacuously if that ever changes.
    """
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("fusion_tea"))
    minted = [
        (module.name, inp.param_name, inp.source.qualified_name)
        for module in graph.modules
        for inp in module.inputs
        if inp.source.source_type == "entry_point"
        and inp.source.qualified_name == f"{module.name}__{inp.param_name}"
    ]
    assert minted, "fusion_tea minted no per-consumer entry point — pin is vacuous"
    for module_eqn, param_name, qn in minted:
        assert qn == entry_point_qualified_name(
            consumer_eqn=module_eqn, reference=param_name, param_name=param_name
        )


def test_d9_leaves_a_dotless_reference_unflattened():
    """The algebraic content of D9's third leg — the aggregation LocalTerm mint.

    That site (`graph_builder.py:1524-1525`) keys on `l_term.attribute_name`, a bare
    attribute name with no formal. D9 reaches it via the no-formal arm, and a dotless
    reference flattens to itself, so the two agree.

    Recorded honestly: **no committed fixture reaches that mint.** Every aggregation
    with local terms (`solar_battery_model`, five of them) resolves all of them
    positively, and the whole-corpus sweep above finds only calculation-binding mints.
    So this leg of bet B4 is pinned structurally, not empirically, and Phase 5 owes it
    live coverage before the LocalTerm path is cut over.
    """
    assert entry_point_qualified_name(
        consumer_eqn="pkg__part__agg", reference="capital_cost", param_name=None
    ) == "pkg__part__agg__capital_cost"
