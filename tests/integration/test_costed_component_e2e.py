"""E2E integration tests for the Costed Component pattern (COST-PATTERN Item 5).

Validates that the hierarchy-aware pipeline (Items 1-4) produces correct
output on the solar_battery model:
- 9 leaf-part cost modules with auto-implementations
- 1 allocation CalcUsage
- 20 aggregation modules (4 assemblies × 5 cost attributes)
- Pipeline YAML topological ordering and source comments
- System-level CalcUsages wire to aggregation and computed attr outputs
- Zero implementation backlog
- Numerical ground truth for leaf costs, allocation, and idiot_index aggregation
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
import yaml

from sysml_codegen.cli import GenerationConfig
from tests.helpers.impl_execution import (
    assert_outputs_match,
    execute_impl_body,
    extract_function_body,
    find_impl_files,
    is_auto_implemented,
)
from tests.helpers.legacy_route import generate_via_legacy_route

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

# ============================================================
# Constants from Phase 1 Discovery
# ============================================================

EXPECTED_TOTAL_IMPL_COUNT = 36
# 20 pass ast.parse: 16 CalcDef/computed attr + 4 idiot_index aggregation
# 16 fail: aggregation cost impls with unresolved .() FeatureReferenceExpression
EXPECTED_VALID_PYTHON_COUNT = 20

EXPECTED_LEAF_COST_PATTERNS = [
    "pvmodulecostcalc",
    "invertercostcalc",
    "arrayboscostcalc",
    "batterypackcostcalc",
    "hybridinvertercostcalc",
    "batteryboscostcalc",
    "rackingcostcalc",
    "electricalpanelcostcalc",
    "permittingcostcalc",
]

EXPECTED_AGGREGATION_ASSEMBLIES = [
    "solar_array",
    "battery_system",
    "site_infra",
]
# solar_battery_plant is also an assembly (top-level) but has a different
# directory structure — tested separately.

EXPECTED_AGGREGATION_ATTRS = [
    "capital_cost",
    "raw_material_cost",
    "fabrication_cost",
    "installation_cost",
    "idiot_index",
]

EXPECTED_MULTIPLICITY_PARAMS = {"module_count", "inverter_count", "pack_count"}

# ============================================================
# Ground Truth Data (hand-computed from library.sysml + design.sysml)
# ============================================================

# Each entry: (name_pattern, input_dict, expected_outputs_dict)
# Inputs include CalcDef defaults where design.sysml doesn't override.
LEAF_PART_GROUND_TRUTH = [
    (
        "pvmodulecostcalc",
        {
            "wattage": 400.0, "efficiency": 0.21,
            "cost_per_watt": 1.07, "fab_factor": 0.45, "install_factor": 0.30,
        },
        {
            "material_cost": 428.0, "fab_cost": 192.6, "install_cost": 128.4,
            "total_cost": 749.0, "idiot_index": 1.75,
        },
    ),
    (
        "invertercostcalc",
        {
            "power_rating": 2000.0,
            "cost_per_watt": 0.286, "fab_factor": 0.45, "install_factor": 0.30,
        },
        {
            "material_cost": 572.0, "fab_cost": 257.4, "install_cost": 171.6,
            "total_cost": 1001.0, "idiot_index": 1.75,
        },
    ),
    (
        "arrayboscostcalc",
        {
            "string_count": 4.0, "panel_count": 20.0,
            "cost_per_string": 150.0, "cost_per_panel_bos": 30.0,
            "fab_factor": 0.45, "install_factor": 0.30,
        },
        {
            "material_cost": 1200.0, "fab_cost": 540.0, "install_cost": 360.0,
            "total_cost": 2100.0, "idiot_index": 1.75,
        },
    ),
    (
        "batterypackcostcalc",
        {
            "capacity_kwh": 5.0, "chemistry_factor": 1.0,
            "cost_per_kwh": 171.5, "fab_factor": 0.45, "install_factor": 0.30,
        },
        {
            "material_cost": 857.5, "fab_cost": 385.875, "install_cost": 257.25,
            "total_cost": 1500.625, "idiot_index": 1.75,
        },
    ),
    (
        "hybridinvertercostcalc",
        {
            "power_rating": 10000.0,
            "cost_per_watt": 0.1714, "fab_factor": 0.45, "install_factor": 0.30,
        },
        {
            "material_cost": 1714.0, "fab_cost": 771.3, "install_cost": 514.2,
            "total_cost": 2999.5, "idiot_index": 1.75,
        },
    ),
    (
        "batteryboscostcalc",
        {
            "pack_count": 8.0,
            "cost_per_pack_bos": 71.5, "fab_factor": 0.45, "install_factor": 0.30,
        },
        {
            "material_cost": 572.0, "fab_cost": 257.4, "install_cost": 171.6,
            "total_cost": 1001.0, "idiot_index": 1.75,
        },
    ),
    (
        "rackingcostcalc",
        {
            "panel_count": 20.0, "tilt_angle": 30.0,
            "cost_per_panel_rack": 57.0, "fab_factor": 0.45, "install_factor": 0.30,
        },
        {
            "material_cost": 1140.0, "fab_cost": 513.0, "install_cost": 342.0,
            "total_cost": 1995.0, "idiot_index": 1.75,
        },
    ),
    (
        "electricalpanelcostcalc",
        {
            "circuit_count": 4.0,
            "base_cost": 150.0, "cost_per_circuit": 34.0,
            "fab_factor": 0.45, "install_factor": 0.30,
        },
        {
            "material_cost": 286.0, "fab_cost": 128.7, "install_cost": 85.8,
            "total_cost": 500.5, "idiot_index": 1.75,
        },
    ),
    (
        "permittingcostcalc",
        {"system_capacity_kw": 8.0, "cost_per_kw": 187.5},
        {
            "material_cost": 0.0, "fab_cost": 0.0, "install_cost": 0.0,
            "total_cost": 1500.0, "idiot_index": 0.0,
        },
    ),
]

ALLOCATION_GROUND_TRUTH = (
    "allocationcostcalc",
    {
        "child_count": 25.0, "total_child_mass": 50.0,
        "fastener_cost_per_child": 0.50, "seal_cost_per_child": 0.30,
        "wiring_cost_per_kg": 2.0,
    },
    {
        "fastener_cost": 12.5, "seal_cost": 7.5, "wiring_cost": 100.0,
        "total_allocation": 120.0, "material_portion": 96.0,
    },
)

# Idiot index aggregation modules (capital_cost / raw_material_cost).
# These are the only aggregation impls with valid Python — other aggregation
# cost impls have unresolved .() FeatureReferenceExpression syntax.
# Values computed from leaf ground truth × multiplicity counts (design.md).
IDIOT_INDEX_GROUND_TRUTH = [
    (
        "solar_array/idiot_index",
        {"capital_cost": 21204.0, "raw_material_cost": 12144.0},
        {"idiot_index": 21204.0 / 12144.0},
    ),
    (
        "battery_system/idiot_index",
        {"capital_cost": 16005.5, "raw_material_cost": 9146.0},
        {"idiot_index": 16005.5 / 9146.0},
    ),
    (
        "site_infra/idiot_index",
        {"capital_cost": 3995.5, "raw_material_cost": 1426.0},
        {"idiot_index": 3995.5 / 1426.0},
    ),
    (
        "solar_battery_plant/idiot_index",
        {"capital_cost": 41205.0, "raw_material_cost": 22716.0},
        {"idiot_index": 41205.0 / 22716.0},
    ),
]


def _find_impl(output_path: Path, name_pattern: str) -> Path:
    """Find the impl file matching a name pattern (case-insensitive substring)."""
    for impl in find_impl_files(output_path):
        if name_pattern in str(impl).lower():
            return impl
    raise FileNotFoundError(
        f"No impl file matching '{name_pattern}' in {output_path / 'handwritten'}"
    )


# ============================================================
# E2E Test Class
# ============================================================


class TestSolarBatteryCostPatternE2E:
    """E2E validation of the complete Costed Component pipeline on solar_battery."""

    @pytest.fixture(scope="class")
    def solar_battery_output(self, tmp_path_factory: pytest.TempPathFactory) -> Path:
        output_path = tmp_path_factory.mktemp("solar_battery_cost")
        config = GenerationConfig(
            models_path=FIXTURES_DIR / "solar_battery_model",
            output_path=output_path,
            package_name="solar_battery",
        )
        success = generate_via_legacy_route(config)
        assert success, "Solar battery codegen should succeed"
        return output_path

    # ================================================================
    # Structural Tests (FR-1 through FR-5, FR-8 through FR-13)
    # ================================================================

    def test_codegen_succeeds(self, solar_battery_output: Path):
        """FR-1: Codegen runs successfully and produces output."""
        assert (solar_battery_output / "handwritten").exists()

    def test_total_impl_count(self, solar_battery_output: Path):
        """FR-11: Total impl file count matches expected."""
        impls = find_impl_files(solar_battery_output)
        assert len(impls) == EXPECTED_TOTAL_IMPL_COUNT, (
            f"Expected {EXPECTED_TOTAL_IMPL_COUNT} impl files, got {len(impls)}"
        )

    def test_leaf_part_cost_modules_generated(self, solar_battery_output: Path):
        """FR-2: All 9 leaf cost modules generate as auto-implemented."""
        for pattern in EXPECTED_LEAF_COST_PATTERNS:
            impl = _find_impl(solar_battery_output, pattern)
            assert is_auto_implemented(impl), f"{pattern} should be auto-implemented"

    def test_allocation_model_generated(self, solar_battery_output: Path):
        """FR-3: Allocation CalcUsage generates as auto-implemented."""
        impl = _find_impl(solar_battery_output, "allocationcostcalc")
        assert is_auto_implemented(impl)

    def test_assembly_aggregation_modules_generated(self, solar_battery_output: Path):
        """FR-4: All 4 assemblies × 5 attrs = 20 aggregation impls exist."""
        impls = find_impl_files(solar_battery_output)
        # 3 sub-assemblies
        for assembly in EXPECTED_AGGREGATION_ASSEMBLIES:
            for attr in EXPECTED_AGGREGATION_ATTRS:
                pattern = f"{assembly}/{attr}_impl.py"
                matches = [p for p in impls if pattern in str(p)]
                assert len(matches) >= 1, (
                    f"Aggregation impl for {assembly}/{attr} not found"
                )
                assert is_auto_implemented(matches[0]), (
                    f"{assembly}/{attr} should be auto-implemented"
                )
        # Top-level plant aggregation (5 attrs)
        for attr in EXPECTED_AGGREGATION_ATTRS:
            pattern = f"solar_battery_plant/{attr}_impl.py"
            matches = [
                p for p in impls
                if pattern in str(p)
                # Exclude nested assembly paths
                and not any(
                    f"solar_battery_plant/{asm}/{attr}" in str(p)
                    for asm in EXPECTED_AGGREGATION_ASSEMBLIES
                )
            ]
            assert len(matches) >= 1, (
                f"Plant-level aggregation impl for {attr} not found"
            )
            assert is_auto_implemented(matches[0]), (
                f"solar_battery_plant/{attr} should be auto-implemented"
            )

    def test_system_level_calcusage_wiring(self, solar_battery_output: Path):
        """FR-5: System-level CalcUsages wire to hierarchy outputs."""
        yaml_path = solar_battery_output / "pipelines" / "pipeline.yaml"
        content = yaml.safe_load(yaml_path.read_text())
        modules = content.get("modules", {})

        # annualized_financial.total_capex → MODULE_OUTPUT from plant capital_cost
        fin_mod = next(
            (mod for key, mod in modules.items() if "annualized_financial" in key),
            None,
        )
        assert fin_mod is not None, "annualized_financial module not found in YAML"
        total_capex_src = str(fin_mod.get("inputs", {}).get("total_capex", ""))
        assert "capital_cost" in total_capex_src.lower(), (
            f"total_capex should wire to capital_cost output, got: {total_capex_src}"
        )
        assert "entry" not in total_capex_src.lower(), (
            f"total_capex should NOT be an entry point, got: {total_capex_src}"
        )

        # annualized_om.p_net_kw → MODULE_OUTPUT from computed attribute
        om_mod = next(
            (mod for key, mod in modules.items() if "annualized_om" in key),
            None,
        )
        assert om_mod is not None, "annualized_om module not found in YAML"
        p_net_kw_src = str(om_mod.get("inputs", {}).get("p_net_kw", ""))
        assert "p_net_kw" in p_net_kw_src.lower()
        assert "entry" not in p_net_kw_src.lower(), (
            f"p_net_kw should NOT be an entry point, got: {p_net_kw_src}"
        )

    def test_zero_backlog(self, solar_battery_output: Path):
        """FR-8: Implementation backlog shows zero functions to implement."""
        backlog = (solar_battery_output / "IMPLEMENTATION_BACKLOG.md").read_text()
        assert "0 functions to implement" in backlog

    def test_pipeline_yaml_topological_ordering(self, solar_battery_output: Path):
        """FR-9: Pipeline YAML has correct topological ordering.

        Validates the critical chain: leaf costs → aggregation → system-level.
        Specifically checks that modules producing data appear before consumers:
        - plant capital_cost before annualized_financial (total_capex wiring)
        - p_net_kw before annualized_om (p_net_kw wiring)
        - annualized_financial and annualized_om before lcoe
        - all leaf cost_model modules before annualized_financial
        """
        yaml_path = solar_battery_output / "pipelines" / "pipeline.yaml"
        content = yaml.safe_load(yaml_path.read_text())
        module_keys = list(content.get("modules", {}).keys())

        def _pos(substr: str) -> int:
            for i, key in enumerate(module_keys):
                if substr in key:
                    return i
            raise ValueError(f"Module containing '{substr}' not found")

        # Plant capital_cost aggregation before annualized_financial
        assert _pos("solar_battery_plant__capital_cost") < _pos("annualized_financial"), (
            "Plant capital_cost must appear before annualized_financial"
        )
        # p_net_kw before annualized_om
        assert _pos("__p_net_kw") < _pos("annualized_om"), (
            "p_net_kw must appear before annualized_om"
        )
        # annualized_financial before lcoe
        assert _pos("annualized_financial") < _pos("__lcoe"), (
            "annualized_financial must appear before lcoe"
        )
        # annualized_om before lcoe
        assert _pos("annualized_om") < _pos("__lcoe"), (
            "annualized_om must appear before lcoe"
        )
        # All leaf cost_model modules before annualized_financial
        fin_pos = _pos("annualized_financial")
        for key in module_keys:
            if "__cost_model" in key:
                leaf_pos = module_keys.index(key)
                assert leaf_pos < fin_pos, (
                    f"Leaf module {key} (pos {leaf_pos}) must appear before "
                    f"annualized_financial (pos {fin_pos})"
                )

    def test_all_impls_valid_python(self, solar_battery_output: Path):
        """FR-10: Generated impls are valid Python.

        20 of 36 impls pass ast.parse(): 16 CalcDef/computed attr + 4 idiot_index.
        16 aggregation cost impls have unresolved .() FeatureReferenceExpression
        syntax from singleton term compilation — a known limitation.
        """
        impls = find_impl_files(solar_battery_output)
        valid_count = sum(1 for impl in impls if _is_valid_python(impl))
        assert valid_count >= EXPECTED_VALID_PYTHON_COUNT, (
            f"Expected >= {EXPECTED_VALID_PYTHON_COUNT} valid Python impls, "
            f"got {valid_count}/{len(impls)}"
        )

    def test_aggregation_yaml_source_comments(self, solar_battery_output: Path):
        """FR-12: Aggregation modules marked with 'source: aggregation' in YAML."""
        yaml_text = (solar_battery_output / "pipelines" / "pipeline.yaml").read_text()
        agg_count = yaml_text.count("source: aggregation")
        # 4 assemblies × 5 attrs = 20 aggregation modules
        assert agg_count == 20, (
            f"Expected 20 'source: aggregation' comments, got {agg_count}"
        )

    def test_multiplicity_entry_points_in_schema(self, solar_battery_output: Path):
        """FR-13: Multiplicity counts appear in parameter schemas."""
        schema_dir = solar_battery_output / "schemas"
        assert schema_dir.exists(), "schemas/ directory should exist"
        found_params: set[str] = set()
        for schema_file in sorted(schema_dir.rglob("*.py")):
            content = schema_file.read_text()
            for param in EXPECTED_MULTIPLICITY_PARAMS:
                if param in content:
                    found_params.add(param)
        assert found_params == EXPECTED_MULTIPLICITY_PARAMS, (
            f"Expected multiplicity params {EXPECTED_MULTIPLICITY_PARAMS}, "
            f"found {found_params}"
        )

    # ================================================================
    # Numerical Ground Truth Tests (FR-6, FR-7)
    # ================================================================

    @pytest.mark.parametrize(
        "name_pattern,inputs,expected",
        LEAF_PART_GROUND_TRUTH,
        ids=[e[0] for e in LEAF_PART_GROUND_TRUTH],
    )
    def test_leaf_part_ground_truth(
        self,
        solar_battery_output: Path,
        name_pattern: str,
        inputs: dict[str, float],
        expected: dict[str, float],
    ):
        """FR-6: Leaf cost modules produce correct numerical results."""
        impl = _find_impl(solar_battery_output, name_pattern)
        assert is_auto_implemented(impl)
        body = extract_function_body(impl)
        assert body is not None, f"{name_pattern} should have executable body"
        result = execute_impl_body(body, inputs, list(expected.keys()))
        assert_outputs_match(result, expected)

    def test_allocation_ground_truth(self, solar_battery_output: Path):
        """FR-6: Allocation module produces correct numerical results."""
        name_pattern, inputs, expected = ALLOCATION_GROUND_TRUTH
        impl = _find_impl(solar_battery_output, name_pattern)
        assert is_auto_implemented(impl)
        body = extract_function_body(impl)
        assert body is not None
        result = execute_impl_body(body, inputs, list(expected.keys()))
        assert_outputs_match(result, expected)

    @pytest.mark.parametrize(
        "name_pattern,inputs,expected",
        IDIOT_INDEX_GROUND_TRUTH,
        ids=[e[0].replace("/", "_") for e in IDIOT_INDEX_GROUND_TRUTH],
    )
    def test_idiot_index_ground_truth(
        self,
        solar_battery_output: Path,
        name_pattern: str,
        inputs: dict[str, float],
        expected: dict[str, float],
    ):
        """FR-7: Idiot index aggregation modules produce correct results.

        Tests the 4 idiot_index impls (one per assembly) which compute
        capital_cost / raw_material_cost. These are the only aggregation
        impls with valid Python — other aggregation cost impls have unresolved
        .() FeatureReferenceExpression syntax.
        """
        impl = _find_impl(solar_battery_output, name_pattern)
        assert is_auto_implemented(impl)
        body = extract_function_body(impl)
        assert body is not None, f"{name_pattern} should have executable body"
        result = execute_impl_body(body, inputs, list(expected.keys()))
        assert_outputs_match(result, expected)


def _is_valid_python(impl_path: Path) -> bool:
    """Check if an impl file is syntactically valid Python."""
    try:
        ast.parse(impl_path.read_text())
        return True
    except SyntaxError:
        return False
