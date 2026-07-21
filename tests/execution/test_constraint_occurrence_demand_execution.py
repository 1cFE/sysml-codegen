"""Real-simkit execution lane for lifecycle-remediation Item 1 (OD-A11).

Sibling instances of one part def carry distinct literal `:>>` overrides. Item 1's
occurrence-stable usage identity is what keeps them apart: under the predecessor's
nullable-QN membership, two anonymous-or-same-named sibling assertions could not be
told apart, and the route-counted demand sweep could collapse or duplicate their
supplied values. This proves the whole thread end to end — extraction, preparation,
enrichment, lowering, generation, and real TEAx execution — by requiring the two
siblings to reach *different* verdicts from their own values.

Runs by hand in the agentic-mbse venv with `teax/packages/teax-simkit` on `sys.path`
(`tests/execution/conftest.py` documents the incantation); excluded from the default
`uv run pytest` via the `execution` marker.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from tests.execution.test_constraint_execution import _generate_full_package, _run

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"

LOW_TARGET = "OccurrenceOverride__plant__low__reading"
HIGH_TARGET = "OccurrenceOverride__plant__high__reading"


def _generated_input_values(pkg_dir: Path) -> dict[str, float]:
    """Every generated JSON input value, merged across the input files."""
    values: dict[str, float] = {}
    for input_file in sorted((pkg_dir / "inputs").glob("*.json")):
        values.update(json.loads(input_file.read_text()))
    return values


@pytest.mark.execution
def test_sibling_literal_overrides_produce_distinct_values_and_verdicts(tmp_path):
    """OD-A11: sibling overrides stay distinct through generation and execution.

    `low` carries `:>> reading = 4.0` and `high` carries `:>> reading = 6.0` against
    `reading >= 5.0`, so a single correct run must produce one violated and one
    satisfied verdict. A collapsed or duplicated supplied value would make both
    siblings agree, and a mis-associated usage would attach the wrong value to the
    wrong occurrence — either failure shows up here as matching verdicts.
    """
    ctx = build_pipeline_context(
        [FIXTURES_DIR / "constraint_occurrence_demand" / "overrides"],
        lower_constraints_enabled=True,
    )
    catalog = ctx.computation_graph.constraint_catalog
    assert catalog is not None
    assert len(catalog.concrete_entries) == 2

    channel_by_owner = {
        entry.owner_instance_path: entry.evaluation_channel
        for entry in catalog.concrete_entries
    }
    low_channel = channel_by_owner["OccurrenceOverride__plant__low"]
    high_channel = channel_by_owner["OccurrenceOverride__plant__high"]
    assert low_channel != high_channel

    pkg_name = "occurrence_override_exec"
    staged = tmp_path / pkg_name
    _generate_full_package(ctx, staged, pkg_name)

    # The two siblings reach generation as distinct entry points with their own values.
    generated = _generated_input_values(staged)
    assert generated[LOW_TARGET] == 4.0
    assert generated[HIGH_TARGET] == 6.0

    result = _run(tmp_path, pkg_name, tmp_path / "run_overrides")
    outputs = dict(result.outputs)

    low = outputs[low_channel]
    high = outputs[high_channel]
    assert (low.status, low.actual_value) == ("violated", False)
    assert (high.status, high.actual_value) == ("satisfied", True)

    # One violated sibling makes the run's headline a violation, and the violated run
    # still completes rather than raising (INV-3).
    report = outputs["constraint_report"]
    assert report.assessed_count == 2
    assert report.headline == "violation"

    written_files = list((tmp_path / "run_overrides").glob("*/constraint_report.json"))
    assert written_files
    written = json.loads(written_files[0].read_text())
    statuses = sorted(entry["status"] for entry in written["results"])
    assert statuses == ["satisfied", "violated"]
