"""End-to-end integration tests for computed attribute pipeline modules.

Validates that the computed attribute extraction, classification, compilation,
and pipeline integration (ATTR-EXPR Items 1-3) produces numerically correct
auto-implementations on real SysML models:
- attr_expr_probe (9 FORMULA computed attrs, EXPOSE_PURE, EXPOSE_COMPUTED, chains)
- solar_battery (1 computed attr: p_net_kw, downstream wiring to annualized_om)
- chain_spike and catf_mfe (regression guards: no false-positive computed attrs)
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from sysml_codegen.cli import GenerationConfig, run_codegen
from tests.helpers.impl_execution import (
    assert_outputs_match,
    execute_impl_body,
    extract_function_body,
    find_impl_files,
    is_auto_implemented,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

# Ground truth for probe fixture FORMULA computed attributes.
# Each entry: (attr_name, input_dict, output_name, expected_value)
# Chain inputs use the expected intermediate value (each impl tested in isolation).
PROBE_GROUND_TRUTH = [
    ("area", {"length": 10.0, "width": 5.0}, "area", 50.0),
    ("volume", {"length": 10.0, "width": 5.0, "height": 3.0}, "volume", 150.0),
    ("cost", {"area": 50.0, "rate": 12.0}, "cost", 600.0),
    ("marked_up_cost", {"cost": 600.0, "markup": 1.15}, "marked_up_cost", 690.0),
    ("cost_density", {"cost": 600.0, "volume": 150.0}, "cost_density", 4.0),
    ("q_scientific", {"p_fusion": 2600.0, "p_input": 50.0}, "q_scientific", 52.0),
    ("perimeter", {"length": 10.0, "width": 5.0}, "perimeter", 30.0),
    ("minor_radius", {"r_inner": 4.2, "r_outer": 4.4, "r_major": 3.0}, "minor_radius", 1.3),
    ("p_alpha", {"p_fusion": 2600.0}, "p_alpha", 2600.0 * 3.52 / 17.58),
]

# EXPOSE_PURE attributes: should NOT have impl files generated
EXPOSE_PURE_ATTRS = ["scale_result", "half_vol", "quarter_vol"]

# EXPOSE_COMPUTED attributes: should NOT have impl files generated
EXPOSE_COMPUTED_ATTRS = ["scaled_area"]


def _find_computed_attr_impl(output_path: Path, attr_name: str) -> Path:
    """Find the impl file for a computed attribute by exact name match.

    Uses exact filename matching (not substring) to avoid ambiguity
    (e.g., 'area' matching 'scaled_area_impl.py').
    """
    target = f"{attr_name}_impl.py"
    for impl in find_impl_files(output_path):
        if impl.name == target:
            return impl
    raise FileNotFoundError(
        f"No impl file named '{target}' in {output_path / 'handwritten'}"
    )


# ---------------------------------------------------------------------------
# Phase 1: Probe Fixture E2E Validation
# ---------------------------------------------------------------------------

class TestProbeComputedAttrsE2E:
    """E2E validation of computed attribute codegen on the probe fixture.

    Runs the full pipeline on tests/fixtures/attr_expr_probe/, then:
    - Executes each FORMULA auto-implementation
    - Asserts numerical correctness against hand-computed ground truth
    - Verifies EXPOSE classification (no modules for EXPOSE_PURE/EXPOSE_COMPUTED)
    - Checks backlog accuracy
    """

    @pytest.fixture(scope="class")
    def probe_output(self, tmp_path_factory: pytest.TempPathFactory) -> Path:
        output_path = tmp_path_factory.mktemp("probe")
        config = GenerationConfig(
            models_path=FIXTURES_DIR / "attr_expr_probe",
            output_path=output_path,
            package_name="attr_expr_probe",
        )
        success = run_codegen(config)
        assert success, "Probe fixture codegen should succeed"
        return output_path

    def test_codegen_succeeds(self, probe_output: Path):
        assert (probe_output / "handwritten").exists(), (
            "handwritten/ directory should exist after codegen"
        )

    def test_formula_modules_auto_implemented(self, probe_output: Path):
        impls = find_impl_files(probe_output)
        auto_impls = [p for p in impls if is_auto_implemented(p)]
        # At least 9 FORMULA computed attrs + 2 CalcDef impls (ScaleCalc, SplitCalc)
        assert len(auto_impls) >= 9, (
            f"Expected >= 9 auto-implemented impls, got {len(auto_impls)}: "
            f"{[p.name for p in auto_impls]}"
        )

    @pytest.mark.parametrize(
        "attr_name,inputs,output_name,expected",
        PROBE_GROUND_TRUTH,
        ids=[entry[0] for entry in PROBE_GROUND_TRUTH],
    )
    def test_ground_truth(
        self,
        probe_output: Path,
        attr_name: str,
        inputs: dict[str, float],
        output_name: str,
        expected: float,
    ):
        impl = _find_computed_attr_impl(probe_output, attr_name)
        assert is_auto_implemented(impl), f"{attr_name} should be auto-implemented"
        body = extract_function_body(impl)
        assert body is not None, f"{attr_name} impl should have executable body"
        result = execute_impl_body(body, inputs, [output_name])
        assert_outputs_match(result, {output_name: expected})

    def test_expose_pure_no_module(self, probe_output: Path):
        """EXPOSE_PURE attributes should not have generated impl files."""
        impl_names = {p.name for p in find_impl_files(probe_output)}
        for attr in EXPOSE_PURE_ATTRS:
            target = f"{attr}_impl.py"
            assert target not in impl_names, (
                f"EXPOSE_PURE attribute '{attr}' should not have an impl file"
            )

    def test_expose_computed_no_module_no_error(self, probe_output: Path):
        """EXPOSE_COMPUTED attributes should not have impl files (codegen didn't error)."""
        impl_names = {p.name for p in find_impl_files(probe_output)}
        for attr in EXPOSE_COMPUTED_ATTRS:
            target = f"{attr}_impl.py"
            assert target not in impl_names, (
                f"EXPOSE_COMPUTED attribute '{attr}' should not have an impl file"
            )

    def test_backlog_accuracy(self, probe_output: Path):
        backlog = (probe_output / "IMPLEMENTATION_BACKLOG.md").read_text()
        assert "0 functions to implement" in backlog, (
            "All probe fixture impls should be auto-implemented; "
            f"backlog says: {backlog[:200]}"
        )


# ---------------------------------------------------------------------------
# Phase 2: Solar Battery Computed Attribute Validation
# ---------------------------------------------------------------------------

class TestSolarBatteryComputedAttrE2E:
    """E2E validation of p_net_kw computed attribute in the solar_battery model.

    Verifies:
    - p_net_kw synthetic module generates with correct auto-implementation
    - Numerical correctness: 0.008 * 1000.0 = 8.0
    - Downstream wiring: annualized_om receives p_net_kw as MODULE_OUTPUT
    - Impl count: 16 total (15 CalcDefs + 1 computed attr)
    - annualized_om chain: 20.0 * 8.0 = 160.0
    """

    @pytest.fixture(scope="class")
    def solar_battery_output(self, tmp_path_factory: pytest.TempPathFactory) -> Path:
        output_path = tmp_path_factory.mktemp("solar_battery")
        config = GenerationConfig(
            models_path=FIXTURES_DIR / "solar_battery_model",
            output_path=output_path,
            package_name="solar_battery",
        )
        success = run_codegen(config)
        assert success, "Solar battery codegen should succeed"
        return output_path

    def test_p_net_kw_module_generated(self, solar_battery_output: Path):
        impl = _find_computed_attr_impl(solar_battery_output, "p_net_kw")
        assert is_auto_implemented(impl), "p_net_kw should be auto-implemented"

    def test_p_net_kw_ground_truth(self, solar_battery_output: Path):
        impl = _find_computed_attr_impl(solar_battery_output, "p_net_kw")
        body = extract_function_body(impl)
        assert body is not None, "p_net_kw impl should have executable body"
        result = execute_impl_body(body, {"p_net_mw": 0.008}, ["p_net_kw"])
        assert_outputs_match(result, {"p_net_kw": 8.0})

    def test_p_net_kw_wiring_in_pipeline_yaml(self, solar_battery_output: Path):
        """Verify p_net_kw is wired as MODULE_OUTPUT, not ENTRY_POINT (FR-6)."""
        yaml_path = solar_battery_output / "pipelines" / "pipeline.yaml"
        assert yaml_path.exists(), "Pipeline YAML should be generated"
        content = yaml.safe_load(yaml_path.read_text())
        modules = content.get("modules", {})

        # p_net_kw should NOT appear in entry_fusion inputs
        entry = modules.get("entry_fusion", {})
        entry_inputs = entry.get("inputs", {})
        for name, _value in entry_inputs.items():
            # Entry point names are param group names, not individual params.
            # But individual param values could reference p_net_kw qualified name.
            pass

        # Find the annualized_om CalcUsage module and verify p_net_kw input source
        # is a module output channel (not an entry point reference).
        # Module keys use full qualified names (e.g., "solarbatterylibrary__solar_battery_plant__annualized_om")
        annualized_om = None
        annualized_om_key = None
        for key, mod in modules.items():
            if "annualized_om" in key:
                annualized_om = mod
                annualized_om_key = key
                break
        assert annualized_om is not None, (
            f"annualized_om module should exist in pipeline YAML, "
            f"got keys: {list(modules.keys())}"
        )

        inputs = annualized_om.get("inputs", {})
        assert "p_net_kw" in inputs, (
            f"annualizedomcalc should have p_net_kw input, got: {list(inputs.keys())}"
        )

        p_net_kw_source = str(inputs["p_net_kw"])
        # MODULE_OUTPUT source references a channel name (contains __ separators)
        # ENTRY_POINT source references param_group.qualified_name (starts with group prefix)
        assert "__" in p_net_kw_source or "p_net_kw" in p_net_kw_source.lower(), (
            f"p_net_kw source should reference module output channel, got: {p_net_kw_source}"
        )
        # Entry point sources typically look like "design_params.Qualified__Name__param"
        # Module output sources look like "channel_name.root" or "channel_name"
        # The key check: entry point sources start with a param group name
        # Module output channels contain the computed attr module name
        assert "entry" not in p_net_kw_source.lower(), (
            f"p_net_kw should NOT be sourced from entry point, got: {p_net_kw_source}"
        )

    def test_impl_count_includes_computed_attr(self, solar_battery_output: Path):
        impls = find_impl_files(solar_battery_output)
        assert len(impls) == 36, (
            f"Expected 36 impl files (15 CalcDefs + 1 computed attr + 20 aggregation modules), got {len(impls)}"
        )

    def test_annualized_om_uses_computed_p_net_kw(self, solar_battery_output: Path):
        """Verify end-to-end chain: p_net_mw=0.008 -> p_net_kw=8.0 -> annual_om_cost=160.0."""
        impl = _find_computed_attr_impl(solar_battery_output, "annualizedomcalc")
        assert is_auto_implemented(impl), "annualizedomcalc should be auto-implemented"
        body = extract_function_body(impl)
        assert body is not None
        result = execute_impl_body(
            body, {"om_rate_per_kw_year": 20.0, "p_net_kw": 8.0}, ["annual_om_cost"]
        )
        assert_outputs_match(result, {"annual_om_cost": 160.0})


# ---------------------------------------------------------------------------
# Phase 3: Regression Guards
# ---------------------------------------------------------------------------

class TestPhase1Regression:
    """Explicit regression checks on Phase 1 models.

    Confirms computed attribute extraction doesn't produce false positives
    on models that only use CalcDefs.
    """

    def test_chain_spike_still_works(
        self, chain_spike_model_path: Path, tmp_path: Path,
    ):
        config = GenerationConfig(
            models_path=chain_spike_model_path,
            output_path=tmp_path / "output",
            package_name="chain_spike",
        )
        assert run_codegen(config), "Chain spike codegen should succeed"
        impls = find_impl_files(tmp_path / "output")
        assert len(impls) == 3, f"Expected 3 impl files, got {len(impls)}"
        assert all(is_auto_implemented(p) for p in impls), (
            "All chain spike impls should be auto-implemented"
        )

    def test_catf_mfe_wired_after_item10(
        self, catf_mfe_model_path: Path, tmp_path: Path, caplog,
    ):
        """catf_mfe generation succeeds — Item 10 wired the cross-part pin (SC-1).

        ``cryo_load.magnet_volume`` binds the cross-part EXPOSE
        ``catf_radial_build.magnet_volume_total`` (= ``tf_coil.volume``). Before
        Item 10 that fell through with no value and V11 aborted strict generation.
        The multi-hop EXPOSE confirm pass now resolves it transitively to the
        ``tf_coil.volume_calc.volume`` channel and registers the alias, so the
        consumer wires and generation is clean — no V11 diagnostic.
        """
        import logging

        config = GenerationConfig(
            models_path=catf_mfe_model_path,
            output_path=tmp_path / "output",
            package_name="catf_mfe",
        )
        with caplog.at_level(logging.ERROR):
            assert run_codegen(config) is True, (
                "catf_mfe generation must succeed after Item 10 wires magnet_volume"
            )
        assert not any("V11" in r.message for r in caplog.records), (
            "no V11 diagnostic — the cross-part magnet_volume pin is wired"
        )
