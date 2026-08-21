"""The pre-graph expression-evidence inventory and the exact-only resolver adapter.

One inventory, built once at the conversion boundary before any calculation definition
is extracted, any elaborator is constructed, or any instance graph is allocated.  Every
expression-bearing consumer reads its row from here; none of them walks a raw expression
for itself.

Three things live in this module, and nothing else
(``design.md#d7-one-codegen-conversion-boundary``):

1. **Site identity.**  A site is one owning declaration plus one closed role.  The roles
   are disjoint by construction — a declaration's role is decided by what owns it — so a
   site key names exactly one expression.
2. **The inventory.**  :func:`build_expression_evidence_inventory` enumerates the closed
   site set, acquires each site's references through Agentic's one total inspection
   operation, and refuses every :class:`IndexedReferenceUse` by name.  That refusal is
   the reason the inventory is pre-graph: an authored index is a capability the toolchain
   does not have, and naming it as an occurrence problem later would point the modeller at
   the wrong thing to fix.
3. **The exact-only adapter.**  :func:`require_exact_use` accepts an
   :class:`ExactReferenceUse` and nothing else — not the union, not a legacy fact, not an
   IR node, not a duck-typed lookalike.  It checks the concrete value at runtime because
   this repository's full static type lane is not a green gate, so the type signature
   alone is not load-bearing.

The pre-graph scan is deliberately not the only index defense.  Consumers branch
exhaustively over the closed union and reach :func:`require_exact_use`, so an indexed use
that somehow bypassed the inventory still raises rather than resolving.  Tests
distinguish the two layers by control flow, never by the public diagnostic, which is the
same on purpose.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import UUID

from agentic_mbse.errors import SemanticEvidenceCode, SemanticEvidenceError
from agentic_mbse.sysml.reference_use import (
    ExactReferenceUse,
    IndexedReferenceUse,
    ReferenceUse,
    inspect_reference_uses,
)
from agentic_mbse.sysml.reference_use import (
    unit_annotation_value as agentic_unit_annotation_value,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter

__all__ = [
    "ExpressionEvidenceInventory",
    "ExpressionInventoryError",
    "ExpressionSite",
    "ExpressionSiteRole",
    "build_expression_evidence_inventory",
    "require_exact_use",
    "unit_annotated_value",
]


class ExpressionSiteRole(str, Enum):
    """The closed set of production expression sites.

    Contextual routing, not semantics: the role says which consumer owns the site, never
    what the expression means.  Disjoint by construction — see :func:`_role_for_owner`.
    """

    CALC_DEFINITION_DEPENDENCY = "calc_definition_dependency"
    BINDING = "binding"
    ALIAS = "alias"
    COMPUTED_ATTRIBUTE = "computed_attribute"
    CONSTRAINT_PREDICATE = "constraint_predicate"


@dataclass(frozen=True)
class ExpressionSite:
    """One expression site's exact identity, plus non-identifying public provenance."""

    declaration_id: UUID
    role: ExpressionSiteRole
    reference: str | None = field(default=None, compare=False, hash=False)
    location: tuple[str, int] | None = field(default=None, compare=False, hash=False)


class ExpressionEvidenceInventory:
    """Every production expression site's acquired reference uses, by site identity.

    Read-only after construction.  A lookup for a site the inventory does not hold is an
    invariant failure rather than an empty result: a consumer that could read "no
    references" out of a missing row would silently drop every dependency the site
    declares, which is the failure mode the inventory exists to remove.
    """

    def __init__(self, rows: dict[ExpressionSite, tuple[ReferenceUse, ...]]) -> None:
        self._rows = dict(rows)
        self._sites_by_declaration: dict[UUID, ExpressionSite] = {}
        for site in self._rows:
            existing = self._sites_by_declaration.get(site.declaration_id)
            if existing is not None and existing.role is not site.role:
                raise ExpressionInventoryError(
                    f"expression declaration {site.declaration_id} has multiple assigned roles: "
                    f"{existing.role.value} and {site.role.value}",
                    reference=site.reference or existing.reference,
                    location=site.location or existing.location,
                )
            self._sites_by_declaration[site.declaration_id] = site

    def __len__(self) -> int:
        return len(self._rows)

    def __contains__(self, site: ExpressionSite) -> bool:
        return site in self._rows

    def sites(self) -> tuple[ExpressionSite, ...]:
        return tuple(self._rows)

    def site_for(
        self,
        declaration_id: UUID,
        *,
        reference: str | None = None,
        location: tuple[str, int] | None = None,
    ) -> ExpressionSite:
        """Return the one role assigned to a declaration at the conversion boundary."""
        try:
            return self._sites_by_declaration[declaration_id]
        except KeyError:
            raise ExpressionInventoryError(
                f"expression declaration {declaration_id} has no assigned evidence site",
                reference=reference,
                location=location,
            ) from None

    def require(self, site: ExpressionSite) -> tuple[ReferenceUse, ...]:
        """The acquired references for one site, or an invariant failure."""
        try:
            return self._rows[site]
        except KeyError:
            raise ExpressionInventoryError(
                f"expression site {site.role.value} "
                f"{site.declaration_id} is absent from the evidence inventory",
                reference=site.reference,
                location=site.location,
            ) from None

    def require_exact(self, site: ExpressionSite) -> tuple[ExactReferenceUse, ...]:
        """One site's references, every one of them proven exact."""
        exact: list[ExactReferenceUse] = []
        for use in self.require(site):
            try:
                exact.append(require_exact_use(use))
            except ExpressionInventoryError as error:
                contextual = ExpressionInventoryError(
                    error.detail,
                    reference=error.reference or site.reference,
                    location=error.location or site.location,
                    cause=error,
                )
                raise contextual from error
        return tuple(exact)


