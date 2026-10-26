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
        # One usage adds the subsetting (part :>> spare :> servers, 15.0): spare is a member
        # in rack_a only; rack_b keeps both copies.
        (
            FIXTURES / "named_subset_members" / "one_usage_adds_subsetting",
            {"ns__rack_a__total__total": 25.0, "ns__rack_b__total__total": 20.0},
        ),
        # The same through a specializing definition; spare keeps Rack's 1.0, so rack_a holds
        # spare and one copy (11.0) and a plain Rack keeps both copies.
        (
            FIXTURES / "named_subset_members" / "specializing_def_adds_subsetting",
            {"ns__rack_a__total__total": 11.0, "ns__rack_b__total__total": 20.0},
        ),
    ],
    ids=lambda value: value.name if isinstance(value, Path) else None,
)
def test_a_sum_counts_each_member_once(models: Path, expected: dict[str, float], tmp_path):
    assert _outputs(models, tmp_path) == expected


@pytest.mark.parametrize(
    ("models", "expected"),
    [
        # sum(servers.power) written inside server_1 (15.0) adds server_1 and the copy.
        (
            FIXTURES / "named_subset_members" / "member_reads_collection",
            {"ns__rack__server_1__seen__seen": 25.0, "ns__rack__total__total": 25.0},
        ),
        # The same with server_1 declared in the definition.
        (
            FIXTURES / "named_subset_members" / "member_in_def_reads_collection",
            {"ns__rack__server_1__seen__seen": 25.0, "ns__rack__total__total": 25.0},
        ),
        # A share of the total: rack_1 is one of two racks at 20.0 each.
        (
            FIXTURES / "named_subset_members" / "member_share_of_total",
            {
                "ns__hall__rack_1__share__share": 0.5,
                "ns__hall__rack_1__total__total": 20.0,
                "ns__hall__racks[0]__total__total": 20.0,
                "ns__hall__total__total": 40.0,
            },
        ),
        # Each member's fraction of the rack's power: 30 / 40 and 10 / 40.
        (
            FIXTURES / "named_subset_members" / "member_fractions",
            {
                "ns__rack__server_1__frac__frac": 0.75,
                "ns__rack__server_2__frac__frac": 0.25,
                "ns__rack__total__total": 1.0,
            },
        ),
        # The same read from inside an indexed copy reaches both copies (10 / 20 each).
        (
            FIXTURES / "named_subset_members" / "copy_fractions",
            {
                "ns__rack__servers[0]__frac__frac": 0.5,
                "ns__rack__servers[1]__frac__frac": 0.5,
                "ns__rack__total__total": 1.0,
            },
        ),
    ],
    ids=lambda value: value.name if isinstance(value, Path) else None,
)
def test_a_member_reading_its_own_collection_reaches_every_member(
    models: Path, expected: dict[str, float], tmp_path
):
    assert _outputs(models, tmp_path) == expected
