"""Unit tests for OutputRegistry and is_transitive_default().

Tests the key format contract (Spike 8), 4-phase registration protocol,
collision handling, exact-match resolution, and transitive default detection.

All test data is synthetic, derived from Spike 8 real data patterns.
The OutputRegistry is tested in isolation from data models it will consume
in Item 3.

See: .project/active/output-registry-foundation/design.md (Component 5)
"""

from __future__ import annotations

import logging

import pytest

from sysml_codegen.core.output_registry import OutputRegistry, is_transitive_default


# ---------------------------------------------------------------------------
# Factory functions (synthetic data grounded in Spike 8)
# ---------------------------------------------------------------------------


def _make_registry_with_calc_usage() -> OutputRegistry:
    """Build a registry with one concrete CalcUsage (2 outputs).

    Represents: solar_battery lcoe CalcUsage with lcoe_per_mwh and npv outputs.
    Registers Key_A, Key_B, Key_C for each output.
    """
    reg = OutputRegistry()
    # Output 1: lcoe_per_mwh
    canonical_1 = "SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh"
    key_a_1 = "lcoe.lcoe_per_mwh"
    key_b_1 = canonical_1  # EQN format = canonical
    key_c_1 = "solar_battery_plant.lcoe.lcoe_per_mwh"
    reg.register(canonical_1, [key_a_1, key_b_1, key_c_1])

    # Output 2: npv
    canonical_2 = "SolarBatteryDesign__solar_battery_plant__lcoe__npv"
    key_a_2 = "lcoe.npv"
    key_b_2 = canonical_2
    key_c_2 = "solar_battery_plant.lcoe.npv"
    reg.register(canonical_2, [key_a_2, key_b_2, key_c_2])

    return reg


def _make_registry_with_virtual_calc_usage() -> OutputRegistry:
    """Build a registry with one virtual CalcUsage (1 output).

    Represents: solar_battery cost_model template instance with total_cost output.
    Key_C is the ONLY key that Phase 2 CHAIN aliases can resolve against.
    """
    reg = OutputRegistry()
    canonical = (
        "SolarBatteryDesign__solar_battery_plant__solar_array"
        "__pv_module__cost_model__total_cost"
    )
    # Key_A for virtual CalcUsage uses the full instance_name
    key_a = "cost_model.total_cost"
    key_b = canonical
    key_c = "solar_battery_plant.solar_array.pv_module.cost_model.total_cost"
    reg.register(canonical, [key_a, key_b, key_c])
    return reg


def _make_registry_with_aggregation() -> OutputRegistry:
    """Build a registry with one aggregation output.

    Represents: solar_array.capital_cost aggregation module.
    Registers Key_D and Key_E.
    """
    reg = OutputRegistry()
    canonical = "SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost"
    key_d = "solar_array.capital_cost"
    key_e = "solar_battery_plant.solar_array.capital_cost"
    reg.register(canonical, [key_d, key_e])
    return reg


def _make_registry_with_formula() -> OutputRegistry:
    """Build a registry with one FORMULA computed attribute.

    Represents: e2e_plant.power_mw synthetic module.
    Registers Key_F.
    """
    reg = OutputRegistry()
    canonical = "E2EDesign__e2e_plant__power_mw"
    key_f = "e2e_plant.power_mw"
    reg.register(canonical, [key_f])
    return reg


# ---------------------------------------------------------------------------
# TestRegister -- FR-2 basic registration
# ---------------------------------------------------------------------------


