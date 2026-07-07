"""SC-3: the generated package computes its lcoe-analog BY EXECUTION, within rel 1e-6.

Graph-level inspection does not satisfy SC-B (spec Must-Fix 5): the value must be
produced by importing the generated modules and running them in pipeline-YAML order.
This exercises the in-repo runner (the Item-3 reuse deliverable) end to end.
"""

from __future__ import annotations

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from tests.conftest import snapshot_fixture
from tests.runtime.pipeline_runner import run_pipeline

# Hand-derived from spec_chain_twolevel's auto-impls and emitted inputs (drive_power=50):
#   gamma = drive_power * 0.02 = 50.0 * 0.02 = 1.0   (meier_cost)
#   lcoe  = cost_per_joule * 100.0 = gamma * 100.0 = 100.0   (lcoe_calc, cross-part chain)
_LCOE_CHANNEL = "TwoLevelDesign__hif_plant__lcoe_calc__lcoe"
_HAND_LCOE = 100.0


def _generate(tmp_path):
    config = GenerationConfig(
        output_path=tmp_path / "pkg",
        from_snapshot=snapshot_fixture("spec_chain_twolevel"),
        package_name="pkg",
        overwrite=True,
    )
    assert run_codegen(config) is True
    return tmp_path / "pkg"


def test_twolevel_executes_to_hand_value(tmp_path):
    """The cross-part gamma->lcoe chain executes to the hand-computed value."""
    pkg = _generate(tmp_path)
    out = run_pipeline(pkg)
    assert out[_LCOE_CHANNEL] == pytest.approx(_HAND_LCOE, rel=1e-6)


def test_runner_honors_input_override(tmp_path):
    """The `inputs` override perturbs the entry point (the Item-3 perturbation path):
    doubling drive_power to 100 doubles lcoe to 200."""
    pkg = _generate(tmp_path)
    out = run_pipeline(
        pkg, inputs={"TwoLevelDesign__hif_plant__driver__meier_cost__drive_power": 100.0}
    )
    assert out[_LCOE_CHANNEL] == pytest.approx(200.0, rel=1e-6)
