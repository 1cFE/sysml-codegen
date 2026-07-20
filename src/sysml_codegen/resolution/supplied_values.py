"""Supplied-value materializer (REQ-SVM-01..04).

The subsystem attribute a plant calc reads already has a value in the model — a
subtype-def literal, a bare `part :>>` override block, a dotted usage override, or an
in-part inherited-attr redefinition. The design-attribute resolution path
(the shared table's design-attribute tier) is a working
value-carrier, but it fails for these because the source attribute is *valueless on its
base def* — its value lives in a redefinition/override no resolution step reads.

This pre-pass reads the two capture buckets (`redefinitions` ∪ `design_overrides`),
resolves the plain-value precedence (usage override > specialized-def `:>>` > base def),
and emits one synthetic `DesignAttributeData` per supplied source attribute, keyed by
its **source QN** and carrying the resolved literal as a string. Returned as a
copy-on-write graph-only map before the backtracker runs, the existing Step-3 path then
carries the value to every consumer and collapses renamed-consumer fan-out for free (two
consumers of one source resolve to one QN → one entry point).

Demand is per normalized target, not per route (Item 1). Every calc binding and every
admitted constraint actual becomes a `DemandOrigin`; origins sharing an exact target QN
merge into one `LogicalDemand`. Its resolver evaluates each distinct lookup context once
and accepts them only when their value/non-literal outcomes agree, then picks grouping
provenance from the resolved evidence. So one target is scanned once, counted once, warns
at most once, and synthesizes at most one attribute regardless of how many routes reached
it. Live generation and same-checkout replay share this one seam.

This is not aggregation LVP (doc 18, per-term) nor VBR-03 (per-consumer): it keys by
source QN and collapses across consumers. See doc 25 §"Supplied-Value Materializer".
"""

from __future__ import annotations

import logging
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from sysml_codegen.analysis.parameter_groups import DesignAttributeData
from sysml_codegen.core.qualified_names import sanitize_qualified_name
from sysml_codegen.extraction.data_models import RedefinitionData, RedefinitionType
from sysml_codegen.extraction.usage_extractor import CalcUsageData

if TYPE_CHECKING:
    from sysml_codegen.analysis.constraint_lowering import PreparedConstraintBatch
    from sysml_codegen.orchestration.pipeline_context import CodeGenerationError

logger = logging.getLogger(__name__)


def _generation_error(message: str) -> CodeGenerationError:
    """Construct a ``CodeGenerationError``, imported lazily to avoid an import cycle."""
    from sysml_codegen.orchestration.pipeline_context import CodeGenerationError

    return CodeGenerationError(message)


@dataclass(frozen=True)
class _BindingTarget:
    """The source attribute a binding references, resolved to what Step 3 will match.

    ``qn`` is the qualified name the design-attribute tier returns (dotted/bare
    match) or matches against (reference match), so the synthetic attribute must carry
    exactly this QN to become the binding's entry point.
    """

    qn: str  # source QN -> becomes the entry-point key (INV-2)
    name: str  # leaf attribute name
    parent_part: str  # owning part-usage / def leaf (for collision + grouping)
    part_usage: str  # part-usage name for tier-1/tier-2a lookup
    attr: str  # attribute name for tier lookups


def _is_number(text: str) -> bool:
    try:
        float(text)
    except (ValueError, TypeError):
        return False
    return True


def _binding_target(source_path: str, instance_scope: str) -> _BindingTarget | None:
    """Classify a binding's source_path into the source attribute it references.

    Returns None for a shape the materializer does not own: a literal (numeric), a
    multi-hop chain (registry's job), or an unparseable bare token.
    """
    if _is_number(source_path):
        return None

    if "::" in source_path:
        # REFERENCE path, e.g. `Lib::'Flow Sub'::throughput`. Step 3's `::` branch
        # matches on the per-segment-sanitized QN, so the synthetic QN is pinned.
        qn = sanitize_qualified_name(source_path)
        segs = qn.split("__")
        if len(segs) < 2:
            return None
        attr = segs[-1]
        parent = segs[-2]
        return _BindingTarget(qn=qn, name=attr, parent_part=parent, part_usage=parent, attr=attr)

    if "." in source_path:
        parts = source_path.split(".")
        # Only a single-hop `part_usage.attr` is a supplied-value source. A deeper
        # `driver.meier_cost.gamma` is a calc-output chain the registry resolves.
        if len(parts) != 2 or not parts[0] or not parts[1]:
            return None
        part_usage, attr = parts
        qn = f"{instance_scope}__{part_usage}__{attr}"
        return _BindingTarget(
            qn=qn, name=attr, parent_part=part_usage, part_usage=part_usage, attr=attr
        )

    # Bare name: an in-part inherited attribute (shape d authored as `in x = throughput`).
    if not source_path.isidentifier():
        return None
    qn = f"{instance_scope}__{source_path}"
    return _BindingTarget(
        qn=qn, name=source_path, parent_part="", part_usage=source_path, attr=source_path
    )