class ExpressionInventoryError(Exception):
    """The inventory was asked for a site it does not hold, or built a duplicate one.

    Not a modelling defect and not a public diagnostic: reaching it means a consumer and
    the site enumerator disagree about the closed site set, which is a defect in this
    package.
    """

    def __init__(
        self,
        detail: str,
        *,
        reference: str | None = None,
        location: tuple[str, int] | None = None,
        cause: BaseException | None = None,
    ) -> None:
        self.detail = detail
        self.reference = reference
        self.location = location
        self.cause = cause
        super().__init__(detail)


def require_exact_use(value: object) -> ExactReferenceUse:
    """Accept one exact reference use, and refuse everything else by name.

    The exhaustive branch every consumer funnels through.  An
    :class:`IndexedReferenceUse` raises the same public capability refusal the inventory
    raises, so bypassing the pre-graph scan changes which layer catches the index but
    never whether it is caught.  Any other value — a legacy fact, an expression IR node,
    an arbitrary duck-typed lookalike carrying a ``path`` attribute — is an invariant
    failure, because reaching this call with one means a conversion happened that the
    static ownership gate forbids.
    """
    if isinstance(value, ExactReferenceUse):
        return value
    if isinstance(value, IndexedReferenceUse):
        raise _indexed_refusal(value)
    raise ExpressionInventoryError(
        f"exact resolution requires an ExactReferenceUse, got {type(value).__name__}"
    )


def _indexed_refusal(use: IndexedReferenceUse) -> SemanticEvidenceError:
    """The one refusal for an authored index, carrying what the modeller wrote and where."""
    return SemanticEvidenceError(
        SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED,
        operation="expression_evidence",
        detail=(
            "indexed element reference is valid SysML but not implemented by this "
            "executable subset; the index is never flattened into a supported source"
        ),
        location=use.location,
        reference=use.reference,
    )


# ======================================================================================
# Site enumeration — Codegen-owned contextual routing
# ======================================================================================

#: Owners whose value-bearing members are calculation-definition dependencies.
_DEFINITION_OWNERS = ("CalculationDefinition",)

#: Owners whose value-bearing members are bindings of a formal parameter.
_BINDING_OWNERS = ("CalculationUsage", "ConstraintUsage")


def build_expression_evidence_inventory(model: Any) -> ExpressionEvidenceInventory:
    """Acquire every production expression site's references, once, before the graph.

    Refuses an authored index the moment it is acquired, so no consumer, occurrence
    resolver, or graph allocation runs first.  Raises
    :class:`~agentic_mbse.errors.SemanticEvidenceError` for an unhonourable reference and
    :class:`ExpressionInventoryError` if the enumerator produced the same site twice.
    """
    rows: dict[ExpressionSite, tuple[ReferenceUse, ...]] = {}
    for site, expression in _enumerate_sites(model):
        if site in rows:
            raise ExpressionInventoryError(
                f"expression site {site.role.value} {site.declaration_id} was enumerated twice",
                reference=site.reference,
                location=site.location,
            )
        rows[site] = _acquire(expression, site=site)
    return ExpressionEvidenceInventory(rows)


def _acquire(
    expression: Any,
    *,
    site: ExpressionSite | None = None,
) -> tuple[ReferenceUse, ...]:
    """One site's references, with every authored index refused by name."""
    try:
        uses = inspect_reference_uses(expression)
    except SemanticEvidenceError as error:
        if error.reference is not None:
            raise
        reference, location = _expression_context(expression)
        contextual = SemanticEvidenceError(
            error.code,
            operation=error.operation,
            detail=error.detail,
            location=error.location or (site.location if site is not None else location),
            reference=(site.reference if site is not None else None) or reference,
            cause=error,
        )
        raise contextual from error
    for use in uses:
        if isinstance(use, IndexedReferenceUse):
            raise _indexed_refusal(use)
    return uses


