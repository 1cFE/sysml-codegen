"""End-to-end integration tests for expression-aware code generation.

Validates that the expression compiler + codegen pipeline produces
numerically correct auto-implementations on real SysML models:
- chain_spike (3 CalcDefs, all Pattern A)
- solar_battery (15 CalcDefs, Patterns A/C/D)
- CATF MFE (21 CalcDefs, Patterns A/B/C/D)
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from tests.helpers.impl_execution import (
    assert_outputs_match,
    execute_impl_body,
    extract_function_body,
    find_impl_files,
    is_auto_implemented,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

SOLAR_BATTERY_HANDWRITTEN_DIR = Path(
    "/home/reid/1cfe/fusion-tea/generated/solar_battery/"
    "handwritten/solarbatterylibrary"
)

# Parametrize data for solar_battery ground truth comparison.
# Each entry: (calc_name, handwritten_filename, input_dict, output_names)
SOLAR_BATTERY_GROUND_TRUTH = [
    ("energyproductioncalc", "energyproductioncalc_impl.py",
     {"p_net_mw": 100.0, "n_mod": 2.0, "plant_availability": 0.9},
     ["annual_energy_mwh"]),
    ("annualizedomcalc", "annualizedomcalc_impl.py",
     {"om_rate_per_kw_year": 20.0, "p_net_kw": 8.0},
     ["annual_om_cost"]),
    ("annualizedfuelcalc", "annualizedfuelcalc_impl.py",
     {"fuel_unit_cost": 10.0, "fuel_consumption": 50.0},
     ["annual_fuel_cost"]),
    ("annualizedfinancialcalc", "annualizedfinancialcalc_impl.py",
     {"total_capex": 1000.0, "discount_rate": 0.05, "plant_lifetime": 25.0},
     ["capital_recovery_factor", "annualized_capital_cost"]),
    ("lcoecalc", "lcoecalc_impl.py",
     {"annualized_capital_cost": 100.0, "annual_om_cost": 20.0,
      "annual_fuel_cost": 5.0, "yearly_inflation": 0.025,
      "plant_lifetime": 25.0, "annual_energy_mwh": 1000.0},
     ["lcoe_per_mwh"]),
]


def _find_impl(output_path: Path, calc_name: str) -> Path:
    """Find the impl file matching a calc name (case-insensitive substring)."""
    for impl in find_impl_files(output_path):
        if calc_name in impl.name:
            return impl
    raise FileNotFoundError(
        f"No impl file found for '{calc_name}' in {output_path / 'handwritten'}"
    )


# ---------------------------------------------------------------------------
# Chain Spike: 3 CalcDefs, all Pattern A (simple single-expression)
# ---------------------------------------------------------------------------

class TestChainSpikeAutoImpl:
    """Smoke tests: simplest model produces auto-implementations."""

    def test_all_three_calcdefs_auto_implemented(
        self, chain_spike_model_path: Path, tmp_path: Path,
    ):
        config = GenerationConfig(
            models_path=chain_spike_model_path,
            output_path=tmp_path / "output",
            package_name="chain_spike",
        )
        success = run_codegen(config)
        assert success, "Chain spike codegen should succeed"

        impls = find_impl_files(tmp_path / "output")
        assert len(impls) == 3, f"Expected 3 impl files, got {len(impls)}"

        for impl in impls:
            assert is_auto_implemented(impl), (
                f"{impl.name} should be auto-implemented"
            )
            content = impl.read_text()
            assert "NotImplementedError" not in content, (
                f"{impl.name} should not contain NotImplementedError"
            )

    def test_auto_impl_files_are_valid_python(
        self, chain_spike_model_path: Path, tmp_path: Path,
    ):
        config = GenerationConfig(
            models_path=chain_spike_model_path,
            output_path=tmp_path / "output",
            package_name="chain_spike",
        )
        run_codegen(config)

        for impl in find_impl_files(tmp_path / "output"):
            content = impl.read_text()
            ast.parse(content)  # Raises SyntaxError if invalid

    def test_backlog_empty_for_chain_spike(
        self, chain_spike_model_path: Path, tmp_path: Path,
    ):
        config = GenerationConfig(
            models_path=chain_spike_model_path,
            output_path=tmp_path / "output",
            package_name="chain_spike",
        )
        run_codegen(config)

        backlog = (tmp_path / "output" / "IMPLEMENTATION_BACKLOG.md").read_text()
        assert "0 functions to implement" in backlog


# ---------------------------------------------------------------------------
# Solar Battery: 15 CalcDefs, Patterns A/C/D
# ---------------------------------------------------------------------------

class TestSolarBatteryValidation:
    """Validates epic success criteria: >=10/15 auto-implemented,
    ground truth comparison against handwritten impls."""

    @pytest.fixture(scope="class")
    def solar_battery_output(self, tmp_path_factory: pytest.TempPathFactory) -> Path:
        model_path = FIXTURES_DIR / "solar_battery_model"
        output_path = tmp_path_factory.mktemp("solar_battery")
        config = GenerationConfig(
            models_path=model_path,
            output_path=output_path,
            package_name="solar_battery",
        )
        success = run_codegen(config)
        assert success, "Solar battery codegen should succeed"
        return output_path

    def test_auto_implementation_count(self, solar_battery_output: Path):
        impls = find_impl_files(solar_battery_output)
        # 15 CalcDef impls + 1 computed attribute auto-impl (p_net_kw) + 20 aggregation modules
        assert len(impls) == 36, f"Expected 36 impl files, got {len(impls)}"

        auto_count = sum(1 for p in impls if is_auto_implemented(p))
        assert auto_count >= 10, (
            f"Epic success criterion: >= 10 auto-implemented, got {auto_count}"
        )

    def test_non_compilable_calcdefs_get_stubs(self, solar_battery_output: Path):
        for impl in find_impl_files(solar_battery_output):
            if not is_auto_implemented(impl):
                content = impl.read_text()
                assert "NotImplementedError" in content, (
                    f"{impl.name} is not auto-implemented but has no "
                    "NotImplementedError stub"
                )

    @pytest.mark.skipif(
        not SOLAR_BATTERY_HANDWRITTEN_DIR.exists(),
        reason="Solar battery handwritten impls not available "
               "(requires fusion-tea repo)",
    )
    @pytest.mark.parametrize(
        "calc_name,hw_file,inputs,outputs",
        SOLAR_BATTERY_GROUND_TRUTH,
    )
    def test_ground_truth(
        self,
        solar_battery_output: Path,
        calc_name: str,
        hw_file: str,
        inputs: dict[str, float],
        outputs: list[str],
    ):
        # Execute auto-generated impl
        auto_impl = _find_impl(solar_battery_output, calc_name)
        auto_body = extract_function_body(auto_impl)
        assert auto_body is not None, f"{calc_name} auto-impl is a stub"
        auto_result = execute_impl_body(auto_body, inputs, outputs)

        # Execute handwritten impl
        hw_path = SOLAR_BATTERY_HANDWRITTEN_DIR / hw_file
        hw_body = extract_function_body(hw_path)
        assert hw_body is not None, f"{calc_name} handwritten impl is a stub"
        hw_result = execute_impl_body(hw_body, inputs, outputs)

        # Compare: auto-generated output must match handwritten within 1e-10
        assert_outputs_match(auto_result, hw_result)

    def test_backlog_excludes_auto_implemented(self, solar_battery_output: Path):
        backlog = (solar_battery_output / "IMPLEMENTATION_BACKLOG.md").read_text()
        assert "0 functions to implement" in backlog


# ---------------------------------------------------------------------------
# CATF MFE: 21 CalcDefs, Patterns A/B/C/D
# ---------------------------------------------------------------------------

class TestCATFMFEValidation:
    """Validates CATF model classification and Pattern B ground truth."""

    @pytest.fixture(scope="class")
    def catf_mfe_output(self, tmp_path_factory: pytest.TempPathFactory) -> Path:
        """catf_mfe generation succeeds — Item 10 wired the cross-part pin (SC-1).

        The cross-part ``cryo_load.magnet_volume = catf_radial_build.magnet_volume_total``
        binding used to fall to a valueless V11 fallback that aborted strict
        generation. Item 10's multi-hop EXPOSE confirm pass now resolves
        ``magnet_volume_total = tf_coil.volume`` (an alias terminal) transitively
        to the ``tf_coil.volume_calc.volume`` channel and registers the alias, so
        the consumer wires and generation is clean again. This fixture pins the
        flip; the downstream tests validate the generated output.
        """
        model_path = FIXTURES_DIR / "catf_mfe_model"
        output_path = tmp_path_factory.mktemp("catf_mfe")
        config = GenerationConfig(
            models_path=model_path,
            output_path=output_path,
            package_name="catf_mfe",
        )
        success = run_codegen(config)
        assert success is True, (
            "catf_mfe generation must succeed — Item 10 wired the magnet_volume "
            "cross-part pin"
        )
        return output_path

    def test_codegen_succeeds(self, catf_mfe_output: Path):
        assert (catf_mfe_output / "handwritten").exists()

    def test_auto_implementation_classification(self, catf_mfe_output: Path):
        # Graph-only pipeline (REQ-PIPE-07): only CalcDefs with usages in the
        # computation graph get stencils.  CATF MFE has 21 CalcDefs extracted
        # but 3 (ThermalCycleEfficiency, PlasmaConfinement, TritiumBreedingRatio)
        # have no calc usages → 18 modules, all FULLY_COMPILABLE.
        impls = find_impl_files(catf_mfe_output)
        assert len(impls) == 18, f"Expected 18 impl files, got {len(impls)}"

        auto_count = sum(1 for p in impls if is_auto_implemented(p))
        stub_count = len(impls) - auto_count

        assert auto_count == 18, (
            f"Expected 18 auto-implemented (all graph modules FC), got {auto_count}"
        )
        assert stub_count == 0, (
            f"Expected 0 stubs (unused CalcDefs excluded from graph), "
            f"got {stub_count}"
        )

    def test_unused_calcdefs_excluded_from_graph_output(
        self, catf_mfe_output: Path,
    ):
        """Graph-only pipeline (REQ-PIPE-07): CalcDefs without calc usages
        are not in the computation graph and produce no output files.

        PlasmaConfinement and TritiumBreedingRatio are defined in the CATF MFE
        model but have no usages, so they should NOT appear in generated output.
        """
        impls = find_impl_files(catf_mfe_output)
        impl_names = {p.stem for p in impls}

        # These CalcDefs have no usages → not in graph → no stencils
        assert "plasmaconfinement_impl" not in impl_names, (
            "PlasmaConfinement has no usages and should not be in graph output"
        )
        assert "tritiumbreedingratio_impl" not in impl_names, (
            "TritiumBreedingRatio has no usages and should not be in graph output"
        )

        # Backlog should NOT list them (they're not in the graph)
        backlog = (catf_mfe_output / "IMPLEMENTATION_BACKLOG.md").read_text()
        assert "PlasmaConfinement" not in backlog
        assert "TritiumBreedingRatio" not in backlog

    def test_pattern_b_engineering_q_factor(self, catf_mfe_output: Path):
        # Hand-computed from SysML expressions (performance_metrics.sysml:140):
        # q_eng = p_electric_gross / p_auxiliary_total = 1500.0 / 200.0 = 7.5
        # f_recirculating = 1.0 / q_eng = 1.0 / 7.5 = 0.13333...
        # p_net = p_electric_gross * (1.0 - f_recirculating)
        #       = 1500.0 * (1.0 - 0.13333...) = 1500.0 * 0.86666... = 1300.0

        inputs = {"p_electric_gross": 1500.0, "p_auxiliary_total": 200.0}
        expected = {
            "q_eng": 7.5,
            "f_recirculating": 1.0 / 7.5,
            "p_net": 1300.0,
        }

        impl = _find_impl(catf_mfe_output, "engineeringqfactor")
        assert is_auto_implemented(impl)
        body = extract_function_body(impl)
        assert body is not None
        result = execute_impl_body(body, inputs, list(expected.keys()))
        assert_outputs_match(result, expected)

    def test_pattern_b_magnet_cryogenic_load(self, catf_mfe_output: Path):
        # Hand-computed from SysML expressions (thermal_loads.sysml:45):
        # nuclear_heating = 0.05 * p_neutron * (magnet_surface_area / first_wall_area)
        #                 = 0.05 * 2000.0 * (500.0 / 800.0) = 62.5
        # ac_losses = 0.0
        # heat_leak = magnet_volume * 0.05 = 100.0 * 0.05 = 5.0
        # thermal_load_cryo = nuclear_heating + ac_losses + heat_leak
        #                   = 62.5 + 0.0 + 5.0 = 67.5
        # cooling_power = (thermal_load_cryo / operating_temp) * (300.0 / carnot_efficiency)
        #               = (67.5 / 20.0) * (300.0 / 0.3) = 3.375 * 1000.0 = 3375.0

        inputs = {
            "magnet_volume": 100.0,
            "magnet_surface_area": 500.0,
            "first_wall_area": 800.0,
            "p_neutron": 2000.0,
            "b_field": 12.0,
            "operating_temp": 20.0,
            "carnot_efficiency": 0.3,
        }
        expected = {"cooling_power": 3375.0}

        impl = _find_impl(catf_mfe_output, "magnetcryogenicload")
        assert is_auto_implemented(impl)
        body = extract_function_body(impl)
        assert body is not None
        result = execute_impl_body(body, inputs, list(expected.keys()))
        assert_outputs_match(result, expected)

    def test_backlog_lists_only_non_compilable(self, catf_mfe_output: Path):
        # Graph-only pipeline: all 18 CATF MFE modules in the graph are
        # FULLY_COMPILABLE → 0 functions to implement in backlog.
        backlog = (catf_mfe_output / "IMPLEMENTATION_BACKLOG.md").read_text()
        assert "0 functions to implement" in backlog

        # Unused CalcDefs (PlasmaConfinement, TritiumBreedingRatio) are
        # excluded from the graph and must NOT appear in backlog.
        assert "PlasmaConfinement" not in backlog
        assert "TritiumBreedingRatio" not in backlog

        # Auto-implemented CalcDefs must NOT appear in backlog
        assert "EngineeringQFactor" not in backlog
        assert "MagnetCryogenicLoad" not in backlog