@dataclass(frozen=True)
class DemandOrigin:
    """One route that referenced a target: a calc binding or a constraint actual.

    ``lookup_context`` is the ``(instance_scope, owning_part_def_qn)`` pair the value
    ladder needs. Two origins may share a target and differ here; that is valid, and
    resolution compares their outcomes rather than rejecting the difference (D5).
    """

    route: Literal["calc", "constraint"]
    target: _BindingTarget
    lookup_context: tuple[str, str | None]
    group_provenance: Path | None
    diagnostic_context: str


@dataclass(frozen=True)
class LogicalDemand:
    """One normalized target plus every origin that referenced it (I6)."""

    target: _BindingTarget
    origins: tuple[DemandOrigin, ...]


@dataclass(frozen=True)
class ValueResolution:
    """The ladder's outcome for one distinct lookup context."""

    lookup_context: tuple[str, str | None]
    value: float | None
    nonliteral: bool
    winning_record: RedefinitionData | None
    winning_source: Path | None


@dataclass(frozen=True)
class ResolvedDemand:
    """One agreed outcome for one target.

    Carries no grouping provenance: whether a target needs one is the caller's
    decision, because a target already covered by a real captured design attribute
    keeps the real value and synthesizes nothing. Call :func:`select_group_source`
    only for a target that will actually be synthesized (D7).
    """

    demand: LogicalDemand
    outcomes: tuple[ValueResolution, ...]
    value: float | None
    nonliteral: bool


_ROUTE_RANK = {"calc": 0, "constraint": 1}


def _origin_sort_key(origin: DemandOrigin) -> tuple[int, str, str, str, str]:
    """Canonical origin order. Reproducibility only — never semantic precedence."""
    return (
        _ROUTE_RANK[origin.route],
        origin.diagnostic_context,
        origin.lookup_context[0],
        origin.lookup_context[1] or "",
        str(origin.group_provenance or ""),
    )


def _match_override(
    instance_scope: str,
    part_usage: str,
    attr: str,
    design_overrides: list[RedefinitionData],
) -> tuple[float | None, bool, RedefinitionData | None]:
    """Precedence tier 1 — a usage-level `:>>` override on this instance.

    Returns (literal_value, saw_non_literal, winning_record). A non-literal override
    (CHAIN/EXPRESSION) is the highest-precedence supplied value, so it does NOT fall
    through to a lower tier — it is reported as a loud skip (INV-3: never silently pick
    the wrong tier). The winning record is retained as provenance evidence; it takes no
    part in value equality.
    """
    saw_non_literal = False
    for ov in design_overrides:
        if ov.attribute_name != attr:
            continue
        if ov.target_path:
            # Dotted override (shape c): `:>> chamber.cost_per_unit = 7.0` on the
            # instance; owner is the instance, target_path is [part_usage, attr].
            matched = (
                ov.owning_part_qn == instance_scope
                and ov.target_path[-1] == attr
                and part_usage in ov.target_path
            )
        else:
            # Bare override block (shape b): `part :>> target_factory { :>> ... }`;
            # owner QN is the sub-part instance itself.
            matched = ov.owning_part_qn == f"{instance_scope}__{part_usage}"
            if not matched and part_usage == attr:
                # Instance self-redefinition tier (D2): a bare-name binding
                # (`in gain = gain`, where part_usage collapses to attr) whose
                # `:>>` override is owned by the instance itself, not a sub-part.
                # Sits below the tier-1 branches above so it never shadows them.
                matched = ov.owning_part_qn == instance_scope
        if not matched:
            continue
        if ov.redefinition_type == RedefinitionType.LITERAL and ov.literal_value is not None:
            try:
                return float(ov.literal_value), False, ov
            except (ValueError, TypeError):
                saw_non_literal = True
        else:
            saw_non_literal = True
    return None, saw_non_literal, None


