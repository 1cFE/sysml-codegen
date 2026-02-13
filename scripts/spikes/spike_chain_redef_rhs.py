#!/usr/bin/env python3
"""Spike 6: :>> CHAIN Redefinition RHS Content.

Examines what the RHS of :>> CHAIN redefinitions contains -- bare name,
dotted path, SYSML_QN, or raw AST text -- to determine how ChannelAlias
canonical_name should be constructed for Phase 2 alias registration.

Answers design_revision_comments_v2.md Issue 9.

Usage:
    uv run python scripts/spikes/spike_chain_redef_rhs.py
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _helpers import (
    DEFAULT_SUITES,
    load_model,
    print_section,
    print_subsection,
    print_table,
    safe_attr,
    type_name,
)
from sysml_codegen.extraction.hierarchy_resolver import extract_hierarchy_data
from sysml_codegen.extraction.data_models import (
    RedefinitionData,
    RedefinitionType,
    HierarchyExtractionResult,
)


# ---------------------------------------------------------------------------
# Format Classification
# ---------------------------------------------------------------------------

def classify_redef_source_path(source_path: str | None) -> str:
    """Classify the format of a CHAIN redefinition's source_path.

    Returns one of: BARE, DOTTED, SYSML_QN, AST_TEXT, NONE.
    """
    if source_path is None or source_path == "":
        return "NONE"
    if "::" in source_path:
        return "SYSML_QN"
    # AST text indicators: starts with ".", contains "(", or has operators
    if source_path.startswith(".") or "(" in source_path:
        return "AST_TEXT"
    if "." in source_path:
        return "DOTTED"
    return "BARE"


# ---------------------------------------------------------------------------
# Spike Logic
# ---------------------------------------------------------------------------

def print_chain_redef(
    idx: int,
    redef: RedefinitionData,
    part_usage_names: dict[str, set[str]],
) -> dict[str, str]:
    """Print details for one CHAIN redefinition and return classification data."""
    fmt = classify_redef_source_path(redef.source_path)

    print(f"\n  #{idx}: owning_part_qn={redef.owning_part_qn!r}")
    print(f"      attribute_name={redef.attribute_name!r}")
    print(f"      source_path={redef.source_path!r}")
    print(f"      expression_text={redef.expression_text!r}")

    # Compare source_path vs expression_text
    if redef.source_path != redef.expression_text:
        print(f"      NOTE: source_path != expression_text")

    # expression_ast info
    if redef.expression_ast is not None:
        print(f"      expression_ast type: {type_name(redef.expression_ast)}")
    else:
        print(f"      expression_ast: None")

    # Deep path info
    if redef.target_path:
        print(f"      target_path: {redef.target_path}")
        print(f"      is_deep_path: {redef.is_deep_path}")

    print(f"      source: {redef.source_file}:{redef.source_line}")

    # Classification
    print(f"\n      FORMAT: {fmt}")

    # Resolvability assessment
    if fmt == "BARE":
        print(f"      RESOLVABLE BY REGISTRY: NO (bare names not registered)")
        # Check if the bare name is a sibling part usage on the owning PartDef
        sibling_usages = part_usage_names.get(redef.owning_part_qn, set())
        sp = redef.source_path or ""
        # For dotted bare like "cost_model.total_cost", check first segment
        first_seg = sp.split(".")[0] if "." in sp else sp
        if first_seg in sibling_usages:
            print(f"      TARGET: sibling part usage '{first_seg}' on {redef.owning_part_qn}")
        else:
            print(f"      TARGET: unknown (not a sibling part usage)")
            print(f"        sibling usages: {sorted(sibling_usages) if sibling_usages else '(none)'}")
        print(f"      SCOPING NEEDED: YES -- needs instance_path prefix")
    elif fmt == "DOTTED":
        print(f"      RESOLVABLE BY REGISTRY: MAYBE (if dotted path matches registered key)")
        # Check first segment against sibling usages
        sp = redef.source_path or ""
        first_seg = sp.split(".")[0]
        sibling_usages = part_usage_names.get(redef.owning_part_qn, set())
        if first_seg in sibling_usages:
            print(f"      TARGET: starts with sibling part usage '{first_seg}'")
        print(f"      SCOPING NEEDED: LIKELY -- dotted path is PartDef-local, not design-scoped")
    elif fmt == "SYSML_QN":
        print(f"      RESOLVABLE BY REGISTRY: MAYBE (if :: normalization works)")
        print(f"      SCOPING NEEDED: NO (already fully qualified)")
    elif fmt == "AST_TEXT":
        print(f"      RESOLVABLE BY REGISTRY: NO (raw AST text)")
        print(f"      NEEDS: AST extraction like EXPOSE_PURE")
    else:
        print(f"      RESOLVABLE BY REGISTRY: N/A (no source_path)")

    return {
        "owning_part_qn": redef.owning_part_qn,
        "attribute_name": redef.attribute_name,
        "source_path": redef.source_path or "",
        "expression_text": redef.expression_text,
        "format": fmt,
    }


def run_spike_for_model(
    suite_name: str,
    model_paths: list[Path],
) -> dict[str, Any] | None:
    """Run Spike 6 on a single model suite."""
    print_subsection(f"Model: {suite_name}")

    model, adapter, extractor = load_model(model_paths)
    if model is None:
        print("  SKIPPED: model failed to load")
        return None

    # Extract hierarchy data
    hier = extract_hierarchy_data(model)

    print(f"  HierarchyExtractionResult:")
    print(f"    redefinitions: {len(hier.redefinitions)}")
    print(f"    design_overrides: {len(hier.design_overrides)}")
    print(f"    multiplicities: {len(hier.multiplicities)}")
    print(f"    aggregation_expressions: {len(hier.aggregation_expressions)}")
    print(f"    part_usage_names: {len(hier.part_usage_names)} PartDefs")
    print(f"    warnings: {len(hier.warnings)}")

    if hier.warnings:
        for w in hier.warnings:
            print(f"      WARNING: {w}")

    # Print part_usage_names for context
    if hier.part_usage_names:
        print(f"\n  PART USAGE NAMES (PartDef -> child usages):")
        for pqn, usages in sorted(hier.part_usage_names.items()):
            print(f"    {pqn}: {sorted(usages)}")

    # --- CHAIN redefinitions (from PartDefs) ---
    chain_redefs = [
        r for r in hier.redefinitions
        if r.redefinition_type == RedefinitionType.CHAIN
    ]
    print(f"\n  CHAIN-TYPED REDEFINITIONS: {len(chain_redefs)}")

    redef_data: list[dict[str, str]] = []
    for i, redef in enumerate(chain_redefs, 1):
        data = print_chain_redef(i, redef, hier.part_usage_names)
        redef_data.append(data)

    # Also show non-CHAIN redefinitions for completeness
    other_redefs = [
        r for r in hier.redefinitions
        if r.redefinition_type != RedefinitionType.CHAIN
    ]
    if other_redefs:
        print(f"\n  OTHER REDEFINITIONS (non-CHAIN): {len(other_redefs)}")
        by_type = Counter(r.redefinition_type.value for r in other_redefs)
        for rtype, count in sorted(by_type.items()):
            print(f"    {rtype}: {count}")

    # --- CHAIN design_overrides ---
    chain_overrides = [
        r for r in hier.design_overrides
        if r.redefinition_type == RedefinitionType.CHAIN
    ]
    print(f"\n  CHAIN-TYPED DESIGN OVERRIDES: {len(chain_overrides)}")

    override_data: list[dict[str, str]] = []
    for i, redef in enumerate(chain_overrides, 1):
        data = print_chain_redef(i, redef, hier.part_usage_names)
        override_data.append(data)

    # Also show non-CHAIN design overrides for completeness
    other_overrides = [
        r for r in hier.design_overrides
        if r.redefinition_type != RedefinitionType.CHAIN
    ]
    if other_overrides:
        print(f"\n  OTHER DESIGN OVERRIDES (non-CHAIN): {len(other_overrides)}")
        by_type = Counter(r.redefinition_type.value for r in other_overrides)
        for rtype, count in sorted(by_type.items()):
            print(f"    {rtype}: {count}")

    # Build format counts
    all_chain = redef_data + override_data
    format_counts = Counter(d["format"] for d in all_chain)

    return {
        "model": suite_name,
        "total_redefs": len(hier.redefinitions),
        "total_overrides": len(hier.design_overrides),
        "chain_redefs": len(chain_redefs),
        "chain_overrides": len(chain_overrides),
        "format_counts": dict(format_counts),
        "all_chain_data": all_chain,
    }


def main() -> None:
    print_section("SPIKE 6: :>> CHAIN Redefinition RHS Content")

    # Only run on solar_battery and e2e_attr_expr (per plan)
    target_models = {"solar_battery", "e2e_attr_expr"}
    suites = [(name, paths) for name, paths in DEFAULT_SUITES if name in target_models]

    if len(sys.argv) > 1:
        paths = [Path(p) for p in sys.argv[1].split(",")]
        suites = [("cli_model", paths)]

    all_stats: list[dict[str, Any]] = []

    for suite_name, model_paths in suites:
        stats = run_spike_for_model(suite_name, model_paths)
        if stats is not None:
            all_stats.append(stats)

    # --- Summary ---
    print_section("SUMMARY: :>> CHAIN Redefinition RHS Content")

    if not all_stats:
        print("  No models produced results.")
        return

    # Summary table
    all_formats = sorted(
        set(
            fmt
            for s in all_stats
            for fmt in s["format_counts"].keys()
        )
    )
    headers = ["Model", "CHAIN redefs", "CHAIN overrides"] + all_formats
    rows = []
    for s in all_stats:
        row = [
            s["model"],
            str(s["chain_redefs"]),
            str(s["chain_overrides"]),
        ]
        for fmt in all_formats:
            row.append(str(s["format_counts"].get(fmt, 0)))
        rows.append(row)

    # Totals row
    total_row = ["TOTAL"]
    total_row.append(str(sum(s["chain_redefs"] for s in all_stats)))
    total_row.append(str(sum(s["chain_overrides"] for s in all_stats)))
    grand_format_counts: Counter[str] = Counter()
    for s in all_stats:
        for fmt, count in s["format_counts"].items():
            grand_format_counts[fmt] += count
    for fmt in all_formats:
        total_row.append(str(grand_format_counts.get(fmt, 0)))
    rows.append(total_row)

    print_table(headers, rows)

    # Verdict
    print(f"\n  VERDICT:")
    if grand_format_counts.get("BARE", 0) > 0:
        bare_count = grand_format_counts["BARE"]
        total = sum(grand_format_counts.values())
        print(f"    BARE source_paths: {bare_count}/{total} CHAIN redefinitions")
        print(f"    Confirms Issue 9: canonical_name IS bare, cannot resolve in OutputRegistry")
        print(f"    Fix: Scope canonical_name at ChannelAlias construction time")
        print(f"         canonical_name = f\"{{instance_path}}.{{redef.source_path}}\"")
    if grand_format_counts.get("DOTTED", 0) > 0:
        dotted_count = grand_format_counts["DOTTED"]
        print(f"    DOTTED source_paths: {dotted_count} -- PartDef-local dotted paths")
        print(f"    These also need scoping (prefix with instance_path)")
    if grand_format_counts.get("NONE", 0) > 0:
        none_count = grand_format_counts["NONE"]
        print(f"    NONE source_paths: {none_count} -- need expression_ast/expression_text extraction")

    # Scoping recommendation
    has_bare = grand_format_counts.get("BARE", 0) > 0
    has_dotted = grand_format_counts.get("DOTTED", 0) > 0
    if has_bare or has_dotted:
        print(f"\n    SCOPING RECOMMENDATION:")
        print(f"      All BARE and DOTTED source_paths need design instance scoping.")
        print(f"      At Step 3.5(D), when building ChannelAlias from CHAIN redefs:")
        print(f"        alias_name   = f\"{{instance_path}}.{{redef.attribute_name}}\"")
        print(f"        canonical_name = f\"{{instance_path}}.{{redef.source_path}}\"")
        print(f"      This uses the same instance_path available from aggregation scoping.")


if __name__ == "__main__":
    main()