class TestRegister:
    """FR-2: Basic register() and self-resolution."""

    def test_register_single_key(self):
        reg = OutputRegistry()
        reg.register("Design__plant__lcoe__lcoe_per_mwh", ["lcoe.lcoe_per_mwh"])
        assert reg.resolve("lcoe.lcoe_per_mwh") == "Design__plant__lcoe__lcoe_per_mwh"

    def test_register_multiple_keys(self):
        reg = OutputRegistry()
        canonical = "Design__plant__lcoe__lcoe_per_mwh"
        reg.register(canonical, [
            "lcoe.lcoe_per_mwh",
            canonical,
            "plant.lcoe.lcoe_per_mwh",
        ])
        assert reg.resolve("lcoe.lcoe_per_mwh") == canonical
        assert reg.resolve(canonical) == canonical
        assert reg.resolve("plant.lcoe.lcoe_per_mwh") == canonical

    def test_canonical_channel_self_resolves(self):
        reg = OutputRegistry()
        canonical = "Design__plant__lcoe__lcoe_per_mwh"
        reg.register(canonical, [])
        assert reg.resolve(canonical) == canonical

    def test_register_duplicate_key_same_channel_is_noop(self, caplog):
        reg = OutputRegistry()
        canonical = "Design__plant__lcoe__lcoe_per_mwh"
        reg.register(canonical, ["lcoe.lcoe_per_mwh"])
        with caplog.at_level(logging.WARNING):
            reg.register(canonical, ["lcoe.lcoe_per_mwh"])
        assert "collision" not in caplog.text.lower()
        assert reg.resolve("lcoe.lcoe_per_mwh") == canonical

    def test_len_reflects_registered_keys(self):
        reg = OutputRegistry()
        reg.register("ch_A", ["key_1", "key_2"])
        # canonical self-key + 2 lookup keys = 3
        assert len(reg) == 3


# ---------------------------------------------------------------------------
# TestCollisionHandling -- FR-2 collision policy
# ---------------------------------------------------------------------------


class TestCollisionHandling:
    """FR-2: Collision policy -- refuse overwrite, log warning, keep first."""

    def test_collision_refuses_overwrite(self):
        reg = OutputRegistry()
        reg.register("channel_A", ["shared.key"])
        reg.register("channel_B", ["shared.key"])
        assert reg.resolve("shared.key") == "channel_A"  # first wins

    def test_collision_logs_warning(self, caplog):
        reg = OutputRegistry()
        reg.register("channel_A", ["shared.key"])
        with caplog.at_level(logging.WARNING):
            reg.register("channel_B", ["shared.key"])
        assert "collision" in caplog.text.lower()
        assert "shared.key" in caplog.text
        assert "channel_A" in caplog.text
        assert "channel_B" in caplog.text

    def test_nine_virtual_calc_usage_collision(self, caplog):
        """Key_A 'cost_model.total_cost' from 9 virtual CalcUsages: first wins, 8 warnings."""
        reg = OutputRegistry()
        first_canonical = "Design__part1__cost_model__total_cost"
        reg.register(first_canonical, ["cost_model.total_cost"])

        with caplog.at_level(logging.WARNING):
            for i in range(2, 10):
                reg.register(
                    f"Design__part{i}__cost_model__total_cost",
                    ["cost_model.total_cost"],
                )

        assert reg.resolve("cost_model.total_cost") == first_canonical
        # 8 collisions (parts 2-9)
        collision_warnings = [
            r for r in caplog.records
            if "collision" in r.message.lower()
        ]
        assert len(collision_warnings) == 8


# ---------------------------------------------------------------------------
# TestRegisterAlias -- FR-2 alias registration
# ---------------------------------------------------------------------------


class TestRegisterAlias:
    """FR-2: register_alias() with phase ordering enforcement."""

    def test_alias_resolves_to_canonical(self):
        reg = OutputRegistry()
        canonical = "Design__plant__cost_model__total_cost"
        reg.register(canonical, [])
        reg.register_alias("solar_array.total_capex", canonical)
        assert reg.resolve("solar_array.total_capex") == canonical

    def test_alias_to_unregistered_channel_warns(self, caplog):
        reg = OutputRegistry()
        with caplog.at_level(logging.WARNING):
            reg.register_alias("alias.key", "nonexistent__channel")
        assert "unregistered" in caplog.text.lower()
        assert reg.resolve("alias.key") is None

    def test_alias_collision_refuses_overwrite(self, caplog):
        reg = OutputRegistry()
        reg.register("channel_A", ["shared.key"])
        reg.register("channel_B", [])
        with caplog.at_level(logging.WARNING):
            reg.register_alias("shared.key", "channel_B")
        assert "collision" in caplog.text.lower()
        assert reg.resolve("shared.key") == "channel_A"  # first wins


# ---------------------------------------------------------------------------
# TestResolve -- FR-2 + FR-5 resolution
# ---------------------------------------------------------------------------


