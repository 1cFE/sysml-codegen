"""Truth-table tests for the part-instance-index cardinality classifier.

License-free: exercises ``classify_cardinality`` against mock multiplicity nodes,
mirroring the mock idiom in ``test_hierarchy_resolver.py`` (``MockMultiplicityRange``
et al.). One test per B1-confirmed shape (`b1-probe-evidence.md`); see
``design.md`` D3 for the dispatch this pins.
"""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

from sysml_codegen.analysis.part_instance_index import (
    Fixed,
    InstanceOccurrence,
    NonFinite,
    PathStep,
    RecursiveContainmentError,
    _occurrence_sort_key,
    classify_cardinality,
)

OWNER_QN = "Owner"
FEATURE = "member"


class _MockLiteralInteger:
    """Class name 'LiteralInteger' drives the is_instance fallback."""

    def __init__(self, value: int) -> None:
        self.value = value


class _MockLiteralInfinity:
    """Class name 'LiteralInfinity' drives the is_instance fallback."""


class _MockFeatureReferenceExpression:
    """Class name 'FeatureReferenceExpression' drives the is_instance fallback."""


class _MockUnknownBoundNode:
    """An unrecognized upper_bound node type — must fail closed."""


class _MockMultiplicityRange:
    def __init__(self, upper_bound: object, lower_bound: object | None = None) -> None:
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound


class _MockUsage:
    def __init__(
        self,
        multiplicity: _MockMultiplicityRange,
        is_ordered: bool = False,
        is_nonunique: bool = False,
    ) -> None:
        self.multiplicity = multiplicity
        self.is_ordered = is_ordered
        self.is_nonunique = is_nonunique


def _usage(
    upper: object,
    lower: object | None = None,
    is_ordered: bool = False,
    is_nonunique: bool = False,
) -> _MockUsage:
    return _MockUsage(
        _MockMultiplicityRange(upper_bound=upper, lower_bound=lower),
        is_ordered=is_ordered,
        is_nonunique=is_nonunique,
    )


def test_bare_fixed() -> None:
    """[3] -> Fixed(3)."""
    usage = _usage(_MockLiteralInteger(3))
    assert classify_cardinality(usage, OWNER_QN, FEATURE) == Fixed(3)


def test_equal_bounds_admit() -> None:
    """[3..3] -> Fixed(3) (C2: equal literal bounds admitted as fixed)."""
    usage = _usage(_MockLiteralInteger(3), lower=_MockLiteralInteger(3))
    assert classify_cardinality(usage, OWNER_QN, FEATURE) == Fixed(3)


def test_range_blocks() -> None:
    """[0..5] -> NonFinite (unequal bounds)."""
    usage = _usage(_MockLiteralInteger(5), lower=_MockLiteralInteger(0))
    result = classify_cardinality(usage, OWNER_QN, FEATURE)
    assert isinstance(result, NonFinite)


def test_unbounded_blocks() -> None:
    """[*] -> NonFinite (unbounded)."""
    usage = _usage(_MockLiteralInfinity())
    result = classify_cardinality(usage, OWNER_QN, FEATURE)
    assert isinstance(result, NonFinite)


def test_parameterized_blocks() -> None:
    """[n] -> NonFinite (parameterized; cached default must not leak through)."""
    usage = _usage(_MockFeatureReferenceExpression())
    result = classify_cardinality(usage, OWNER_QN, FEATURE)
    assert isinstance(result, NonFinite)


def test_ordered_blocks() -> None:
    """[3] ordered -> NonFinite."""
    usage = _usage(_MockLiteralInteger(3), is_ordered=True)
    result = classify_cardinality(usage, OWNER_QN, FEATURE)
    assert isinstance(result, NonFinite)


def test_nonunique_blocks() -> None:
    """[3] nonunique -> NonFinite."""
    usage = _usage(_MockLiteralInteger(3), is_nonunique=True)
    result = classify_cardinality(usage, OWNER_QN, FEATURE)
    assert isinstance(result, NonFinite)


def test_unrecognized_upper_bound_node_blocks() -> None:
    """An upper_bound node type this dispatch doesn't recognize -> NonFinite (fail-closed)."""
    usage = _usage(_MockUnknownBoundNode())
    result = classify_cardinality(usage, OWNER_QN, FEATURE)
    assert isinstance(result, NonFinite)


def test_occurrence_sort_key_distinguishes_root_and_leaf_identity() -> None:
    root_a = InstanceOccurrence("LeafB", (PathStep("RootA", "member", 0),))
    root_b = InstanceOccurrence("LeafA", (PathStep("RootB", "member", 0),))
    same_root_other_leaf = InstanceOccurrence("LeafA", (PathStep("RootA", "member", 0),))

    assert _occurrence_sort_key(root_a) != _occurrence_sort_key(root_b)
    assert _occurrence_sort_key(root_a) != _occurrence_sort_key(same_root_other_leaf)


