"""A sum over a collection with named members counts each member once, in real TEAx.

A named subset (``part server_1 :> servers;``) is one of the collection's members, so the
generator builds the declared number of parts and ``sum(servers.power)`` adds the named
members and the unnamed copies left over, each once (``.project/active/named-subset-members``).
Before the fix the named member was built as an extra part and left out of the sum.

Expected values are worked from the models: every ``power`` or ``cost`` is 10.0 unless a
named member sets its own.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.execution.real_teax import generate_package_from_models, package_loader

pytestmark = pytest.mark.execution

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _outputs(models: Path, root: Path) -> dict[str, float]:
    from simkit.evaluation.evaluator import PreparedEvaluator
    from simkit.study.bridge import CandidateBridge

    # One package name per model: the loader keys loaded packages by name.
    package_name = "named_" + models.name.replace("-", "_")
    package = generate_package_from_models(models, root / "pkg", package_name)
    evaluator = PreparedEvaluator(
        package_loader(package, package_name, root / "link"),
        package / "pipelines" / "pipeline.yaml",
        expects_constraint_report=False,
    )
    result = evaluator.evaluate(CandidateBridge(evaluator.entry_models).build({}))
    assert result.responses == {}
    return dict(result.outputs)


@pytest.mark.parametrize(
    ("models", "expected"),
    [
        # servers : Server[2] with server_1 (15.0) named: server_1 and one copy (10.0).
        (FIXTURES / "named_subset_members" / "one_named", {"ns__rack__total__total": 25.0}),
        # Both members named (15.0, 20.0): no unnamed copy.
        (FIXTURES / "named_subset_members" / "two_named", {"ns__rack__total__total": 35.0}),
        # The same rule for package-level parts: servers[2] beside server_1 (15.0).
        (FIXTURES / "named_subset_members" / "package_roots", {"ns__total__total": 25.0}),
        # dc3's shape: racks[*] narrowed to racks[2] in a specializing definition, both named.
        (
            FIXTURES / "named_subset_members" / "specializing_def",
            {"ns__site__facility__it_system__total__total": 35.0},
        ),
        # A redefinition of a named member keeps it in its collection (15.0 + one copy).
        (
            FIXTURES / "refusal_cases" / "named-member__redefined_member__part_usage",
            {"fx__rack__total__total": 25.0},
        ),
        # The same in dc3's form: rack_1 redefined in the usage (15.0), rack_2 at 10.0.
        (
            FIXTURES
            / "refusal_cases"
            / "named-member__redefined_member__part_usage__specializing_def",
            {"fx__site__total__total": 25.0},
        ),
    ],
    ids=lambda value: value.name if isinstance(value, Path) else None,
)
def test_a_sum_counts_each_member_once(models: Path, expected: dict[str, float], tmp_path):
    assert _outputs(models, tmp_path) == expected
