"""Capture the exact satisfied/violated evidence tuples for the collision-free control.

Reuses the production generation + real-simkit execution helpers from the kept execution
node (`tests/execution/test_constraint_execution.py`) so the printed tuples come from the
same code path the pinned pytest gate asserts — no re-implemented generation, no mock.

Run in a fresh subprocess from the agentic-mbse venv (pandas + teax-simkit present):

    PYTHONPATH=<repo>/src TEAX_SIMKIT_PATH=<teax>/packages/teax-simkit \
      <agentic-mbse-venv>/bin/python \
      .project/active/constraint-wave-name-safety/evidence/capture_collision_free_tuples.py <out_dir>

Prints two lines, each the exact 4-tuple (actual_value, status, margin, observed).
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SRC = _REPO_ROOT / "src"
for _p in (_REPO_ROOT, _SRC):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

# teax-simkit discovery mirrors tests/execution/conftest.py.
from tests.helpers.teax_discovery import discover_teax_simkit  # noqa: E402

_TEAX = discover_teax_simkit(os.environ, repository_root=_REPO_ROOT)
if str(_TEAX) not in sys.path:
    sys.path.insert(0, str(_TEAX))

from tests.execution.test_constraint_execution import (  # noqa: E402
    _cmp_ir,
    _generate_full_package,
    _run,
    _set_json_value,
    _single_constraint_graph,
)
from sysml_codegen.resolution.models import (  # noqa: E402
    ConcreteConstraintInput,
    ConstraintInputResolution,
)


def capture(tmp_path: Path) -> None:
    inputs = [
        ConcreteConstraintInput(
            formal_name="x",
            resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
            design_attribute_qn="pkg__Demo__x",
        ),
        ConcreteConstraintInput(
            formal_name="limit",
            resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
            design_attribute_qn="pkg__Demo__limit",
        ),
    ]
    ctx = _single_constraint_graph(
        constraint_id="name_safety_control",
        predicate_ir=_cmp_ir("<=", "x", "limit"),
        negated=False,
        inputs=inputs,
        design_attrs={"pkg__Demo__x": "2.0", "pkg__Demo__limit": "3.0"},
    )
    pkg_name = "name_safety_exec"
    staged = tmp_path / pkg_name
    _generate_full_package(ctx, staged, pkg_name)

    # Assert the generated module import path and that no colliding-name mapping exists.
    predicates = (staged / "modules" / "constraints" / "predicates.py").read_text()
    assert predicates.count("def constraint_pred_") == 1, "expected exactly one predicate def"

    satisfied = dict(_run(tmp_path, pkg_name, tmp_path / "run_satisfied").outputs)[
        "name_safety_control__evaluation"
    ]
    sat_tuple = (
        satisfied.actual_value,
        satisfied.status,
        satisfied.margin,
        satisfied.observed,
    )

    _set_json_value(staged, "pkg__Demo__x", 4.0)
    violated = dict(_run(tmp_path, pkg_name, tmp_path / "run_violated").outputs)[
        "name_safety_control__evaluation"
    ]
    vio_tuple = (
        violated.actual_value,
        violated.status,
        violated.margin,
        violated.observed,
    )

    print(f"SATISFIED_TUPLE={sat_tuple!r}")
    print(f"VIOLATED_TUPLE={vio_tuple!r}")


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.mkdtemp())
    out.mkdir(parents=True, exist_ok=True)
    capture(out)
