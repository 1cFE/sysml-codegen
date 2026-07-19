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
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from agentic_mbse.sysml.executable_profile import (
    PROFILE_SEMANTIC_VERSION,
    Eligibility,
    EligibilityDiagnostic,
    UsageDecision,
    evaluate_profile,
)
from agentic_mbse.sysml.expression_ir import (
    ExpressionIR,
    FeatureReferenceNode,
    InvocationNode,
    LiteralNode,
    OperatorNode,
    UnitAnnotationNode,
    parse_expression,
    serialize_expression,
)

from sysml_codegen.analysis.dependency_backtracker import terminal_disposition
from sysml_codegen.analysis.part_instance_index import NonFiniteCardinalityError
from sysml_codegen.analysis.source_referent import (
    map_live_source_referent,
    validate_snapshot_source_referent,
)
from sysml_codegen.core.identifier_types import ScopedAliasKey, ScopedKey
from sysml_codegen.core.qualified_names import sanitize_name, sanitize_qualified_name
from sysml_codegen.resolution.models import (
    ComputationGraph,
    ConcreteConstraint,
    ConcreteConstraintInput,
    ConstraintExclusion,
    ConstraintInputResolution,
    EntryPoint,
    EntryPointType,
    InputSource,
    ModuleInput,
    ModuleKind,
    ModuleOutput,
    ParameterGroup,
    PipelineModule,
)

if TYPE_CHECKING:
    from agentic_mbse.sysml.constraint_facts import (
        ActualFact,
        ConstraintDefinitionFact,
        ConstraintFacts,
        ConstraintUsageFact,
        FormalFact,
    )
    from agentic_mbse.sysml.expression_facts import FeatureReferenceFact

    from sysml_codegen.analysis.parameter_groups import DesignAttributeData, ParameterGroupDeriver
    from sysml_codegen.analysis.part_instance_index import OccurrenceIndex
    from sysml_codegen.core.output_registry import OutputRegistry
    from sysml_codegen.extraction.usage_extractor import CalcUsageData
    from sysml_codegen.orchestration.pipeline_context import CodeGenerationError


logger = logging.getLogger(__name__)


