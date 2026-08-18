"""The closed binding-source variants and the total deep-relationship-path factory.

Two closed surfaces, both valid by construction, both scoped-strict
(``design.md#scoped-strict-type-boundary``).

**Binding sources.**  A binding's right-hand side is exactly one of four things, and
each variant carries only what that thing can supply.  An exact reference carries an
:class:`~agentic_mbse.sysml.reference_use.ExactReferenceUse`; an authored ``#(i)``
carries the indexed variant, which has no path at all; an expression and a literal
carry no semantic path field whatsoever.  The permissive predecessor had one record
with ``semantic_reference: ... | None``, so "a supported reference binding with no
path" was a representable state the resolver had to defend against with a bare
``RuntimeError``.  Here it cannot be constructed.

**Deep relationship paths.**  :func:`exact_path_from_relationship` materializes the
complete ``chaining_features`` sequence of a redefined feature.  It is total: every
segment must be a mapped ``Feature`` with one typed target fact, and the first segment
that is not raises, naming its ordinal, authored target, and location.  It never filters
a missing element and never returns a shortened path — which is what its predecessor
did, silently turning a three-step override into whatever two steps happened to resolve.

See ``design.md#binding-and-deep-path-values-are-valid-by-construction``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from agentic_mbse.errors import SemanticEvidenceCode, SemanticEvidenceError
from agentic_mbse.sysml.data_models import ResolvedTargetFact
from agentic_mbse.sysml.reference_use import (
    ExactReferenceUse,
    ExactSemanticPath,
    IndexedReferenceUse,
    evidence_error,
    resolved_target_fact,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter

__all__ = [
    "BindingSourceEvidence",
    "BoundFormal",
    "ExactBindingSource",
    "ExpressionBindingSource",
    "IndexedBindingSource",
    "LiteralBindingSource",
    "bound_formal",
    "binding_source_kind",
    "exact_path_from_relationship",
    "relationship_has_path",
    "require_exact_binding_use",
]


@dataclass(frozen=True)
class BoundFormal:
    """The consumer side of a binding: which formal is being bound, exactly.

    A consumer coordinate, never an identity source (design D3).  Self-binding is an
    exact comparison of the right-hand side's leaf against :attr:`element_id`, never
    ``param_name == leaf``.
    """

    element_id: UUID
    qualified_name: str
    redefined_element_ids: tuple[UUID, ...]
    redefined_qualified_names: tuple[str, ...]


@dataclass(frozen=True)
class ExactBindingSource:
    """A binding whose right-hand side is one reference the toolchain can honor."""

    formal: BoundFormal
    use: ExactReferenceUse

    def __post_init__(self) -> None:
        if not isinstance(self.use, ExactReferenceUse):
            raise TypeError("ExactBindingSource requires an ExactReferenceUse")

    @property
    def written_text(self) -> str:
        return self.use.authored_text

    @property
    def is_self_binding(self) -> bool:
        return self.use.path.leaf.element_id == self.formal.element_id


@dataclass(frozen=True)
class IndexedBindingSource:
    """A binding whose right-hand side is an authored ``#(i)``.

    Carries no path, because none exists.  A consumer cannot drop the index by reading
    a field off this value; there is no field to read.
    """

    formal: BoundFormal
    use: IndexedReferenceUse

    def __post_init__(self) -> None:
        if not isinstance(self.use, IndexedReferenceUse):
            raise TypeError("IndexedBindingSource requires an IndexedReferenceUse")

    @property
    def written_text(self) -> str:
        return self.use.reference

    @property
    def is_self_binding(self) -> bool:
        return False


@dataclass(frozen=True)
class ExpressionBindingSource:
    """A binding whose right-hand side is general math, with no source feature."""

    formal: BoundFormal
    written_text: str | None
    location: tuple[str, int] | None

    @property
    def is_self_binding(self) -> bool:
        return False


@dataclass(frozen=True)
class LiteralBindingSource:
    """A binding whose right-hand side is an authored literal — its own source."""

    formal: BoundFormal
    value: float | int | str | bool | None

    @property
    def written_text(self) -> str | None:
        return str(self.value) if self.value is not None else None

    @property
    def is_self_binding(self) -> bool:
        return False


type BindingSourceEvidence = (
    ExactBindingSource | IndexedBindingSource | ExpressionBindingSource | LiteralBindingSource
)


def binding_source_kind(evidence: object) -> str:
    """Render one closed binding variant, failing on any value outside the union."""
    if isinstance(evidence, ExactBindingSource):
        return "reference"
    if isinstance(evidence, IndexedBindingSource):
        return "indexed_source"
    if isinstance(evidence, ExpressionBindingSource):
        return "expression_source"
    if isinstance(evidence, LiteralBindingSource):
        return "authored_literal"
    raise TypeError(f"value is not BindingSourceEvidence: {type(evidence).__name__}")


def require_exact_binding_use(evidence: object) -> ExactReferenceUse:
    """Return an exact binding use; name an index even when inventory was bypassed."""
    if isinstance(evidence, ExactBindingSource):
        return evidence.use
    if isinstance(evidence, IndexedBindingSource):
        raise SemanticEvidenceError(
            SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED,
            operation="binding_source",
            detail=(
                "indexed element reference is valid SysML but not implemented by this "
                "executable subset; the index cannot form an exact binding source"
            ),
            location=evidence.use.location,
            reference=evidence.use.reference,
        )
    if isinstance(evidence, (ExpressionBindingSource, LiteralBindingSource)):
        raise TypeError(f"{type(evidence).__name__} is not an exact binding source")
    raise TypeError(f"value is not BindingSourceEvidence: {type(evidence).__name__}")


def bound_formal(param_elem: Any) -> BoundFormal:
    """Capture the bound formal's own identity and the calc-def formals it redefines."""
    redefined_names: list[str] = []
    redefined_ids: list[UUID] = []
    for redefinition in getattr(param_elem, "owned_redefinitions", None) or []:
        redefined_feature = getattr(redefinition, "redefined_feature", None)
        redefined_qn = getattr(redefined_feature, "qualified_name", None)
        if redefined_qn is not None:
            redefined_names.append(str(redefined_qn))
        if redefined_feature is not None:
            redefined_ids.append(SysideAdapter.element_id(redefined_feature))
    qualified_name = getattr(param_elem, "qualified_name", None)
    return BoundFormal(
        element_id=SysideAdapter.element_id(param_elem),
        qualified_name=str(qualified_name) if qualified_name is not None else "",
        redefined_element_ids=tuple(redefined_ids),
        redefined_qualified_names=tuple(redefined_names),
    )


