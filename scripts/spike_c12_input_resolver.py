#!/usr/bin/env python3
"""Spike diagnostic: C12 Input Resolver.

Answers 7 spike questions from the C12 plan:
1. Strategy ordering: A-first vs C-first — does it change any outcome?
2. Strategy B: Does any aggregation ref contain "::"?
3. Strategy D: Do any agg entry points duplicate backtracker design attrs?
4. consumer_scope equivalence: module_eqn vs instance_path derivation
5. REQ-DRA-04: Cross-path overlap (ref in both CalcUsage and aggregation)
6. Self-reference: Does any agg term resolve to its own module?
7. Strategy A hit rate: How many resolve via scoped registry vs CHAIN redef?

NOT a test — a diagnostic for informing C12 build plan.
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

# Ensure project is importable
_proj_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_proj_root / "src"))
sys.path.insert(0, str(_proj_root))

from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
from sysml_codegen.core.identifier_types import (
    CanonicalChannel,
    ScopedKey,
    SysMLQN,
)
from sysml_codegen.core.qualified_names import (
    get_channel_name,
    sanitize_name,
)
from sysml_codegen.extraction.data_models import (
    RedefinitionData,
    RedefinitionType,
    ScopedAggregationData,
)
from sysml_codegen.generation.initialization import build_output_registry
from tests.helpers.snapshot_loader import load_extraction_snapshot

# Models with aggregation expressions
MODELS = [
    "solar_battery_model",
    "issue22_model",
    "alias_agg_probe",
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


def _derive_consumer_scope_from_module_eqn(module_eqn: str) -> str:
    """Doc 04 method: split on __, drop [0] (design prefix) and [-1] (self), join with '.'."""
    parts = module_eqn.split("__")
    if len(parts) < 3:
        return ""
    return ".".join(parts[1:-1])


def _derive_consumer_scope_from_instance_path(instance_path: str) -> str:
    """Current code method: split on __, drop [0] (design prefix), join with '.'."""
    parts = instance_path.split("__")
    if len(parts) < 2:
        return ""
    return ".".join(parts[1:])


def _try_strategy_c(
    symbolic_ref: str,
    instance_path: str,
    redefinitions: list[RedefinitionData],
    registry,
) -> str | None:
    """Simulate current Strategy C (CHAIN redef follow) logic."""
    if "." not in symbolic_ref:
        return None

    part_usage, attr = symbolic_ref.rsplit(".", 1)
    visited = set()

    def _follow(ref: str) -> str | None:
        if "." not in ref:
            return None
        pu, at = ref.rsplit(".", 1)
        vk = f"{pu}.{at}"
        if vk in visited:
            return None
        visited.add(vk)

        chain_redef = None
        for redef in redefinitions:
            if (redef.redefinition_type == RedefinitionType.CHAIN
                    and redef.attribute_name == at):
                redef_part_name = redef.owning_part_qn.split("__")[-1]
                if sanitize_name(redef_part_name).lower() == pu.lower():
                    chain_redef = redef
                    break

        if chain_redef and chain_redef.source_path:
            if "." in chain_redef.source_path:
                calc_usage, output = chain_redef.source_path.rsplit(".", 1)
                channel = get_channel_name(
                    f"{instance_path}__{pu}__{calc_usage}", output,
                )
                if channel in registry.canonical_channels:
                    return channel
            return _follow(chain_redef.source_path)
        return None

    return _follow(symbolic_ref)


def _try_strategy_a(
    symbolic_ref: str,
    instance_path: str,
    registry,
) -> str | None:
    """Simulate Strategy A (scoped registry lookup)."""
    if "." not in symbolic_ref:
        return None

    part_usage, attr = symbolic_ref.rsplit(".", 1)

    # Primary: scoped lookup
    instance_parts = instance_path.split("__")
    if len(instance_parts) > 1:
        dotted_scope = ".".join(instance_parts[1:])
        scoped_key = f"{dotted_scope}.{part_usage}.{attr}"
        channel = registry.scoped_lookup(ScopedKey(scoped_key))
        if channel is None:
            channel = registry.alias_lookup(ScopedKey(scoped_key))
        if channel is not None:
            return channel

    # Unscoped fallback
    catalog_key = f"{part_usage}.{attr}"
    channel = registry.scoped_lookup(ScopedKey(catalog_key))
    if channel is None:
        channel = registry.alias_lookup(ScopedKey(catalog_key))
    if channel is not None:
        return channel

    return None


# =====================================================================
# QUESTION 1: Strategy ordering — A-first vs C-first
# =====================================================================
def question_1():
    """For each agg input, compare A-first vs C-first resolution outcome."""
    print("\n" + "=" * 70)
    print("QUESTION 1: Strategy ordering — A-first vs C-first")
    print("=" * 70)

    conflicts = []
    total = 0

    for model_name in MODELS:
        _, registry, snap = build_all(model_name)
        agg_data: list[ScopedAggregationData] = snap["aggregation_expressions"]
        redefs: list[RedefinitionData] = snap["hierarchy_data"].redefinitions

        for agg in agg_data:
            # SumTerms
            for term in agg.expression.sum_terms:
                ref = f"{term.part_usage_name}.{term.attribute_name}"
                total += 1

                a_result = _try_strategy_a(ref, agg.instance_path, registry)
                c_result = _try_strategy_c(ref, agg.instance_path, redefs, registry)

                if a_result is not None and c_result is not None and a_result != c_result:
                    conflicts.append({
                        "model": model_name,
                        "agg": agg.module_eqn,
                        "ref": ref,
                        "strategy_a": a_result,
                        "strategy_c": c_result,
                    })

            # SingletonTerms
            for s_term in agg.expression.singleton_terms:
                if "." not in s_term.source_path:
                    continue
                ref = s_term.source_path
                total += 1

                a_result = _try_strategy_a(ref, agg.instance_path, registry)
                c_result = _try_strategy_c(ref, agg.instance_path, redefs, registry)

                if a_result is not None and c_result is not None and a_result != c_result:
                    conflicts.append({
                        "model": model_name,
                        "agg": agg.module_eqn,
                        "ref": ref,
                        "strategy_a": a_result,
                        "strategy_c": c_result,
                    })

    print(f"\nTotal aggregation refs checked: {total}")
    print(f"Conflicts (A and C both hit but return different channel): {len(conflicts)}")
    if conflicts:
        for c in conflicts:
            print(f"  CONFLICT: {c['model']}/{c['agg']}: ref='{c['ref']}'")
            print(f"    Strategy A → {c['strategy_a']}")
            print(f"    Strategy C → {c['strategy_c']}")
    else:
        print("  No conflicts — A-first ordering is safe.")

    # Also show which strategy hits for each ref
    print("\n  Per-ref breakdown:")
    for model_name in MODELS:
        _, registry, snap = build_all(model_name)
        agg_data = snap["aggregation_expressions"]
        redefs = snap["hierarchy_data"].redefinitions

        for agg in agg_data:
            refs = []
            for term in agg.expression.sum_terms:
                refs.append(f"{term.part_usage_name}.{term.attribute_name}")
            for s_term in agg.expression.singleton_terms:
                if "." in s_term.source_path:
                    refs.append(s_term.source_path)

            for ref in refs:
                a = _try_strategy_a(ref, agg.instance_path, registry)
                c = _try_strategy_c(ref, agg.instance_path, redefs, registry)
                status = []
                if a is not None:
                    status.append("A:HIT")
                else:
                    status.append("A:MISS")
                if c is not None:
                    status.append("C:HIT")
                else:
                    status.append("C:MISS")
                winner = "BOTH_MISS"
                if a is not None:
                    winner = "A_WINS"
                elif c is not None:
                    winner = "C_WINS"
                print(f"    [{model_name}] {agg.module_eqn} | ref='{ref}' | {' '.join(status)} | first_hit={winner}")


# =====================================================================
# QUESTION 2: Strategy B — any aggregation ref with "::"?
# =====================================================================
def question_2():
    print("\n" + "=" * 70)
    print("QUESTION 2: Strategy B — any aggregation ref with '::'?")
    print("=" * 70)

    double_colon_refs = []
    total = 0

    for model_name in MODELS:
        _, _, snap = build_all(model_name)
        agg_data = snap["aggregation_expressions"]

        for agg in agg_data:
            for term in agg.expression.sum_terms:
                ref = f"{term.part_usage_name}.{term.attribute_name}"
                total += 1
                if "::" in ref:
                    double_colon_refs.append((model_name, agg.module_eqn, ref))
            for s_term in agg.expression.singleton_terms:
                total += 1
                if "::" in s_term.source_path:
                    double_colon_refs.append((model_name, agg.module_eqn, s_term.source_path))
            for l_term in agg.expression.local_terms:
                total += 1
                if "::" in l_term.attribute_name:
                    double_colon_refs.append((model_name, agg.module_eqn, l_term.attribute_name))

    print(f"\nTotal aggregation term refs: {total}")
    print(f"Refs containing '::': {len(double_colon_refs)}")
    if double_colon_refs:
        for model, eqn, ref in double_colon_refs:
            print(f"  {model}/{eqn}: '{ref}'")
    else:
        print("  CONFIRMED: Zero '::' refs in aggregation terms. Strategy B is zero-exercise for agg scope.")


# =====================================================================
# QUESTION 3: Strategy D — do agg entry points duplicate design attrs?
# =====================================================================
def question_3():
    print("\n" + "=" * 70)
    print("QUESTION 3: Strategy D — agg entry points vs design attributes")
    print("=" * 70)

    for model_name in MODELS:
        _, registry, snap = build_all(model_name)
        agg_data = snap["aggregation_expressions"]
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = snap.get("design_attributes", {})

        # Flatten design attrs: collect all (name, qualified_name) pairs
        all_design_attrs = {}
        for path, attrs in design_attrs.items():
            for da in attrs:
                all_design_attrs[da.name] = da
                if da.qualified_name:
                    all_design_attrs[da.qualified_name] = da

        # Find agg terms that resolve to entry points (Strategy A and C both miss)
        entry_point_refs = []
        for agg in agg_data:
            for term in agg.expression.sum_terms:
                ref = f"{term.part_usage_name}.{term.attribute_name}"
                a = _try_strategy_a(ref, agg.instance_path, registry)
                c = _try_strategy_c(ref, agg.instance_path, redefs, registry)
                if a is None and c is None:
                    entry_point_refs.append((agg, ref, term.attribute_name))
            for s_term in agg.expression.singleton_terms:
                if "." not in s_term.source_path:
                    continue
                ref = s_term.source_path
                a = _try_strategy_a(ref, agg.instance_path, registry)
                c = _try_strategy_c(ref, agg.instance_path, redefs, registry)
                if a is None and c is None:
                    leaf = ref.rsplit(".", 1)[-1]
                    entry_point_refs.append((agg, ref, leaf))

        print(f"\n  [{model_name}]")
        print(f"    Aggregation entry points (both A and C miss): {len(entry_point_refs)}")
        print(f"    Design attributes in model: {len(all_design_attrs)}")

        matches = []
        for agg, ref, leaf in entry_point_refs:
            if leaf in all_design_attrs:
                matches.append((agg.module_eqn, ref, leaf, all_design_attrs[leaf]))
        print(f"    Leaf-name matches with design attrs: {len(matches)}")
        if matches:
            for eqn, ref, leaf, da in matches:
                print(f"      {eqn}: ref='{ref}' leaf='{leaf}' → design_attr={da.qualified_name}")
        else:
            print(f"    No duplicates — Strategy D is a no-op for {model_name}.")


# =====================================================================
# QUESTION 4: consumer_scope equivalence
# =====================================================================
def question_4():
    print("\n" + "=" * 70)
    print("QUESTION 4: consumer_scope equivalence")
    print("=" * 70)

    total = 0
    mismatches = []

    for model_name in MODELS:
        _, _, snap = build_all(model_name)
        agg_data = snap["aggregation_expressions"]

        for agg in agg_data:
            total += 1
            from_eqn = _derive_consumer_scope_from_module_eqn(agg.module_eqn)
            from_path = _derive_consumer_scope_from_instance_path(agg.instance_path)

            if from_eqn != from_path:
                mismatches.append({
                    "model": model_name,
                    "module_eqn": agg.module_eqn,
                    "instance_path": agg.instance_path,
                    "from_eqn": from_eqn,
                    "from_path": from_path,
                })

    print(f"\nTotal ScopedAggregationData entries: {total}")
    print(f"consumer_scope mismatches: {len(mismatches)}")
    if mismatches:
        for m in mismatches:
            print(f"  MISMATCH: {m['model']}/{m['module_eqn']}")
            print(f"    instance_path={m['instance_path']}")
            print(f"    from_eqn='{m['from_eqn']}' vs from_path='{m['from_path']}'")
    else:
        print("  CONFIRMED: Both derivations produce identical consumer_scope for all entries.")
        for model_name in MODELS:
            _, _, snap = build_all(model_name)
            for agg in snap["aggregation_expressions"]:
                scope = _derive_consumer_scope_from_module_eqn(agg.module_eqn)
                print(f"    [{model_name}] {agg.module_eqn} → consumer_scope='{scope}'")


# =====================================================================
# QUESTION 5: REQ-DRA-04 cross-path overlap
# =====================================================================
def question_5():
    print("\n" + "=" * 70)
    print("QUESTION 5: REQ-DRA-04 cross-path overlap")
    print("=" * 70)

    for model_name in MODELS:
        result, registry, snap = build_all(model_name)
        agg_data = snap["aggregation_expressions"]

        # Collect all backtracker binding resolution refs: (scope, ref) → channel
        backtracker_refs: dict[tuple[str, str], str] = {}
        for key, res in result.binding_resolutions.items():
            # key format: "usage_qn|param_name"
            if "|" in key:
                usage_qn = key.split("|")[0]
                # Derive scope from usage_qn
                parts = usage_qn.split("__")
                if len(parts) >= 3:
                    scope = ".".join(parts[1:-1])
                else:
                    scope = ""
                # The source_path is the ref
                if res.source_path:
                    backtracker_refs[(scope, res.source_path)] = res.qualified_name

        # Collect all aggregation refs: (scope, ref)
        agg_refs: set[tuple[str, str]] = set()
        for agg in agg_data:
            scope = _derive_consumer_scope_from_module_eqn(agg.module_eqn)
            for term in agg.expression.sum_terms:
                agg_refs.add((scope, f"{term.part_usage_name}.{term.attribute_name}"))
            for s_term in agg.expression.singleton_terms:
                if "." in s_term.source_path:
                    agg_refs.add((scope, s_term.source_path))

        # Find overlaps
        overlaps = agg_refs & set(backtracker_refs.keys())

        print(f"\n  [{model_name}]")
        print(f"    Backtracker (scope, ref) pairs: {len(backtracker_refs)}")
        print(f"    Aggregation (scope, ref) pairs: {len(agg_refs)}")
        print(f"    Overlaps: {len(overlaps)}")
        if overlaps:
            for scope, ref in overlaps:
                bt_channel = backtracker_refs[(scope, ref)]
                print(f"      scope='{scope}' ref='{ref}' → backtracker_channel='{bt_channel}'")
        else:
            print(f"    No natural overlap in {model_name}.")

    # Also check the doc 24 concrete trace example
    print("\n  Doc 24 concrete trace verification:")
    print("    ref='cost_model.total_cost' scope='plant.battery_pack'")
    result, registry, snap = build_all("solar_battery_model")
    # Strategy A for this ref
    scoped_key = "plant.battery_pack.cost_model.total_cost"
    channel = registry.scoped_lookup(ScopedKey(scoped_key))
    if channel:
        print(f"    Strategy A scoped_lookup('{scoped_key}') → HIT: {channel}")
    else:
        alias_channel = registry.alias_lookup(ScopedKey(scoped_key))
        if alias_channel:
            print(f"    Strategy A alias_lookup('{scoped_key}') → HIT: {alias_channel}")
        else:
            print(f"    Strategy A MISS for '{scoped_key}'")

    # Check if backtracker has this ref
    for key, res in result.binding_resolutions.items():
        if res.source_path and "cost_model.total_cost" in res.source_path:
            usage_qn = key.split("|")[0]
            parts = usage_qn.split("__")
            scope = ".".join(parts[1:-1]) if len(parts) >= 3 else ""
            print(f"    Backtracker: key='{key}' scope='{scope}' source='{res.source_path}' → '{res.qualified_name}'")


# =====================================================================
# QUESTION 6: Self-reference check
# =====================================================================
def question_6():
    print("\n" + "=" * 70)
    print("QUESTION 6: Self-reference in aggregation resolution")
    print("=" * 70)

    self_refs = []

    for model_name in MODELS:
        _, registry, snap = build_all(model_name)
        agg_data = snap["aggregation_expressions"]
        redefs = snap["hierarchy_data"].redefinitions

        for agg in agg_data:
            module_eqn = agg.module_eqn

            for term in agg.expression.sum_terms:
                ref = f"{term.part_usage_name}.{term.attribute_name}"
                for strategy_name, result in [
                    ("A", _try_strategy_a(ref, agg.instance_path, registry)),
                    ("C", _try_strategy_c(ref, agg.instance_path, redefs, registry)),
                ]:
                    if result is not None:
                        producing_module = result.rsplit("__", 1)[0]
                        if producing_module == module_eqn:
                            self_refs.append((model_name, module_eqn, ref, strategy_name, result))

            for s_term in agg.expression.singleton_terms:
                if "." not in s_term.source_path:
                    continue
                ref = s_term.source_path
                for strategy_name, result in [
                    ("A", _try_strategy_a(ref, agg.instance_path, registry)),
                    ("C", _try_strategy_c(ref, agg.instance_path, redefs, registry)),
                ]:
                    if result is not None:
                        producing_module = result.rsplit("__", 1)[0]
                        if producing_module == module_eqn:
                            self_refs.append((model_name, module_eqn, ref, strategy_name, result))

    print(f"\nSelf-reference hits: {len(self_refs)}")
    if self_refs:
        for model, eqn, ref, strategy, channel in self_refs:
            print(f"  [{model}] {eqn}: ref='{ref}' Strategy {strategy} → channel='{channel}' (SELF)")
    else:
        print("  No self-references found in any aggregation resolution.")


# =====================================================================
# QUESTION 7: Strategy A hit rate
# =====================================================================
def question_7():
    print("\n" + "=" * 70)
    print("QUESTION 7: Strategy A vs C hit rate")
    print("=" * 70)

    stats = Counter()

    for model_name in MODELS:
        _, registry, snap = build_all(model_name)
        agg_data = snap["aggregation_expressions"]
        redefs = snap["hierarchy_data"].redefinitions

        model_stats = Counter()

        for agg in agg_data:
            refs = []
            for term in agg.expression.sum_terms:
                refs.append(f"{term.part_usage_name}.{term.attribute_name}")
            for s_term in agg.expression.singleton_terms:
                if "." in s_term.source_path:
                    refs.append(s_term.source_path)

            for ref in refs:
                a = _try_strategy_a(ref, agg.instance_path, registry)
                c = _try_strategy_c(ref, agg.instance_path, redefs, registry)

                if a is not None and c is not None:
                    model_stats["both_hit"] += 1
                elif a is not None:
                    model_stats["a_only"] += 1
                elif c is not None:
                    model_stats["c_only"] += 1
                else:
                    model_stats["both_miss"] += 1

        print(f"\n  [{model_name}]")
        for k, v in model_stats.most_common():
            print(f"    {k}: {v}")
        stats += model_stats

    print(f"\n  TOTAL across all models:")
    for k, v in stats.most_common():
        print(f"    {k}: {v}")

    # Summary
    total = sum(stats.values())
    a_hits = stats["a_only"] + stats["both_hit"]
    c_hits = stats["c_only"] + stats["both_hit"]
    print(f"\n  Strategy A resolves {a_hits}/{total} refs ({100*a_hits/total:.0f}%)")
    print(f"  Strategy C resolves {c_hits}/{total} refs ({100*c_hits/total:.0f}%)")
    if stats["both_hit"]:
        print(f"  Both hit same ref: {stats['both_hit']}/{total} — A-first ordering is an optimization")
    if stats["both_miss"]:
        print(f"  Neither resolves: {stats['both_miss']}/{total} — these become entry points")


# =====================================================================
# MAIN
# =====================================================================
if __name__ == "__main__":
    question_1()
    question_2()
    question_3()
    question_4()
    question_5()
    question_6()
    question_7()

    print("\n" + "=" * 70)
    print("SPIKE COMPLETE")
    print("=" * 70)
