"""Live conformance tests for the part-instance index (Item 4).

Every test here loads the ``instance_index_probe`` fixture live via
``SysMLDataExtractor`` — no committed snapshot, since the index reads the live
``multiplicity`` node (D8), which a snapshot does not carry. All tests are marked
``@requires_license`` and skip in the plain codegen venv (no syside license);
they are proven green through the licensed sibling env (see plan.md
"Implementation Strategy").
"""

import pytest

from sysml_codegen.analysis.part_instance_index import (
    NonFiniteCardinalityError,
    build_part_instance_index,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import FIXTURES_DIR, requires_license

# The exact nine-instance oracle from the S3 spike
# (spike-concrete-expansion-instance-index/probe_instance_index.py:31-41), unchanged.
EXPECTED_NINE = {
    "InstanceIndexProbe__root__bank__member[0]",
    "InstanceIndexProbe__root__bank__member[1]",
    "InstanceIndexProbe__root__bank__member[2]",
    "InstanceIndexProbe__root__direct_a",
    "InstanceIndexProbe__root__direct_b",
    "InstanceIndexProbe__root__container_a__leaf",
    "InstanceIndexProbe__root__plain_subtype",
    "InstanceIndexProbe__root__container_b__leaf",
    "InstanceIndexProbe__root__specialized__leaf",
}


@pytest.fixture
def instance_index_model():
    """Load the instance_index_probe fixture live; skip if syside is unavailable."""
    extractor = SysMLDataExtractor([FIXTURES_DIR / "instance_index_probe"])
    try:
        loaded = extractor.load_models()
    except ImportError as exc:  # syside license not configured
        pytest.skip(f"syside unavailable: {exc}")
    if not loaded:
        pytest.skip("Could not load instance_index_probe")
    return extractor.model


@requires_license
def test_nine_instance_oracle(instance_index_model) -> None:
    """Validation #1: the 9/9 oracle, including the plain subtype the calc-driven
    finder misses."""
    index = build_part_instance_index(instance_index_model)
    occurrences = index.occurrences_of("InstanceIndexProbe__ConstrainedLeaf")
    paths = {occ.instance_path for occ in occurrences}
    assert paths == EXPECTED_NINE


@requires_license
def test_same_name_collision(instance_index_model) -> None:
    """Validation #2: two definitions own a same-named member with different
    counts; each keeps its own count, keyed by owning def, never by bare name."""
    index = build_part_instance_index(instance_index_model)
    occurrences = index.occurrences_of("InstanceIndexProbe__CollisionLeaf")
    by_owner: dict[str, int] = {}
    for occ in occurrences:
        owner = occ.steps[-1].owning_def_qn
        by_owner[owner] = by_owner.get(owner, 0) + 1
    assert by_owner == {
        "InstanceIndexProbe__BankA": 3,
        "InstanceIndexProbe__BankB": 2,
    }


@requires_license
def test_equal_bounds_admit(instance_index_model) -> None:
    """Validation #7: [3..3] (C2) expands to exactly 3 occurrences."""
    index = build_part_instance_index(instance_index_model)
    occurrences = index.occurrences_of("InstanceIndexProbe__Leaf33")
    assert len(occurrences) == 3
    assert {occ.instance_path for occ in occurrences} == {
        "InstanceIndexProbe__b33__m33[0]",
        "InstanceIndexProbe__b33__m33[1]",
        "InstanceIndexProbe__b33__m33[2]",
    }


@requires_license
def test_cartesian_expansion(instance_index_model) -> None:
    """Validation #8: a fixed [2] container of a fixed [3] leaf expands to 6,
    each occurrence carrying both step indices."""
    index = build_part_instance_index(instance_index_model)
    occurrences = index.occurrences_of("InstanceIndexProbe__CartLeaf")
    assert len(occurrences) == 6
    expected = {
        f"InstanceIndexProbe__outer__c[{i}]__leaf[{j}]" for i in range(2) for j in range(3)
    }
    assert {occ.instance_path for occ in occurrences} == expected


@requires_license
def test_closure_times_multiplicity(instance_index_model) -> None:
    """Validation #8: the query type is reached only via subtype closure, and the
    reaching member has a fixed multiplicity — both effects compose."""
    index = build_part_instance_index(instance_index_model)
    occurrences = index.occurrences_of("InstanceIndexProbe__ClosureBase")
    assert len(occurrences) == 2
    assert {occ.instance_path for occ in occurrences} == {
        "InstanceIndexProbe__chost__cs[0]",
        "InstanceIndexProbe__chost__cs[1]",
    }
    assert {occ.part_def_qn for occ in occurrences} == {"InstanceIndexProbe__ClosureSub"}


@requires_license
def test_determinism(instance_index_model) -> None:
    """Validation #4: two fresh live loads produce identical ordered instance_path
    lists."""
    extractor_b = SysMLDataExtractor([FIXTURES_DIR / "instance_index_probe"])
    assert extractor_b.load_models()
    index_a = build_part_instance_index(instance_index_model)
    index_b = build_part_instance_index(extractor_b.model)

    leaf_qn = "InstanceIndexProbe__ConstrainedLeaf"
    paths_a = [occ.instance_path for occ in index_a.occurrences_of(leaf_qn)]
    paths_b = [occ.instance_path for occ in index_b.occurrences_of(leaf_qn)]
    assert paths_a == paths_b

    result_a = index_a.all_occurrences()
    result_b = index_b.all_occurrences()
    all_a = [occ.instance_path for occ in result_a.occurrences]
    all_b = [occ.instance_path for occ in result_b.occurrences]
    assert all_a == all_b
    assert result_a.blocked == result_b.blocked


@requires_license
def test_all_occurrences_surfaces_blocked_definitions(instance_index_model) -> None:
    """Cure (post-audit): a blocked definition must APPEAR in the blocked mapping,
    not merely be absent from occurrences — a bulk caller can no longer mistake a
    partial dump for a complete one (design.md API section, "cured post-audit")."""
    index = build_part_instance_index(instance_index_model)

    result = index.all_occurrences()
    assert "InstanceIndexProbe__LeafN" in result.blocked
    assert "n_member" in result.blocked["InstanceIndexProbe__LeafN"]
    assert "InstanceIndexProbe__BlockHost" in result.blocked["InstanceIndexProbe__LeafN"]
    # A blocked definition contributes no occurrences to the dump.
    assert not any(
        occ.part_def_qn == "InstanceIndexProbe__LeafN" for occ in result.occurrences
    )
    # Occurrences unrelated to the blocked shapes are still present — the dump
    # isn't aborted wholesale, just honest about what it dropped.
    assert any(occ.part_def_qn == "InstanceIndexProbe__CartLeaf" for occ in result.occurrences)

    owners_result = index.all_source_owners()
    assert owners_result.blocked == result.blocked


@requires_license
@pytest.mark.parametrize(
    "leaf_qn,owner,feature",
    [
        ("InstanceIndexProbe__LeafN", "InstanceIndexProbe__BlockHost", "n_member"),
        ("InstanceIndexProbe__LeafStar", "InstanceIndexProbe__BlockHost", "star_member"),
        ("InstanceIndexProbe__LeafRange", "InstanceIndexProbe__BlockHost", "range_member"),
        ("InstanceIndexProbe__LeafOrdered", "InstanceIndexProbe__BlockHost", "ordered_member"),
    ],
)
def test_blocking_names_owner_and_feature(
    instance_index_model, leaf_qn: str, owner: str, feature: str
) -> None:
    """Validation #3: each non-finite shape blocks with a diagnostic naming its
    owner and feature (nonunique is covered by the Phase-1 mock-node truth table —
    it cannot live in this fixture; see PROVENANCE note)."""
    index = build_part_instance_index(instance_index_model)
    with pytest.raises(NonFiniteCardinalityError) as excinfo:
        index.occurrences_of(leaf_qn)
    assert owner in str(excinfo.value)
    assert feature in str(excinfo.value)


@requires_license
def test_exact_reverse_lookups_for_source_identity() -> None:
    """Item 4, Phase 2: the raw-QN reverse queries the identity projection
    needs, answered from the same index — no second walker (I5)."""
    pkg = "source_identity_mixed_consumers"
    extractor = SysMLDataExtractor([FIXTURES_DIR / pkg])
    assert extractor.load_models()
    index = build_part_instance_index(extractor.model)

    (sensor_a,) = index.occurrences_of_part_usage(f"{pkg}::'Twin Bay'::sensor_a")
    assert sensor_a.steps[-1].feature_name == "sensor_a"
    assert index.occurrences_of_part_usage(f"{pkg}::'Twin Bay'::no_such") == []

    both = index.occurrences_of_definition(f"{pkg}::'Twin Sensor'")
    assert [occ.steps[-1].feature_name for occ in both] == ["sensor_a", "sensor_b"]
    assert index.occurrences_of_definition(f"{pkg}::'No Such Def'") == []

    fact = index.redefining_target_on(sensor_a, f"{pkg}::'Twin Sensor'::reading")
    assert fact is not None
    assert fact.qualified_name == f"{pkg}::'Twin Bay'::sensor_a::reading"
    assert index.redefining_target_on(sensor_a, f"{pkg}::'Rig'::gain_setting") is None
