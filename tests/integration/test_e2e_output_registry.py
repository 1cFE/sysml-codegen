"""E2E validation: YAML diff against baselines and Issue 22 regression.

Phase 5 of the OutputRegistry cut-over (Item 4). Validates that the full
codegen pipeline with OutputRegistry as sole resolution path produces
correct pipeline YAML for all 4 models, and that Issue 22
(REFERENCE->aggregation same-scope) resolves correctly.
"""

from __future__ import annotations

from pathlib import Path

import jinja2
import pytest

from sysml_codegen.core.models import BindingResolutionType
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.generation.pipeline import generate_pipeline_yaml

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
BASELINE_DIR = FIXTURES_DIR / "baseline_yaml"

MODELS = [
    ("solar_battery", FIXTURES_DIR / "solar_battery_model", "solar_battery"),
    ("attr_expr_probe", FIXTURES_DIR / "attr_expr_probe", "attr_expr_probe"),
    ("chain_spike", FIXTURES_DIR / "chain_spike_model", "chain_spike"),
    ("sample_model", FIXTURES_DIR / "sample_model", "sample_model"),
]


@pytest.fixture(scope="module")
def template_env():
    """Jinja2 template environment for pipeline YAML generation."""
    template_dir = (
        Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "templates"
    )
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


class TestYamlDiffValidation:
    """Diff generated YAML against pre-cutover baselines.

    All 4 models should produce YAML identical to baselines captured
    before the OutputRegistry cut-over. The cut-over produces identical
    resolution outcomes (verified by parallel validation with zero
    divergences on 215+ bindings).
    """

    @pytest.mark.parametrize(
        "model_name,model_path,package_name",
        MODELS,
        ids=[m[0] for m in MODELS],
    )
    def test_yaml_matches_baseline(
        self, model_name, model_path, package_name, template_env
    ):
        """Generated pipeline YAML matches pre-cutover baseline."""
        ctx = build_pipeline_context([model_path])
        generated = generate_pipeline_yaml(
            graph=ctx.computation_graph,
            package_name=package_name,
            template_env=template_env,
        )
        baseline = (BASELINE_DIR / f"{model_name}.yaml").read_text()
        assert generated == baseline, (
            f"YAML diff for {model_name}: generated output differs from baseline.\n"
            f"If this is expected (e.g., Bug 2 fix), update the baseline with:\n"
            f"  uv run python scripts/capture_baseline_yaml.py"
        )


class TestIssue22ReferenceToAggregation:
    """Issue 22: REFERENCE binding to same-scope aggregation output.

    In WidgetAssembly:
      :>> total_cost = sum(widget.total_cost)                    # aggregation
      calc margin_calc { in component_total = total_cost; }      # REFERENCE

    The component_total binding should resolve to MODULE_OUTPUT
    (the aggregation module's output channel), not ENTRY_POINT.
    """

    @pytest.fixture(scope="class")
    def pipeline_context(self):
        return build_pipeline_context([FIXTURES_DIR / "issue22_model"])

    def test_reference_to_aggregation_resolves_to_module_output(self, pipeline_context):
        """REFERENCE binding to same-scope aggregation resolves to MODULE_OUTPUT."""
        resolutions = pipeline_context.backtracking_result.binding_resolutions

        component_total_keys = [
            k for k in resolutions
            if "component_total" in k
        ]
        assert component_total_keys, (
            f"Expected binding resolution for 'component_total'. "
            f"Available keys: {sorted(resolutions.keys())}"
        )

        for key in component_total_keys:
            resolution = resolutions[key]
            assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT, (
                f"Issue 22: {key} should resolve to MODULE_OUTPUT but got "
                f"{resolution.resolution_type.value} "
                f"(qualified_name={resolution.qualified_name!r})"
            )

    def test_margin_calc_module_wired_to_aggregation_output(self, pipeline_context):
        """margin_calc's component_total input is wired to aggregation channel."""
        graph = pipeline_context.computation_graph

        margin_modules = [
            m for m in graph.modules
            if "margin" in m.name.lower()
        ]
        assert margin_modules, (
            f"Expected margin_calc module. "
            f"Available modules: {[m.name for m in graph.modules]}"
        )

        margin = margin_modules[0]
        ct_inputs = [
            inp for inp in margin.inputs
            if inp.param_name == "component_total"
        ]
        assert ct_inputs, (
            f"Expected component_total input on margin_calc. "
            f"Inputs: {[i.param_name for i in margin.inputs]}"
        )

        ct = ct_inputs[0]
        assert ct.source.source_type == "module_output", (
            f"Issue 22: component_total should be module_output but is "
            f"{ct.source.source_type}"
        )