def _enumerate_sites(model: Any) -> list[tuple[ExpressionSite, Any]]:
    """The closed production site set, in a stable order.

    Only declared features are sites.  SysIDE also models an expression's own operands as
    anonymous features carrying value expressions; those are parts of an expression, not
    declarations of one, and enumerating them would report a sub-span of the authored text
    as if the modeller had written it.
    """
    sites: list[tuple[ExpressionSite, Any]] = []
    for feature in SysideAdapter.elements_of_type(model, "Feature", include_subtypes=True):
        if getattr(feature, "qualified_name", None) is None:
            continue
        expression = getattr(feature, "feature_value_expression", None)
        if expression is None:
            continue
        role = _role_for_owner(feature, expression)
        reference, location = _expression_context(expression)
        sites.append(
            (
                ExpressionSite(
                    SysideAdapter.element_id(feature),
                    role,
                    reference=reference,
                    location=location,
                ),
                expression,
            )
        )

    for type_name in ("ConstraintDefinition", "ConstraintUsage"):
        for declaration in SysideAdapter.elements_of_type(
            model, type_name, include_subtypes=True
        ):
            predicate = getattr(declaration, "result_expression", None)
            if predicate is None:
                continue
            reference, location = _expression_context(predicate)
            site = ExpressionSite(
                SysideAdapter.element_id(declaration),
                ExpressionSiteRole.CONSTRAINT_PREDICATE,
                reference=reference,
                location=location,
            )
            sites.append((site, predicate))
    return sites


def _role_for_owner(feature: Any, expression: Any) -> ExpressionSiteRole:
    """Which consumer owns this declaration's expression.

    Decided by what declares the feature, so the roles cannot overlap: a calculation
    definition's member is a dependency, a calculation or constraint usage's member is a
    binding, and anything else is a modelled value — an alias when it is a plain reference
    and a computed attribute when it is anything more.
    """
    owner = getattr(feature, "owning_type", None)
    if owner is not None:
        if any(SysideAdapter.is_instance(owner, name) for name in _DEFINITION_OWNERS):
            return ExpressionSiteRole.CALC_DEFINITION_DEPENDENCY
        if any(SysideAdapter.is_instance(owner, name) for name in _BINDING_OWNERS):
            return ExpressionSiteRole.BINDING
    try:
        value_expression = unit_annotated_value(expression)
    except SemanticEvidenceError as error:
        raise _contextualize(error, expression) from error
    if _is_plain_reference(value_expression):
        return ExpressionSiteRole.ALIAS
    return ExpressionSiteRole.COMPUTED_ATTRIBUTE


def _expression_context(expression: Any) -> tuple[str | None, tuple[str, int] | None]:
    """Best available authored spelling and source location for a public failure."""
    location = SysideAdapter.get_source_location(expression)
    try:
        return SysideAdapter.authored_text(expression), location
    except SemanticEvidenceError:
        qualified_name = getattr(expression, "qualified_name", None)
        return (str(qualified_name) if qualified_name else None), location


def _contextualize(error: SemanticEvidenceError, expression: Any) -> SemanticEvidenceError:
    """Attach site-level authored context when a structural primitive has none."""
    if error.reference is not None:
        return error
    reference, location = _expression_context(expression)
    return SemanticEvidenceError(
        error.code,
        operation=error.operation,
        detail=error.detail,
        location=error.location or location,
        reference=reference,
        cause=error,
    )


def _is_plain_reference(expression: Any) -> bool:
    """Whether a value expression is a bare reference or feature chain and nothing more."""
    return SysideAdapter.is_instance(
        expression, "FeatureChainExpression"
    ) or SysideAdapter.is_instance(expression, "FeatureReferenceExpression")


def unit_annotated_value(expression: Any) -> Any:
    """Apply Codegen's value-site policy over Agentic's structural primitive.

    ``= 0.2 [m]`` means the number ``0.2``; ``[m]`` says how to read it.  The unit is not a
    data dependency, so the elaborator's value-shape decision looks past it — otherwise a
    unit-annotated literal reads as general math and mints a computed node instead of a
    value.

    Agentic owns every structural question: mapped metatype, operator, arity, and which
    operand is the value.  ``None`` from that primitive means the expression is not an
    annotation, so Codegen passes it through.  A malformed annotation raises upstream and
    reaches the one public conversion boundary; this policy never catches it.
    """
    annotated_value = agentic_unit_annotation_value(expression)
    return expression if annotated_value is None else annotated_value
