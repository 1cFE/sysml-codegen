#!/usr/bin/env python3
"""Spike diagnostic: Analyze DependencyBacktracker resolution paths.

Questions answered:
1. Per fixture model: MODULE_OUTPUT vs ENTRY_POINT breakdown
2. For each MODULE_OUTPUT: is the channel reachable via typed lookups or only _compat?
3. Does catf_mfe cross-package resolution work?

NOT a test — a diagnostic for informing C11a conformance test design.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

# Ensure project is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "tests"))

from agentic_mbse.sysml.types import BindingType

from sysml_codegen.analysis.dependency_backtracker import (
    BacktrackingResult,
    DependencyBacktracker,
)
from sysml_codegen.core.identifier_types import ScopedKey, SysMLQN
from sysml_codegen.core.models import BindingResolutionType
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.core.qualified_names import sanitize_name
from sysml_codegen.generation.initialization import build_output_registry
from tests.helpers.snapshot_loader import load_extraction_snapshot


def build_backtracker_from_snapshot(
    model_name: str,
) -> tuple[BacktrackingResult, OutputRegistry, dict]:
    """Build and run backtracker from an extraction snapshot."""
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


def check_typed_reachability(
    channel: str, source_path: str, binding_type: BindingType, registry: OutputRegistry, usage_qn: str
) -> dict:
    """Check if a resolved MODULE_OUTPUT channel is reachable via typed lookups.

    Returns dict describing which registries can reach it.
    """
    result = {
        "channel": channel,
        "source_path": source_path,
        "binding_type": binding_type.value if binding_type else "UNKNOWN",
        "scoped_hit": False,
        "alias_hit": False,
        "sysml_qn_hit": False,
        "compat_only": False,
        "scoped_key_tried": None,
        "alias_key_tried": None,
        "sysml_qn_key_tried": None,
    }

    has_colons = "::" in source_path if source_path else False

    if not has_colons and source_path:
        # CHAIN path: try scoped with consumer_scope
        # Step 1: scoped_lookup with consumer scope prefix
        segments = usage_qn.split("__")
        if len(segments) > 2:
            consumer_scope = ".".join(segments[1:-1])
            scoped_key = ScopedKey(f"{consumer_scope}.{source_path}")
            result["scoped_key_tried"] = str(scoped_key)
            if registry.scoped_lookup(scoped_key) == channel:
                result["scoped_hit"] = True

        # Step 2: alias_lookup with bare source_path
        alias_key = ScopedKey(source_path)
        result["alias_key_tried"] = str(alias_key)
        if registry.alias_lookup(alias_key) == channel:
            result["alias_hit"] = True

    elif has_colons and source_path:
        # REFERENCE path
        # Step 1: sysml_qn_lookup
        sysml_key = SysMLQN(source_path)
        result["sysml_qn_key_tried"] = str(sysml_key)
        if registry.sysml_qn_lookup(sysml_key) == channel:
            result["sysml_qn_hit"] = True

        # Step 1b: normalized scoped_lookup
        parts = source_path.split("::")
        if len(parts) >= 2:
            sanitized_part = sanitize_name(parts[-2]).lower()
            dotted = f"{sanitized_part}.{parts[-1]}"
            scoped_key = ScopedKey(dotted)
            result["scoped_key_tried"] = str(scoped_key)
            if registry.scoped_lookup(scoped_key) == channel:
                result["scoped_hit"] = True

    # Check if it's compat-only
    if not result["scoped_hit"] and not result["alias_hit"] and not result["sysml_qn_hit"]:
        result["compat_only"] = True

    return result


def analyze_model(model_name: str) -> dict:
    """Run full analysis on one model."""
    print(f"\n{'=' * 70}")
    print(f"MODEL: {model_name}")
    print(f"{'=' * 70}")

    try:
        bt_result, registry, snap = build_backtracker_from_snapshot(model_name)
    except Exception as e:
        print(f"  FAILED: {e}")
        return {"error": str(e)}

    # Build binding type lookup from snapshot
    binding_type_map: dict[str, BindingType] = {}
    for usage in snap["calc_usages"]:
        for binding in usage.bindings:
            key = f"{usage.qualified_name}|{binding.param_name}"
            binding_type_map[key] = binding.binding_type

    # Analyze resolutions
    module_outputs = []
    entry_points = []
    resolution_types = Counter()
    binding_type_counts = Counter()

    for key, resolution in bt_result.binding_resolutions.items():
        resolution_types[resolution.resolution_type.value] += 1
        bt = binding_type_map.get(key)
        if bt:
            binding_type_counts[bt.value] += 1

        if resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT:
            module_outputs.append((key, resolution, bt))
        else:
            entry_points.append((key, resolution, bt))

    print(f"\n  Required usages: {len(bt_result.required_usages)}")
    print(f"  Total resolutions: {len(bt_result.binding_resolutions)}")
    print(f"  Resolution types: {dict(resolution_types)}")
    print(f"  Binding types: {dict(binding_type_counts)}")
    print(f"  Entry points: {len(bt_result.entry_points)}")
    print(f"  MODULE_OUTPUT: {len(module_outputs)}")
    print(f"  ENTRY_POINT: {len(entry_points)}")

    # Check typed reachability for MODULE_OUTPUT resolutions
    typed_reach_results = []
    compat_only_count = 0

    print(f"\n  --- MODULE_OUTPUT typed reachability ---")
    for key, resolution, bt in module_outputs:
        usage_qn = key.split("|")[0]
        reach = check_typed_reachability(
            channel=resolution.qualified_name,
            source_path=resolution.source_path or "",
            binding_type=bt or BindingType.UNBOUND,
            registry=registry,
            usage_qn=usage_qn,
        )
        typed_reach_results.append(reach)
        if reach["compat_only"]:
            compat_only_count += 1
            print(f"    COMPAT-ONLY: {key} -> {resolution.qualified_name}")
            print(f"      source_path={resolution.source_path}")
            print(f"      binding_type={bt.value if bt else 'UNKNOWN'}")
            print(f"      scoped_key_tried={reach['scoped_key_tried']}")
            print(f"      alias_key_tried={reach['alias_key_tried']}")
            print(f"      sysml_qn_key_tried={reach['sysml_qn_key_tried']}")

    scoped_hits = sum(1 for r in typed_reach_results if r["scoped_hit"])
    alias_hits = sum(1 for r in typed_reach_results if r["alias_hit"])
    sysml_qn_hits = sum(1 for r in typed_reach_results if r["sysml_qn_hit"])

    print(f"\n  Scoped hits: {scoped_hits}")
    print(f"  Alias hits: {alias_hits}")
    print(f"  SysML QN hits: {sysml_qn_hits}")
    print(f"  Compat-only: {compat_only_count}")

    # Check key format
    bad_keys = []
    for key in bt_result.binding_resolutions:
        if "|" not in key:
            bad_keys.append(key)
    if bad_keys:
        print(f"\n  BAD KEY FORMAT (no pipe): {bad_keys[:5]}")
    else:
        print(f"\n  All {len(bt_result.binding_resolutions)} keys use pipe separator format")

    # Topological order validation
    usage_positions = {
        u.qualified_name: i for i, u in enumerate(bt_result.required_usages)
    }
    topo_violations = []
    for key, resolution, _ in module_outputs:
        consumer_qn = key.split("|")[0]
        producer_channel = resolution.qualified_name
        if "__" in producer_channel:
            producer_qn = producer_channel.rsplit("__", 1)[0]
            consumer_pos = usage_positions.get(consumer_qn)
            producer_pos = usage_positions.get(producer_qn)
            if consumer_pos is not None and producer_pos is not None:
                if producer_pos >= consumer_pos:
                    topo_violations.append(
                        f"{producer_qn}[{producer_pos}] >= {consumer_qn}[{consumer_pos}]"
                    )

    if topo_violations:
        print(f"\n  TOPOLOGICAL VIOLATIONS: {len(topo_violations)}")
        for v in topo_violations[:5]:
            print(f"    {v}")
    else:
        print(f"\n  Topological order: VALID ({len(bt_result.required_usages)} usages)")

    return {
        "required_usages": len(bt_result.required_usages),
        "total_resolutions": len(bt_result.binding_resolutions),
        "module_output": len(module_outputs),
        "entry_point": len(entry_points),
        "scoped_hits": scoped_hits,
        "alias_hits": alias_hits,
        "sysml_qn_hits": sysml_qn_hits,
        "compat_only": compat_only_count,
        "topo_valid": len(topo_violations) == 0,
    }


def main():
    models = [
        "solar_battery_model",
        "catf_mfe_model",
        "attr_expr_probe",
        "chain_spike_model",
        "sample_model",
        "chain_override_probe",
    ]

    results = {}
    for model in models:
        results[model] = analyze_model(model)

    # Try expression_binding_probe (expected to crash)
    print(f"\n{'=' * 70}")
    print(f"MODEL: expression_binding_probe (expected crash)")
    print(f"{'=' * 70}")
    try:
        bt_result, registry, snap = build_backtracker_from_snapshot("expression_binding_probe")
        print("  UNEXPECTEDLY SUCCEEDED!")
        results["expression_binding_probe"] = {"error": None, "note": "Succeeded unexpectedly"}
    except Exception as e:
        print(f"  CRASHED as expected: {type(e).__name__}: {e}")
        results["expression_binding_probe"] = {"error": str(e), "error_type": type(e).__name__}

    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    total_module_output = 0
    total_compat_only = 0
    for model, r in results.items():
        if "error" not in r or r.get("error") is None:
            total_module_output += r.get("module_output", 0)
            total_compat_only += r.get("compat_only", 0)
            print(
                f"  {model:30s}: MO={r.get('module_output',0):3d}  "
                f"EP={r.get('entry_point',0):3d}  "
                f"scoped={r.get('scoped_hits',0):3d}  "
                f"alias={r.get('alias_hits',0):3d}  "
                f"sysml_qn={r.get('sysml_qn_hits',0):3d}  "
                f"compat_only={r.get('compat_only',0):3d}  "
                f"topo={'OK' if r.get('topo_valid') else 'FAIL'}"
            )
        else:
            print(f"  {model:30s}: ERROR — {r['error'][:60]}")

    print(f"\n  TOTAL MODULE_OUTPUT: {total_module_output}")
    print(f"  TOTAL COMPAT-ONLY: {total_compat_only}")
    if total_compat_only == 0:
        print("  CONCLUSION: ALL MODULE_OUTPUT resolutions reachable via typed lookups!")
        print("  C11b can be a no-behavior-change migration.")
    else:
        print(f"  WARNING: {total_compat_only} resolutions ONLY reachable via _compat!")
        print("  C11b will change resolution outcomes for these bindings.")


if __name__ == "__main__":
    main()
