"""Smoke test: OutputRegistry with real solar_battery model data.

Validates that the OutputRegistry key format contract holds for real
extracted data, not just synthetic fixtures. This catches key format
mismatches that would only surface with real SysIDE AST data.

See: spec "Smoke Test (real model data)" requirement.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.core.identifier_types import make_scoped_key
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.core.qualified_names import get_channel_name
from sysml_codegen.generation.initialization import build_pipeline_context
from tests.helpers.registry_compat import registry_resolve, registry_register

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestOutputRegistrySmokeRealData:
    """Build an OutputRegistry from real solar_battery data and verify resolution."""

    @pytest.fixture(scope="class")
    def pipeline_context(self):
        model_path = FIXTURES_DIR / "solar_battery_model"
        return build_pipeline_context([model_path])

    @pytest.fixture(scope="class")
    def registry(self, pipeline_context) -> OutputRegistry:
        """Build a Phase 1 registry from real extracted CalcUsage data."""
        reg = OutputRegistry()
        ctx = pipeline_context

        # Phase 1: Register CalcUsage outputs (Key_A, Key_B, Key_C)
        calc_def_map = {cd.name: cd for cd in ctx.calc_defs}
        for usage in ctx.calc_usages:
            calc_def = calc_def_map.get(usage.calc_def_name)
            if not calc_def:
                continue
            for attr in calc_def.output_attributes:
                canonical = get_channel_name(usage.qualified_name, attr.name)
                key_a = f"{usage.instance_name}.{attr.name}"
                key_b = canonical  # EQN format = canonical
                key_c = make_scoped_key(
                    usage.qualified_name, attr.name,
                )
                registry_register(reg,canonical, [key_a, key_b, key_c])

        return reg

    def test_registry_has_entries(self, registry: OutputRegistry):
        """Sanity: registry should have registered keys from real data."""
        assert len(registry) > 0, "Registry should have entries from solar_battery"

    def test_known_chain_source_path_resolves(self, registry: OutputRegistry):
        """A known CHAIN binding source_path resolves to non-None.

        solar_battery has CHAIN bindings in dotted format that should
        resolve via Key_C (dotted hierarchy path).
        """
        # lcoe.lcoe_per_mwh is a known concrete CalcUsage output (Key_A)
        result = registry_resolve(registry,"lcoe.lcoe_per_mwh")
        assert result is not None, (
            "Expected 'lcoe.lcoe_per_mwh' (Key_A) to resolve in "
            "solar_battery registry"
        )

    def test_key_c_resolves_for_virtual_calc_usage(self, registry: OutputRegistry):
        """A virtual CalcUsage output resolves via Key_C (dotted hierarchy).

        cost_model template instances produce outputs accessible only via
        Key_C in the real solar_battery model.
        """
        # This is a known virtual CalcUsage Key_C path from Spike 8
        key_c = "solar_battery_plant.solar_array.pv_module.cost_model.total_cost"
        result = registry_resolve(registry,key_c)
        assert result is not None, (
            f"Expected Key_C '{key_c}' to resolve for virtual CalcUsage "
            "in solar_battery registry"
        )
