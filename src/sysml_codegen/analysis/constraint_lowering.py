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
from pathlib import Path
from typing import TYPE_CHECKING

from agentic_mbse.sysml.expression_ir import FeatureReferenceNode, serialize_expression

from sysml_codegen.analysis.dependency_backtracker import terminal_disposition
from sysml_codegen.analysis.part_instance_index import NonFiniteCardinalityError
from sysml_codegen.core.identifier_types import ScopedKey
from sysml_codegen.core.qualified_names import sanitize_name, sanitize_qualified_name
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from sysml_codegen.resolution.models import (
    ConcreteConstraint,
    ConcreteConstraintInput,
    ConstraintInputResolution,
)

if TYPE_CHECKING:
    from agentic_mbse.sysml.constraint_facts import ConstraintFacts, ConstraintUsageFact
    from agentic_mbse.sysml.expression_facts import FeatureReferenceFact

    from sysml_codegen.analysis.parameter_groups import DesignAttributeData
    from sysml_codegen.analysis.part_instance_index import PartInstanceIndex
    from sysml_codegen.core.output_registry import OutputRegistry
    from sysml_codegen.extraction.usage_extractor import CalcUsageData


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


def guard_polarity(*, is_negated: bool | None, usage_qualified_name: str) -> bool:
    """INV-8: a ``None`` polarity reaching lowering is a generation error naming
    the usage — never a defaulted guess.

    The executable profile is expected to guarantee a polarity-known usage
    (B3); this is the defensive check for when that upstream guarantee is
    violated.

    **Scoped to ``is_negated`` only (a design correction, recorded here — see
    plan.md Phase 3 Implementation Notes for the live evidence).** The design's
    original INV-8 guard also covered ``membership_kind``, on the assumption
    every in-profile assertion carries a literal ``"assert"`` value there (S4
    hardcoded this string rather than reading it live). Live extraction shows
    ``membership_kind`` is populated **only** for a
    ``RequirementConstraintMembership`` — the `requirement_def` / out-of-profile
    territory Item 5 already catalogs unassessed (D7) — and is structurally
    ``None`` for every ordinary top-level ``assert constraint``, including
    S4's own proven ``wi014_toy::affordable`` case. Guarding it here would
    reject 100% of in-profile input, so ``membership_kind`` passes through to
    :class:`~sysml_codegen.resolution.models.ConcreteConstraint` unguarded,
    carrying whatever the fact actually holds (usually ``None``).
    """
    if is_negated is None:
        raise CodeGenerationError(
            f"{usage_qualified_name}: is_negated is None (nullable-fact guard, INV-8) "
            "— the executable profile expects a polarity-known assertion"
        )
    return is_negated


def _design_attr_index(
    design_attrs: dict[Path, list[DesignAttributeData]],
) -> dict[str, DesignAttributeData]:
    """Flatten the per-file design-attribute lists into one QN-keyed index."""
    index: dict[str, DesignAttributeData] = {}
    for attrs in design_attrs.values():
        for attr in attrs:
            if attr.qualified_name:
                index[attr.qualified_name] = attr
    return index


def _expand_owner_instances(
    usage: ConstraintUsageFact, occ_index: PartInstanceIndex, calc_usages: list[CalcUsageData]
) -> list[tuple[str, str]]:
    """The owner-kind axis (D5): ``(owner_instance_path, occurrence_scope)`` pairs.

    ``part_def`` → one pair per :meth:`PartInstanceIndex.occurrences_of` occurrence
    (INV-3). ``calc_def`` → one pair per matching concrete calc usage (existing
    calc-usage discovery, not the part index). ``package`` → already concrete:
    exactly one pair, at top-level scope. Any other kind is the caller's
    unassessed branch — never reached here.
    """
    kind = usage.owner.owning_definition.kind
    owner_qn = usage.owner.owning_definition.qualified_name

    if kind == "part_def":
        owner_eqn = sanitize_qualified_name(owner_qn)
        try:
            occurrences = occ_index.occurrences_of(owner_eqn)
        except NonFiniteCardinalityError as error:
            raise CodeGenerationError(
                f"{usage.identity.qualified_name}: owner '{owner_eqn}' is reached only "
                f"through a non-finite multiplicity ({error}) — cannot expand to "
                "concrete instances (generation error, never a silent skip)"
            ) from error
        if not occurrences:
            raise CodeGenerationError(
                f"{usage.identity.qualified_name}: owner '{owner_eqn}' has no concrete "
                "instances — an expected instance cannot be formed (validation error)"
            )
        return [(occ.instance_path, occurrence_scope(occ.instance_path)) for occ in occurrences]

    if kind == "calc_def":
        matches = [cu for cu in calc_usages if cu.calc_def_qualified_name == owner_qn]
        if not matches:
            raise CodeGenerationError(
                f"{usage.identity.qualified_name}: owner '{owner_qn}' (calc_def) has no "
                "concrete calc usages — an expected instance cannot be formed"
            )
        return [(cu.qualified_name, occurrence_scope(cu.qualified_name)) for cu in matches]

    # kind == "package": already concrete — exactly one instance, top-level scope.
    return [(sanitize_qualified_name(usage.identity.qualified_name or owner_qn), "")]


