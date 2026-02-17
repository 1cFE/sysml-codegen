"""Parallel validation integration tests: zero divergences on all 4 models.

Phase 5: Run both old cascade and new registry resolution paths on real
models, assert zero divergences, verify EXPOSE_PURE and REFERENCE secondary
resolution cases.

See: design.md#component-6-parallel-validation-integration-tests
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from sysml_codegen.core.models import BindingResolutionType
from sysml_codegen.generation.initialization import build_output_registry, build_pipeline_context
from tests.helpers.registry_compat import registry_resolve

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


# ---------------------------------------------------------------------------
# Custom log capture for class-scoped fixtures
# (pytest caplog is function-scoped; we need to capture during fixture setup)
# ---------------------------------------------------------------------------


class _LogCapture(logging.Handler):
    """Collects log records during pipeline construction."""

    def __init__(self):
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def _build_pipeline_with_log_capture(model_path: Path):
    """Run build_pipeline_context and capture backtracker warnings.

    Returns (pipeline_context, list[LogRecord]).
    """
    capture = _LogCapture()
    capture.setLevel(logging.WARNING)
    bt_logger = logging.getLogger("sysml_codegen.analysis.dependency_backtracker")
    bt_logger.addHandler(capture)
    original_level = bt_logger.level
    bt_logger.setLevel(logging.WARNING)
    try:
        ctx = build_pipeline_context([model_path])
    finally:
        bt_logger.removeHandler(capture)
        bt_logger.setLevel(original_level)
    return ctx, capture.records


# ===========================================================================
# Zero-divergence tests: one class per model
# ===========================================================================


class TestParallelValidationSolarBattery:
    """Parallel validation on solar_battery model."""

    @pytest.fixture(scope="class")
    def pipeline_result(self):
        return _build_pipeline_with_log_capture(FIXTURES_DIR / "solar_battery_model")

    @pytest.fixture(scope="class")
    def pipeline_context(self, pipeline_result):
        return pipeline_result[0]

    @pytest.fixture(scope="class")
    def log_records(self, pipeline_result):
        return pipeline_result[1]

    def test_zero_divergences(self, log_records):
        """No PARALLEL DIVERGENCE warnings on solar_battery."""
        divergences = [r for r in log_records if "PARALLEL DIVERGENCE" in r.getMessage()]
        assert divergences == [], (
            f"Divergences:\n" + "\n".join(r.getMessage() for r in divergences)
        )

    def test_reference_secondary_p_net_kw(self, pipeline_context):
        """REFERENCE secondary: p_net_kw resolves to MODULE_OUTPUT.

        p_net_kw is a FORMULA computed attribute on solar_battery_plant.
        The old path resolves it via _computed_attr_index; the new path
        resolves it via registry_resolve(registry,) (Phase 1 Key_F registration).
        """
        resolutions = pipeline_context.backtracking_result.binding_resolutions
        p_net_kw_keys = [k for k in resolutions if "p_net_kw" in k]
        assert p_net_kw_keys, "Expected at least one p_net_kw binding resolution"

        p_net_kw_module_outputs = [
            k for k in p_net_kw_keys
            if resolutions[k].resolution_type == BindingResolutionType.MODULE_OUTPUT
        ]
        assert p_net_kw_module_outputs, (
            f"p_net_kw should have at least one MODULE_OUTPUT resolution. "
            f"Got: {[(k, resolutions[k].resolution_type.value) for k in p_net_kw_keys]}"
        )

    def test_reference_secondary_capital_cost(self, pipeline_context):
        """REFERENCE secondary: capital_cost resolves to MODULE_OUTPUT.

        capital_cost is an aggregation output on solar_array.
        The registry resolves it via Phase 1b Key_E_stripped registration
        (full scoped path from design root).
        """
        registry = build_output_registry(
            calc_usages=pipeline_context.calc_usages,
            calc_defs=pipeline_context.calc_defs,
            aggregation_data=pipeline_context.aggregation_expressions,
            computed_attributes=pipeline_context.computed_attributes,
            channel_aliases=pipeline_context.channel_aliases,
            design_attributes=pipeline_context.design_attributes,
        )
        # Key_E_stripped format: design root path (minus design prefix) + attr
        result = registry_resolve(registry, "solar_battery_plant.solar_array.capital_cost")
        assert result is not None, (
            "solar_battery_plant.solar_array.capital_cost should resolve via "
            "Phase 1b Key_E_stripped scoped registration"
        )

    def test_unresolved_bindings_produce_warnings(self, log_records):
        """Unresolved bindings in new path produce logger.warning().

        solar_battery has self-referential SysML QN bindings (e.g., FeatureReferenceExpression
        pointing to the usage's own part) that legitimately resolve to ENTRY_POINT. These
        produce "Registry unresolved" warnings because the registry's self-reference guard
        rejects them. If a future registry improvement resolves all bindings, this test
        should be updated to assert == 0 instead.
        """
        unresolved = [r for r in log_records if "Registry unresolved" in r.getMessage()]
        assert len(unresolved) > 0, (
            "Expected 'Registry unresolved' warnings for self-referential entry point bindings"
        )


class TestParallelValidationAttrExprProbe:
    """Parallel validation on attr_expr_probe model."""

    @pytest.fixture(scope="class")
    def pipeline_result(self):
        return _build_pipeline_with_log_capture(FIXTURES_DIR / "attr_expr_probe")

    @pytest.fixture(scope="class")
    def pipeline_context(self, pipeline_result):
        return pipeline_result[0]

    @pytest.fixture(scope="class")
    def log_records(self, pipeline_result):
        return pipeline_result[1]

    def test_zero_divergences(self, log_records):
        """No PARALLEL DIVERGENCE warnings on attr_expr_probe."""
        divergences = [r for r in log_records if "PARALLEL DIVERGENCE" in r.getMessage()]
        assert divergences == [], (
            f"Divergences:\n" + "\n".join(r.getMessage() for r in divergences)
        )

    def test_expose_pure_scale_result_resolves_via_registry(self, pipeline_context):
        """EXPOSE_PURE: scale_result resolves to MODULE_OUTPUT via Phase 3 scoped key.

        This verifies the EXPOSE_PURE registration path works on real data.
        Phase 3 scopes the alias as "probe_design.scale_result" which resolves
        to the scale_calc__result canonical channel.
        """
        registry = build_output_registry(
            calc_usages=pipeline_context.calc_usages,
            calc_defs=pipeline_context.calc_defs,
            aggregation_data=pipeline_context.aggregation_expressions,
            computed_attributes=pipeline_context.computed_attributes,
            channel_aliases=pipeline_context.channel_aliases,
            design_attributes=pipeline_context.design_attributes,
        )
        result = registry_resolve(registry,"probe_design.scale_result")
        assert result is not None, (
            "EXPOSE_PURE 'probe_design.scale_result' should resolve via Phase 3"
        )
        assert "scale_calc__result" in result


class TestParallelValidationChainSpike:
    """Parallel validation on chain_spike model."""

    @pytest.fixture(scope="class")
    def pipeline_result(self):
        return _build_pipeline_with_log_capture(FIXTURES_DIR / "chain_spike_model")

    @pytest.fixture(scope="class")
    def log_records(self, pipeline_result):
        return pipeline_result[1]

    def test_zero_divergences(self, log_records):
        """No PARALLEL DIVERGENCE warnings on chain_spike."""
        divergences = [r for r in log_records if "PARALLEL DIVERGENCE" in r.getMessage()]
        assert divergences == [], (
            f"Divergences:\n" + "\n".join(r.getMessage() for r in divergences)
        )


class TestParallelValidationSampleModel:
    """Parallel validation on sample_model."""

    @pytest.fixture(scope="class")
    def pipeline_result(self):
        return _build_pipeline_with_log_capture(FIXTURES_DIR / "sample_model")

    @pytest.fixture(scope="class")
    def log_records(self, pipeline_result):
        return pipeline_result[1]

    def test_zero_divergences(self, log_records):
        """No PARALLEL DIVERGENCE warnings on sample_model."""
        divergences = [r for r in log_records if "PARALLEL DIVERGENCE" in r.getMessage()]
        assert divergences == [], (
            f"Divergences:\n" + "\n".join(r.getMessage() for r in divergences)
        )