class TestResolve:
    """FR-2 + FR-5: Exact-match resolution and 'no normalization' contract."""

    def test_resolve_exact_match(self):
        reg = _make_registry_with_calc_usage()
        assert reg.resolve("lcoe.lcoe_per_mwh") == (
            "SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh"
        )

    def test_resolve_unregistered_returns_none(self):
        reg = _make_registry_with_calc_usage()
        assert reg.resolve("nonexistent.key") is None

    def test_resolve_bare_name_returns_none(self):
        reg = _make_registry_with_calc_usage()
        assert reg.resolve("lcoe_per_mwh") is None

    def test_resolve_sysml_qn_returns_none(self):
        reg = _make_registry_with_calc_usage()
        assert reg.resolve("SolarBatteryDesign::solar_battery_plant::lcoe") is None

    def test_resolve_no_normalization(self):
        """Register 'a.b', resolve 'a__b' -- must return None (no format conversion)."""
        reg = OutputRegistry()
        reg.register("canonical", ["a.b"])
        assert reg.resolve("a__b") is None


# ---------------------------------------------------------------------------
# TestKeyFormats -- FR-3 key format contract (Spike 8 data)
# ---------------------------------------------------------------------------


class TestKeyFormats:
    """FR-3: Key format contract validated with Spike 8 data patterns."""

    def test_key_a_dotted_short_resolves(self):
        reg = _make_registry_with_calc_usage()
        result = reg.resolve("lcoe.lcoe_per_mwh")
        assert result == "SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh"

    def test_key_b_eqn_resolves(self):
        reg = _make_registry_with_calc_usage()
        result = reg.resolve(
            "SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh"
        )
        assert result == "SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh"

    def test_key_c_dotted_hierarchy_resolves(self):
        reg = _make_registry_with_calc_usage()
        result = reg.resolve("solar_battery_plant.lcoe.lcoe_per_mwh")
        assert result == "SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh"

    def test_key_c_virtual_calc_usage(self):
        reg = _make_registry_with_virtual_calc_usage()
        result = reg.resolve(
            "solar_battery_plant.solar_array.pv_module.cost_model.total_cost"
        )
        assert result == (
            "SolarBatteryDesign__solar_battery_plant__solar_array"
            "__pv_module__cost_model__total_cost"
        )

    def test_key_d_aggregation_resolves(self):
        reg = _make_registry_with_aggregation()
        result = reg.resolve("solar_array.capital_cost")
        assert result == (
            "SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost"
        )

    def test_key_f_formula_resolves(self):
        reg = _make_registry_with_formula()
        result = reg.resolve("e2e_plant.power_mw")
        assert result == "E2EDesign__e2e_plant__power_mw"


# ---------------------------------------------------------------------------
# TestDeriveKeyC -- FR-6 Key_C utility
# ---------------------------------------------------------------------------


class TestDeriveKeyC:
    """FR-6: Key_C derivation from usage QN + output attr name."""

    def test_concrete_calc_usage(self):
        result = OutputRegistry.derive_key_c("Design__plant__lcoe", "lcoe_per_mwh")
        assert result == "plant.lcoe.lcoe_per_mwh"

    def test_virtual_calc_usage_deep(self):
        result = OutputRegistry.derive_key_c(
            "SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model",
            "total_cost",
        )
        assert result == (
            "solar_battery_plant.solar_array.pv_module.cost_model.total_cost"
        )

    def test_single_segment_after_prefix(self):
        result = OutputRegistry.derive_key_c("Design__lcoe", "out")
        assert result == "lcoe.out"


# ---------------------------------------------------------------------------
# TestPhaseOrdering -- FR-3 4-phase protocol
# ---------------------------------------------------------------------------


