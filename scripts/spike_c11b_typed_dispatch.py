#!/usr/bin/env python3
"""Spike diagnostic: C11b Typed Dispatch Migration Feasibility.

Answers 6 spike questions from the C11b plan:
1. catf_mfe Key_A alias collision safety (12 cross-scope CHAIN bindings)
2. Phase 2 CHAIN alias: scoped_lookup(canonical_name) feasibility
3. Phase 3 EXPOSE_PURE alias: canonical_name format + resolution options
4. Phase 4 transitive alias: post-Phase-2/3 resolvability
5. solar_battery REFERENCE secondary: full-path normalization
6. D1 option evaluation (a/b/c) for Phase 2/3/4 migration

NOT a test — a diagnostic for informing C11b build plan.
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

# Ensure project is importable
_proj_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_proj_root / "src"))
sys.path.insert(0, str(_proj_root))

from agentic_mbse.sysml.types import BindingType

from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
from sysml_codegen.core.identifier_types import (
    CanonicalChannel,
    ScopedKey,
    SysMLQN,
    make_canonical_channel,
    make_scoped_key,
)
from sysml_codegen.core.models import BindingResolutionType, ChannelAlias
from sysml_codegen.core.output_registry import OutputRegistry, is_transitive_default
from sysml_codegen.core.qualified_names import sanitize_name, get_channel_name, sysml_to_python_qualified_name
from sysml_codegen.extraction.data_models import ComputedAttributeClassification
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.generation.initialization import build_output_registry
from tests.helpers.snapshot_loader import load_extraction_snapshot

MODELS = [
    "solar_battery_model",
    "catf_mfe_model",
    "attr_expr_probe",
    "chain_spike_model",
]


def build_all(model_name: str):
    """Load snapshot + build registry + run backtracker."""
    snap = load_extraction_snapshot(model_name)
    registry = build_output_registry(
        calc_usages=snap["calc_usages"],
        calc_defs=snap["calc_defs"],
        aggregation_data=snap["aggregation_expressions"],
        computed_attributes=snap["computed_attributes"],
        channel_aliases=snap.get("channel_aliases", []),
        design_attributes=snap.get("design_attributes", {}),
    )
    backtracker = DependencyBacktracker(
        all_usages=snap["calc_usages"],
        calc_defs=snap["calc_defs"],
        design_attributes=snap.get("design_attributes", {}),
        output_registry=registry,
    )
    result = backtracker.find_required_modules([], include_all=True)
    return result, registry, snap


# =====================================================================
# QUESTION 1: catf_mfe Key_A alias collision safety
# =====================================================================
def question_1():
    """Check if registering instance_name.attr as alias (first-wins) gives
    correct results for all 12 catf_mfe compat-only CHAIN resolutions."""
    print("\n" + "=" * 70)
    print("QUESTION 1: catf_mfe Key_A alias collision safety")
    print("=" * 70)

    bt_result, registry, snap = build_all("catf_mfe_model")

    # Build the Key_A alias map we WOULD register: instance_name.attr -> CanonicalChannel
    # (first-wins, same collision policy as current _compat)
    calc_def_by_name = {cd.name: cd for cd in snap["calc_defs"]}
    key_a_alias_map: dict[str, CanonicalChannel] = {}
    key_a_collisions: list[tuple[str, CanonicalChannel, CanonicalChannel]] = []

    for usage in snap["calc_usages"]:
        calc_def = calc_def_by_name.get(usage.calc_def_name)
        if not calc_def:
            continue
        for attr in calc_def.output_attributes:
            key_a = f"{usage.instance_name}.{attr.name}"
            canonical = make_canonical_channel(usage.qualified_name, attr.name)
            if key_a in key_a_alias_map:
                if key_a_alias_map[key_a] != canonical:
                    key_a_collisions.append((key_a, key_a_alias_map[key_a], canonical))
            else:
                key_a_alias_map[key_a] = canonical

    print(f"\n  Total Key_A entries: {len(key_a_alias_map)}")
    print(f"  Key_A collisions: {len(key_a_collisions)}")
    if key_a_collisions:
        for key, first, second in key_a_collisions:
            print(f"    COLLISION: {key}")
            print(f"      first-wins: {first}")
            print(f"      would-lose: {second}")

    # Find the 12 compat-only resolutions and check each against alias map
    binding_type_map = {}
    for usage in snap["calc_usages"]:
        for binding in usage.bindings:
            key = f"{usage.qualified_name}|{binding.param_name}"
            binding_type_map[key] = binding.binding_type

    compat_only = []
    for key, resolution in bt_result.binding_resolutions.items():
        if resolution.resolution_type != BindingResolutionType.MODULE_OUTPUT:
            continue
        usage_qn = key.split("|")[0]
        source_path = resolution.source_path or ""
        bt = binding_type_map.get(key)

        # Check typed reachability
        has_colons = "::" in source_path
        typed_reachable = False
        if not has_colons and source_path:
            segments = usage_qn.split("__")
            if len(segments) > 2:
                consumer_scope = ".".join(segments[1:-1])
                scoped_key = ScopedKey(f"{consumer_scope}.{source_path}")
                if registry.scoped_lookup(scoped_key) == resolution.qualified_name:
                    typed_reachable = True
            alias_key = ScopedKey(source_path)
            if registry.alias_lookup(alias_key) == resolution.qualified_name:
                typed_reachable = True
        elif has_colons:
            if registry.sysml_qn_lookup(SysMLQN(source_path)) == resolution.qualified_name:
                typed_reachable = True

        if not typed_reachable:
            compat_only.append((key, resolution, source_path))

    print(f"\n  Compat-only MODULE_OUTPUT resolutions: {len(compat_only)}")

    # For each compat-only, check if key_a_alias_map would resolve correctly
    all_correct = True
    for key, resolution, source_path in compat_only:
        alias_result = key_a_alias_map.get(source_path)
        correct = alias_result == resolution.qualified_name
        status = "OK" if correct else "MISMATCH"
        if not correct:
            all_correct = False
        print(f"    {status}: {key}")
        print(f"      source_path={source_path}")
        print(f"      expected={resolution.qualified_name}")
        print(f"      alias_map={alias_result}")

    print(f"\n  CONCLUSION Q1: {'ALL CORRECT' if all_correct else 'MISMATCHES FOUND'}")
    print(f"  Key_A alias collisions: {len(key_a_collisions)}")
    if all_correct and not key_a_collisions:
        print("  Safe to register instance_name.attr as alias (first-wins)")
    return all_correct


# =====================================================================
# QUESTION 2: Phase 2 CHAIN alias scoped_lookup feasibility
# =====================================================================
def question_2():
    """Check if scoped_lookup(ScopedKey(alias.canonical_name)) works
    for ALL Phase 2 CHAIN aliases across all models."""
    print("\n" + "=" * 70)
    print("QUESTION 2: Phase 2 CHAIN alias scoped_lookup feasibility")
    print("=" * 70)

    results = {}
    for model_name in MODELS:
        snap = load_extraction_snapshot(model_name)
        registry = build_output_registry(
            calc_usages=snap["calc_usages"],
            calc_defs=snap["calc_defs"],
            aggregation_data=snap["aggregation_expressions"],
            computed_attributes=snap["computed_attributes"],
            channel_aliases=snap.get("channel_aliases", []),
            design_attributes=snap.get("design_attributes", {}),
        )

        chain_aliases = [a for a in snap.get("channel_aliases", [])
                         if a.source == "redefinition"]

        total = len(chain_aliases)
        scoped_ok = 0
        scoped_fail = []
        for alias in chain_aliases:
            resolve_result = registry.resolve(alias.canonical_name)
            scoped_result = registry.scoped_lookup(ScopedKey(alias.canonical_name))

            if resolve_result is not None:
                if scoped_result == resolve_result:
                    scoped_ok += 1
                else:
                    scoped_fail.append({
                        "alias": alias.alias_name,
                        "canonical_name": alias.canonical_name,
                        "resolve": resolve_result,
                        "scoped_lookup": scoped_result,
                    })

        results[model_name] = {"total": total, "scoped_ok": scoped_ok, "scoped_fail": scoped_fail}
        print(f"\n  {model_name}: {total} CHAIN aliases, {scoped_ok} scoped_lookup OK, {len(scoped_fail)} FAIL")
        for f in scoped_fail:
            print(f"    FAIL: canonical_name={f['canonical_name']}")
            print(f"      resolve()={f['resolve']}")
            print(f"      scoped_lookup()={f['scoped_lookup']}")

    all_ok = all(len(r["scoped_fail"]) == 0 for r in results.values())
    print(f"\n  CONCLUSION Q2: {'ALL Phase 2 CHAIN aliases resolvable via scoped_lookup' if all_ok else 'SOME FAIL'}")
    return all_ok


# =====================================================================
# QUESTION 3: Phase 3 EXPOSE_PURE canonical_name format + resolution
# =====================================================================
def question_3():
    """Analyze Phase 3 EXPOSE_PURE canonical_name values and test resolution options."""
    print("\n" + "=" * 70)
    print("QUESTION 3: Phase 3 EXPOSE_PURE canonical_name format + resolution")
    print("=" * 70)

    results = {}
    for model_name in MODELS:
        snap = load_extraction_snapshot(model_name)

        # Build instance_attr_to_channel map (proposed Option B helper)
        calc_def_by_name = {cd.name: cd for cd in snap["calc_defs"]}
        instance_attr_to_channel: dict[str, CanonicalChannel] = {}
        for usage in snap["calc_usages"]:
            calc_def = calc_def_by_name.get(usage.calc_def_name)
            if not calc_def:
                continue
            for attr in calc_def.output_attributes:
                key_a = f"{usage.instance_name}.{attr.name}"
                canonical = make_canonical_channel(usage.qualified_name, attr.name)
                if key_a not in instance_attr_to_channel:
                    instance_attr_to_channel[key_a] = canonical

        # Build registry for comparison
        registry = build_output_registry(
            calc_usages=snap["calc_usages"],
            calc_defs=snap["calc_defs"],
            aggregation_data=snap["aggregation_expressions"],
            computed_attributes=snap["computed_attributes"],
            channel_aliases=snap.get("channel_aliases", []),
            design_attributes=snap.get("design_attributes", {}),
        )

        expose_aliases = [a for a in snap.get("channel_aliases", [])
                          if a.source == "expose_pure"]

        if not expose_aliases:
            results[model_name] = {"total": 0}
            print(f"\n  {model_name}: 0 EXPOSE_PURE aliases")
            continue

        total = len(expose_aliases)
        analysis = []
        for alias in expose_aliases:
            cn = alias.canonical_name
            resolve_result = registry.resolve(cn)

            # Option A: Would ScopedKey-format canonical_name work?
            scoped_result = registry.scoped_lookup(ScopedKey(cn))

            # Option B: instance_attr_to_channel helper
            helper_result = instance_attr_to_channel.get(cn)

            # Option A+: alias_lookup (might work if Phase 2 registered it)
            alias_result = registry.alias_lookup(ScopedKey(cn))

            analysis.append({
                "canonical_name": cn,
                "owning_part_qn": alias.owning_part_qn,
                "alias_name": alias.alias_name,
                "resolve": resolve_result,
                "scoped_lookup": scoped_result,
                "alias_lookup": alias_result,
                "instance_attr_helper": helper_result,
                "option_a_works": scoped_result == resolve_result and resolve_result is not None,
                "option_b_works": helper_result == resolve_result and resolve_result is not None,
                "alias_works": alias_result == resolve_result and resolve_result is not None,
            })

        option_a_ok = sum(1 for a in analysis if a["option_a_works"])
        option_b_ok = sum(1 for a in analysis if a["option_b_works"])
        alias_ok = sum(1 for a in analysis if a["alias_works"])
        resolvable = sum(1 for a in analysis if a["resolve"] is not None)

        results[model_name] = {
            "total": total, "resolvable": resolvable,
            "option_a": option_a_ok, "option_b": option_b_ok, "alias": alias_ok,
        }

        print(f"\n  {model_name}: {total} EXPOSE_PURE aliases, {resolvable} resolvable")
        print(f"    Option A (scoped_lookup): {option_a_ok}/{resolvable}")
        print(f"    Option B (instance_attr helper): {option_b_ok}/{resolvable}")
        print(f"    alias_lookup (post-Phase-2): {alias_ok}/{resolvable}")
        for a in analysis:
            if a["resolve"] is not None:
                tag = []
                if a["option_a_works"]: tag.append("A")
                if a["option_b_works"]: tag.append("B")
                if a["alias_works"]: tag.append("alias")
                print(f"    [{','.join(tag) or 'NONE'}] cn={a['canonical_name']} -> {a['resolve']}")

    print(f"\n  CONCLUSION Q3: See per-model breakdown above")
    return results


# =====================================================================
# QUESTION 4: Phase 4 transitive alias post-Phase-2/3 resolvability
# =====================================================================
def question_4():
    """Check if Phase 4 transitive default values are resolvable via
    scoped_lookup + alias_lookup after Phase 2/3 aliases are registered."""
    print("\n" + "=" * 70)
    print("QUESTION 4: Phase 4 transitive alias resolvability")
    print("=" * 70)

    results = {}
    for model_name in MODELS:
        snap = load_extraction_snapshot(model_name)

        # Build instance_attr_to_channel (Option B helper)
        calc_def_by_name = {cd.name: cd for cd in snap["calc_defs"]}
        instance_attr_to_channel: dict[str, CanonicalChannel] = {}
        for usage in snap["calc_usages"]:
            calc_def = calc_def_by_name.get(usage.calc_def_name)
            if not calc_def:
                continue
            for attr in calc_def.output_attributes:
                key_a = f"{usage.instance_name}.{attr.name}"
                canonical = make_canonical_channel(usage.qualified_name, attr.name)
                if key_a not in instance_attr_to_channel:
                    instance_attr_to_channel[key_a] = canonical

        registry = build_output_registry(
            calc_usages=snap["calc_usages"],
            calc_defs=snap["calc_defs"],
            aggregation_data=snap["aggregation_expressions"],
            computed_attributes=snap["computed_attributes"],
            channel_aliases=snap.get("channel_aliases", []),
            design_attributes=snap.get("design_attributes", {}),
        )

        # Find Phase 4 candidates
        phase4_candidates = []
        for _path, attrs in snap.get("design_attributes", {}).items():
            for attr in attrs:
                if is_transitive_default(attr.default_value):
                    phase4_candidates.append(attr)

        if not phase4_candidates:
            results[model_name] = {"total": 0}
            print(f"\n  {model_name}: 0 transitive candidates")
            continue

        analysis = []
        for attr in phase4_candidates:
            val = str(attr.default_value)
            resolve_result = registry.resolve(val)

            scoped_result = registry.scoped_lookup(ScopedKey(val))
            alias_result = registry.alias_lookup(ScopedKey(val))
            helper_result = instance_attr_to_channel.get(val)

            # Combined: scoped OR alias
            combined = scoped_result or alias_result
            works = combined == resolve_result and resolve_result is not None

            analysis.append({
                "attr": f"{attr.parent_part}.{attr.name}",
                "default_value": val,
                "resolve": resolve_result,
                "scoped": scoped_result,
                "alias": alias_result,
                "helper": helper_result,
                "scoped_or_alias_works": works,
                "helper_works": helper_result == resolve_result and resolve_result is not None,
            })

        resolvable = sum(1 for a in analysis if a["resolve"] is not None)
        typed_ok = sum(1 for a in analysis if a["scoped_or_alias_works"])
        helper_ok = sum(1 for a in analysis if a["helper_works"])

        results[model_name] = {
            "total": len(phase4_candidates), "resolvable": resolvable,
            "scoped_or_alias": typed_ok, "helper": helper_ok,
        }

        print(f"\n  {model_name}: {len(phase4_candidates)} transitive candidates, {resolvable} resolvable")
        print(f"    scoped_or_alias: {typed_ok}/{resolvable}")
        print(f"    instance_attr_helper: {helper_ok}/{resolvable}")
        for a in analysis:
            if a["resolve"] is not None:
                tag = []
                if a["scoped_or_alias_works"]: tag.append("typed")
                if a["helper_works"]: tag.append("helper")
                print(f"    [{','.join(tag) or 'NONE'}] {a['attr']}={a['default_value']} -> {a['resolve']}")
            elif a["resolve"] is None:
                print(f"    [UNRESOLVABLE] {a['attr']}={a['default_value']}")

    print(f"\n  CONCLUSION Q4: See per-model breakdown above")
    return results


# =====================================================================
# QUESTION 5: solar_battery REFERENCE secondary full-path normalization
# =====================================================================
def question_5():
    """Verify full-path normalization for the 1 solar_battery REFERENCE secondary."""
    print("\n" + "=" * 70)
    print("QUESTION 5: solar_battery REFERENCE secondary normalization")
    print("=" * 70)

    bt_result, registry, snap = build_all("solar_battery_model")

    # Find the compat-only REFERENCE resolution
    binding_type_map = {}
    for usage in snap["calc_usages"]:
        for binding in usage.bindings:
            key = f"{usage.qualified_name}|{binding.param_name}"
            binding_type_map[key] = binding

    compat_only_refs = []
    for key, resolution in bt_result.binding_resolutions.items():
        if resolution.resolution_type != BindingResolutionType.MODULE_OUTPUT:
            continue
        binding = binding_type_map.get(key)
        if not binding or binding.binding_type != BindingType.REFERENCE:
            continue
        source_path = resolution.source_path or ""
        if "::" not in source_path:
            continue

        # Check if typed reachable
        sysml_hit = registry.sysml_qn_lookup(SysMLQN(source_path)) == resolution.qualified_name
        if not sysml_hit:
            compat_only_refs.append((key, resolution, source_path))

    print(f"\n  Compat-only REFERENCE resolutions: {len(compat_only_refs)}")

    for key, resolution, source_path in compat_only_refs:
        usage_qn = key.split("|")[0]
        print(f"\n  Case: {key}")
        print(f"    source_path={source_path}")
        print(f"    expected_channel={resolution.qualified_name}")

        # Current approach: parent_part.leaf (2 segments only)
        parts_sp = source_path.split("::")
        leaf = parts_sp[-1]
        segments = usage_qn.split("__")
        parent_part = segments[-2] if len(segments) >= 2 else None
        current_key = f"{parent_part}.{leaf}" if parent_part else leaf
        current_result = registry.resolve(current_key)
        print(f"    Current approach (parent.leaf): key={current_key} -> {current_result}")

        # Proposed: full-path normalization (drop segment[0], sanitize, join with .)
        full_parts = source_path.split("::")
        sanitized = [sanitize_name(p).lower() for p in full_parts[1:]]
        full_path_key = ".".join(sanitized)
        full_path_scoped = registry.scoped_lookup(ScopedKey(full_path_key))
        print(f"    Full-path normalization: key={full_path_key} -> {full_path_scoped}")

        # Also try with raw (not sanitized) segments
        raw_parts = [p.lower() for p in full_parts[1:]]
        raw_key = ".".join(raw_parts)
        raw_scoped = registry.scoped_lookup(ScopedKey(raw_key))
        print(f"    Raw full-path: key={raw_key} -> {raw_scoped}")

        correct = full_path_scoped == resolution.qualified_name
        print(f"    MATCH: {correct}")

        if not correct:
            # Debug: show all scoped keys containing the leaf
            matching_keys = [k for k in registry._scoped if leaf in str(k)]
            print(f"    Scoped keys containing '{leaf}': {matching_keys[:10]}")

    all_ok = all(
        registry.scoped_lookup(ScopedKey(
            ".".join(sanitize_name(p).lower() for p in sp.split("::")[1:])
        )) == res.qualified_name
        for _, res, sp in compat_only_refs
    )
    print(f"\n  CONCLUSION Q5: {'Full-path normalization CORRECT' if all_ok else 'MISMATCH'}")
    return all_ok


# =====================================================================
# QUESTION 6: D1 evaluation — Option A/B/C for Phase 2/3/4 migration
# =====================================================================
def question_6():
    """Comprehensive evaluation of all 3 options for Phase 2/3/4 resolve() migration."""
    print("\n" + "=" * 70)
    print("QUESTION 6: D1 evaluation — Phase 2/3/4 migration options")
    print("=" * 70)

    summary = {}

    for model_name in MODELS:
        print(f"\n  --- {model_name} ---")
        snap = load_extraction_snapshot(model_name)

        # Build instance_attr_to_channel (Option B)
        calc_def_by_name = {cd.name: cd for cd in snap["calc_defs"]}
        instance_attr_to_channel: dict[str, CanonicalChannel] = {}
        for usage in snap["calc_usages"]:
            calc_def = calc_def_by_name.get(usage.calc_def_name)
            if not calc_def:
                continue
            for attr in calc_def.output_attributes:
                key_a = f"{usage.instance_name}.{attr.name}"
                canonical = make_canonical_channel(usage.qualified_name, attr.name)
                if key_a not in instance_attr_to_channel:
                    instance_attr_to_channel[key_a] = canonical

        registry = build_output_registry(
            calc_usages=snap["calc_usages"],
            calc_defs=snap["calc_defs"],
            aggregation_data=snap["aggregation_expressions"],
            computed_attributes=snap["computed_attributes"],
            channel_aliases=snap.get("channel_aliases", []),
            design_attributes=snap.get("design_attributes", {}),
        )

        aliases = snap.get("channel_aliases", [])
        model_summary = {"phase2": {}, "phase3": {}, "phase4": {}}

        # --- Phase 2: CHAIN ---
        chain_aliases = [a for a in aliases if a.source == "redefinition"]
        p2_total = 0
        p2_option_a = 0  # scoped_lookup(cn) works
        p2_option_b = 0  # instance_attr_to_channel[cn] works
        p2_resolve = 0

        for alias in chain_aliases:
            cn = alias.canonical_name
            resolve_result = registry.resolve(cn)
            if resolve_result is None:
                continue
            p2_resolve += 1
            p2_total += 1

            if registry.scoped_lookup(ScopedKey(cn)) == resolve_result:
                p2_option_a += 1
            if instance_attr_to_channel.get(cn) == resolve_result:
                p2_option_b += 1

        model_summary["phase2"] = {"total": p2_total, "a": p2_option_a, "b": p2_option_b}
        print(f"    Phase 2 CHAIN: {p2_total} resolvable, A={p2_option_a} B={p2_option_b}")

        # --- Phase 3: EXPOSE_PURE ---
        expose_aliases = [a for a in aliases if a.source == "expose_pure"]
        p3_total = 0
        p3_option_a = 0
        p3_option_b = 0
        p3_resolve = 0

        for alias in expose_aliases:
            cn = alias.canonical_name
            resolve_result = registry.resolve(cn)
            if resolve_result is None:
                continue
            p3_resolve += 1
            p3_total += 1

            if registry.scoped_lookup(ScopedKey(cn)) == resolve_result:
                p3_option_a += 1
            if instance_attr_to_channel.get(cn) == resolve_result:
                p3_option_b += 1

        model_summary["phase3"] = {"total": p3_total, "a": p3_option_a, "b": p3_option_b}
        print(f"    Phase 3 EXPOSE: {p3_total} resolvable, A={p3_option_a} B={p3_option_b}")

        # --- Phase 4: Transitive ---
        p4_total = 0
        p4_scoped = 0
        p4_alias = 0
        p4_option_b = 0
        p4_resolve = 0

        for _path, attrs in snap.get("design_attributes", {}).items():
            for attr in attrs:
                if not is_transitive_default(attr.default_value):
                    continue
                val = str(attr.default_value)
                resolve_result = registry.resolve(val)
                if resolve_result is None:
                    continue
                p4_resolve += 1
                p4_total += 1

                if registry.scoped_lookup(ScopedKey(val)) == resolve_result:
                    p4_scoped += 1
                if registry.alias_lookup(ScopedKey(val)) == resolve_result:
                    p4_alias += 1
                if instance_attr_to_channel.get(val) == resolve_result:
                    p4_option_b += 1

        model_summary["phase4"] = {
            "total": p4_total, "scoped": p4_scoped, "alias": p4_alias, "b": p4_option_b,
        }
        print(f"    Phase 4 TRANS: {p4_total} resolvable, scoped={p4_scoped} alias={p4_alias} B={p4_option_b}")

        summary[model_name] = model_summary

    # Aggregate
    print(f"\n  --- AGGREGATE ---")
    agg = {"phase2": Counter(), "phase3": Counter(), "phase4": Counter()}
    for model_name, ms in summary.items():
        for phase in ["phase2", "phase3", "phase4"]:
            for k, v in ms[phase].items():
                agg[phase][k] += v

    print(f"  Phase 2 CHAIN:   total={agg['phase2']['total']}, Option A={agg['phase2']['a']}, Option B={agg['phase2']['b']}")
    print(f"  Phase 3 EXPOSE:  total={agg['phase3']['total']}, Option A={agg['phase3']['a']}, Option B={agg['phase3']['b']}")
    print(f"  Phase 4 TRANS:   total={agg['phase4']['total']}, scoped={agg['phase4']['scoped']}, alias={agg['phase4']['alias']}, Option B={agg['phase4']['b']}")

    # Recommendation
    p2_a_pass = agg["phase2"]["a"] == agg["phase2"]["total"]
    p3_b_pass = agg["phase3"]["b"] == agg["phase3"]["total"]
    p4_needs_helper = agg["phase4"]["total"] > 0 and agg["phase4"]["scoped"] + agg["phase4"]["alias"] < agg["phase4"]["total"]

    print(f"\n  RECOMMENDATION:")
    if p2_a_pass:
        print(f"    Phase 2: Option A (scoped_lookup) — ALL {agg['phase2']['total']} CHAIN aliases work")
    else:
        print(f"    Phase 2: Option B needed — {agg['phase2']['total'] - agg['phase2']['a']} scoped_lookup failures")

    if agg["phase3"]["total"] == 0:
        print(f"    Phase 3: No EXPOSE_PURE aliases to migrate")
    elif p3_b_pass:
        if agg["phase3"]["a"] == agg["phase3"]["total"]:
            print(f"    Phase 3: Option A (scoped_lookup) works for all")
        else:
            print(f"    Phase 3: Option B (instance_attr helper) — needed for {agg['phase3']['total'] - agg['phase3']['a']} aliases")
    else:
        print(f"    Phase 3: NEITHER A NOR B covers all — investigate further")

    if agg["phase4"]["total"] == 0:
        print(f"    Phase 4: No transitive aliases to migrate")
    elif not p4_needs_helper:
        print(f"    Phase 4: scoped+alias covers all {agg['phase4']['total']} — no helper needed")
    else:
        p4_gap = agg["phase4"]["total"] - agg["phase4"]["scoped"] - agg["phase4"]["alias"]
        print(f"    Phase 4: Gap of {p4_gap} — need instance_attr helper or alias registration")

    return summary


# =====================================================================
# Additional: catf_mfe compat-only cross-scope detail
# =====================================================================
def bonus_catf_detail():
    """Detailed dump of the 12 catf_mfe compat-only resolutions for verification."""
    print("\n" + "=" * 70)
    print("BONUS: catf_mfe compat-only cross-scope detail")
    print("=" * 70)

    bt_result, registry, snap = build_all("catf_mfe_model")

    # Build binding map
    binding_map = {}
    for usage in snap["calc_usages"]:
        for binding in usage.bindings:
            key = f"{usage.qualified_name}|{binding.param_name}"
            binding_map[key] = binding

    for key, resolution in bt_result.binding_resolutions.items():
        if resolution.resolution_type != BindingResolutionType.MODULE_OUTPUT:
            continue
        binding = binding_map.get(key)
        if not binding:
            continue
        source_path = resolution.source_path or ""
        if "::" in source_path:
            continue

        usage_qn = key.split("|")[0]
        segments = usage_qn.split("__")
        if len(segments) > 2:
            consumer_scope = ".".join(segments[1:-1])
            scoped_key = ScopedKey(f"{consumer_scope}.{source_path}")
            scoped_result = registry.scoped_lookup(scoped_key)
        else:
            scoped_result = None

        alias_key = ScopedKey(source_path)
        alias_result = registry.alias_lookup(alias_key)
        compat_result = registry._compat.get(source_path)

        if scoped_result is None and alias_result is None:
            # This is compat-only
            print(f"\n  COMPAT-ONLY: {key}")
            print(f"    source_path={source_path}")
            print(f"    binding_type={binding.binding_type.value}")
            print(f"    expected={resolution.qualified_name}")
            print(f"    compat_hit={compat_result}")
            print(f"    scoped_tried={consumer_scope}.{source_path} -> {scoped_result}")
            print(f"    alias_tried={source_path} -> {alias_result}")

            # What Key_A entry is being hit?
            print(f"    _compat keys containing '{source_path}': ", end="")
            matches = {k: v for k, v in registry._compat.items() if source_path in k}
            print(matches)


def main():
    q1_ok = question_1()
    q2_ok = question_2()
    q3_results = question_3()
    q4_results = question_4()
    q5_ok = question_5()
    q6_summary = question_6()
    bonus_catf_detail()

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"  Q1 (catf_mfe alias collision): {'PASS' if q1_ok else 'FAIL'}")
    print(f"  Q2 (Phase 2 scoped_lookup): {'PASS' if q2_ok else 'FAIL'}")
    print(f"  Q3 (Phase 3 EXPOSE_PURE): see detail")
    print(f"  Q4 (Phase 4 transitive): see detail")
    print(f"  Q5 (REFERENCE full-path): {'PASS' if q5_ok else 'FAIL'}")
    print(f"  Q6 (D1 option evaluation): see detail")


if __name__ == "__main__":
    main()
