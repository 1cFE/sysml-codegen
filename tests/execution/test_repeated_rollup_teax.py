"""Repeated computed sub-assemblies compute per-copy values in real TEAx.

Copies of one formula or rollup class share that class, registered once, with one
pipeline entry per copy (``.project/active/repeated-rollup-collision``). These cases run
the generated package through its own registry and check every copy's number, and that
changing one copy's input moves only that copy and what sums it.

Expected values are worked from the models in ``tests/fixtures/repeated_rollup``: every
leaf is 10.0 unless stated, and every leaf value is set at the leaf definition, except in
``leak_rollup``, the one nested value override.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.execution.real_teax import generate_package_from_models, package_loader

pytestmark = pytest.mark.execution

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "repeated_rollup"


def _evaluator(model: str, root: Path):
    from simkit.evaluation.evaluator import PreparedEvaluator
    from simkit.study.bridge import CandidateBridge

    package_name = f"repeated_{model}"
    package = generate_package_from_models(FIXTURES / model, root / "pkg", package_name)
    evaluator = PreparedEvaluator(
        package_loader(package, package_name, root / "link"),
        package / "pipelines" / "pipeline.yaml",
        expects_constraint_report=False,
    )
    return evaluator, CandidateBridge(evaluator.entry_models)


def _outputs(model: str, root: Path, selected: dict[str, float] | None = None):
    evaluator, bridge = _evaluator(model, root)
    result = evaluator.evaluate(bridge.build(selected or {}))
    assert result.responses == {}
    return dict(result.outputs)


def _cost(path: str) -> str:
    """The output channel of the ``capital_cost`` computed at occurrence ``path``."""
    return f"{path}__capital_cost__capital_cost"


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        (
            "two",
            {_cost("P__top"): 60.0, _cost("P__top__sub[0]"): 30.0, _cost("P__top__sub[1]"): 30.0},
        ),
        (
            "named",
            {_cost("P__top"): 60.0, _cost("P__top__a"): 30.0, _cost("P__top__b"): 30.0},
        ),
        (
            "nested",
            {
                _cost("P__hall"): 120.0,
                _cost("P__hall__row[0]"): 60.0,
                _cost("P__hall__row[1]"): 60.0,
                _cost("P__hall__row[0]__rack[0]"): 30.0,
                _cost("P__hall__row[0]__rack[1]"): 30.0,
                _cost("P__hall__row[1]__rack[0]"): 30.0,
                _cost("P__hall__row[1]__rack[1]"): 30.0,
            },
        ),
        (
            "named_total",
            {
                _cost("P__top"): 60.0,
                "P__top__sub[0]__sub_total__sub_total": 30.0,
                "P__top__sub[1]__sub_total__sub_total": 30.0,
            },
        ),
        # Each leaf is a * 5.0 with a = 2.0.
        (
            "leafformula",
            {
                _cost("P__top"): 30.0,
                _cost("P__top__leaf[0]"): 10.0,
                _cost("P__top__leaf[1]"): 10.0,
                _cost("P__top__leaf[2]"): 10.0,
            },
        ),
        # b redefines its leaves to two, so the two copies split into two classes.
        (
            "arity",
            {_cost("P__top"): 50.0, _cost("P__top__a"): 30.0, _cost("P__top__b"): 20.0},
        ),
        (
            "nestdiv",
            {
                _cost("P__top"): 100.0,
                _cost("P__top__row[0]"): 50.0,
                _cost("P__top__row[1]"): 50.0,
                _cost("P__top__row[0]__a"): 30.0,
                _cost("P__top__row[1]__a"): 30.0,
                _cost("P__top__row[0]__b"): 20.0,
                _cost("P__top__row[1]__b"): 20.0,
            },
        ),
        (
            "trio",
            {
                _cost("P__top"): 80.0,
                _cost("P__top__s[0]"): 30.0,
                _cost("P__top__s[1]"): 30.0,
                _cost("P__top__b"): 20.0,
            },
        ),
        # One copy, plus a parent formula whose class shares the rollup's class name.
        ("onenamed", {_cost("P__top"): 35.0, _cost("P__top__a"): 30.0}),
        # A specialized parent redefines its racks to a two-leaf subtype under a new name
        # (the workaround for the alias limit pinned by ``specialized``).
        (
            "specialized_renamed",
            {
                _cost("P__top"): 100.0,
                _cost("P__top__a"): 60.0,
                _cost("P__top__a__sub[0]"): 30.0,
                _cost("P__top__a__sub[1]"): 30.0,
                _cost("P__top__b"): 40.0,
                _cost("P__top__b__racks2[0]"): 20.0,
                _cost("P__top__b__racks2[1]"): 20.0,
            },
        ),
        # b's nested override sets its own three leaves to 20.0; a keeps 10.0 each
        # ([NESTED-OVERRIDE-LEAKS-TO-SIBLING] once gave a 20.0 too: 60 / 60 / 120).
        (
            "leak_rollup",
            {_cost("P__top"): 90.0, _cost("P__top__a"): 30.0, _cost("P__top__b"): 60.0},
        ),
        # The part named after its definition, with a different shape.
        (
            "subname",
            {_cost("P__top"): 50.0, _cost("P__top__a"): 30.0, _cost("P__top__sub"): 20.0},
        ),
    ],
)
def test_every_copy_computes_its_own_value(model: str, expected: dict[str, float], tmp_path):
    assert _outputs(model, tmp_path) == expected


@pytest.mark.parametrize(
    ("model", "field", "moved"),
    [
        (
            "two",
            "P__top__sub_1__leaf_0__capital_cost",
            {_cost("P__top__sub[1]"): 40.0, _cost("P__top"): 70.0},
        ),
        (
            "nested",
            "P__hall__row_1__rack_0__leaf_0__capital_cost",
            {
                _cost("P__hall__row[1]__rack[0]"): 40.0,
                _cost("P__hall__row[1]"): 70.0,
                _cost("P__hall"): 130.0,
            },
        ),
        (
            "nestdiv",
            "P__top__row_1__a__leaf_0__capital_cost",
            {
                _cost("P__top__row[1]__a"): 40.0,
                _cost("P__top__row[1]"): 60.0,
                _cost("P__top"): 110.0,
            },
        ),
    ],
)
def test_one_copys_input_moves_only_that_copy_and_its_sums(
    model: str, field: str, moved: dict[str, float], tmp_path
):
    baseline = _outputs(model, tmp_path / "baseline")
    mutated = _outputs(model, tmp_path / "mutated", {field: 20.0})
    assert {name for name in baseline if baseline[name] != mutated[name]} == set(moved)
    assert {name: mutated[name] for name in moved} == moved
