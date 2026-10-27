"""What one copy's redefinition owns stays in that copy (``[NESTED-OVERRIDE-LEAKS-TO-SIBLING]``).

Before the fix, anything owned by a part usage that redefines another part usage (a value,
a deeper chain, a new attribute, a constraint) also reached every other copy of the
redefined part, anywhere in the model, unless that copy had its own value. The cause was
``OccurrenceIndex.occurrences_for_declaration`` (``elaboration/occurrence.py``) selecting by
redefinition family rather than by each occurrence's effective declaration; design D9 of
``.project/active/repeated-rollup-collision``. Native SysIDE gives the per-copy values these
tests expect (``evidence/leak-investigation/report.md`` there).

Each case generates one fixture through the public route and reads the generated package:
the per-copy values in ``inputs/m_params.json``, and which nodes exist in
``pipelines/pipeline.yaml``. Every fixture leaked before the fix. Licensed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from sysml_codegen.cli import GenerationConfig, run_codegen
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

LEAK = FIXTURES_DIR / "sibling_override_leak"


def _generate(models: Path, tmp_path: Path) -> tuple[dict[str, object], set[str]]:
    """The package's input values and its pipeline module names."""
    package = tmp_path / "pkg"
    config = GenerationConfig(
        models_path=models / "models",
        output_path=package,
        package_name="leak_pkg",
        overwrite=True,
    )
    assert run_codegen(config) is True
    inputs = json.loads((package / "inputs" / "m_params.json").read_text())
    pipeline = yaml.safe_load((package / "pipelines" / "pipeline.yaml").read_text())
    return inputs, set(pipeline["modules"])


def _leaves(prefix: str, value: float, count: int = 3) -> dict[str, float]:
    return {f"{prefix}__leaf[{index}]__capital_cost": value for index in range(count)}


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        # A nested value override inside one usage (b's ``part :>> leaf[3]``).
        (
            FIXTURES_DIR / "repeated_rollup" / "leak_rollup",
            {**_leaves("P__top__a", 10.0), **_leaves("P__top__b", 20.0)},
        ),
        # The same override in a specializing definition (``Sub20 :> Sub``).
        (
            LEAK / "nested_specdef",
            {**_leaves("P__top__a", 10.0), **_leaves("P__top__b", 20.0)},
        ),
        # A one-level part redefinition in a specialized definition (``Top2 :> Top``) must
        # not reach the unrelated root ``top``.
        (LEAK / "specialized_top", {"P__top__a__x": 1.0, "P__top2__a__x": 5.0}),
        # A deep chain (``:>> leaf.capital_cost``) owned by a redefining usage in ``Top2``
        # must not reach ``top.b``.
        (
            LEAK / "deep_chain",
            {
                "P__top__a__leaf__capital_cost": 10.0,
                "P__top__b__leaf__capital_cost": 10.0,
                "P__top2__a__leaf__capital_cost": 10.0,
                "P__top2__b__leaf__capital_cost": 20.0,
            },
        ),
    ],
    ids=lambda value: value.name if isinstance(value, Path) else None,
)
def test_each_copy_gets_only_its_own_value(fixture: Path, expected, tmp_path):
    inputs, _modules = _generate(fixture, tmp_path)
    assert inputs == expected


def test_members_declared_in_one_copys_redefinition_exist_only_in_that_copy(tmp_path):
    """``b``'s ``part :>> leaf`` declares an attribute ``x`` and a constraint ``cap``.

    Only ``b.leaf`` gets them; ``a.leaf`` keeps its own value and gains neither node, so
    ``base`` (read only by ``x``) is an input for ``b.leaf`` alone.
    """
    inputs, modules = _generate(LEAK / "new_members", tmp_path)
    assert inputs == {
        "P__top__a__leaf__capital_cost": 10.0,
        "P__top__b__leaf__base": 3.0,
        "P__top__b__leaf__capital_cost": 10.0,
    }
    assert "p__top__b__leaf__x" in modules
    assert [name for name in modules if name.startswith("p__top__b__leaf__cap__")]
    assert not [name for name in modules if name.startswith("p__top__a__leaf__")]