def _source_local_identity(usage: ConstraintUsageFact) -> tuple[str, tuple]:
    """The usage's source-local identity (D3 `[HARD]`): its simple name when
    named, else its ``LocationFact`` rendering — the anonymous-assertion
    identity. Returns ``(sanitized_local_name, id_tuple_component)``."""
    if usage.identity.name:
        local = sanitize_name(usage.identity.name)
        return local, (usage.identity.qualified_name,)
    if usage.location is not None:
        loc = usage.location
        return "anon", (f"{loc.file}:{loc.line}:{loc.column}",)
    raise CodeGenerationError(
        f"{usage.identity.qualified_name or '<unknown>'}: anonymous assertion has no "
        "LocationFact — cannot form a source-local identity (D3 `[HARD]`)"
    )


def _resolve_formal(
    *,
    formal_name: str,
    value: object,
    occ_scope: str,
    usage_qualified_name: str,
    registry: OutputRegistry,
    design_attr_by_qn: dict[str, DesignAttributeData],
) -> ConcreteConstraintInput:
    """Resolve one bound actual's value to a :class:`ConcreteConstraintInput`.

    The executable profile's actuals are feature references (spec §Strict
    resolution); anything else is a generation error naming the actual and its
    kind, never silently coerced.
    """
    if not isinstance(value, FeatureReferenceNode):
        kind = type(value).__name__ if value is not None else "None"
        raise CodeGenerationError(
            f"{usage_qualified_name}.{formal_name}: actual value is not a feature "
            f"reference (got {kind}) — the executable profile expects a reference actual"
        )
    return resolve_actual(
        reference=value.reference,
        occ_scope=occ_scope,
        formal_name=formal_name,
        usage_qualified_name=usage_qualified_name,
        registry=registry,
        design_attr_by_qn=design_attr_by_qn,
    )


def _formal_default_index(facts: ConstraintFacts) -> dict[str, str | None]:
    """QN -> serialized default IR, across every ``ConstraintDefinitionFact``'s formals."""
    index: dict[str, str | None] = {}
    for definition in facts.definitions:
        for formal in definition.formals:
            if formal.qualified_name is not None:
                index[formal.qualified_name] = (
                    serialize_expression(formal.default) if formal.default is not None else None
                )
    return index


