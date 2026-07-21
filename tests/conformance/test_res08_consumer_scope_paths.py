"""REQ-RES-08: consumer-scope derivation applies on every resolution path.

Per-path pins over real fixtures (R1: never a mock, every expectation
hand-authored from the fixture source, never computed by the code under test).

The enumerated paths and their REAL mechanisms (the row text names them —
deliberately NOT one shared derivation; asserting a uniform mechanism would
be a false pin):

  1. Backtracker base leg — ``_consumer_scope_dotted``: dotted scope from the
     usage QN's ``segments[1:-1]``.
  2. Backtracker climb leg (Item 2) — Step CLIMB retries ``scoped_lookup``
     with ancestor prefixes of the consumer scope for 3+-segment chains.
  3. Aggregation leg — ``ResolutionContext.consumer_scope`` from the module
     EQN's ``segments[1:-1]`` (graph_builder ``_build_aggregation_module``),
     consumed by Strategy A's primary (consumer-scope-prefixed) lookup form.
  4. FORMULA leg — no dotted scope string at all: the attribute resolution
     map is keyed by ``owning_part_name`` (for a computed attribute the
     owner IS the consumer).

This is per-path scope application over the enumerated paths, not an
exhaustiveness proof.
"""

from pathlib import Path

import pytest

from sysml_codegen.resolution.producer_resolution import (
    Outcome,
    ProducerRequest,
    TerminalPolicy,
    resolve_producer,
)

def _channel(bt, source_path, usage):
    """The observable outcome the deleted `_resolve_chain_dispatch` produced, read
    through the shared table (SR-R43). The climb is now the tier-1 terminal search,
    running after every tier-1 row rather than mid-sequence; it keeps its
    collect-then-require-unique ambiguity guard.
    """
    resolution = resolve_producer(
        ProducerRequest(
            consumer_eqn=usage.qualified_name,
            reference=source_path,
            param_name="probe",
            consumer_scope=bt._consumer_scope_dotted(usage),
            parent_scope=bt._get_parent_part_for_usage(usage),
            policy=TerminalPolicy.LENIENT,
            diagnostic_context="climb probe",
        ),
        bt._producer_context(),
    )
    return resolution.identity if resolution.outcome is Outcome.MODULE_OUTPUT else None


from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
from sysml_codegen.core.identifier_types import ScopedKey
from sysml_codegen.orchestration.output_registry_builder import build_output_registry
from sysml_codegen.resolution.graph_builder import _build_attribute_resolution_map
from sysml_codegen.snapshot.loader import load_extraction_snapshot
from tests.conftest import snapshot_fixture

def _probe_ctx(registry):
    """These probes carry no design attributes; the shared table sees an empty tier 2."""
    from sysml_codegen.resolution.producer_resolution import ProducerContext

    return ProducerContext(output_registry=registry)




def _backtracker_for(snap) -> DependencyBacktracker:
    registry = build_output_registry(
        calc_usages=snap["calc_usages"],
        calc_defs=snap["calc_defs"],
        aggregation_data=snap["aggregation_expressions"],
        computed_attributes=snap["computed_attributes"],
        channel_aliases=snap.get("channel_aliases", []),
        design_attributes=snap.get("design_attributes", {}),
    )
    return DependencyBacktracker(
        all_usages=snap["calc_usages"],
        calc_defs=snap["calc_defs"],
        design_attributes=snap.get("design_attributes", {}),
        output_registry=registry,
    )


def _usage(snap, qualified_name: str):
    matches = [u for u in snap["calc_usages"] if u.qualified_name == qualified_name]
    assert len(matches) == 1, f"expected exactly one usage {qualified_name}, got {len(matches)}"
    return matches[0]