def test_occurrence_order_is_stable_across_python_hash_seeds() -> None:
    probe = """
from sysml_codegen.analysis.part_instance_index import (
    InstanceOccurrence,
    PathStep,
    _occurrence_sort_key,
)
occurrences = {
    InstanceOccurrence("LeafA", (PathStep("RootB", "member", 0),)),
    InstanceOccurrence("LeafB", (PathStep("RootA", "member", 0),)),
}
print(",".join(item.part_def_qn for item in sorted(occurrences, key=_occurrence_sort_key)))
"""
    outputs = []
    for seed in (1, 2, 3, 5, 10, 42):
        env = {**os.environ, "PYTHONHASHSEED": str(seed)}
        completed = subprocess.run(
            [sys.executable, "-c", probe],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        outputs.append(completed.stdout.strip())
    assert outputs == ["LeafB,LeafA"] * len(outputs)


# ---------------------------------------------------------------------------
# Structural containment walk: cycle detection and finite preservation.
#
# These drive ``_structured_paths`` directly against a mock part-usage index —
# the same license-free idiom as the cardinality table above.
# ---------------------------------------------------------------------------


class _MockPartDefinition:
    """Class name 'PartDefinition' drives the is_instance fallback."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.owner = None


class _MockPackage:
    def __init__(self, name: str) -> None:
        self.name = name
        self.owner = None


class _MockPartUsage:
    """A part usage as the walker reads it: a name, an owner, and a multiplicity."""

    def __init__(self, name: str, *, owning_type=None, owner=None, multiplicity=None) -> None:
        self.name = name
        self.owning_type = owning_type
        self.owner = owner
        self.multiplicity = multiplicity
        self.is_ordered = False
        self.is_nonunique = False


def _feature(name: str, owning_def: str, **kwargs) -> _MockPartUsage:
    """A usage owned by a PartDefinition — the walker's recursive step."""
    return _MockPartUsage(name, owning_type=_MockPartDefinition(owning_def), **kwargs)


def _root(name: str, package: str = "Pkg", **kwargs) -> _MockPartUsage:
    """A usage owned by a package — the walker's terminal step."""
    return _MockPartUsage(name, owner=_MockPackage(package), **kwargs)


def _paths(index: dict, requested: str) -> list[tuple[PathStep, ...]]:
    return [path for path, _usage in _structured_paths(index, requested)]


def _structured_paths(index: dict, requested: str):
    from sysml_codegen.analysis.part_instance_index import _structured_paths as walk

    return walk(requested, index, requested)


def test_self_cycle_raises_structured_context() -> None:
    index = {"Node": [_feature("recursive", "Node")]}
    with pytest.raises(RecursiveContainmentError) as caught:
        _paths(index, "Node")
    error = caught.value
    assert error.requested_owner_qn == "Node"
    assert error.edge_owner_qn == "Node"
    assert error.edge_feature_name == "recursive"
    assert error.edge_type_qn == "Node"
    assert error.cycle_path == ("Node", "Node")


def test_indirect_cycle_raises_structured_context() -> None:
    index = {"A": [_feature("a", "B")], "B": [_feature("b", "A")]}
    with pytest.raises(RecursiveContainmentError) as caught:
        _paths(index, "A")
    error = caught.value
    assert error.cycle_path == ("A", "B", "A")
    assert (error.edge_owner_qn, error.edge_feature_name, error.edge_type_qn) == ("A", "b", "B")
    assert error.requested_owner_qn == "A"


def test_finite_first_cycle_is_atomic_under_feature_reversal() -> None:
    """A finite sibling walked before the cycle yields no partial result, and the
    reported edge does not depend on declaration order."""
    finite = _root("finite")
    cyclic = _feature("cyclic", "X")
    forward = {"X": [finite, cyclic]}
    reversed_order = {"X": [cyclic, finite]}

    errors = []
    for index in (forward, reversed_order):
        with pytest.raises(RecursiveContainmentError) as caught:
            _paths(index, "X")
        errors.append(caught.value)

    first, second = errors
    assert first.cycle_path == second.cycle_path == ("X", "X")
    assert first.edge_feature_name == second.edge_feature_name == "cyclic"
    # Repeat traversal of the same index is identical, not order- or state-dependent.
    with pytest.raises(RecursiveContainmentError) as repeated:
        _paths(forward, "X")
    assert repeated.value.cycle_path == first.cycle_path


def test_active_stack_is_per_path_not_a_global_visited_set() -> None:
    """A diamond re-reaches ``Top`` on two independent paths. A global visited set
    would drop the second; the per-path active stack keeps both."""
    index = {
        "Leaf": [_feature("l", "Mid")],
        "Mid": [_feature("m1", "Top"), _feature("m2", "Top")],
        "Top": [_root("top")],
    }
    paths = _paths(index, "Leaf")
    assert len(paths) == 2
    assert {step.feature_name for path in paths for step in path} == {"top", "m1", "m2", "l"}


def test_subtype_reentry_on_a_sibling_branch_is_not_a_cycle() -> None:
    """Two sibling features of the same definition each walk the same parent
    independently; neither sees the other's stack."""
    index = {
        "Part": [_feature("left", "Holder"), _feature("right", "Holder")],
        "Holder": [_root("holder")],
    }
    assert len(_paths(index, "Part")) == 2


def test_zero_count_returns_empty() -> None:
    index = {"Empty": [_root("none", multiplicity=_MockMultiplicityRange(_MockLiteralInteger(0)))]}
    assert _paths(index, "Empty") == []


def test_multi_digit_occurrence_order_is_numeric() -> None:
    """Occurrence 2 precedes occurrence 10 — integer order, never rendered-string."""
    occurrences = [
        InstanceOccurrence("Bank", (PathStep("Pkg", "member", index),)) for index in (10, 2)
    ]
    ordered = sorted(occurrences, key=_occurrence_sort_key)
    assert [occurrence.steps[0].occurrence_index for occurrence in ordered] == [2, 10]