def _resolve_value(
    target: _BindingTarget,
    instance_scope: str,
    owning_part_def_qn: str | None,
    redefinitions: list[RedefinitionData],
    design_overrides: list[RedefinitionData],
    usage_type_map: dict[tuple[str, str], str],
) -> tuple[float | None, bool, RedefinitionData | None]:
    """Resolve the supplied literal by precedence.

    Returns (value, saw_non_literal, winning_record).

    Tier 1: usage override (`design_overrides`).
    Tier 2a: specialized-def `:>>` matched by exact type QN from `usage_type_map`. The
             match is local rather than delegated to the float-only general helper, so
             the winning record survives as provenance and the helper's brittle
             name-fallback (Strategy 2) stays structurally unreachable from here.
    Tier 2b: in-part inherited-attr redefine (shape d) — a LITERAL redef owned directly
             by the consuming calc's own part def (`redef.owning_part_qn ==
             calc.owning_part_def_qn`). A direct owner match, NOT the name-fallback (F4):
             `plant_value_shapes` has an empty `usage_type_map`, so (d) must not route
             through tier 2a.
    """
    value, saw_non_literal, record = _match_override(
        instance_scope, target.part_usage, target.attr, design_overrides
    )
    if value is not None:
        return value, False, record
    if saw_non_literal:
        return None, True, None

    type_qn = usage_type_map.get((instance_scope, target.part_usage))
    for owner_qn in (type_qn, owning_part_def_qn):
        if not owner_qn:
            continue
        for redef in redefinitions:
            if (
                redef.redefinition_type == RedefinitionType.LITERAL
                and redef.attribute_name == target.attr
                and redef.owning_part_qn == owner_qn
                and redef.literal_value is not None
            ):
                try:
                    return float(redef.literal_value), False, redef
                except (ValueError, TypeError):
                    # A malformed literal is not an answer, so it must not consume the
                    # tiers below it: keep looking. Merging tiers 2a and 2b into one
                    # loop previously let a bad literal on the type def suppress a good
                    # one on the consuming part def, losing a resolvable value silently.
                    continue

    return None, False, None


def _usable_source(path: Path | None) -> bool:
    """Whether a path can name an existing parameter group.

    ``None`` and the ``unknown`` sentinel are absences, not groups: routing a numeric
    value into one of them invents a group (D7/I8).

    Deliberately reads no process state. An earlier form also excluded ``Path.cwd()``,
    which made an otherwise pure helper classify identical inputs differently depending
    on the directory the generator ran from.
    """
    return path is not None and path != Path("unknown") and path.name != ""


def _unique_source(demand: LogicalDemand, tier: str, candidates: set[Path | None]) -> Path:
    """The single usable source at the selected provenance tier, or a loud failure."""
    usable = sorted({str(path) for path in candidates if _usable_source(path)})
    if len(usable) == 1:
        return Path(usable[0])
    raise _generation_error(
        f"supplied-value demand {demand.target.qn}: {tier} provenance is "
        f"{'ambiguous' if usable else 'missing'} ({usable}) — a numeric supplied value "
        "must group into exactly one existing source file"
    )


def _owner_source(
    record: RedefinitionData | None, exact_real_sources: Mapping[str, Path]
) -> Path | None:
    """The real captured source file of the winning record's owner, when unambiguous.

    ``RedefinitionData`` carries no path of its own, so the only real source available
    is the file a captured design attribute of that owner was extracted from.
    """
    if record is None or not record.owning_part_qn:
        return None
    prefix = f"{record.owning_part_qn}__"
    sources = {path for qn, path in exact_real_sources.items() if qn.startswith(prefix)}
    return sources.pop() if len(sources) == 1 else None


def select_group_source(
    resolved: ResolvedDemand, *, exact_real_sources: Mapping[str, Path]
) -> Path:
    """Select grouping provenance for a target that will be synthesized (D7).

    Calc-route source wins whenever any calc origin exists (B3). Otherwise: the exact
    captured design-attribute source for this target, then the real source behind the
    winning record, then the portable constraint-usage source. Ambiguity or absence at
    the selected tier fails rather than inventing a sentinel.

    Call this only once the caller has decided the target really is being synthesized.
    A target whose value is discarded — no numeric result, or a real captured attribute
    already covers it — has no grouping decision to make, so validating provenance for
    it would raise over a value nobody uses.
    """
    demand = resolved.demand
    outcomes = resolved.outcomes
    calc_sources = {origin.group_provenance for origin in demand.origins if origin.route == "calc"}
    if calc_sources:
        return _unique_source(demand, "calc-origin", calc_sources)
    exact = exact_real_sources.get(demand.target.qn)
    if _usable_source(exact):
        return Path(str(exact))
    record_sources = {outcome.winning_source for outcome in outcomes}
    if any(_usable_source(path) for path in record_sources):
        return _unique_source(demand, "winning-record", record_sources)
    return _unique_source(
        demand,
        "constraint-usage",
        {origin.group_provenance for origin in demand.origins if origin.route == "constraint"},
    )