def _generation_error(message: str) -> CodeGenerationError:
    """Construct a ``CodeGenerationError``, imported lazily.

    ``orchestration/__init__.py`` eagerly imports ``pipeline_builder``, which
    imports this module (Item 5's pipeline wiring) — a module-level import of
    ``sysml_codegen.orchestration.pipeline_context`` here would make importing
    this module *first* (e.g. a test importing ``constraint_lowering`` before
    anything else touches ``orchestration``) circular. Matches the same late-
    import pattern already used in
    :func:`~sysml_codegen.analysis.dependency_backtracker.terminal_disposition`.
    """
    from sysml_codegen.orchestration.pipeline_context import CodeGenerationError

    return CodeGenerationError(message)


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
    owner_def_qn: str | None = None,
) -> ConcreteConstraintInput:
    """Resolve one constraint actual through the ordered strict ladder (D1 amended,
    R5-widened — see the ``scoped_alias_lookup`` rung below).

    ``scoped_lookup`` (occurrence-scoped key first, then the shared de-indexed
    key — B1) → ``alias_lookup`` (same two keys) → ``scoped_alias_lookup``
    (same two keys, structured ``(scope, leaf)`` — R5 amendment) →
    design-attribute match on the reference's target QN → a base-def literal
    default (the constraint-actual twin of ADR-001's LIBRARY_DEFAULT: a modeled
    value, not synthesis — INV-2 forbids inventing a value the model doesn't
    carry, not recognizing one via a third key shape) → the shared
    terminal-disposition switch
    (:func:`~sysml_codegen.analysis.dependency_backtracker.terminal_disposition`,
    always called ``strict=True`` — constraint actuals never take the lenient
    calc-path fallback, INV-2. The switch itself supports both dispositions;
    this caller only ever exercises the strict one).
    """
    dotted = _reference_dotted(reference)
    deindexed_scope = _deindexed_scope(occ_scope)

    if dotted:
        occ_key = ScopedKey(f"{occ_scope}.{dotted}" if occ_scope else dotted)
        deindexed_key = ScopedKey(f"{deindexed_scope}.{dotted}" if deindexed_scope else dotted)

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

        # scoped_alias_lookup (R5 amendment, evidence-driven): a structured
        # part-def EXPOSE alias (backtracker Step 1c) that plain scoped_lookup/
        # alias_lookup — both flat ScopedKey namespaces — cannot reach. Proven
        # in-profile and needed live: `fusion_tea`'s `hif_plant.eta` actual
        # (`driver.efficiency`) is profile-ADMIT (Item 3 does not block it) yet
        # unresolvable without this rung — verified against the live fixture,
        # not a hypothetical. Split at the LAST dot into (prefix, leaf), same
        # occ-key-then-deindexed order as every other rung above.
        if "." in dotted:
            prefix, leaf = dotted.rsplit(".", 1)
            deindexed_prefix = _deindexed_scope(prefix)
            for scope_candidate in (occ_scope, deindexed_scope):
                if not scope_candidate:
                    continue
                key_prefix = deindexed_prefix if scope_candidate == deindexed_scope else prefix
                channel = registry.scoped_alias_lookup(
                    ScopedAliasKey((f"{scope_candidate}.{key_prefix}", leaf))
                )
                if channel is not None:
                    return ConcreteConstraintInput(
                        formal_name=formal_name,
                        resolution=ConstraintInputResolution.MODULE_OUTPUT,
                        bound_channel=str(channel),
                    )
            channel = registry.scoped_alias_lookup(ScopedAliasKey((prefix, leaf)))
            if channel is None and deindexed_prefix != prefix:
                channel = registry.scoped_alias_lookup(ScopedAliasKey((deindexed_prefix, leaf)))
            if channel is not None:
                return ConcreteConstraintInput(
                    formal_name=formal_name,
                    resolution=ConstraintInputResolution.MODULE_OUTPUT,
                    bound_channel=str(channel),
                )

    # Design-attribute match, two forms tried in occurrence-then-definition order
    # (R5 amendment #2, evidence-driven — see below):
    #
    # (i) Occurrence-scoped materialized QN: `{owner_instance_path}__{dotted
    #     chain, "." -> "__"}`. The supplied-value materializer
    #     (`resolution/supplied_values.py`, threaded into `graph_design_attrs`
    #     the caller passes as `design_attrs`) synthesizes exactly this QN shape
    #     for a `:>>` redefinition/override reached through a chain — proven
    #     live against `fusion_tea`'s `hif_plant.eta` actual (`driver.efficiency`
    #     resolves via the synthesized `hif_plant_pkg__hif_plant__driver__
    #     efficiency`, not any registry channel or alias: `efficiency` is a
    #     `:>>` literal redefinition on the driver instance, not a calc output).
    # (ii) Definition-scoped target QN: `reference.target.qualified_name` is
    #     SysML `::`-form (e.g. "toy_plant::'Toy Plant'::plant_budget");
    #     sanitized to the EQN `__`-form every design attribute is keyed by
    #     (verified against `wi014_toy` live).
    if dotted:
        occ_attr_qn = f"{usage_qualified_name}__{'__'.join(dotted.split('.'))}"
        if occ_attr_qn in design_attr_by_qn:
            return ConcreteConstraintInput(
                formal_name=formal_name,
                resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
                design_attribute_qn=occ_attr_qn,
            )

    target_qn_sysml = reference.target.qualified_name if reference.target else None
    target_qn = sanitize_qualified_name(target_qn_sysml) if target_qn_sysml else None
    if target_qn is not None and target_qn in design_attr_by_qn:
        return ConcreteConstraintInput(
            formal_name=formal_name,
            resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
            design_attribute_qn=target_qn,
        )

    # (iii) Definition-scoped base-def literal default: `{owner_def_qn}__{dotted
    # chain}`. Covers an attribute that carries only a plain base-def default
    # (no `:>>` override, no channel) — e.g. `plant_values`' `attribute gain :
    # Real = 40.0`, read bare in the same part's own assert (`in gain = gain`).
    # The calc backtracker's Step 3 has an equivalent def-level fallback; constraint
    # actuals had none until this rung. Real, already-captured attribute — same
    # dedup-by-QN discipline as (i)/(ii) above, no new EP-key shape (F4).
    if dotted and owner_def_qn:
        def_attr_qn = f"{owner_def_qn}__{'__'.join(dotted.split('.'))}"
        if def_attr_qn in design_attr_by_qn:
            return ConcreteConstraintInput(
                formal_name=formal_name,
                resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
                design_attribute_qn=def_attr_qn,
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


def mint_constraint_id(
    *,
    instance_path: str,
    source_local: str,
    tuple_: tuple,
    digest_hex_length: int = 16,
) -> str:
    """Mint a deterministic, collision-checkable ``constraint_id`` (D3/N1).

    ``{instance_path}__{source_local}__{sha256[:16] of the canonical tuple}``.
    The prefix is human-scannable; the suffix folds source-local identity,
    owner-instance identity, membership kind, and polarity into a 64-bit
    collision-visible fingerprint (a hard duplicate is a generation error,
    checked post-expansion by :func:`assert_unique_constraint_ids`).
    """
    canonical = json.dumps(list(tuple_), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    if digest_hex_length < 1 or digest_hex_length > 64:
        raise ValueError("digest_hex_length must be between 1 and 64")
    suffix = hashlib.sha256(canonical.encode()).hexdigest()[:digest_hex_length]
    return f"{instance_path}__{source_local}__{suffix}"


def assert_unique_constraint_ids(concrete: list[ConcreteConstraint]) -> None:
    """Raise if any two concrete constraints share a ``constraint_id`` (D3, INV-4)."""

    def describe(record: ConcreteConstraint) -> str:
        location = record.exclusion.location if record.exclusion is not None else "<executable>"
        return (
            f"usage={record.usage_qualified_name!r}, "
            f"source_local={record.source_local_identity!r}, source={location!r}, "
            f"owner_definition={record.owner_qualified_name!r}, "
            f"owner_instance={record.owner_instance_path!r}"
        )

    seen: dict[str, ConcreteConstraint] = {}
    for c in concrete:
        prior = seen.get(c.constraint_id)
        if prior is not None:
            raise _generation_error(
                f"duplicate constraint_id {c.constraint_id!r}; first record: "
                f"{describe(prior)}; second record: {describe(c)}"
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
        raise _generation_error(
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
    usage: ConstraintUsageFact, occ_index: OccurrenceIndex, calc_usages: list[CalcUsageData]
) -> list[tuple[str, str]]:
    """The owner-kind axis (D5): ``(owner_instance_path, occurrence_scope)`` pairs.

    ``part_def`` → one pair per :meth:`OccurrenceIndex.occurrences_of` occurrence
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
            raise _generation_error(
                f"{usage.identity.qualified_name}: owner '{owner_eqn}' is reached only "
                f"through a non-finite multiplicity ({error}) — cannot expand to "
                "concrete instances (generation error, never a silent skip)"
            ) from error
        if not occurrences:
            raise _generation_error(
                f"{usage.identity.qualified_name}: owner '{owner_eqn}' has no concrete "
                "instances — an expected instance cannot be formed (validation error)"
            )
        return [(occ.instance_path, occurrence_scope(occ.instance_path)) for occ in occurrences]

    if kind == "calc_def":
        matches = [cu for cu in calc_usages if cu.calc_def_qualified_name == owner_qn]
        if not matches:
            raise _generation_error(
                f"{usage.identity.qualified_name}: owner '{owner_qn}' (calc_def) has no "
                "concrete calc usages — an expected instance cannot be formed"
            )
        return [(cu.qualified_name, occurrence_scope(cu.qualified_name)) for cu in matches]

    # kind == "package": already concrete — exactly one instance, top-level scope.
    return [(sanitize_qualified_name(usage.identity.qualified_name or owner_qn), "")]


def collect_bare_actual_demand(
    facts: ConstraintFacts,
    occ_index: OccurrenceIndex,
    calc_usages: list[CalcUsageData],
) -> list[tuple[str, str, str | None]]:
    """The demand set (D2) the supplied-value materializer needs beyond calc-usage
    bindings: ``(instance_scope, source_path, source_file)`` for every ADMIT
    constraint usage's feature-reference actual.

    A constraint actual referenced by nothing else (e.g. a self-named ``in gain =
    gain`` with no calc-usage binding of its own) is otherwise invisible to
    ``materialize_supplied_values``, which only scans ``calc_usages`` bindings — so
    an instance self-redefinition (D2) it alone could resolve never gets synthesized.
    This is a read-only probe, not authoritative: it reuses the same profile
    evaluation and owner-instance expansion ``lower_constraints`` performs later, and
    any usage that would fail expansion there is simply skipped here — the real,
    authoritative failure (if any) happens in ``lower_constraints`` itself.
    """
    from sysml_codegen.orchestration.pipeline_context import CodeGenerationError

    profile = evaluate_profile(facts)
    admit_qns = {
        decision.identity.qualified_name
        for decision in profile.decisions
        if decision.eligibility is Eligibility.ADMIT
    }
    demand: list[tuple[str, str, str | None]] = []
    for usage in facts.usages:
        if usage.identity.qualified_name not in admit_qns:
            continue
        try:
            owner_instances = _expand_owner_instances(usage, occ_index, calc_usages)
        except (NonFiniteCardinalityError, CodeGenerationError):
            continue
        source_file = usage.location.file if usage.location is not None else None
        for actual in usage.actuals:
            if actual.name is None or not isinstance(actual.value, FeatureReferenceNode):
                continue
            dotted = _reference_dotted(actual.value.reference)
            if not dotted:
                continue
            for owner_instance_path, _occ_scope in owner_instances:
                demand.append((owner_instance_path, dotted, source_file))
    return demand


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
    raise _generation_error(
        f"{usage.identity.qualified_name or '<unknown>'}: anonymous assertion has no "
        "LocationFact — cannot form a source-local identity (D3 `[HARD]`)"
    )


def _render_location(decision: UsageDecision) -> str:
    location = decision.location
    if location is None:
        return "<no location>"
    return f"{location.file}:{location.line}:{location.column}"


def _exclusion_for(decision: UsageDecision, owner_kind: str) -> ConstraintExclusion:
    """Project profile/owner policy into one total non-execution payload."""
    kind: Literal["non_numerical", "unassessed_form", "unsupported_owner"]
    if owner_kind not in ("part_def", "calc_def", "package"):
        kind = "unsupported_owner"
        reasons: list[str] = []
    elif decision.eligibility is Eligibility.NON_NUMERICAL:
        kind = "non_numerical"
        reasons = [diagnostic.reason for diagnostic in decision.diagnostics]
    else:
        kind = "unassessed_form"
        reasons = []
    return ConstraintExclusion(kind=kind, reasons=reasons, location=_render_location(decision))


def excluded_usage_indices(
    facts: ConstraintFacts, decisions: list[UsageDecision]
) -> tuple[int, ...]:
    """Return the ordered indices lowering sends to the excluded-record branch."""
    if len(facts.usages) != len(decisions):
        raise _generation_error(
            "constraint facts/profile decision cardinality mismatch: "
            f"{len(facts.usages)} usages versus {len(decisions)} decisions"
        )
    supported_owners = {"part_def", "calc_def", "package"}
    return tuple(
        index
        for index, (usage, decision) in enumerate(zip(facts.usages, decisions, strict=True))
        if usage.owner.owning_definition.kind not in supported_owners
        or decision.eligibility is not Eligibility.ADMIT
    )


def _canonical_anonymous_location(
    usage: ConstraintUsageFact,
    *,
    source_location_mode: Literal["live", "snapshot"] | None,
    source_roots: list[Path],
) -> tuple[str, str]:
    if usage.location is None:
        raise _generation_error(
            "<anonymous>: anonymous assertion has no LocationFact — cannot form a portable "
            "source identity"
        )
    if source_location_mode is None:
        raise _generation_error(
            "<anonymous>: anonymous excluded assertion requires an explicit source-location route"
        )
    try:
        if source_location_mode == "live":
            referent = map_live_source_referent(usage.location.file, source_roots)
        else:
            referent = validate_snapshot_source_referent(usage.location.file)
    except ValueError as error:
        raise _generation_error(str(error)) from error
    location = f"{referent}:{usage.location.line}:{usage.location.column}"
    return referent, location


def _warning_location(
    usage: ConstraintUsageFact,
    decision: UsageDecision,
    *,
    source_location_mode: Literal["live", "snapshot"] | None,
    source_roots: list[Path],
) -> str:
    """Render the route-stable warning location for one profile decision."""
    if usage.identity.name is not None:
        return _render_location(decision)
    _, location = _canonical_anonymous_location(
        usage,
        source_location_mode=source_location_mode,
        source_roots=source_roots,
    )
    return location


def _report_non_numerical_warnings(
    facts: ConstraintFacts,
    decisions: list[UsageDecision],
    *,
    source_location_mode: Literal["live", "snapshot"] | None,
    source_roots: list[Path],
) -> None:
    """Report every non-numerical decision once in source/profile order."""
    for usage, decision in zip(facts.usages, decisions, strict=True):
        if decision.eligibility is not Eligibility.NON_NUMERICAL:
            continue
        usage_qn = usage.identity.qualified_name or "<anonymous>"
        diagnostics = "; ".join(
            f"{diagnostic.reason}: {diagnostic.message}" for diagnostic in decision.diagnostics
        )
        logger.warning(
            "Constraint %s at %s is not numerical and will not execute: %s",
            usage_qn,
            _warning_location(
                usage,
                decision,
                source_location_mode=source_location_mode,
                source_roots=source_roots,
            ),
            diagnostics,
        )


def _resolve_formal(
    *,
    formal_name: str,
    value: object,
    occ_scope: str,
    usage_qualified_name: str,
    registry: OutputRegistry,
    design_attr_by_qn: dict[str, DesignAttributeData],
    owner_def_qn: str | None = None,
) -> ConcreteConstraintInput:
    """Resolve one bound actual's value to a :class:`ConcreteConstraintInput`.

    The executable profile's actuals are feature references (spec §Strict
    resolution); anything else is a generation error naming the actual and its
    kind, never silently coerced.
    """
    if not isinstance(value, FeatureReferenceNode):
        kind = type(value).__name__ if value is not None else "None"
        raise _generation_error(
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
        owner_def_qn=owner_def_qn,
    )


def _inline_reference_leaves(predicate: ExpressionIR) -> list[FeatureReferenceNode]:
    """Return unique inline feature leaves in predicate order.

    Inline constraints have no definition formals or usage actuals. Their feature leaves are the
    input contract, so lowering must resolve them before graph construction. Profile preflight has
    already blocked chains and invocations; walking both here keeps this boundary total for any
    future admitted shape without silently losing nested leaves.
    """
    leaves: list[FeatureReferenceNode] = []
    seen_names: set[str] = set()

    def visit(node: ExpressionIR) -> None:
        if isinstance(node, FeatureReferenceNode):
            name = node.reference.source_name
            if name is None:
                raise _generation_error("inline predicate contains a nameless feature reference")
            if name not in seen_names:
                seen_names.add(name)
                leaves.append(node)
            return
        if isinstance(node, OperatorNode):
            for operand in node.operands:
                visit(operand)
        elif isinstance(node, UnitAnnotationNode):
            visit(node.value)
        elif isinstance(node, InvocationNode):
            for argument in node.arguments:
                visit(argument)

    visit(predicate)
    return leaves


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


def _referenced_definition(
    facts: ConstraintFacts, usage: ConstraintUsageFact
) -> ConstraintDefinitionFact:
    source_definition = usage.source.constraint_definition
    definition_qn = source_definition.qualified_name if source_definition is not None else None
    if definition_qn is None:
        raise _generation_error(
            f"{usage.identity.qualified_name}: definition-typed constraint has no referenced "
            "constraint definition"
        )
    matches = [
        definition
        for definition in facts.definitions
        if definition.identity.qualified_name == definition_qn
    ]
    if len(matches) != 1:
        raise _generation_error(
            f"{usage.identity.qualified_name}: referenced constraint definition "
            f"{definition_qn!r} resolved to {len(matches)} fact records; expected exactly one"
        )
    return matches[0]


def _formal_name(formal: FormalFact) -> str:
    if formal.name is not None:
        return sanitize_name(formal.name)
    if formal.qualified_name is not None:
        return sanitize_name(formal.qualified_name.rsplit("::", 1)[-1])
    raise _generation_error("constraint definition contains a formal with no identity")


def _definition_formal_index(
    definition: ConstraintDefinitionFact,
) -> dict[str, FormalFact]:
    formal_by_qn: dict[str, FormalFact] = {}
    for formal in definition.formals:
        formal_qn = formal.qualified_name
        if formal_qn is None:
            raise _generation_error(
                f"{definition.identity.qualified_name}: formal {_formal_name(formal)!r} has no "
                "qualified identity"
            )
        if formal_qn in formal_by_qn:
            raise _generation_error(
                f"{definition.identity.qualified_name}: duplicate formal identity {formal_qn!r}"
            )
        formal_by_qn[formal_qn] = formal
    return formal_by_qn


def _actuals_by_formal_target(
    usage: ConstraintUsageFact,
    definition: ConstraintDefinitionFact,
    formal_by_qn: dict[str, FormalFact],
) -> dict[str, ActualFact]:
    actual_by_target: dict[str, ActualFact] = {}
    usage_qn = usage.identity.qualified_name or "<anonymous>"
    for actual in usage.actuals:
        label = actual.name or "<unnamed>"
        if len(actual.formal_targets) != 1:
            raise _generation_error(
                f"{usage_qn}: actual {label!r} must name exactly one formal target; "
                f"got {len(actual.formal_targets)}"
            )
        target_qn = actual.formal_targets[0]
        if target_qn not in formal_by_qn:
            raise _generation_error(
                f"{usage_qn}: actual {label!r} targets {target_qn!r}, which is not a formal of "
                f"{definition.identity.qualified_name!r}"
            )
        if target_qn in actual_by_target:
            raise _generation_error(
                f"{usage_qn}: multiple actuals target formal "
                f"{_formal_name(formal_by_qn[target_qn])!r}"
            )
        actual_by_target[target_qn] = actual
    return actual_by_target


def _omitted_default_targets(
    usage: ConstraintUsageFact,
    definition: ConstraintDefinitionFact,
    formal_by_qn: dict[str, FormalFact],
) -> set[str]:
    usage_qn = usage.identity.qualified_name or "<anonymous>"
    omitted = usage.omitted_default_formals
    if len(set(omitted)) != len(omitted):
        raise _generation_error(f"{usage_qn}: omitted_default_formals contains duplicates")
    omitted_set = set(omitted)
    foreign_omissions = omitted_set - formal_by_qn.keys()
    if foreign_omissions:
        raise _generation_error(
            f"{usage_qn}: omitted default targets are not formals of "
            f"{definition.identity.qualified_name!r}: {sorted(foreign_omissions)!r}"
        )
    return omitted_set


def _decide_definition_formals(
    usage: ConstraintUsageFact,
    definition: ConstraintDefinitionFact,
    actual_by_target: dict[str, ActualFact],
    omitted_set: set[str],
) -> list[tuple[FormalFact, ActualFact | None]]:
    decisions: list[tuple[FormalFact, ActualFact | None]] = []
    usage_qn = usage.identity.qualified_name or "<anonymous>"
    for formal in definition.formals:
        formal_qn = formal.qualified_name
        if formal_qn is None:  # guarded by _definition_formal_index
            raise AssertionError("formal qualified identity was validated")
        bound_actual = actual_by_target.get(formal_qn)
        if bound_actual is not None:
            if formal_qn in omitted_set:
                raise _generation_error(
                    f"{usage_qn}: formal {_formal_name(formal)!r} has both an actual and an "
                    "omitted-default marker"
                )
            decisions.append((formal, bound_actual))
        elif formal_qn in omitted_set and formal.has_default:
            decisions.append((formal, None))
        else:
            raise _generation_error(
                f"{usage_qn}: formal {_formal_name(formal)!r} has no actual and no explicit "
                "modeled default"
            )
    return decisions


def _definition_formal_bindings(
    facts: ConstraintFacts, usage: ConstraintUsageFact
) -> list[tuple[FormalFact, ActualFact | None]] | None:
    """Resolve one definition-typed usage to exactly one decision per formal.

    ``ActualFact.formal_targets`` is the binding identity. The actual's local ``name`` is
    diagnostic-only and cannot rename a definition formal. A missing actual is legal only when
    extraction explicitly listed that formal in ``omitted_default_formals`` and the definition
    fact says it has a modeled default. ``default=None`` remains a valid modeled-default payload.
    """
    if usage.source.form != "definition_typed":
        return None

    definition = _referenced_definition(facts, usage)
    formal_by_qn = _definition_formal_index(definition)
    actual_by_target = _actuals_by_formal_target(usage, definition, formal_by_qn)
    omitted_set = _omitted_default_targets(usage, definition, formal_by_qn)
    return _decide_definition_formals(usage, definition, actual_by_target, omitted_set)


def lower_constraints(
    facts: ConstraintFacts,
    *,
    occ_index: OccurrenceIndex,
    registry: OutputRegistry,
    design_attrs: dict[Path, list[DesignAttributeData]],
    calc_usages: list[CalcUsageData],
    source_location_mode: Literal["live", "snapshot"] | None = None,
    source_roots: list[Path] | None = None,
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
    if PROFILE_SEMANTIC_VERSION != "executable-profile/v3":
        raise RuntimeError(
            f"agentic-mbse executable-profile semantics changed ({PROFILE_SEMANTIC_VERSION}); "
            "review before re-pinning"
        )
    profile = evaluate_profile(facts)
    _report_non_numerical_warnings(
        facts,
        profile.decisions,
        source_location_mode=source_location_mode,
        source_roots=source_roots or [],
    )
    blocking = [d for d in profile.decisions if d.eligibility is Eligibility.BLOCK]
    if blocking:

        def _describe(decision: UsageDecision, diag: EligibilityDiagnostic) -> str:
            name = decision.identity.qualified_name or decision.identity.name or "<anonymous>"
            where = (
                f"{decision.location.file}:{decision.location.line}"
                if decision.location
                else "<no location>"
            )
            return f"  - {name} at {where}: {diag.construct} ({diag.reason}): {diag.message}"

        lines = [_describe(d, diag) for d in blocking for diag in d.diagnostics]
        raise _generation_error(
            "Constraint generation halted — the following asserted constraints are not "
            "executable:\n" + "\n".join(lines)
        )

    design_attr_by_qn = _design_attr_index(design_attrs)
    formal_default_by_qn = _formal_default_index(facts)
    concrete: list[ConcreteConstraint] = []
    excluded_indices = set(excluded_usage_indices(facts, profile.decisions))

    for index, (usage, decision) in enumerate(zip(facts.usages, profile.decisions, strict=True)):
        kind = usage.owner.owning_definition.kind
        usage_qn = usage.identity.qualified_name or "<anonymous>"

        if index in excluded_indices:
            local, _id_component = _source_local_identity(usage)
            exclusion = _exclusion_for(decision, kind)
            if usage.identity.name is None:
                referent, canonical_location = _canonical_anonymous_location(
                    usage,
                    source_location_mode=source_location_mode,
                    source_roots=source_roots or [],
                )
                location = usage.location
                if location is None:
                    raise RuntimeError("anonymous source identity returned without a LocationFact")
                constraint_id = mint_constraint_id(
                    instance_path=sanitize_qualified_name(usage_qn),
                    source_local=local,
                    tuple_=(
                        referent,
                        location.line,
                        location.column,
                        usage_qn,
                        kind,
                        usage.source.form,
                    ),
                    digest_hex_length=32,
                )
                exclusion = ConstraintExclusion(
                    kind=exclusion.kind,
                    reasons=exclusion.reasons,
                    location=canonical_location,
                )
            else:
                constraint_id = mint_constraint_id(
                    instance_path=sanitize_qualified_name(usage_qn),
                    source_local=local,
                    tuple_=(usage_qn, kind, usage.source.form),
                )
            concrete.append(
                ConcreteConstraint(
                    constraint_id=constraint_id,
                    usage_qualified_name=usage_qn,
                    source_local_identity=local,
                    source_form=usage.source.form,
                    owner_kind=kind,
                    owner_qualified_name=usage.owner.owning_definition.qualified_name,
                    owner_instance_path=sanitize_qualified_name(usage_qn),
                    membership_kind=usage.membership_kind,
                    is_negated=usage.is_negated,
                    expected_value=None,
                    predicate_ir=None,
                    inputs=[],
                    evaluation_channel=None,
                    eligible=False,
                    exclusion=exclusion,
                )
            )
            continue

        is_negated = guard_polarity(is_negated=usage.is_negated, usage_qualified_name=usage_qn)
        local, id_component = _source_local_identity(usage)
        # Same-IR guarantee (Item 3 D7/I5), two arms: object identity for inline usages
        # (single-parse in-process path); serialization equality for definition-typed
        # usages, whose effective predicate is the definition's object — a different
        # instance than usage.predicate by construction (Item 3 audit correction).
        effective = decision.effective_predicate
        same_ir = effective is usage.predicate or (
            effective is not None
            and usage.predicate is not None
            and serialize_expression(effective) == serialize_expression(usage.predicate)
        )
        if not same_ir:
            raise _generation_error(
                f"same-IR violation (Item 3 I5/D7) for {usage_qn}: the profile walked a "
                "different predicate than the one about to be lowered"
            )
        predicate_ir = serialize_expression(effective) if effective is not None else None

        formal_bindings = _definition_formal_bindings(facts, usage)
        actual_by_name = {
            actual.name: actual.value for actual in usage.actuals if actual.name is not None
        }

        owner_def_qn = sanitize_qualified_name(usage.owner.owning_definition.qualified_name)
        owner_instances = _expand_owner_instances(usage, occ_index, calc_usages)
        for owner_instance_path, occ_scope in owner_instances:
            inputs: list[ConcreteConstraintInput] = []
            if formal_bindings is not None:
                for formal, actual in formal_bindings:
                    formal_name = _formal_name(formal)
                    if actual is None:
                        inputs.append(
                            ConcreteConstraintInput(
                                formal_name=formal_name,
                                resolution=ConstraintInputResolution.MODELED_DEFAULT,
                                default_ir=(
                                    serialize_expression(formal.default)
                                    if formal.default is not None
                                    else None
                                ),
                            )
                        )
                    else:
                        inputs.append(
                            _resolve_formal(
                                formal_name=formal_name,
                                value=actual.value,
                                occ_scope=occ_scope,
                                usage_qualified_name=owner_instance_path,
                                registry=registry,
                                design_attr_by_qn=design_attr_by_qn,
                                owner_def_qn=owner_def_qn,
                            )
                        )
            else:
                for formal_name, value in actual_by_name.items():
                    inputs.append(
                        _resolve_formal(
                            formal_name=formal_name,
                            value=value,
                            occ_scope=occ_scope,
                            usage_qualified_name=owner_instance_path,
                            registry=registry,
                            design_attr_by_qn=design_attr_by_qn,
                            owner_def_qn=owner_def_qn,
                        )
                    )
                if usage.source.form == "inline" and effective is not None:
                    existing_names = {item.formal_name for item in inputs}
                    for leaf in _inline_reference_leaves(effective):
                        source_name = leaf.reference.source_name
                        if source_name is None:  # guarded by _inline_reference_leaves
                            raise RuntimeError(
                                "inline reference collection returned a nameless leaf"
                            )
                        formal_name = sanitize_name(source_name)
                        if formal_name in existing_names:
                            continue
                        inputs.append(
                            _resolve_formal(
                                formal_name=formal_name,
                                value=leaf,
                                occ_scope=occ_scope,
                                usage_qualified_name=owner_instance_path,
                                registry=registry,
                                design_attr_by_qn=design_attr_by_qn,
                                owner_def_qn=owner_def_qn,
                            )
                        )
                        existing_names.add(formal_name)
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


# ---------------------------------------------------------------------------
# P3 EXTEND: graph structure + minted entry points (Phase 4).
# ---------------------------------------------------------------------------

AGGREGATOR_MODULE_NAME = "constraint_report_aggregator"
_CONSTRAINT_DEFAULTS_GROUP = "constraint_defaults"


def _pascal(s: str) -> str:
    return "".join(part.capitalize() for part in s.split("_") if part)


def _constraint_module_type(c: ConcreteConstraint) -> str:
    """Deterministic ``module_type`` (D9: "adopt Item 5's placeholder scheme as production").

    Item 5 sets the CONSTRAINT node's ``name`` (= ``constraint_id``) and
    ``evaluation_channel``; generated-class identity is Item 7's decision
    (design.md Implementation Notes, Appendix A).

    ``owner_instance_path`` carries ``[i]`` occurrence brackets for a part_def owner with
    multiple occurrences (e.g. ``cell[0]``) — stripped/renamed to ``_i`` before Pascal-casing
    so every occurrence still gets a *distinct* class name (``Cell0ConstraintModule``,
    ``Cell1ConstraintModule``, ...) that is also a valid Python identifier (execution-lane
    finding: a bracket character reaching an import statement is a ``SyntaxError``, not a
    generation-time failure — caught only by actually executing the generated package).
    """
    inst_local = "__".join(c.owner_instance_path.split("__")[1:]) or c.owner_instance_path
    inst_local = inst_local.replace("[", "_").replace("]", "")
    base = _pascal(f"{inst_local}_{c.source_local_identity}")
    namespace = c.owner_instance_path.split("__")[0].lower()
    return f"{namespace}.{base}ConstraintModule"


def _literal_float(serialized_ir: str | None) -> float | None:
    """A modeled default's numeric value, if the default IR is a plain literal."""
    if serialized_ir is None:
        return None
    ir = parse_expression(serialized_ir)
    if not isinstance(ir, LiteralNode):
        return None
    try:
        return float(ir.literal.value)
    except (TypeError, ValueError):
        return None


def _group_for_qn(
    qn: str, derived_groups: list, existing: list[ParameterGroup]
) -> tuple[str, str, str]:
    """The derived group ``(name, class_name, source_identifier)`` owning ``qn``.

    Mirrors S4's ``group_for`` (`s4_lib.py:490-494`): search the deriver's own
    groups first (the authoritative classification), falling back to
    ``system_design`` / ``SystemDesign`` for a QN no derived group claims (a
    synthetic per-constraint default has no design-attribute home).
    """
    for group in existing:
        if any(p.qualified_name == qn for p in group.parameters):
            return group.name, group.class_name, str(group.source_file)
    for dg in derived_groups:
        if any(ps.name == qn for ps in dg.parameters):
            return dg.name, dg.class_name, dg.source_identifier
    return "system_design", "SystemDesign", "hierarchy"


def extend_graph_with_constraints(
    graph: ComputationGraph,
    concrete: list[ConcreteConstraint],
    group_deriver: ParameterGroupDeriver,
) -> ComputationGraph:
    """P3 EXTEND: append constraint + report-aggregator nodes, mint entry points.

    One ``CONSTRAINT`` module per **eligible** concrete assertion (own
    evaluation channel, INV-3), one ``REPORT_AGGREGATOR`` module when at least
    one assertion is eligible (one required input per assertion, S4
    convention). Unassessed records (``eligible=False``, D7) contribute
    neither — no node, no minted EP, per design.

    Minted ``DESIGN_ATTRIBUTE`` entry points are QN-keyed and QN-deduped
    (INV-5, F4-safe) into their derived parameter group (reuses the same
    ``group_deriver`` instance built earlier in the pipeline — additive,
    post-Step-7, no mutation-after-read hazard, N3). Modeled-default formals
    mint a ``LIBRARY_DEFAULT`` entry point scoped to the owning constraint
    (``{constraint_id}__{formal}``) — a per-instance formal, not a shared
    design attribute, so it is never QN-deduped against another constraint's.

    Re-runs ``_validate_channel_references`` and ``collect_uncovered_params``
    on the extended graph (INV-6) — raises naming the uncovered params on
    violation.
    """
    from sysml_codegen.resolution.graph_builder import (
        _validate_channel_references,
        collect_uncovered_params,
    )

    modules = [m.model_copy(deep=True) for m in graph.modules]
    groups = [g.model_copy(deep=True) for g in graph.entry_point_groups]
    eligible = [c for c in concrete if c.eligible]
    derived_groups = group_deriver.derive_groups()
    existing_param_qns = {p.qualified_name for g in groups for p in g.parameters}

    def mint(qn: str, entry_type: EntryPointType, default_value: float | None) -> str:
        """Mint (or reuse) an entry point; returns its param_group name."""
        gname, gclass, gsource = _group_for_qn(qn, derived_groups, groups)
        if qn in existing_param_qns:
            return gname
        target = next((g for g in groups if g.name == gname), None)
        if target is None:
            target = ParameterGroup(
                name=gname, class_name=gclass, source_file=Path(gsource), parameters=[]
            )
            groups.append(target)
        target.parameters.append(
            EntryPoint(
                qualified_name=qn,
                simple_name=qn.split("__")[-1],
                entry_type=entry_type,
                default_value=default_value,
                param_group=gname,
            )
        )
        existing_param_qns.add(qn)
        return gname

    order = len(modules)
    for c in eligible:
        if c.evaluation_channel is None:  # enforced by ConcreteConstraint's validator
            raise RuntimeError(f"eligible constraint {c.constraint_id!r} has no evaluation_channel")
        inputs: list[ModuleInput] = []
        for inp in c.inputs:
            if inp.resolution == ConstraintInputResolution.MODULE_OUTPUT:
                source = InputSource(
                    source_type="module_output", producer_channel=inp.bound_channel
                )
            elif inp.resolution == ConstraintInputResolution.DESIGN_ATTRIBUTE:
                qn = inp.design_attribute_qn
                if qn is None:  # enforced by ConcreteConstraintInput's validator
                    raise RuntimeError(
                        f"DESIGN_ATTRIBUTE input {inp.formal_name!r} on "
                        f"{c.constraint_id!r} has no design_attribute_qn"
                    )
                gname = mint(
                    qn,
                    EntryPointType.DESIGN_ATTRIBUTE,
                    group_deriver.design_attribute_default_value(qn),
                )
                source = InputSource(
                    source_type="entry_point", param_group=gname, qualified_name=qn
                )
            else:  # MODELED_DEFAULT
                qn = f"{c.constraint_id}__{inp.formal_name}"
                gname = mint(qn, EntryPointType.LIBRARY_DEFAULT, _literal_float(inp.default_ir))
                source = InputSource(
                    source_type="entry_point", param_group=gname, qualified_name=qn
                )
            inputs.append(
                ModuleInput(param_name=inp.formal_name, python_type="float", source=source)
            )

        modules.append(
            PipelineModule(
                name=c.constraint_id.lower(),
                module_type=_constraint_module_type(c),
                inputs=inputs,
                outputs=[
                    ModuleOutput(
                        field_name="evaluation",
                        python_type="ConstraintEvaluation",
                        channel_name=c.evaluation_channel,
                    )
                ],
                execution_order=order,
                module_kind=ModuleKind.CONSTRAINT,
                calc_def_name=None,
                calc_def_qualified_name=None,
            )
        )
        order += 1

    # D11: the aggregator emits whenever this function runs at all (the constraint
    # pathway is active — see the `if concrete_constraints:` call-site guard in
    # `pipeline_builder.py`), even with zero eligible constraints — a model that asserts
    # nothing still produces the `not_assessed` report surface. `agg_inputs` stays sourced
    # from `eligible` (empty list here is fine — zero-required-field aggregator input).
    # `param_name` is sanitized (not the raw `constraint_id`): it becomes both a YAML
    # wiring key and the aggregator's exact-schema Pydantic field name (Item 7 D5), which
    # must be a valid Python identifier — `constraint_id` embeds `owner_instance_path`,
    # which carries `[i]` occurrence brackets for a multi-occurrence part_def owner
    # (execution-lane finding: an aggregator field like `cell[0]__nonneg__<sha>` is a
    # `SyntaxError` in the generated class body). `evaluation_channel` (the wiring target)
    # and `ConstraintEvaluation.constraint_id` (the runtime evidence string) are untouched —
    # only this Python-identifier site changes.
    agg_inputs = [
        ModuleInput(
            param_name=sanitize_name(c.constraint_id),
            python_type="ConstraintEvaluation",
            source=InputSource(source_type="module_output", producer_channel=c.evaluation_channel),
        )
        for c in eligible
    ]
    modules.append(
        PipelineModule(
            name=AGGREGATOR_MODULE_NAME,
            module_type="constraints.ConstraintReportAggregatorModule",
            inputs=agg_inputs,
            outputs=[
                ModuleOutput(
                    field_name="constraint_report",
                    python_type="ConstraintReport",
                    channel_name="constraint_report",
                )
            ],
            execution_order=order,
            module_kind=ModuleKind.REPORT_AGGREGATOR,
            calc_def_name=None,
            calc_def_qualified_name=None,
        )
    )

    for g in groups:
        g.parameters.sort(key=lambda p: p.qualified_name)
    groups.sort(key=lambda g: g.name)

    extended = ComputationGraph(
        modules=modules,
        entry_point_groups=groups,
        execution_order=[m.name for m in modules],
        fallback_entry_points=set(graph.fallback_entry_points),
        output_aliases=graph.output_aliases,
    )
    _validate_channel_references(extended.modules)
    uncovered = collect_uncovered_params(extended)
    if uncovered:
        raise _generation_error(f"V11 coverage violations in extended graph: {uncovered}")
    return extended


__all__ = [
    "AGGREGATOR_MODULE_NAME",
    "ConcreteConstraint",
    "ConcreteConstraintInput",
    "ConstraintInputResolution",
    "assert_unique_constraint_ids",
    "extend_graph_with_constraints",
    "guard_polarity",
    "lower_constraints",
    "mint_constraint_id",
    "occurrence_scope",
    "resolve_actual",
]
