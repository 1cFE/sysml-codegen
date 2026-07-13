"""Concrete constraint lowering (Item 5).

Expands each extracted ``assert constraint`` into concrete graph structure: one
:class:`~sysml_codegen.resolution.models.ConcreteConstraint` per concrete owner
instance, every formal strictly resolved to a real producer channel, a real
design attribute, or an overridable modeled default — never synthesized. See
``.project/active/constraint-lowering/design.md`` for the full design.
"""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING

from sysml_codegen.analysis.dependency_backtracker import terminal_disposition
from sysml_codegen.core.identifier_types import ScopedKey
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from sysml_codegen.resolution.models import (
    ConcreteConstraint,
    ConcreteConstraintInput,
    ConstraintInputResolution,
)

if TYPE_CHECKING:
    from agentic_mbse.sysml.expression_facts import FeatureReferenceFact

    from sysml_codegen.analysis.parameter_groups import DesignAttributeData
    from sysml_codegen.core.output_registry import OutputRegistry


def occurrence_scope(instance_path: str) -> str:
    """Transform an occurrence's ``instance_path`` into a registry-dotted scope.

    ``instance_path`` renders ``Root__feat[i]__feat2[j]``; the registry's
    ``ScopedKey`` namespace is a design-prefix-stripped, dotted path (Item 4/5
    boundary, probe-confirmed against ``b1-probe-evidence.md``). Strips the
    leading design-root segment and joins the rest with ``.`` — the ``[i]``
    occurrence brackets stay attached to their segment (not their own dotted
    component), so this key is byte-distinct from the de-indexed scope
    ``scoped_lookup`` actually holds for a fixed-multiplicity ``[N]`` calc
    sibling, and a miss here correctly falls through to the de-indexed key.
    """
    segments = instance_path.split("__")
    return ".".join(segments[1:])


def _deindexed_scope(scope: str) -> str:
    """Strip every ``[i]`` occurrence bracket from a dotted scope (B1)."""
    result = []
    skip = False
    for ch in scope:
        if ch == "[":
            skip = True
            continue
        if ch == "]":
            skip = False
            continue
        if not skip:
            result.append(ch)
    return "".join(result)


def _reference_dotted(reference: FeatureReferenceFact) -> str | None:
    """The reference's own path, joined by ``.`` — chain segments, else the
    single source name. ``None`` when neither is available."""
    if reference.chain_segments:
        return ".".join(reference.chain_segments)
    return reference.source_name


def resolve_actual(
    *,
    reference: FeatureReferenceFact,
    occ_scope: str,
    formal_name: str,
    usage_qualified_name: str,
    registry: OutputRegistry,
    design_attr_by_qn: dict[str, DesignAttributeData],
) -> ConcreteConstraintInput:
    """Resolve one constraint actual through the ordered strict ladder (D1 amended).

    ``scoped_lookup`` (occurrence-scoped key first, then the shared de-indexed
    key — B1) → ``alias_lookup`` (same two keys) → design-attribute match on
    the reference's target QN → the shared terminal-disposition switch
    (:func:`~sysml_codegen.analysis.dependency_backtracker.terminal_disposition`,
    always called ``strict=True`` — constraint actuals never take the lenient
    calc-path fallback, INV-2. The switch itself supports both dispositions;
    this caller only ever exercises the strict one).
    """
    dotted = _reference_dotted(reference)
    deindexed_scope = _deindexed_scope(occ_scope)

    if dotted:
        occ_key = ScopedKey(f"{occ_scope}.{dotted}" if occ_scope else dotted)
        deindexed_key = ScopedKey(
            f"{deindexed_scope}.{dotted}" if deindexed_scope else dotted
        )

        channel = registry.scoped_lookup(occ_key)
        if channel is not None:
            return ConcreteConstraintInput(
                formal_name=formal_name,
                resolution=ConstraintInputResolution.MODULE_OUTPUT,
                bound_channel=str(channel),
            )
        if deindexed_key != occ_key:
            channel = registry.scoped_lookup(deindexed_key)
            if channel is not None:
                return ConcreteConstraintInput(
                    formal_name=formal_name,
                    resolution=ConstraintInputResolution.MODULE_OUTPUT,
                    bound_channel=str(channel),
                )

        channel = registry.alias_lookup(occ_key)
        if channel is not None:
            return ConcreteConstraintInput(
                formal_name=formal_name,
                resolution=ConstraintInputResolution.MODULE_OUTPUT,
                bound_channel=str(channel),
            )
        if deindexed_key != occ_key:
            channel = registry.alias_lookup(deindexed_key)
            if channel is not None:
                return ConcreteConstraintInput(
                    formal_name=formal_name,
                    resolution=ConstraintInputResolution.MODULE_OUTPUT,
                    bound_channel=str(channel),
                )

    target_qn = reference.target.qualified_name if reference.target else None
    if target_qn is not None and target_qn in design_attr_by_qn:
        return ConcreteConstraintInput(
            formal_name=formal_name,
            resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
            design_attribute_qn=target_qn,
        )

    # Terminal disposition (D1): strict=True makes fallback synthesis
    # physically unreachable — this call always raises (INV-2).
    terminal_disposition(
        usage_qualified_name=usage_qualified_name,
        param_name=formal_name,
        source_path=dotted or (target_qn or "<unresolved>"),
        strict=True,
    )
    raise AssertionError("unreachable: terminal_disposition(strict=True) always raises")


