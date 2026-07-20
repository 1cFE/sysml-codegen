"""Gate A under real simkit: the usage-owned literal reaches execution and moves the verdict.

Item 2, SR-A01 / SR-R22. Resolving to a non-null design attribute is not the claim —
Item 1's OD-R35 lesson is that distinct wrappers can hide a collapsed value. So this lane
observes a real evaluated verdict from the generated package, then changes the literal in
the generated inputs and observes the verdict flip.

Runs by hand in the agentic-mbse venv with `teax/packages/teax-simkit` on `sys.path`
(`tests/execution/conftest.py` documents the incantation); excluded from the default run
via the `execution` marker.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from tests.execution.test_constraint_execution import _generate_full_package, _run

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"

# The usage-owned attribute's real qualified name — the whole point of Gate A. Before the
# owner-classification fix, resolution asked for `GateA__the_host__viability__gain` (the
# constraint's own QN as the root) and generation failed at the strict terminal miss.
GAIN_QN = "GateA__the_host__gain"
REPORT_CH = "constraint_report"


def _override_gain(pkg_dir: Path, value: float) -> None:
    for jf in (pkg_dir / "inputs").glob("*.json"):
        data = json.loads(jf.read_text())
        if GAIN_QN in data:
            data[GAIN_QN] = value
            jf.write_text(json.dumps(data, indent=2) + "\n")
            return
    raise RuntimeError(f"{GAIN_QN} not found in any inputs JSON")


@pytest.mark.execution
def test_gate_a_usage_owned_literal_drives_the_verdict(tmp_path):
    """SR-A01/SR-R22: `gain = 40.0`, declared on the concrete PartUsage `the_host` and
    read by the self-named actual `in gain = gain`, satisfies `gain >= threshold`
    (default 10.0). Dropping it below the threshold flips the verdict to violated."""
    ctx = build_pipeline_context([FIXTURES_DIR / "gate_a"], lower_constraints_enabled=True)
    catalog = ctx.computation_graph.constraint_catalog
    assert catalog is not None and len(catalog.concrete_entries) == 1
    eval_channel = catalog.concrete_entries[0].evaluation_channel

    pkg_name = "gate_a_exec"
    staged = tmp_path / pkg_name
    _generate_full_package(ctx, staged, pkg_name)

    # The literal reached the generated inputs under its real QN, not a fallback key.
    inputs = {}
    for jf in (staged / "inputs").glob("*.json"):
        inputs.update(json.loads(jf.read_text()))
    assert inputs[GAIN_QN] == 40.0

    outs_true = dict(_run(tmp_path, pkg_name, tmp_path / "run_satisfied").outputs)
    ev_true = outs_true[eval_channel]
    assert ev_true.status == "satisfied" and ev_true.actual_value is True
    assert outs_true[REPORT_CH].headline == "all_satisfied"

    _override_gain(staged, 5.0)
    outs_false = dict(_run(tmp_path, pkg_name, tmp_path / "run_violated").outputs)
    ev_false = outs_false[eval_channel]
    assert ev_false.status == "violated" and ev_false.actual_value is False
    assert outs_false[REPORT_CH].headline == "violation"