def exact_path_from_relationship(redefined_feature: Any) -> ExactSemanticPath:
    """Materialize one redefinition endpoint's complete chaining-feature path.

    SysIDE types ``chaining_features`` as a sequence of ``Feature``, not as an expression
    sequence, so this is a relationship selector and not an expression walk.  The factory
    is total over it: every materialized segment must be a mapped ``Feature`` carrying one
    typed target fact.

    Raises on the first segment that is not, naming its ordinal, authored target, and
    location.  A mapped ``IndexExpression`` — necessarily not a ``Feature`` — is refused as
    ``INDEXED_REFERENCE_UNSUPPORTED``; any other absent or non-feature segment is
    ``RESOLVED_TARGET_MISSING``.  Nothing here filters a segment out, so a shortened path
    is not a reachable result.
    """
    segments = _relationship_segments(redefined_feature)
    if not segments:
        raise evidence_error(
            SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
            "exact_path_from_relationship",
            "redefinition endpoint materializes no chaining features",
            redefined_feature,
        )

    facts: list[ResolvedTargetFact] = []
    for ordinal, segment in enumerate(segments):
        if SysideAdapter.is_instance(segment, "IndexExpression"):
            raise _segment_error(
                SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED,
                "deep override segment is an authored index",
                segment,
                ordinal,
            )
        if not SysideAdapter.is_instance(segment, "Feature"):
            raise _segment_error(
                SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
                f"deep override segment is a {type(segment).__name__}, not a Feature",
                segment,
                ordinal,
            )
        fact = resolved_target_fact(segment)
        if fact is None:
            raise _segment_error(
                SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
                "deep override segment has no exact target fact",
                segment,
                ordinal,
            )
        facts.append(fact)

    materialized = tuple(facts)
    return ExactSemanticPath(
        root=materialized[0],
        segments=materialized,
        leaf=materialized[-1],
        resolved_member_names=tuple(fact.element_name for fact in materialized[1:]),
    )


def _relationship_segments(redefined_feature: Any) -> tuple[Any, ...]:
    """The one Codegen-owned read of a relationship's authored feature sequence."""
    return tuple(getattr(redefined_feature, "chaining_features", None) or ())


def relationship_has_path(redefined_feature: Any) -> bool:
    """Whether a redefinition endpoint names a deep relationship path."""
    return bool(_relationship_segments(redefined_feature))


def _segment_error(
    code: SemanticEvidenceCode,
    detail: str,
    segment: Any,
    ordinal: int,
) -> SemanticEvidenceError:
    """One located refusal that names which segment of the path failed."""
    return evidence_error(
        code,
        "exact_path_from_relationship",
        f"segment {ordinal}: {detail}",
        segment,
    )
