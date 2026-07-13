"""Part-instance index: subtype closure and cardinality expansion over part structure.

A second, structure-only enumerator that answers, per part definition, what all the
concrete occurrences of that definition are — counting subtype instances and
fixed-multiplicity siblings, each as its own identity. It runs beside the calc-driven
instantiation-path finder in ``usage_extractor.py`` and never through it: this module
is additive, imported by nothing else in this item (Item 5 wires it in).
"""

from dataclasses import dataclass
from typing import Any

from agentic_mbse.sysml.syside_adapter import SysideAdapter


@dataclass(frozen=True)
class PathStep:
    """One step of a structured instantiation path.

    ``occurrence_index`` is set only when the step's usage carries a fixed
    multiplicity (``classify_cardinality`` returned ``Fixed``); it is ``None`` for a
    singleton step.
    """

    owning_def_qn: str
    feature_name: str
    occurrence_index: int | None


@dataclass(frozen=True)
class Fixed:
    """A usage's multiplicity is a single, provably finite literal count."""

    count: int


@dataclass(frozen=True)
class NonFinite:
    """A usage's multiplicity cannot be proven to be a single finite count."""

    reason: str


class NonFiniteCardinalityError(Exception):
    """Raised when a queried path passes through a non-finite multiplicity.

    Names the owning part definition and the part usage feature so the diagnostic
    is actionable — the index never silently drops a non-finite shape (Design
    Principle 5: no third disposition beyond expand-finite or block-loud).
    """

    def __init__(self, owning_part_def_qn: str, part_usage_name: str, reason: str) -> None:
        self.owning_part_def_qn = owning_part_def_qn
        self.part_usage_name = part_usage_name
        self.reason = reason
        super().__init__(
            f"Non-finite multiplicity on '{part_usage_name}' owned by "
            f"'{owning_part_def_qn}' ({reason}); cannot expand to concrete instances."
        )


def classify_cardinality(usage: Any, owning_def_qn: str, feature_name: str) -> Fixed | NonFinite:
    """Classify a usage's multiplicity as a single fixed count or non-finite.

    Called only for a usage that carries a multiplicity node (``usage.multiplicity
    is not None``); a singleton usage is the walker's job, not this function's.

    Reads only the usage's live ``multiplicity`` node and its ``is_ordered`` /
    ``is_nonunique`` flags — never ``MultiplicityData`` or any cached bound, both of
    which are confirmed unreliable for this gate (B1/B2 evidence, design.md D3/D8):
    a parameterized ``[n]`` resolves its default into ``cached_upper_bound``, so a
    cached-value gate would silently expand the default instead of blocking it.

    Dispatch is fail-closed: any ``upper_bound`` node type other than
    ``LiteralInteger`` or the two explicitly recognized non-finite shapes
    (``LiteralInfinity``, ``FeatureReferenceExpression``) blocks, so a future SysIDE
    surface change cannot silently start expanding.
    """
    if usage.is_ordered:
        return NonFinite(reason=f"'{feature_name}' is ordered")
    if usage.is_nonunique:
        return NonFinite(reason=f"'{feature_name}' is nonunique")

    multiplicity = usage.multiplicity
    upper_bound = multiplicity.upper_bound
    lower_bound = multiplicity.lower_bound

    if SysideAdapter.is_instance(upper_bound, "LiteralInfinity"):
        return NonFinite(reason=f"'{feature_name}' is unbounded ([*])")
    if SysideAdapter.is_instance(upper_bound, "FeatureReferenceExpression"):
        return NonFinite(reason=f"'{feature_name}' has a parameterized multiplicity")
    if not SysideAdapter.is_instance(upper_bound, "LiteralInteger"):
        return NonFinite(
            reason=f"'{feature_name}' has an unrecognized multiplicity bound "
            f"({type(upper_bound).__name__})"
        )

    upper = upper_bound.value
    if lower_bound is None:
        return Fixed(count=upper)
    if not SysideAdapter.is_instance(lower_bound, "LiteralInteger"):
        return NonFinite(
            reason=f"'{feature_name}' has an unrecognized lower multiplicity bound "
            f"({type(lower_bound).__name__})"
        )

    lower = lower_bound.value
    if lower == upper:
        return Fixed(count=upper)
    return NonFinite(reason=f"'{feature_name}' has a multiplicity range [{lower}..{upper}]")