def resolve_logical_demand(
    demand: LogicalDemand,
    *,
    redefinitions: list[RedefinitionData],
    design_overrides: list[RedefinitionData],
    usage_type_map: dict[tuple[str, str], str],
    exact_real_sources: Mapping[str, Path],
) -> ResolvedDemand:
    """Resolve one target through every distinct lookup context (D6).

    Each distinct context is evaluated exactly once. The contexts may differ freely;
    what may not differ is their semantic outcome — the same number, or the same
    unresolved/non-literal disposition. Disagreement names the target and every ordered
    origin context rather than letting order decide.
    """
    contexts: dict[tuple[str, str | None], None] = {}
    for origin in demand.origins:
        contexts.setdefault(origin.lookup_context, None)

    outcomes: list[ValueResolution] = []
    for instance_scope, owning_part_def_qn in contexts:
        value, nonliteral, record = _resolve_value(
            demand.target,
            instance_scope,
            owning_part_def_qn,
            redefinitions,
            design_overrides,
            usage_type_map,
        )
        outcomes.append(
            ValueResolution(
                lookup_context=(instance_scope, owning_part_def_qn),
                value=value,
                nonliteral=nonliteral,
                winning_record=record,
                winning_source=_owner_source(record, exact_real_sources),
            )
        )

    semantic = {(outcome.value, outcome.nonliteral) for outcome in outcomes}
    if len(semantic) > 1:
        by_context = {outcome.lookup_context: outcome for outcome in outcomes}

        def rendered_outcome(origin: DemandOrigin) -> str:
            outcome = by_context[origin.lookup_context]
            return "non-literal" if outcome.nonliteral else str(outcome.value)

        rendered = ", ".join(
            f"{origin.diagnostic_context} -> {rendered_outcome(origin)}"
            for origin in demand.origins
        )
        raise _generation_error(
            f"supplied-value demand {demand.target.qn}: distinct lookup contexts disagree "
            f"({rendered}) — one normalized target must resolve to one semantic outcome"
        )
    value, nonliteral = next(iter(semantic))
    return ResolvedDemand(
        demand=demand, outcomes=tuple(outcomes), value=value, nonliteral=nonliteral
    )


def _calc_origins(calc_usages: list[CalcUsageData]) -> Iterator[DemandOrigin]:
    """Every calc-usage binding that normalizes to a supplied-value target."""
    for usage in calc_usages:
        qn = usage.qualified_name
        if not qn or "__" not in qn:
            continue
        instance_scope = qn.rsplit("__", 1)[0]
        for binding in usage.bindings:
            if not binding.source_path:
                continue
            target = _binding_target(binding.source_path, instance_scope)
            if target is None:
                continue
            yield DemandOrigin(
                route="calc",
                target=target,
                lookup_context=(instance_scope, usage.owning_part_def_qn),
                group_provenance=Path(usage.source_file) if usage.source_file else None,
                diagnostic_context=f"calc {qn}.{binding.source_path}",
            )


def _constraint_origins(prepared: PreparedConstraintBatch | None) -> Iterator[DemandOrigin]:
    """Every admitted constraint actual that normalizes to a supplied-value target.

    A constraint actual referenced by nothing else (a self-named ``in gain = gain``)
    is invisible to the calc-binding sweep, so it must enter demand here or the
    instance self-redefinition it alone could resolve is never synthesized.
    """
    from sysml_codegen.analysis.constraint_lowering import reference_dotted

    if prepared is None:
        return
    for item in prepared.items:
        if item.projected_exclusion is not None:
            continue
        usage_qn = item.usage.identity.qualified_name or "<anonymous>"
        source = item.usage.location.file if item.usage.location is not None else None
        for actual in item.usage.actuals:
            dotted = reference_dotted(actual)
            if dotted is None:
                continue
            for owner_instance_path, _occ_scope in item.owner_instances:
                target = _binding_target(dotted, owner_instance_path)
                if target is None:
                    continue
                yield DemandOrigin(
                    route="constraint",
                    target=target,
                    lookup_context=(owner_instance_path, None),
                    group_provenance=Path(source) if source else None,
                    diagnostic_context=f"constraint {usage_qn}.{actual.name}",
                )


