"""The snapshot subcommand refuses a declined model with its typed message, not a traceback.

Audit-7 finding F3: ``cmd_snapshot`` had no handler, so any model the exact route refuses
— 22 of the 37 corpus fixtures — greeted the user with a Python stack trace. The command
now carries the same distinct refusal classes ``run_codegen`` keeps distinct.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from sysml_codegen.cli import cmd_snapshot
from tests.conftest import requires_license

ROOT = Path(__file__).resolve().parents[2]


def _args(models: Path, output: Path) -> argparse.Namespace:
    return argparse.Namespace(models=models, output=output, verbose=False)


@requires_license
def test_a_refused_model_exits_one_with_the_typed_message(tmp_path, caplog) -> None:
    """ife_plant is a ratified refusal (21x SI_SELF_BINDING); the user sees the codes."""
    output = tmp_path / "instance_graph_snapshot.json"
    with caplog.at_level("ERROR"):
        rc = cmd_snapshot(_args(ROOT / "tests" / "fixtures" / "ife_plant", output))
    assert rc == 1
    assert not output.exists(), "a refused model must write nothing"
    joined = "\n".join(record.getMessage() for record in caplog.records)
    assert "SI_SELF_BINDING" in joined
    assert "Traceback" not in joined


@requires_license
def test_an_accepted_model_still_captures(tmp_path) -> None:
    """The handler discriminates: sample_model captures exactly as before."""
    output = tmp_path / "instance_graph_snapshot.json"
    rc = cmd_snapshot(_args(ROOT / "tests" / "fixtures" / "sample_model", output))
    assert rc == 0
    assert output.is_file()


@requires_license
def test_unit_collision_exits_one_with_exact_diagnostic_and_preserves_destination(
    tmp_path, caplog
) -> None:
    output = tmp_path / "instance_graph_snapshot.json"
    sentinel = b"item-8-cli-sentinel\n"
    output.write_bytes(sentinel)
    fixture = ROOT / "tests" / "fixtures" / "unit_lane_constraint_disagreement"

    with caplog.at_level("ERROR"):
        rc = cmd_snapshot(_args(fixture, output))

    assert rc == 1
    assert output.read_bytes() == sentinel
    assert not list(tmp_path.glob(".instance_graph_snapshot.json.*.tmp"))
    joined = "\n".join(record.getMessage() for record in caplog.records)
    assert "SI_RENDERING_COLLISION" in joined
    assert "UnitLaneConstraintDisagreement__disagreement__shared_length" in joined
    assert "conflicting projected metadata" in joined
    assert "reference='UnitLaneConstraintDisagreement__disagreement__shared_length'" in joined
    assert "[root-0/model.sysml:15]" in joined
    assert "Traceback" not in joined
