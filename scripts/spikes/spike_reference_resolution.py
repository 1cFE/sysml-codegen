#!/usr/bin/env python3
"""Spike 5: REFERENCE Binding Resolution Outcomes.

Traces every binding through the backtracker and records whether it resolves
to MODULE_OUTPUT or ENTRY_POINT.  Builds a cross-tabulation of
binding_type x resolution_type to determine:

  - Do REFERENCE bindings ever resolve to MODULE_OUTPUT?
  - Is the SYSML_QN normalization in resolve() exercised, dead, or broken?

Answers design_revision_comments_v2.md Issue 11.

Usage:
    uv run python scripts/spikes/spike_reference_resolution.py
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _helpers import (
    EXTENDED_SUITES,
    load_model,
    print_section,
    print_subsection,
    print_table,
)
from sysml_codegen.core.models import BindingResolution, BindingResolutionType
from sysml_codegen.extraction.usage_extractor import (
    CalcUsageData,
    extract_calculation_usages,
)
from agentic_mbse.sysml.types import BindingType


# ---------------------------------------------------------------------------
# Source-path format classifier (reused from Spike 1)
# ---------------------------------------------------------------------------

def classify_source_path(source_path: str | None, binding_type: BindingType) -> str:
    """Classify the format of a binding's source_path.

    Returns one of: BARE, DOTTED, SYSML_QN, LITERAL, NONE, EXPRESSION.
    """
    if binding_type == BindingType.LITERAL:
        return "LITERAL"
    if binding_type == BindingType.EXPRESSION:
        return "EXPRESSION"
    if source_path is None or source_path == "":
        return "NONE"
    if "::" in source_path:
        return "SYSML_QN"
    if "." in source_path:
        return "DOTTED"
    return "BARE"


# ---------------------------------------------------------------------------
# Pipeline context builder (with fallback)
# ---------------------------------------------------------------------------

def get_backtracking_result(
    suite_name: str,
    model_paths: list[Path],
) -> tuple[dict[str, BindingResolution], list[CalcUsageData]] | None:
    """Get binding_resolutions from the full pipeline, with fallback.

    Returns (binding_resolutions, calc_usages) or None on total failure.
    """
    # Try full pipeline first
    try:
        from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

        print(f"  Attempting build_pipeline_context()...")
        ctx = build_pipeline_context(model_paths)
        print(f"  SUCCESS: got {len(ctx.backtracking_result.binding_resolutions)} binding resolutions")
        return ctx.backtracking_result.binding_resolutions, ctx.calc_usages
    except Exception as exc:
        print(f"  build_pipeline_context() FAILED: {type(exc).__name__}: {exc}")
        print(f"  Falling back to manual backtracker construction...")

    # Fallback: manual backtracker construction (skip graph builder)
    try:
        model, adapter, extractor = load_model(model_paths)
        if model is None:
            return None

        calc_defs = extractor.extract_calculation_definitions()
        calc_usages, _ = extract_calculation_usages(
            model, calc_defs=calc_defs, expand_templates=True,
        )

        from sysml_codegen.analysis.parameter_groups import extract_design_attributes
        from sysml_codegen.orchestration.pipeline_builder import (
            _extract_and_filter_computed_attributes,
            _extract_hierarchy_and_rewrite_bindings,
            _scope_aggregation_expressions,
        )

        design_attrs = extract_design_attributes(model)

        # Step 3.5: hierarchy extraction + binding rewrite
        hierarchy_data = _extract_hierarchy_and_rewrite_bindings(model, calc_usages)
        _enrich_aliases_from_bindings(hierarchy_data, calc_usages)

        # Step 4.5: computed attributes
        computed_attrs = _extract_and_filter_computed_attributes(
            model, calc_usages, design_attrs,
        )

        # Step 4.7: scoped aggregation
        agg_data = _scope_aggregation_expressions(hierarchy_data, calc_usages)

        # Build backtracker
        from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker

        bt = DependencyBacktracker(
            all_usages=calc_usages,
            calc_defs=calc_defs,
            design_attributes=design_attrs,
            computed_attributes=computed_attrs,
            aggregation_data=agg_data,
        )
        result = bt.find_required_modules(target_outputs=[], include_all=True)
        print(f"  FALLBACK SUCCESS: got {len(result.binding_resolutions)} binding resolutions")
        return result.binding_resolutions, calc_usages

    except Exception as exc:
        print(f"  FALLBACK ALSO FAILED: {type(exc).__name__}: {exc}")
        import traceback
        traceback.print_exc()
        return None


# ---------------------------------------------------------------------------
# Cross-tabulation builder
# ---------------------------------------------------------------------------

def build_cross_tab(
    binding_resolutions: dict[str, BindingResolution],
    calc_usages: list[CalcUsageData],
) -> tuple[
    dict[tuple[str, str], int],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    """Build binding_type x resolution_type cross-tabulation.

    Returns:
        (cross_tab, ref_module_output_cases, ref_entry_point_cases)
    """
    # Build CalcUsage lookup by qualified_name
    usage_map: dict[str, CalcUsageData] = {}
    for u in calc_usages:
        usage_map[u.qualified_name] = u

    cross_tab: dict[tuple[str, str], int] = Counter()
    ref_module_output_cases: list[dict[str, Any]] = []
    ref_entry_point_cases: list[dict[str, Any]] = []

    for mapping_key, resolution in binding_resolutions.items():
        # Parse mapping_key: "{usage_qn}|{param_name}"
        parts = mapping_key.rsplit("|", 1)
        if len(parts) != 2:
            print(f"  WARNING: unparseable mapping_key: {mapping_key!r}")
            continue
        usage_qn, param_name = parts

        # Find the CalcUsage
        usage = usage_map.get(usage_qn)
        if usage is None:
            # The backtracker may use qualified_name format -- try all usages
            cross_tab[("UNKNOWN", resolution.resolution_type.value)] += 1
            continue

        # Find the binding by param_name
        binding = next(
            (b for b in usage.bindings if b.param_name == param_name),
            None,
        )

        if binding is not None:
            bt_name = binding.binding_type.name
        else:
            # Might be an unbound param (no binding object)
            bt_name = "UNBOUND"

        cross_tab[(bt_name, resolution.resolution_type.value)] += 1

        # Collect REFERENCE cases for detailed analysis
        if bt_name == "REFERENCE":
            case = {
                "usage_qn": usage_qn,
                "param_name": param_name,
                "source_path": binding.source_path if binding else None,
                "resolution_type": resolution.resolution_type.value,
                "resolved_to": resolution.qualified_name,
                "is_transitive": resolution.is_transitive,
            }
            if resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT:
                ref_module_output_cases.append(case)
            else:
                ref_entry_point_cases.append(case)

    return cross_tab, ref_module_output_cases, ref_entry_point_cases


# ---------------------------------------------------------------------------
# Spike Logic
# ---------------------------------------------------------------------------

def run_spike_for_model(
    suite_name: str,
    model_paths: list[Path],
) -> dict[str, Any] | None:
    """Run Spike 5 on a single model suite.

    Returns stats dict for summary, or None on failure.
    """
    print_subsection(f"Model: {suite_name}")

    result = get_backtracking_result(suite_name, model_paths)
    if result is None:
        print("  SKIPPED: could not obtain binding resolutions")
        return None

    binding_resolutions, calc_usages = result
    print(f"  CalcUsages: {len(calc_usages)}")
    print(f"  Binding resolutions: {len(binding_resolutions)}")

    # Build cross-tabulation
    cross_tab, ref_mod_cases, ref_ep_cases = build_cross_tab(
        binding_resolutions, calc_usages,
    )

    # --- Print cross-tabulation ---
    print(f"\n  CROSS-TABULATION:")

    # Determine all binding types and resolution types present
    all_bt = sorted(set(bt for bt, _ in cross_tab.keys()))
    all_rt = sorted(set(rt for _, rt in cross_tab.keys()))

    # Build table rows
    headers = ["BindingType"] + all_rt + ["Total"]
    rows = []
    col_totals = {rt: 0 for rt in all_rt}
    for bt in all_bt:
        row = [bt]
        row_total = 0
        for rt in all_rt:
            count = cross_tab.get((bt, rt), 0)
            row.append(str(count))
            row_total += count
            col_totals[rt] += count
        row.append(str(row_total))
        rows.append(row)

    # Add totals row
    total_row = ["Total"]
    grand_total = 0
    for rt in all_rt:
        total_row.append(str(col_totals[rt]))
        grand_total += col_totals[rt]
    total_row.append(str(grand_total))
    rows.append(total_row)

    print_table(headers, rows)

    # --- REFERENCE -> MODULE_OUTPUT cases ---
    print(f"\n  REFERENCE -> MODULE_OUTPUT CASES: ", end="")
    if ref_mod_cases:
        print(f"{len(ref_mod_cases)} found")
        for case in ref_mod_cases:
            sp = case["source_path"] or ""
            print(f"\n    source_path: {sp!r}")
            print(f"    resolved_to: {case['resolved_to']!r}")
            print(f"    is_transitive: {case['is_transitive']}")
            # Test: does source_path.replace("::", "__") match the channel?
            if "::" in sp:
                normalized = sp.replace("::", "__")
                match_exact = normalized == case["resolved_to"]
                match_lower = normalized.lower() == case["resolved_to"].lower()
                print(f"    SYSML_QN normalization test:")
                print(f"      replace('::','__') = {normalized!r}")
                print(f"      exact match: {match_exact}")
                print(f"      lower match: {match_lower}")
    else:
        print("(none)")

    # --- REFERENCE -> ENTRY_POINT cases ---
    print(f"\n  REFERENCE -> ENTRY_POINT CASES: {len(ref_ep_cases)}")
    if ref_ep_cases:
        # Count by source_path format
        format_counts: Counter[str] = Counter()
        for case in ref_ep_cases:
            sp = case["source_path"]
            if sp is None or sp == "":
                format_counts["NONE"] += 1
            elif "::" in sp:
                format_counts["SYSML_QN"] += 1
            elif "." in sp:
                format_counts["DOTTED"] += 1
            else:
                format_counts["BARE"] += 1

        print(f"  Source path format distribution:")
        for fmt, count in sorted(format_counts.items()):
            print(f"    {fmt}: {count}")

        # Print a few examples of each format
        by_format: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for case in ref_ep_cases:
            sp = case["source_path"]
            if sp is None or sp == "":
                by_format["NONE"].append(case)
            elif "::" in sp:
                by_format["SYSML_QN"].append(case)
            elif "." in sp:
                by_format["DOTTED"].append(case)
            else:
                by_format["BARE"].append(case)

        for fmt in sorted(by_format.keys()):
            cases = by_format[fmt]
            print(f"\n  {fmt} examples (up to 5):")
            for case in cases[:5]:
                print(f"    {case['usage_qn']}|{case['param_name']}")
                print(f"      source_path: {case['source_path']!r}")
                print(f"      resolved_to: {case['resolved_to']!r}")
                print(f"      is_transitive: {case['is_transitive']}")

    return {
        "model": suite_name,
        "total_resolutions": len(binding_resolutions),
        "cross_tab": dict(cross_tab),
        "ref_module_output_count": len(ref_mod_cases),
        "ref_entry_point_count": len(ref_ep_cases),
    }


def main() -> None:
    print_section("SPIKE 5: REFERENCE Binding Resolution Outcomes")

    suites = EXTENDED_SUITES
    if len(sys.argv) > 1:
        paths = [Path(p) for p in sys.argv[1].split(",")]
        suites = [("cli_model", paths)]

    all_stats: list[dict[str, Any]] = []

    for suite_name, model_paths in suites:
        stats = run_spike_for_model(suite_name, model_paths)
        if stats is not None:
            all_stats.append(stats)

    # --- Overall Summary ---
    print_section("SUMMARY: REFERENCE Binding Resolution Outcomes")

    if not all_stats:
        print("  No models produced results.")
        return

    # Summary table
    headers = [
        "Model", "Total", "REF->MOD_OUT", "REF->ENTRY_PT",
    ]
    rows = []
    for s in all_stats:
        rows.append([
            s["model"],
            str(s["total_resolutions"]),
            str(s["ref_module_output_count"]),
            str(s["ref_entry_point_count"]),
        ])
    print_table(headers, rows)

    # Grand cross-tab across all models
    print_subsection("Grand Cross-Tabulation (all models)")
    grand_tab: Counter[tuple[str, str]] = Counter()
    for s in all_stats:
        for key, count in s["cross_tab"].items():
            grand_tab[key] += count

    all_bt = sorted(set(bt for bt, _ in grand_tab.keys()))
    all_rt = sorted(set(rt for _, rt in grand_tab.keys()))
    headers = ["BindingType"] + all_rt + ["Total"]
    rows = []
    col_totals = {rt: 0 for rt in all_rt}
    for bt in all_bt:
        row = [bt]
        row_total = 0
        for rt in all_rt:
            count = grand_tab.get((bt, rt), 0)
            row.append(str(count))
            row_total += count
            col_totals[rt] += count
        row.append(str(row_total))
        rows.append(row)
    total_row = ["Total"]
    grand_total = 0
    for rt in all_rt:
        total_row.append(str(col_totals[rt]))
        grand_total += col_totals[rt]
    total_row.append(str(grand_total))
    rows.append(total_row)
    print_table(headers, rows)

    # Verdict
    total_ref_mod = sum(s["ref_module_output_count"] for s in all_stats)
    total_ref_ep = sum(s["ref_entry_point_count"] for s in all_stats)

    print(f"\n  VERDICT:")
    if total_ref_mod == 0:
        print(f"    REFERENCE -> MODULE_OUTPUT: NEVER OCCURS ({total_ref_ep} REFERENCE bindings, all ENTRY_POINT)")
        print(f"    SYSML_QN normalization in resolve(): DEAD CODE for MODULE_OUTPUT resolution")
        print(f"    Recommendation: Remove or simplify SYSML_QN normalization in OutputRegistry.resolve()")
    else:
        print(f"    REFERENCE -> MODULE_OUTPUT: OCCURS ({total_ref_mod} cases)")
        print(f"    SYSML_QN normalization in resolve(): EXERCISED but may need fixing")
        print(f"    Review the cases above for format match correctness")


if __name__ == "__main__":
    main()