class TestRes08ConsumerScopePaths:
    """REQ-RES-08: each resolution path applies the consumer's scope."""

    @pytest.mark.req("REQ-RES-08")
    def test_backtracker_base_leg_scopes_to_consumer(self, extraction_snapshots):
        """Leg 1: dotted consumer scope = QN segments[1:-1], hand-transcribed.

        Two depths: plant_values (1-segment scope) and catf_mfe (2-segment).
        Expectations are literal strings read off the usage QNs in the
        committed snapshots — not derived via the function under test.
        """
        pv = extraction_snapshots["plant_values"]
        bt = _backtracker_for(pv)
        usage = _usage(pv, "PlantValuesDesign__plant__cost_calc")
        assert bt._consumer_scope_dotted(usage) == "plant"

        catf = extraction_snapshots["catf_mfe_model"]
        bt2 = _backtracker_for(catf)
        nested = _usage(catf, "CATFMFERadialBuild__catf_radial_build__plasma_region__minor_calc")
        assert bt2._consumer_scope_dotted(nested) == "catf_radial_build.plasma_region"

    @pytest.mark.req("REQ-RES-08")
    def test_backtracker_climb_leg_finds_ancestor_scope_channel(self):
        """Leg 2 (Item 2 climb): a deep CHAIN resolves at an ANCESTOR of the
        consumer scope, to the exact hand-derived channel.

        deep_cross_scope_probe (read directly — deliberately not
        session-registered, see conformance/conftest.py): consumer
        ``chain_analysis`` lives in scope ``measurement_system.analyzer``;
        its chain ``station.array.derived_calc.derived_value`` only resolves
        after climbing to the ancestor scope ``measurement_system``. Expected
        channel is hand-assembled from the producing usage's QN in the
        fixture: DeepCrossScopeDesign__measurement_system__station__array__derived_calc
        + __derived_value.
        """
        snap = load_extraction_snapshot(snapshot_fixture("deep_cross_scope_probe"))
        bt = _backtracker_for(snap)
        consumer = _usage(
            snap, "DeepCrossScopeDesign__measurement_system__analyzer__chain_analysis"
        )

        # The consumer's own scope does NOT resolve the chain — the climb is
        # load-bearing, not decorative.
        own_scope_key = ScopedKey(
            "measurement_system.analyzer.station.array.derived_calc.derived_value"
        )
        assert bt._output_registry.scoped_lookup(own_scope_key) is None

        resolved = _channel(bt, "station.array.derived_calc.derived_value", consumer
        )
        assert resolved == (
            "DeepCrossScopeDesign__measurement_system__station__array"
            "__derived_calc__derived_value"
        )

    @pytest.mark.req("REQ-RES-08")
    def test_aggregation_leg_carries_consumer_scope(self):
        """Leg 3: the aggregation factory wires through the consumer-scoped
        (primary-form) key; the unscoped form provably misses.

        solar_battery whole-plant ``capital_cost`` aggregation: consumer scope
        ``solar_battery_plant``; singleton src ``solar_array.capital_cost``.
        Registered key (hand-derived per doc 04 key grammar):
        ``solar_battery_plant.solar_array.capital_cost`` →
        channel ``SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost``.
        """
        from sysml_codegen.resolution.graph_builder import _build_aggregation_module
        from tests.conformance.test_factory_aggregation import (
            build_aggregation_factory_inputs,
        )

        f = build_aggregation_factory_inputs("solar_battery_model")
        registry = f["registry"]

        # Hand-derived per ADR-003: the child aggregation's module EQN is
        # {instance_path}__{attribute} = …__solar_array__capital_cost, and a
        # channel is {module_eqn}__{output}, so the output channel repeats the
        # attribute segment.
        expected_channel = (
            "SolarBatteryDesign__solar_battery_plant__solar_array"
            "__capital_cost__capital_cost"
        )
        # The consumer-scope-prefixed key resolves; the bare (unscoped) key
        # does not — consumer scope is load-bearing for this wire.
        assert (
            registry.scoped_lookup(ScopedKey("solar_battery_plant.solar_array.capital_cost"))
            == expected_channel
        )
        assert registry.scoped_lookup(ScopedKey("solar_array.capital_cost")) is None

        plant_aggs = [
            a for a in f["aggregation_data"]
            if a.instance_path == "SolarBatteryDesign__solar_battery_plant"
            and a.expression.attribute_name == "capital_cost"
        ]
        assert len(plant_aggs) == 1
        module, _eps = _build_aggregation_module(
            plant_aggs[0],
            f["redefinitions"],
            f["registry"],
            f["entry_points"],
            f["group_deriver"],
            expose_aliases=f.get("expose_aliases", {}),
            usage_type_map=f["usage_type_map"],
            producer_ctx=_probe_ctx(registry),
        )
        wired = {i.param_name: i.source.producer_channel for i in module.inputs}
        assert wired.get("solar_array_capital_cost") == expected_channel

    @pytest.mark.req("REQ-RES-08")
    def test_formula_leg_scopes_by_owning_part_name(self, extraction_snapshots):
        """Leg 4: FORMULA scoping is owner-keyed, not a dotted scope string.

        attr_expr_probe: the resolution map's top-level keys are owning part
        names; the known FORMULA attr ``area`` sits under ``probe_design``
        (owner = consumer for a computed attribute). There is no
        ``consumer_scope`` string anywhere in this mechanism — that mechanism
        divergence is exactly what the row text names.
        """
        snap = extraction_snapshots["attr_expr_probe"]
        registry = build_output_registry(
            calc_usages=snap["calc_usages"],
            calc_defs=snap["calc_defs"],
            aggregation_data=snap["aggregation_expressions"],
            computed_attributes=snap["computed_attributes"],
            channel_aliases=snap.get("channel_aliases", []),
            design_attributes=snap.get("design_attributes", {}),
        )
        design_attrs = {Path(k): v for k, v in snap["design_attributes"].items()}
        calc_usage_names = {u.instance_name for u in snap["calc_usages"]}

        amap = _build_attribute_resolution_map(
            snap["computed_attributes"], design_attrs, registry, calc_usage_names
        )
        assert "probe_design" in amap, f"map keys: {sorted(amap)}"
        assert "area" in amap["probe_design"]
        # Owner-keyed means exactly that: every top-level key is a part NAME
        # (no dots, no dotted consumer-scope strings).
        assert all("." not in k for k in amap), sorted(amap)