def mint_constraint_id(*, instance_path: str, source_local: str, tuple_: tuple) -> str:
    """Mint a deterministic, collision-checkable ``constraint_id`` (D3/N1).

    ``{instance_path}__{source_local}__{sha256[:16] of the canonical tuple}``.
    The prefix is human-scannable; the suffix folds source-local identity,
    owner-instance identity, membership kind, and polarity into a 64-bit
    collision-visible fingerprint (a hard duplicate is a generation error,
    checked post-expansion by :func:`assert_unique_constraint_ids`).
    """
    canonical = json.dumps(list(tuple_), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    suffix = hashlib.sha256(canonical.encode()).hexdigest()[:16]
    return f"{instance_path}__{source_local}__{suffix}"


def assert_unique_constraint_ids(concrete: list[ConcreteConstraint]) -> None:
    """Raise if any two concrete constraints share a ``constraint_id`` (D3, INV-4).

    A collision under a 64-bit hash on a valid model means something upstream is
    broken (e.g. two owner instances sharing an identity) — never silently kept.
    """
    seen: dict[str, ConcreteConstraint] = {}
    for c in concrete:
        prior = seen.get(c.constraint_id)
        if prior is not None:
            raise CodeGenerationError(
                f"constraint_id collision: '{c.constraint_id}' minted for both "
                f"'{prior.owner_instance_path}' and '{c.owner_instance_path}' "
                "(generation error, never silently kept — D3/INV-4)"
            )
        seen[c.constraint_id] = c


def guard_nullable_facts(
    *, is_negated: bool | None, membership_kind: str | None, usage_qualified_name: str
) -> tuple[bool, str]:
    """INV-8: a ``None`` polarity or membership kind reaching lowering is a
    generation error naming the field and usage — never a defaulted guess.

    The executable profile is expected to guarantee an asserted, polarity-known
    usage (B3); this is the defensive check for when that upstream guarantee is
    violated.
    """
    if is_negated is None:
        raise CodeGenerationError(
            f"{usage_qualified_name}: is_negated is None (nullable-fact guard, INV-8) "
            "— the executable profile expects a polarity-known assertion"
        )
    if membership_kind is None:
        raise CodeGenerationError(
            f"{usage_qualified_name}: membership_kind is None (nullable-fact guard, "
            "INV-8) — the executable profile expects an asserted usage"
        )
    return is_negated, membership_kind


__all__ = [
    "ConcreteConstraint",
    "ConcreteConstraintInput",
    "ConstraintInputResolution",
    "assert_unique_constraint_ids",
    "guard_nullable_facts",
    "mint_constraint_id",
    "occurrence_scope",
    "resolve_actual",
]
