"""Case 18 (Appendix C) under real simkit: a definition-owned assert whose actual is
redefined at a package-level usage reaches execution and produces the expected verdict.

Item 2 case-18 addendum (Item 13 composed proof). `part def Panel` owns
`assert constraint within : 'Within Limit' { in v = source.reading; }`; the redefining usage
`part panel : Panel { :>> source.reading = 80.0; }` supplies the actual. The redefined
attribute resolves under exact identity (shared resolver row 16, occurrence_materialized_qn)
to the design attribute `constraint_def_owned_redefining__panel__source__reading` — no
leniency, no constraint-specific shim. `80.0 <= 100.0` → satisfied; raising it above 100.0
flips the verdict to violated, proving the redefined value truly drives execution.

Runs by hand in the agentic-mbse venv with `teax/packages/teax-simkit` on `sys.path`
(`tests/execution/conftest.py` documents the incantation); excluded from the default run via
the `execution` marker.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from tests.execution.test_constraint_execution import _generate_full_package, _run

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"

READING_QN = "constraint_def_owned_redefining__panel__source__reading"
REPORT_CH = "constraint_report"


def _override_reading(pkg_dir: Path, value: float) -> None:
    for jf in (pkg_dir / "inputs").glob("*.json"):
        data = json.loads(jf.read_text())
        if READING_QN in data:
            data[READING_QN] = value
            jf.write_text(json.dumps(data, indent=2) + "\n")
            return
    raise RuntimeError(f"{READING_QN} not found in any inputs JSON")


@pytest.mark.execution
def test_redefined_actual_drives_the_verdict(tmp_path):
    """The `:>> source.reading = 80.0` redefinition satisfies `v <= 100.0`; raising the
    redefined value above the limit flips the verdict to violated."""
    ctx = build_pipeline_context(
        [FIXTURES_DIR / "constraint_def_owned_redefining"], lower_constraints_enabled=True
    )
    catalog = ctx.computation_graph.constraint_catalog
    assert catalog is not None and len(catalog.concrete_entries) == 1
    eval_channel = catalog.concrete_entries[0].evaluation_channel

    pkg_name = "constraint_def_owned_redefining_exec"
    staged = tmp_path / pkg_name
    _generate_full_package(ctx, staged, pkg_name)

    # The redefined literal reached the generated inputs under its exact design-attribute QN.
    inputs: dict = {}
    for jf in (staged / "inputs").glob("*.json"):
        inputs.update(json.loads(jf.read_text()))
    assert inputs[READING_QN] == 80.0

    outs_true = dict(_run(tmp_path, pkg_name, tmp_path / "run_satisfied").outputs)
    ev_true = outs_true[eval_channel]
    assert ev_true.status == "satisfied" and ev_true.actual_value is True
    assert outs_true[REPORT_CH].headline == "all_satisfied"

    _override_reading(staged, 120.0)
    outs_false = dict(_run(tmp_path, pkg_name, tmp_path / "run_violated").outputs)
    ev_false = outs_false[eval_channel]
    assert ev_false.status == "violated" and ev_false.actual_value is False
    assert outs_false[REPORT_CH].headline == "violation"