def lower_constraints(
    facts: ConstraintFacts,
    *,
    occ_index: PartInstanceIndex,
    registry: OutputRegistry,
    design_attrs: dict[Path, list[DesignAttributeData]],
    calc_usages: list[CalcUsageData],
) -> list[ConcreteConstraint]:
    """Expand every fact into concrete graph structure (P1 RESOLVE).

    Dispatches on the owner-kind axis (D5) to find each source assertion's
    concrete owner instances; for each, strictly resolves every bound actual
    (:func:`resolve_actual`) and every defaulted-omitted formal, mints a
    deterministic ``constraint_id`` (:func:`mint_constraint_id`), and selects
    the effective predicate. ``ConstraintUsageFact.predicate`` already carries
    the source-form-selected effective predicate (extraction resolves
    ``effective_predicate_source.result_expression`` at fact-construction
    time, `agentic_mbse.sysml.constraint_extraction._usage_fact`) — Item 5
    does not re-select it, only serializes it (D5-IR).

    A ``requirement_def`` / any other out-of-profile owner kind is
    defensively cataloged **unassessed** (D7): one record per usage,
    ``eligible=False``, no expansion, no formal resolution, no node.

    Catalog ordering is by ``constraint_id`` (INV-4); duplicate IDs raise via
    :func:`assert_unique_constraint_ids` before returning.
    """
    design_attr_by_qn = _design_attr_index(design_attrs)
    formal_default_by_qn = _formal_default_index(facts)
    concrete: list[ConcreteConstraint] = []

    for usage in facts.usages:
        kind = usage.owner.owning_definition.kind
        usage_qn = usage.identity.qualified_name or "<anonymous>"

        if kind not in ("part_def", "calc_def", "package"):
            local, _id_component = _source_local_identity(usage)
            concrete.append(
                ConcreteConstraint(
                    constraint_id=mint_constraint_id(
                        instance_path=sanitize_qualified_name(usage_qn),
                        source_local=local,
                        tuple_=(usage_qn, kind, usage.source.form),
                    ),
                    usage_qualified_name=usage_qn,
                    source_local_identity=local,
                    source_form=usage.source.form,
                    owner_kind=kind,
                    owner_qualified_name=usage.owner.owning_definition.qualified_name,
                    owner_instance_path=sanitize_qualified_name(usage_qn),
                    membership_kind=usage.membership_kind,
                    is_negated=usage.is_negated,
                    expected_value=(not usage.is_negated) if usage.is_negated is not None else None,
                    predicate_ir=None,
                    inputs=[],
                    evaluation_channel=None,
                    eligible=False,
                )
            )
            continue

        is_negated = guard_polarity(is_negated=usage.is_negated, usage_qualified_name=usage_qn)
        local, id_component = _source_local_identity(usage)
        predicate_ir = (
            serialize_expression(usage.predicate) if usage.predicate is not None else None
        )

        actual_by_target: dict[str, object] = {}
        for actual in usage.actuals:
            if actual.name is None:
                continue
            actual_by_target[actual.name] = actual.value

        owner_instances = _expand_owner_instances(usage, occ_index, calc_usages)
        for owner_instance_path, occ_scope in owner_instances:
            inputs: list[ConcreteConstraintInput] = []
            for formal_name, value in actual_by_target.items():
                inputs.append(
                    _resolve_formal(
                        formal_name=formal_name,
                        value=value,
                        occ_scope=occ_scope,
                        usage_qualified_name=owner_instance_path,
                        registry=registry,
                        design_attr_by_qn=design_attr_by_qn,
                    )
                )
            for formal_qn in usage.omitted_default_formals:
                inputs.append(
                    ConcreteConstraintInput(
                        formal_name=sanitize_name(formal_qn.rsplit("::", 1)[-1]),
                        resolution=ConstraintInputResolution.MODELED_DEFAULT,
                        default_ir=formal_default_by_qn.get(formal_qn),
                    )
                )

            constraint_id = mint_constraint_id(
                instance_path=owner_instance_path,
                source_local=local,
                tuple_=(*id_component, owner_instance_path, usage.membership_kind, is_negated),
            )
            concrete.append(
                ConcreteConstraint(
                    constraint_id=constraint_id,
                    usage_qualified_name=usage_qn,
                    source_local_identity=local,
                    source_form=usage.source.form,
                    owner_kind=kind,
                    owner_qualified_name=usage.owner.owning_definition.qualified_name,
                    owner_instance_path=owner_instance_path,
                    membership_kind=usage.membership_kind,
                    is_negated=is_negated,
                    expected_value=not is_negated,
                    predicate_ir=predicate_ir,
                    inputs=inputs,
                    evaluation_channel=f"{constraint_id}__evaluation",
                    eligible=True,
                )
            )

    concrete.sort(key=lambda c: c.constraint_id)
    assert_unique_constraint_ids(concrete)
    return concrete


__all__ = [
    "ConcreteConstraint",
    "ConcreteConstraintInput",
    "ConstraintInputResolution",
    "assert_unique_constraint_ids",
    "guard_polarity",
    "lower_constraints",
    "mint_constraint_id",
    "occurrence_scope",
    "resolve_actual",
]