def _logical_demands(
    calc_usages: list[CalcUsageData], prepared: PreparedConstraintBatch | None
) -> list[LogicalDemand]:
    """Group every origin by exact normalized target QN, in ascending target order."""
    grouped: dict[str, list[DemandOrigin]] = {}
    for origin in chain(_calc_origins(calc_usages), _constraint_origins(prepared)):
        grouped.setdefault(origin.target.qn, []).append(origin)
    return [
        LogicalDemand(
            target=grouped[qn][0].target,
            origins=tuple(sorted(grouped[qn], key=_origin_sort_key)),
        )
        for qn in sorted(grouped)
    ]


def enrich_graph_design_attributes(
    # Keys are ``Path`` live and ``str`` from a loaded snapshot; both normalize to
    # ``Path`` below. ``Mapping`` is invariant in its key type, so a union annotation
    # would reject the live ``dict[Path, ...]`` caller outright.
    real_design_attrs: Mapping[Any, Sequence[DesignAttributeData]],
    *,
    calc_usages: list[CalcUsageData],
    prepared: PreparedConstraintBatch | None,
    redefinitions: list[RedefinitionData] | None,
    design_overrides: list[RedefinitionData] | None,
    usage_type_map: dict[tuple[str, str], str] | None,
) -> dict[Path, list[DesignAttributeData]]:
    """Return a graph-only attribute map enriched with supplied subsystem values.

    Copy-on-write (I9): the returned mapping is new, ``Path``-keyed, and holds copied
    lists, so the caller's extraction-boundary map and its lists are never mutated.

    One logical operation per normalized target (I7): each target is scanned once,
    counted once, warns at most once, and synthesizes at most one attribute. Every
    resolution is staged and only published after the whole ordered set succeeds.
    """
    exact_real_sources: dict[str, Path] = {}
    enriched: dict[Path, list[DesignAttributeData]] = {}
    real_name_parent: set[tuple[str, str]] = set()
    for key, attrs in real_design_attrs.items():
        enriched.setdefault(Path(key), []).extend(attrs)
        for attr in attrs:
            real_name_parent.add((attr.name, attr.parent_part))
            if attr.qualified_name:
                exact_real_sources[attr.qualified_name] = Path(key)

    synthesized: list[tuple[Path, DesignAttributeData]] = []
    collisions: list[_BindingTarget] = []
    non_literal_skips: list[str] = []
    demands = _logical_demands(calc_usages, prepared)
    applied = 0
    for demand in demands:
        resolved = resolve_logical_demand(
            demand,
            redefinitions=redefinitions or [],
            design_overrides=design_overrides or [],
            usage_type_map=usage_type_map or {},
            exact_real_sources=exact_real_sources,
        )
        target = demand.target
        if resolved.value is None:
            if resolved.nonliteral:
                non_literal_skips.append(f"{target.part_usage}.{target.attr}")
            continue
        applied += 1
        # REQ-SVM-03 collision guard: a real captured design attribute wins. It still
        # counts as applied — the value was resolved, the real one simply carries it.
        if target.qn in exact_real_sources or (target.name, target.parent_part) in real_name_parent:
            collisions.append(target)
            continue
        # Only now is a grouping decision real, so only now is provenance validated.
        group_source = select_group_source(resolved, exact_real_sources=exact_real_sources)
        synthesized.append(
            (
                group_source,
                DesignAttributeData(
                    name=target.name,
                    sysml_type="Real",
                    default_value=str(resolved.value),
                    unit=None,
                    source_file=group_source,
                    source_line=0,
                    parent_part=target.parent_part,
                    qualified_name=target.qn,
                ),
            )
        )

    for target in collisions:
        logger.warning(
            "supplied-value materializer: a real design attribute already covers "
            "%s (%s.%s); keeping the real value, skipping synthesis (REQ-SVM-03).",
            target.qn,
            target.parent_part,
            target.name,
        )
    # NOTE (audit F6): "referenced bindings" now under-counts by design — the value is
    # `len(demands)`, the number of normalized targets, and collapsing many bindings into
    # one target is the whole point of this seam. The noun is wrong and should read
    # "demand targets", but these exact bytes are pinned in the Phase 0 acceptance
    # overlay, whose SHA-256 is the RED/GREEN anchor. Correct both together once the
    # anchor is retired.
    if non_literal_skips:
        logger.warning(
            "supplied-value materializer scanned %d referenced bindings: %d literal "
            "applied, %d non-literal skipped (deferred: %s).",
            len(demands),
            applied,
            len(non_literal_skips),
            sorted(set(non_literal_skips)),
        )
    else:
        logger.info(
            "supplied-value materializer scanned %d referenced bindings: %d literal "
            "applied, 0 non-literal skipped.",
            len(demands),
            applied,
        )
    for source, attr in synthesized:
        enriched.setdefault(source, []).append(attr)
    return enriched
