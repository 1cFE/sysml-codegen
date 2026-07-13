"""Truth-table tests for the part-instance-index cardinality classifier.

License-free: exercises ``classify_cardinality`` against mock multiplicity nodes,
mirroring the mock idiom in ``test_hierarchy_resolver.py`` (``MockMultiplicityRange``
et al.). One test per B1-confirmed shape (`b1-probe-evidence.md`); see
``design.md`` D3 for the dispatch this pins.
"""

from sysml_codegen.analysis.part_instance_index import (
    Fixed,
    NonFinite,
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
