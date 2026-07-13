"""Supplied-value materializer (REQ-SVM-01..04).

The subsystem attribute a plant calc reads already has a value in the model — a
subtype-def literal, a bare `part :>>` override block, a dotted usage override, or an
in-part inherited-attr redefinition. The design-attribute resolution path
(`DependencyBacktracker._resolve_to_design_attribute`, Step 3) is a working
value-carrier, but it fails for these because the source attribute is *valueless on its
base def* — its value lives in a redefinition/override no resolution step reads.

This pre-pass reads the two capture buckets (`redefinitions` ∪ `design_overrides`),
resolves the plain-value precedence (usage override > specialized-def `:>>` > base def),
and emits one synthetic `DesignAttributeData` per supplied source attribute, keyed by
its **source QN** and carrying the resolved literal as a string. Merged into
`design_attributes` before the backtracker runs, the existing Step-3 path then carries
the value to every consumer and collapses renamed-consumer fan-out for free (two
consumers of one source resolve to one QN → one entry point).

This is not aggregation LVP (doc 18, per-term) nor VBR-03 (per-consumer): it keys by
source QN and collapses across consumers. See doc 25 §"Supplied-Value Materializer".
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from sysml_codegen.analysis.parameter_groups import DesignAttributeData
from sysml_codegen.core.qualified_names import sanitize_qualified_name
from sysml_codegen.extraction.data_models import RedefinitionData, RedefinitionType
from sysml_codegen.extraction.usage_extractor import CalcUsageData
from sysml_codegen.resolution.graph_builder import _find_literal_redefinition

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _BindingTarget:
    """The source attribute a binding references, resolved to what Step 3 will match.

    ``qn`` is the qualified name ``_resolve_to_design_attribute`` returns (dotted/bare
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


def _match_override(
    instance_scope: str,
    part_usage: str,
    attr: str,
    design_overrides: list[RedefinitionData],
) -> tuple[float | None, bool]:
    """Precedence tier 1 — a usage-level `:>>` override on this instance.

    Returns (literal_value, saw_non_literal). A non-literal override (CHAIN/EXPRESSION)
    is the highest-precedence supplied value, so it does NOT fall through to a lower
    tier — it is reported as a loud skip (INV-3: never silently pick the wrong tier).
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
                return float(ov.literal_value), False
            except (ValueError, TypeError):
                saw_non_literal = True
        else:
            saw_non_literal = True
    return None, saw_non_literal


def _resolve_value(
    target: _BindingTarget,
    instance_scope: str,
    owning_part_def_qn: str | None,
    redefinitions: list[RedefinitionData],
    design_overrides: list[RedefinitionData],
    usage_type_map: dict[tuple[str, str], str],
) -> tuple[float | None, bool]:
    """Resolve the supplied literal by precedence. Returns (value, saw_non_literal).

    Tier 1: usage override (`design_overrides`).
    Tier 2a: specialized-def `:>>` via `usage_type_map` (reuse `_find_literal_redefinition`
             Strategy 1 only — gated on the type key existing, so the brittle Strategy-2
             name-fallback is never reached).
    Tier 2b: in-part inherited-attr redefine (shape d) — a LITERAL redef owned directly
             by the consuming calc's own part def (`redef.owning_part_qn ==
             calc.owning_part_def_qn`). A direct owner match, NOT the name-fallback (F4):
             `plant_value_shapes` has an empty `usage_type_map`, so (d) must not route
             through tier 2a.
    """
    value, saw_non_literal = _match_override(
        instance_scope, target.part_usage, target.attr, design_overrides
    )
    if value is not None:
        return value, False
    if saw_non_literal:
        return None, True

    # Tier 2a: gate on the type key so `_find_literal_redefinition` matches the
    # retyped PartDef by exact QN (Strategy 1) and never falls to Strategy 2.
    if (instance_scope, target.part_usage) in usage_type_map:
        value = _find_literal_redefinition(
            target.part_usage,
            target.attr,
            redefinitions,
            usage_type_map=usage_type_map,
            owning_part_qn=instance_scope,
        )
        if value is not None:
            return value, False

    # Tier 2b (shape d): direct-owner LITERAL redef on the consuming calc's part def.
    if owning_part_def_qn:
        for redef in redefinitions:
            if (
                redef.redefinition_type == RedefinitionType.LITERAL
                and redef.attribute_name == target.attr
                and redef.owning_part_qn == owning_part_def_qn
                and redef.literal_value is not None
            ):
                try:
                    return float(redef.literal_value), False
                except (ValueError, TypeError):
                    return None, False

    return None, False


def materialize_supplied_values(
    calc_usages: list[CalcUsageData],
    redefinitions: list[RedefinitionData] | None,
    design_overrides: list[RedefinitionData] | None,
    usage_type_map: dict[tuple[str, str], str] | None,
    real_design_attrs: dict[Path, list[DesignAttributeData]],
    constraint_actual_demand: list[tuple[str, str, str | None]] | None = None,
) -> list[DesignAttributeData]:
    """Synthesize design attributes for supplied subsystem-attr values (REQ-SVM-01..04).

    Demand-scoped (INV-4): synthesizes only for an attribute a calc-usage binding
    references AND that has a LITERAL supplied value. Never overwrites a real captured
    design attribute (REQ-SVM-03, real wins + WARN). Non-literal-only supplied values
    are skipped loudly with a count summary (REQ-SVM-04 / INV-7).

    ``constraint_actual_demand`` (D2) widens the demand set to a constraint actual
    that has no calc-usage binding of its own — ``(instance_scope, source_path,
    source_file)`` triples, e.g. from
    :func:`~sysml_codegen.analysis.constraint_lowering.collect_bare_actual_demand`.
    Without it, an instance self-redefinition only a constraint's actual references
    (a self-named ``in gain = gain``) is invisible to this scan.
    """
    redefinitions = redefinitions or []
    design_overrides = design_overrides or []
    usage_type_map = usage_type_map or {}

    real_qns = {
        a.qualified_name
        for attrs in real_design_attrs.values()
        for a in attrs
        if a.qualified_name
    }
    real_name_parent = {
        (a.name, a.parent_part) for attrs in real_design_attrs.values() for a in attrs
    }

    synth: dict[str, DesignAttributeData] = {}
    non_literal_skips: list[str] = []
    scanned = 0
    applied = 0

    def _demand() -> list[tuple[str, str, str | None, Path]]:
        """Unify calc-usage bindings and constraint-actual demand into one sweep:
        ``(instance_scope, source_path, owning_part_def_qn, source_file)``. An
        entry with no resolvable source file (constraint demand only — an
        anonymous assertion with no LocationFact) cannot be bucketed and is
        dropped from the sweep."""
        out: list[tuple[str, str, str | None, Path]] = []
        for usage in calc_usages:
            qn = usage.qualified_name
            if not qn or "__" not in qn:
                continue
            instance_scope = qn.rsplit("__", 1)[0]
            for binding in usage.bindings:
                if binding.source_path:
                    out.append(
                        (instance_scope, binding.source_path, usage.owning_part_def_qn,
                         usage.source_file)
                    )
        for instance_scope, source_path, source_file in constraint_actual_demand or []:
            if source_file is None:
                continue
            out.append((instance_scope, source_path, None, Path(source_file)))
        return out

    for instance_scope, source_path, owning_part_def_qn, source_file in _demand():
        target = _binding_target(source_path, instance_scope)
        if target is None:
            continue
        scanned += 1
        value, saw_non_literal = _resolve_value(
            target,
            instance_scope,
            owning_part_def_qn,
            redefinitions,
            design_overrides,
            usage_type_map,
        )
        if value is None:
            if saw_non_literal:
                non_literal_skips.append(f"{target.part_usage}.{target.attr}")
            continue
        applied += 1
        # REQ-SVM-03 collision guard: a real captured design attribute wins.
        if target.qn in real_qns or (target.name, target.parent_part) in real_name_parent:
            logger.warning(
                "supplied-value materializer: a real design attribute already covers "
                "%s (%s.%s); keeping the real value, skipping synthesis (REQ-SVM-03).",
                target.qn,
                target.parent_part,
                target.name,
            )
            continue
        synth[target.qn] = DesignAttributeData(
            name=target.name,
            sysml_type="Real",
            default_value=str(value),
            unit=None,
            # Group the supplied value with the consuming usage's file so it lands
            # in a valid, existing parameter group (the sentinel filename would
            # render an invalid Python schema class). A design-supplied value is a
            # JSON-fillable key like any design attribute (D1).
            source_file=source_file,
            source_line=0,
            parent_part=target.parent_part,
            qualified_name=target.qn,
        )

    # REQ-SVM-04 / INV-7: count summary, Item-5 sentinel style. Silent-on-clean: a run
    # with zero non-literal skips emits an INFO summary only, never a WARNING.
    if non_literal_skips:
        logger.warning(
            "supplied-value materializer scanned %d referenced bindings: %d literal "
            "applied, %d non-literal skipped (deferred: %s).",
            scanned,
            applied,
            len(non_literal_skips),
            sorted(set(non_literal_skips)),
        )
    else:
        logger.info(
            "supplied-value materializer scanned %d referenced bindings: %d literal "
            "applied, 0 non-literal skipped.",
            scanned,
            applied,
        )
    return list(synth.values())
