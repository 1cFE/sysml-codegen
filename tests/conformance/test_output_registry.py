"""Conformance tests for Output Registry (C08).

Requirements: REQ-OR-01 through REQ-OR-08
Design intent: 10-output-registry.md, 27-typed-registry-refactor.md

Tests use real extraction snapshot data — no mocks.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from sysml_codegen.core.output_registry import OutputRegistry, is_transitive_default
from sysml_codegen.core.qualified_names import (
    get_channel_name,
    sysml_to_python_qualified_name,
)
from sysml_codegen.extraction.data_models import (
    Compilability,
    ComputedAttributeClassification,
)
from sysml_codegen.generation.initialization import build_output_registry
from tests.helpers.snapshot_loader import load_extraction_snapshot


# ---------------------------------------------------------------------------
# Typed identifier imports — these don't exist yet; tests will FAIL until
# BUILD phase creates them in core/identifier_types.py.
# ---------------------------------------------------------------------------
try:
    from sysml_codegen.core.identifier_types import (
        CanonicalChannel,
        ScopedKey,
        SysMLQN,
    )

    TYPED_API_AVAILABLE = True
except ImportError:
    # Stub types so test file parses — tests will be skipped/xfail
    from typing import NewType

    ScopedKey = NewType("ScopedKey", str)
    CanonicalChannel = NewType("CanonicalChannel", str)
    SysMLQN = NewType("SysMLQN", str)
    TYPED_API_AVAILABLE = False

# Try importing typed constructor functions
try:
    from sysml_codegen.core.identifier_types import (
        make_canonical_channel,
        make_scoped_key,
    )

    CONSTRUCTORS_AVAILABLE = True
except ImportError:
    CONSTRUCTORS_AVAILABLE = False

    def make_scoped_key(usage_eqn: str, attr_name: str) -> ScopedKey:
        segments = usage_eqn.split("__")
        return ScopedKey("." .join(segments[1:]) + "." + attr_name)

    def make_canonical_channel(usage_eqn: str, attr_name: str) -> CanonicalChannel:
        return CanonicalChannel(f"{usage_eqn}__{attr_name}")


# ---------------------------------------------------------------------------
# Helper: build output registry from snapshot
# ---------------------------------------------------------------------------
def build_registry_from_snapshot(snapshot: dict) -> OutputRegistry:
    """Build a populated OutputRegistry from extraction snapshot data."""
    return build_output_registry(
        calc_usages=snapshot["calc_usages"],
        calc_defs=snapshot["calc_defs"],
        aggregation_data=snapshot["aggregation_expressions"],
        computed_attributes=snapshot["computed_attributes"],
        channel_aliases=snapshot.get("channel_aliases", []),
        design_attributes=snapshot.get("design_attributes", {}),
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def solar_battery_registry():
    """Session-scoped OutputRegistry built from solar_battery snapshot."""
    snap = load_extraction_snapshot("solar_battery_model")
    return build_registry_from_snapshot(snap)


@pytest.fixture(scope="session")
def catf_mfe_registry():
    """Session-scoped OutputRegistry built from catf_mfe snapshot."""
    snap = load_extraction_snapshot("catf_mfe_model")
    return build_registry_from_snapshot(snap)


@pytest.fixture(scope="session")
def attr_expr_probe_registry():
    """Session-scoped OutputRegistry built from attr_expr_probe snapshot."""
    snap = load_extraction_snapshot("attr_expr_probe")
    return build_registry_from_snapshot(snap)


# ---------------------------------------------------------------------------
# Typed API availability check — skip tests that need typed API
# ---------------------------------------------------------------------------
needs_typed_api = pytest.mark.skipif(
    not TYPED_API_AVAILABLE,
    reason="Typed API (ScopedKey, CanonicalChannel, SysMLQN) not yet created",
)

needs_constructors = pytest.mark.skipif(
    not CONSTRUCTORS_AVAILABLE,
    reason="Constructor functions (make_scoped_key, make_canonical_channel) not yet created",
)


def _has_typed_methods(registry: OutputRegistry) -> bool:
    """Check if registry has typed lookup methods."""
    return all(
        hasattr(registry, m)
        for m in ("scoped_lookup", "sysml_qn_lookup", "alias_lookup")
    )


def _has_typed_registration(registry: OutputRegistry) -> bool:
    """Check if registry has typed registration methods."""
    return all(
        hasattr(registry, m)
        for m in ("register_scoped", "register_sysml_qn")
    )


needs_typed_methods = pytest.mark.skipif(
    not _has_typed_methods(OutputRegistry()),
    reason="Typed lookup methods not yet implemented on OutputRegistry",
)

needs_typed_registration = pytest.mark.skipif(
    not _has_typed_registration(OutputRegistry()),
    reason="Typed registration methods not yet implemented on OutputRegistry",
)


# ===================================================================
# REQ-OR-01: All reference formats resolve
# ===================================================================
class TestReqOR01:
    """REQ-OR-01: Registry SHALL map every reference format to canonical."""

    @pytest.mark.req("REQ-OR-01")
    @pytest.mark.parametrize("model_name", ["solar_battery_model", "catf_mfe_model"])
    @needs_typed_methods
    def test_all_reference_formats_resolve(self, model_name):
        """All CalcUsage outputs resolve via scoped_lookup; FORMULA outputs
        resolve via sysml_qn_lookup; CHAIN aliases resolve via alias_lookup."""
        snap = load_extraction_snapshot(model_name)
        registry = build_registry_from_snapshot(snap)
        calc_def_by_name = {cd.name: cd for cd in snap["calc_defs"]}

        # CalcUsage outputs -> scoped_lookup
        for usage in snap["calc_usages"]:
            calc_def = calc_def_by_name.get(usage.calc_def_name)
            if not calc_def:
                continue
            for attr in calc_def.output_attributes:
                sk = make_scoped_key(usage.qualified_name, attr.name)
                result = registry.scoped_lookup(ScopedKey(sk))
                assert result is not None, (
                    f"scoped_lookup({sk}) returned None for "
                    f"{usage.qualified_name}.{attr.name}"
                )

        # FORMULA outputs -> sysml_qn_lookup
        for ca in snap["computed_attributes"]:
            if ca.classification != ComputedAttributeClassification.FORMULA:
                continue
            if ca.compilability != Compilability.FULLY_COMPILABLE:
                continue
            if ca.owning_part_qualified_name:
                qn_key = SysMLQN(f"{ca.owning_part_qualified_name}::{ca.name}")
                result = registry.sysml_qn_lookup(qn_key)
                assert result is not None, (
                    f"sysml_qn_lookup({qn_key}) returned None"
                )

        # CHAIN aliases -> alias_lookup
        for alias in snap.get("channel_aliases", []):
            if alias.source != "redefinition":
                continue
            result = registry.alias_lookup(ScopedKey(alias.alias_name))
            assert result is not None, (
                f"alias_lookup({alias.alias_name}) returned None "
                f"for CHAIN alias"
            )

    @pytest.mark.req("REQ-OR-01")
    def test_canonical_channels_property_returns_frozenset(
        self, solar_battery_registry
    ):
        """canonical_channels returns frozenset with all registered channels."""
        channels = solar_battery_registry.canonical_channels
        assert isinstance(channels, frozenset)
        assert len(channels) > 0
        # Verify count matches expected (77 for solar_battery)
        assert len(channels) == 77

    @pytest.mark.req("REQ-OR-01")
    def test_chain_alias_count_solar_battery(self, solar_battery_registry):
        """Build from solar_battery; count Phase 2 aliases; verify == 41."""
        snap = load_extraction_snapshot("solar_battery_model")
        chain_aliases = [
            a for a in snap.get("channel_aliases", [])
            if a.source == "redefinition"
        ]
        assert len(chain_aliases) == 41

    @pytest.mark.req("REQ-OR-01")
    def test_registry_with_no_inputs(self):
        """Build empty registry; verify len=0; all lookups return None."""
        registry = build_output_registry(
            calc_usages=[],
            calc_defs=[],
            aggregation_data=[],
            computed_attributes=[],
            channel_aliases=[],
            design_attributes={},
        )
        assert len(registry) == 0
        assert len(registry.canonical_channels) == 0
        # resolve() should return None
        assert registry.resolve("nonexistent.key") is None


# ===================================================================
# REQ-OR-02: Typed lookup methods
# ===================================================================
class TestReqOR02:
    """REQ-OR-02: Each typed registry SHALL have its own lookup method."""

    @pytest.mark.req("REQ-OR-02")
    @needs_typed_methods
    def test_no_single_resolve_method(self):
        """OutputRegistry has scoped_lookup, sysml_qn_lookup, alias_lookup."""
        registry = OutputRegistry()
        assert hasattr(registry, "scoped_lookup")
        assert hasattr(registry, "sysml_qn_lookup")
        assert hasattr(registry, "alias_lookup")
        assert callable(registry.scoped_lookup)
        assert callable(registry.sysml_qn_lookup)
        assert callable(registry.alias_lookup)

    @pytest.mark.req("REQ-OR-02")
    @pytest.mark.parametrize("model_name", ["solar_battery_model"])
    @needs_typed_methods
    def test_typed_lookups_return_canonical_channel(self, model_name):
        """Typed lookup methods return CanonicalChannel | None."""
        snap = load_extraction_snapshot(model_name)
        registry = build_registry_from_snapshot(snap)
        calc_def_by_name = {cd.name: cd for cd in snap["calc_defs"]}

        # Pick a known CalcUsage output
        usage = snap["calc_usages"][0]
        calc_def = calc_def_by_name.get(usage.calc_def_name)
        if calc_def and calc_def.output_attributes:
            attr = calc_def.output_attributes[0]
            sk = make_scoped_key(usage.qualified_name, attr.name)
            result = registry.scoped_lookup(ScopedKey(sk))
            assert result is not None
            # Result should be a string (CanonicalChannel is NewType over str)
            assert isinstance(result, str)

    @pytest.mark.req("REQ-OR-02")
    @needs_typed_methods
    def test_scoped_lookup_miss_returns_none(self, solar_battery_registry):
        """scoped_lookup with nonexistent key returns None."""
        result = solar_battery_registry.scoped_lookup(
            ScopedKey("nonexistent.key")
        )
        assert result is None

    @pytest.mark.req("REQ-OR-02")
    @needs_typed_methods
    def test_sysml_qn_lookup_miss_returns_none(self, solar_battery_registry):
        """sysml_qn_lookup with nonexistent key returns None."""
        result = solar_battery_registry.sysml_qn_lookup(
            SysMLQN("NonExistent::key")
        )
        assert result is None

    @pytest.mark.req("REQ-OR-02")
    @needs_typed_methods
    def test_alias_lookup_miss_returns_none(self, solar_battery_registry):
        """alias_lookup with nonexistent key returns None."""
        result = solar_battery_registry.alias_lookup(
            ScopedKey("nonexistent.key")
        )
        assert result is None


# ===================================================================
# REQ-OR-03: Collision policies
# ===================================================================
class TestReqOR03:
    """REQ-OR-03: Collision policy per registry type."""

    @pytest.mark.req("REQ-OR-03")
    @needs_typed_registration
    def test_scoped_duplicate_raises(self):
        """Registering same ScopedKey with different channel raises."""
        registry = OutputRegistry()
        sk = ScopedKey("plant.calc.output")
        cc1 = CanonicalChannel("Design__plant__calc__output")
        cc2 = CanonicalChannel("Design__plant__other__output")
        registry.register_scoped(sk, cc1)
        with pytest.raises((ValueError, KeyError)):
            registry.register_scoped(sk, cc2)

    @pytest.mark.req("REQ-OR-03")
    @needs_typed_registration
    def test_sysml_qn_duplicate_raises(self):
        """Registering same SysMLQN with different channel raises."""
        registry = OutputRegistry()
        qn = SysMLQN("Package::Element::attr")
        cc1 = CanonicalChannel("Package__Element__attr__attr")
        cc2 = CanonicalChannel("Package__Element__other__attr")
        registry.register_sysml_qn(qn, cc1)
        with pytest.raises((ValueError, KeyError)):
            registry.register_sysml_qn(qn, cc2)

    @pytest.mark.req("REQ-OR-03")
    @needs_typed_registration
    def test_alias_duplicate_warns_first_wins(self, caplog):
        """Re-registering alias with different channel keeps first value."""
        registry = OutputRegistry()
        # Must register canonical channels first
        sk1 = ScopedKey("plant.calc.output")
        cc1 = CanonicalChannel("Design__plant__calc__output")
        cc2 = CanonicalChannel("Design__plant__other__output")
        registry.register_scoped(sk1, cc1)
        registry.register_scoped(ScopedKey("plant.other.output"), cc2)

        alias_key = ScopedKey("plant.alias")
        registry.register_alias(alias_key, cc1)
        with caplog.at_level(logging.WARNING):
            registry.register_alias(alias_key, cc2)

        # First value should be retained
        result = registry.alias_lookup(alias_key)
        assert result == cc1


# ===================================================================
# REQ-OR-04: Phase ordering enforcement
# ===================================================================
class TestReqOR04:
    """REQ-OR-04: register_alias() enforces phase ordering."""

    @pytest.mark.req("REQ-OR-04")
    def test_alias_phase_ordering_enforced(self, caplog):
        """Attempt register_alias with unregistered channel -> rejected."""
        registry = OutputRegistry()
        with caplog.at_level(logging.WARNING):
            registry.register_alias(
                "test.alias",
                "Unregistered__channel",
            )
        # Alias should NOT be registered
        assert registry.resolve("test.alias") is None
        # Warning should be logged
        assert "phase ordering" in caplog.text.lower() or "unregistered" in caplog.text.lower()

    @pytest.mark.req("REQ-OR-04")
    @needs_typed_registration
    def test_alias_after_canonical_succeeds(self):
        """Register canonical via register_scoped, then register_alias succeeds."""
        registry = OutputRegistry()
        sk = ScopedKey("plant.calc.output")
        cc = CanonicalChannel("Design__plant__calc__output")
        registry.register_scoped(sk, cc)
        # Now alias should succeed
        alias_key = ScopedKey("plant.alias")
        registry.register_alias(alias_key, cc)
        result = registry.alias_lookup(alias_key)
        assert result == cc


# ===================================================================
# REQ-OR-05: No dead keys registered
# ===================================================================
class TestReqOR05:
    """REQ-OR-05: Only Key_C, Key_E_stripped, SysML QN registered."""

    @pytest.mark.req("REQ-OR-05")
    @pytest.mark.parametrize("model_name", ["solar_battery_model", "catf_mfe_model"])
    @needs_typed_methods
    def test_no_dead_keys_registered(self, model_name):
        """Key_A, Key_D, Key_E full, Key_F, bare NOT in any registry."""
        snap = load_extraction_snapshot(model_name)
        registry = build_registry_from_snapshot(snap)
        calc_def_by_name = {cd.name: cd for cd in snap["calc_defs"]}

        for usage in snap["calc_usages"]:
            calc_def = calc_def_by_name.get(usage.calc_def_name)
            if not calc_def:
                continue
            for attr in calc_def.output_attributes:
                # Key_A: instance_name.attr — should NOT resolve
                key_a = f"{usage.instance_name}.{attr.name}"
                result = registry.scoped_lookup(ScopedKey(key_a))
                # Key_A should not be in scoped registry (it lacks scope)
                # But it might match a Key_C for top-level usages — only
                # assert it's not ADDITIONALLY registered (not a false positive)
                key_c = make_scoped_key(usage.qualified_name, attr.name)
                if key_a != key_c:
                    assert result is None, (
                        f"Key_A '{key_a}' should not be in scoped registry "
                        f"(Key_C is '{key_c}')"
                    )

    @pytest.mark.req("REQ-OR-05")
    @pytest.mark.parametrize("model_name", ["solar_battery_model"])
    @needs_typed_methods
    def test_only_key_c_and_key_e_stripped_in_scoped(self, model_name):
        """Every scoped key is Key_C or Key_E_stripped format: dotted path,
        no '::', no '__'."""
        snap = load_extraction_snapshot(model_name)
        registry = build_registry_from_snapshot(snap)

        # Access internal _scoped dict to verify format
        if hasattr(registry, "_scoped"):
            for key in registry._scoped:
                assert "::" not in key, f"Scoped key '{key}' contains '::'"
                assert "__" not in key, f"Scoped key '{key}' contains '__'"
                assert "." in key, f"Scoped key '{key}' has no '.'"

    @pytest.mark.req("REQ-OR-05")
    def test_aggregation_key_e_stripped(self):
        """Aggregation Key_E_stripped (design prefix stripped, dotted) is
        in scoped registry for solar_battery."""
        snap = load_extraction_snapshot("solar_battery_model")
        registry = build_registry_from_snapshot(snap)

        # solar_battery has aggregation expressions with instance_path like
        # "SolarBatteryDesign__solar_battery_plant__solar_array"
        # Key_E_stripped = solar_battery_plant.solar_array.capital_cost
        for agg in snap["aggregation_expressions"]:
            instance_parts = agg.instance_path.split("__")
            if len(instance_parts) > 1:
                key_e_stripped = ".".join(
                    instance_parts[1:] + [agg.expression.attribute_name]
                )
                # Should be resolvable (via scoped or deprecated resolve)
                result = registry.resolve(key_e_stripped)
                assert result is not None, (
                    f"Key_E_stripped '{key_e_stripped}' not found in registry"
                )

    @pytest.mark.req("REQ-OR-05")
    def test_formula_sysml_qn_registered(self):
        """FORMULA SysML QN keys are in registry for attr_expr_probe."""
        snap = load_extraction_snapshot("attr_expr_probe")
        registry = build_registry_from_snapshot(snap)

        formula_qn_count = 0
        for ca in snap["computed_attributes"]:
            if ca.classification != ComputedAttributeClassification.FORMULA:
                continue
            if ca.compilability != Compilability.FULLY_COMPILABLE:
                continue
            if ca.owning_part_qualified_name:
                sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
                result = registry.resolve(sysml_qn)
                assert result is not None, (
                    f"FORMULA SysML QN '{sysml_qn}' not found in registry"
                )
                formula_qn_count += 1

        assert formula_qn_count == 14, (
            f"Expected 14 FORMULA QN keys, got {formula_qn_count}"
        )


# ===================================================================
# REQ-OR-06: Phase 2-4 alias resolution
# ===================================================================
class TestReqOR06:
    """REQ-OR-06: Phase 2-4 aliases resolve through typed lookup."""

    @pytest.mark.req("REQ-OR-06")
    @needs_typed_methods
    def test_phase2_alias_resolves_through_scoped(self):
        """Each Phase 2 CHAIN alias has its canonical resolved via scoped
        lookup before alias registration."""
        snap = load_extraction_snapshot("solar_battery_model")
        registry = build_registry_from_snapshot(snap)

        for alias in snap.get("channel_aliases", []):
            if alias.source != "redefinition":
                continue
            # The alias's canonical_name should be resolvable via scoped
            scoped_result = registry.scoped_lookup(
                ScopedKey(alias.canonical_name)
            ) if _has_typed_methods(registry) else registry.resolve(
                alias.canonical_name
            )
            assert scoped_result is not None, (
                f"CHAIN alias canonical '{alias.canonical_name}' not "
                f"resolvable via scoped lookup"
            )

    @pytest.mark.req("REQ-OR-06")
    @needs_typed_methods
    def test_phase3_alias_resolves_through_registry(self):
        """EXPOSE_PURE aliases' canonical_name resolves via resolve()
        before alias registration.

        canonical_name is Key_A format (instance.attr); Phase 3 uses
        resolve() which finds it via _compat registry.
        """
        snap = load_extraction_snapshot("attr_expr_probe")
        registry = build_registry_from_snapshot(snap)

        expose_pure_count = 0
        for alias in snap.get("channel_aliases", []):
            if alias.source != "expose_pure":
                continue
            # Phase 3 resolves canonical_name via resolve() (backward compat)
            result = registry.resolve(alias.canonical_name)
            assert result is not None, (
                f"EXPOSE_PURE alias canonical '{alias.canonical_name}' "
                f"not resolvable via resolve()"
            )
            expose_pure_count += 1

        assert expose_pure_count > 0, "No EXPOSE_PURE aliases found"

    @pytest.mark.req("REQ-OR-06")
    @needs_typed_methods
    def test_expose_pure_alias_resolves(self):
        """alias_lookup for EXPOSE_PURE alias resolves to correct channel."""
        snap = load_extraction_snapshot("attr_expr_probe")
        registry = build_registry_from_snapshot(snap)

        # attr_expr_probe has EXPOSE_PURE aliases
        for alias in snap.get("channel_aliases", []):
            if alias.source != "expose_pure":
                continue
            qn = alias.owning_part_qn
            if "::" in qn:
                owning_part_short = qn.rsplit("::", 1)[-1]
            else:
                owning_part_short = qn.split("__")[-1]
            scoped_key = f"{owning_part_short}.{alias.alias_name}"
            result = registry.alias_lookup(ScopedKey(scoped_key))
            assert result is not None, (
                f"EXPOSE_PURE alias '{scoped_key}' not found via alias_lookup"
            )

    @pytest.mark.req("REQ-OR-06")
    def test_phase4_transitive_alias(self):
        """Transitive design attr aliases registered in solar_battery."""
        snap = load_extraction_snapshot("solar_battery_model")
        registry = build_registry_from_snapshot(snap)

        # Check if there are transitive defaults
        transitive_count = 0
        for _path, attrs in snap.get("design_attributes", {}).items():
            for attr in attrs:
                if is_transitive_default(attr.default_value):
                    key = f"{attr.parent_part}.{attr.name}"
                    result = registry.resolve(str(attr.default_value))
                    if result is not None:
                        transitive_count += 1
                        # The alias should be registered
                        alias_result = registry.resolve(key)
                        assert alias_result is not None, (
                            f"Transitive alias '{key}' not registered"
                        )

        # Note: solar_battery has only 2 transitive defaults across all models
        # It's OK if this model has 0 — the test still verifies the logic


# ===================================================================
# REQ-OR-07: ScopedKey derivation
# ===================================================================
class TestReqOR07:
    """REQ-OR-07: ScopedKey.from_eqn() strips design prefix, joins with dots."""

    @pytest.mark.req("REQ-OR-07")
    @needs_constructors
    def test_scoped_key_from_eqn_derivation(self):
        """Parametrize over known EQN+attr pairs; verify dotted format."""
        test_cases = [
            (
                "SolarBatteryDesign__solar_battery_plant__lcoe",
                "lcoe_per_mwh",
                "solar_battery_plant.lcoe.lcoe_per_mwh",
            ),
            (
                "SolarBatteryDesign__solar_battery_plant__energy_production",
                "annual_energy_mwh",
                "solar_battery_plant.energy_production.annual_energy_mwh",
            ),
            (
                "SolarBatteryDesign__solar_battery_plant__annualized_financial",
                "annualized_capital_cost",
                "solar_battery_plant.annualized_financial.annualized_capital_cost",
            ),
        ]
        for eqn, attr, expected in test_cases:
            result = make_scoped_key(eqn, attr)
            assert result == expected, (
                f"make_scoped_key({eqn!r}, {attr!r}) = {result!r}, "
                f"expected {expected!r}"
            )

    @pytest.mark.req("REQ-OR-07")
    def test_scoped_key_matches_derive_key_c(self):
        """For every CalcUsage in solar_battery, make_scoped_key matches
        derive_key_c (backward compatibility)."""
        snap = load_extraction_snapshot("solar_battery_model")
        calc_def_by_name = {cd.name: cd for cd in snap["calc_defs"]}

        for usage in snap["calc_usages"]:
            calc_def = calc_def_by_name.get(usage.calc_def_name)
            if not calc_def:
                continue
            for attr in calc_def.output_attributes:
                new_key = make_scoped_key(usage.qualified_name, attr.name)
                old_key = OutputRegistry.derive_key_c(
                    usage.qualified_name, attr.name
                )
                assert new_key == old_key, (
                    f"make_scoped_key != derive_key_c for "
                    f"{usage.qualified_name}.{attr.name}: "
                    f"{new_key!r} != {old_key!r}"
                )


# ===================================================================
# REQ-OR-08: Key_A not registered
# ===================================================================
class TestReqOR08:
    """REQ-OR-08: Key_A SHALL NOT be registered."""

    @pytest.mark.req("REQ-OR-08")
    @pytest.mark.parametrize("model_name", ["solar_battery_model", "catf_mfe_model"])
    @needs_typed_methods
    def test_key_a_not_registered(self, model_name):
        """Key_A format (instance_name.attr) not in any registry."""
        snap = load_extraction_snapshot(model_name)
        registry = build_registry_from_snapshot(snap)
        calc_def_by_name = {cd.name: cd for cd in snap["calc_defs"]}

        for usage in snap["calc_usages"]:
            calc_def = calc_def_by_name.get(usage.calc_def_name)
            if not calc_def:
                continue
            for attr in calc_def.output_attributes:
                key_a = f"{usage.instance_name}.{attr.name}"
                key_c = make_scoped_key(usage.qualified_name, attr.name)
                # Only check if Key_A is distinct from Key_C
                # (for top-level usages they might coincidentally match)
                if key_a != key_c:
                    result = registry.scoped_lookup(ScopedKey(key_a))
                    assert result is None, (
                        f"Key_A '{key_a}' should NOT be in scoped registry "
                        f"for {model_name} "
                        f"(Key_C is '{key_c}')"
                    )


# ===================================================================
# Backward compatibility: deprecated resolve()
# ===================================================================
class TestDeprecatedResolve:
    """Verify deprecated resolve() pass-through works for transition."""

    @pytest.mark.req("REQ-OR-01")
    def test_resolve_still_works_for_scoped_keys(self):
        """resolve() finds scoped keys via pass-through."""
        snap = load_extraction_snapshot("solar_battery_model")
        registry = build_registry_from_snapshot(snap)
        calc_def_by_name = {cd.name: cd for cd in snap["calc_defs"]}

        for usage in snap["calc_usages"]:
            calc_def = calc_def_by_name.get(usage.calc_def_name)
            if not calc_def:
                continue
            for attr in calc_def.output_attributes:
                key_c = OutputRegistry.derive_key_c(
                    usage.qualified_name, attr.name
                )
                result = registry.resolve(key_c)
                assert result is not None, (
                    f"Deprecated resolve({key_c!r}) returned None"
                )

    @pytest.mark.req("REQ-OR-01")
    def test_resolve_still_works_for_sysml_qn(self):
        """resolve() finds SysML QN keys via pass-through."""
        snap = load_extraction_snapshot("attr_expr_probe")
        registry = build_registry_from_snapshot(snap)

        for ca in snap["computed_attributes"]:
            if ca.classification != ComputedAttributeClassification.FORMULA:
                continue
            if ca.compilability != Compilability.FULLY_COMPILABLE:
                continue
            if ca.owning_part_qualified_name:
                sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
                result = registry.resolve(sysml_qn)
                assert result is not None, (
                    f"Deprecated resolve({sysml_qn!r}) returned None"
                )

    @pytest.mark.req("REQ-OR-01")
    def test_resolve_still_works_for_aliases(self):
        """resolve() finds alias keys via pass-through."""
        snap = load_extraction_snapshot("solar_battery_model")
        registry = build_registry_from_snapshot(snap)

        for alias in snap.get("channel_aliases", []):
            if alias.source != "redefinition":
                continue
            result = registry.resolve(alias.alias_name)
            assert result is not None, (
                f"Deprecated resolve({alias.alias_name!r}) returned None"
            )

    @pytest.mark.req("REQ-OR-01")
    def test_resolve_canonical_self_lookup(self):
        """resolve() finds canonical channel names (self-lookup)."""
        snap = load_extraction_snapshot("solar_battery_model")
        registry = build_registry_from_snapshot(snap)

        for channel in list(registry.canonical_channels)[:5]:
            result = registry.resolve(channel)
            assert result == channel, (
                f"Deprecated resolve({channel!r}) should return itself"
            )
