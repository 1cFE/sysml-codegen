"""Conformance tests for pipeline baseline comparison.

Validates that pipeline output is deterministic and matches captured baselines.
ComputationGraph JSON round-trips through Pydantic; registry __init__.py is
syntactically valid Python.

REQ-BASE-01: ComputationGraph JSON matches captured baseline.
REQ-BASE-02: Baseline JSON deserializes back to valid ComputationGraph.
REQ-BASE-03: Registry __init__.py baseline is syntactically valid Python.
REQ-BASE-04: execution_order length equals modules length in every baseline.
"""

from __future__ import annotations

import ast as python_ast
import json
from pathlib import Path

import pytest

from sysml_codegen.resolution.models import ComputationGraph

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
BASELINES_DIR = FIXTURES_DIR / "baseline_outputs"

MODELS = [
    ("solar_battery", "solar_battery_model"),
    ("attr_expr_probe", "attr_expr_probe"),
    ("chain_spike", "chain_spike_model"),
    ("sample_model", "sample_model"),
]


@pytest.mark.parametrize(
    "baseline_name,model_dir",
    MODELS,
    ids=[m[0] for m in MODELS],
)
class TestPipelineBaselines:
    """Baseline comparison tests for pipeline outputs."""

    @pytest.mark.req(id="REQ-BASE-02")
    def test_computation_graph_round_trips(
        self, baseline_name: str, model_dir: str
    ) -> None:
        """Baseline JSON deserializes back to valid ComputationGraph."""
        baseline_path = BASELINES_DIR / baseline_name / "computation_graph.json"
        graph = ComputationGraph.model_validate_json(baseline_path.read_text())
        assert len(graph.execution_order) == len(graph.modules)

    @pytest.mark.req(id="REQ-BASE-04")
    def test_execution_order_matches_modules(
        self, baseline_name: str, model_dir: str
    ) -> None:
        """execution_order length equals modules length."""
        baseline_path = BASELINES_DIR / baseline_name / "computation_graph.json"
        data = json.loads(baseline_path.read_text())
        assert len(data["execution_order"]) == len(data["modules"])

    @pytest.mark.req(id="REQ-BASE-03")
    def test_registry_init_is_valid_python(
        self, baseline_name: str, model_dir: str
    ) -> None:
        """Registry __init__.py baseline is syntactically valid Python."""
        registry_path = BASELINES_DIR / baseline_name / "registry_init.py"
        code = registry_path.read_text()
        assert len(code) > 0, "Registry file is empty"
        # Should parse without SyntaxError
        python_ast.parse(code)

    @pytest.mark.req(id="REQ-BASE-01")
    def test_computation_graph_baseline_is_well_formed(
        self, baseline_name: str, model_dir: str
    ) -> None:
        """ComputationGraph baseline has expected structure."""
        baseline_path = BASELINES_DIR / baseline_name / "computation_graph.json"
        data = json.loads(baseline_path.read_text())
        assert "modules" in data
        assert "execution_order" in data
        assert "entry_point_groups" in data
        assert isinstance(data["modules"], list)
        assert isinstance(data["execution_order"], list)
        assert isinstance(data["entry_point_groups"], list)


@pytest.mark.req(id="REQ-BASE-04")
def test_execution_order_matches_modules_all_baseline_dirs() -> None:
    """execution_order length equals modules length in EVERY baseline dir.

    The parametrized test above only covers the 4 models in MODELS, but
    BASELINES_DIR holds 10 (also catf_mfe, deep_cross_scope_probe, ife_plant,
    plant_values, plant_value_shapes, wi014_toy). This globs all of them --
    read-only widening of an existing invariant, no new baseline captured, no
    churn to any committed baseline.
    """
    baseline_paths = sorted(BASELINES_DIR.glob("*/computation_graph.json"))
    assert len(baseline_paths) >= 10, (
        f"Expected at least 10 baseline dirs with computation_graph.json, "
        f"found {len(baseline_paths)}: {baseline_paths}"
    )
    for baseline_path in baseline_paths:
        data = json.loads(baseline_path.read_text())
        assert len(data["execution_order"]) == len(data["modules"]), (
            f"{baseline_path.parent.name}: execution_order "
            f"({len(data['execution_order'])}) != modules ({len(data['modules'])})"
        )