class TestPhaseOrdering:
    """FR-3: 4-phase registration protocol ordering."""

    def test_phase2_alias_resolves_via_phase1_key_c(self):
        """Phase 2 CHAIN alias resolves against Phase 1 Key_C entry."""
        reg = OutputRegistry()
        # Phase 1: register virtual CalcUsage with Key_C
        canonical = "Design__plant__solar_array__cost_model__total_cost"
        key_c = "plant.solar_array.cost_model.total_cost"
        reg.register(canonical, [key_c])

        # Phase 2: CHAIN alias points to canonical
        reg.register_alias("plant.solar_array.total_capex", canonical)

        assert reg.resolve("plant.solar_array.total_capex") == canonical

    def test_phase3_alias_resolves_via_phase1_and_phase2(self):
        """Phase 3 EXPOSE_PURE alias resolves against Phase 1+2 entries."""
        reg = OutputRegistry()
        # Phase 1
        canonical = "Design__plant__lcoe__lcoe_per_mwh"
        reg.register(canonical, ["lcoe.lcoe_per_mwh"])

        # Phase 2: CHAIN alias
        reg.register_alias("plant.lcoe.lcoe_per_mwh_alias", canonical)

        # Phase 3: EXPOSE_PURE alias also points to same canonical
        reg.register_alias("plant.lcoe_result", canonical)

        assert reg.resolve("plant.lcoe_result") == canonical

    def test_phase4_alias_resolves_via_phase1_through_3(self):
        """Phase 4 transitive alias resolves against Phase 1-3 entries."""
        reg = OutputRegistry()
        # Phase 1
        canonical = "Design__plant__cost_model__total_cost"
        reg.register(canonical, ["cost_model.total_cost"])

        # Phase 2: CHAIN alias
        reg.register_alias("plant.cost_model.total_cost", canonical)

        # Phase 3: EXPOSE_PURE alias
        reg.register_alias("plant.total_capex", canonical)

        # Phase 4: transitive design attr alias
        reg.register_alias("design.total_capex", canonical)

        assert reg.resolve("design.total_capex") == canonical

    def test_phase2_before_phase1_warns(self, caplog):
        """register_alias() warns if canonical isn't registered yet."""
        reg = OutputRegistry()
        with caplog.at_level(logging.WARNING):
            reg.register_alias("alias.key", "unregistered__canonical")
        assert "unregistered" in caplog.text.lower()
        assert "phase ordering" in caplog.text.lower()


# ---------------------------------------------------------------------------
# TestIsTransitiveDefault -- FR-4
# ---------------------------------------------------------------------------


class TestIsTransitiveDefault:
    """FR-4: is_transitive_default() edge cases."""

    def test_dotted_path_is_transitive(self):
        assert is_transitive_default("cost_model.total_cost") is True

    def test_numeric_with_dot_not_transitive(self):
        assert is_transitive_default("3.14") is False

    def test_none_not_transitive(self):
        assert is_transitive_default(None) is False

    def test_bare_name_not_transitive(self):
        assert is_transitive_default("width") is False

    def test_integer_not_transitive(self):
        assert is_transitive_default("42") is False

    def test_empty_string_not_transitive(self):
        assert is_transitive_default("") is False

    def test_complex_dotted_path_is_transitive(self):
        assert is_transitive_default("solar_array.cost_model.total_cost") is True

    def test_scientific_notation_not_transitive(self):
        assert is_transitive_default("1.5e3") is False


# ---------------------------------------------------------------------------
# TestDiagnostics -- canonical_channels property and __repr__
# ---------------------------------------------------------------------------


class TestDiagnostics:
    """Diagnostic helpers: canonical_channels property and __repr__."""

    def test_canonical_channels_returns_frozenset(self):
        reg = OutputRegistry()
        reg.register("ch_A", ["key_1"])
        reg.register("ch_B", ["key_2"])
        result = reg.canonical_channels
        assert isinstance(result, frozenset)
        assert result == frozenset({"ch_A", "ch_B"})

    def test_canonical_channels_empty_registry(self):
        reg = OutputRegistry()
        assert reg.canonical_channels == frozenset()

    def test_repr_shows_key_and_channel_counts(self):
        reg = OutputRegistry()
        reg.register("ch_A", ["key_1", "key_2"])
        # 1 canonical self-key + 2 lookup keys = 3 keys, 1 channel
        assert repr(reg) == "OutputRegistry(keys=3, channels=1)"

    def test_repr_empty_registry(self):
        reg = OutputRegistry()
        assert repr(reg) == "OutputRegistry(keys=0, channels=0)"
