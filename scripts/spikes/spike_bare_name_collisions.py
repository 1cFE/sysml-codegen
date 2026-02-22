#!/usr/bin/env python3
"""Spike 4: Bare-Name Ambiguity in Real Models.

Counts how many CalcUsage output names collide across multiple CalcUsages
after template expansion. Determines whether bare-name registration in the
OutputRegistry is viable, needs collision handling, or should be skipped.

Answers design_revision_comments.md Issue 2 (bare-name collision policy).

Usage:
    uv run python scripts/spikes/spike_bare_name_collisions.py
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _helpers import (
    EXTENDED_SUITES,
    load_model,
    print_section,
    print_subsection,
    print_table,
)
from sysml_codegen.extraction.usage_extractor import (
    extract_calculation_usages,
)
from agentic_mbse.sysml.types import BindingType


# ---------------------------------------------------------------------------
# Spike Logic
# ---------------------------------------------------------------------------

def run_spike_for_model(
    suite_name: str,
    model_paths: list[Path],
) -> dict[str, object]:
    """Run Spike 4 on a single model.

    Returns stats dict for the summary.
    """
    print_subsection(f"Model: {suite_name}")

    model, adapter, extractor = load_model(model_paths)
    if model is None:
        print("  SKIPPED: model failed to load")
        return {}

    calc_defs = extractor.extract_calculation_definitions()
    calc_def_map = {cd.name: cd for cd in calc_defs}
    print(f"  CalcDefs: {len(calc_defs)}")

    usages, _ = extract_calculation_usages(
        model, calc_defs=calc_defs, expand_templates=True,
    )
    print(f"  CalcUsages (expanded): {len(usages)}")

    # --- Collect all (instance_name, output_name) pairs ---
    all_pairs: list[tuple[str, str]] = []
    output_name_to_usages: dict[str, list[str]] = defaultdict(list)

    for usage in usages:
        cd = calc_def_map.get(usage.calc_def_name)
        if cd is None:
            continue
        for attr in cd.output_attributes:
            all_pairs.append((usage.instance_name, attr.name))
            output_name_to_usages[attr.name].append(usage.instance_name)

    N = len(all_pairs)
    M = len(output_name_to_usages)
    ambiguous = {k: v for k, v in output_name_to_usages.items() if len(v) > 1}
    K = len(ambiguous)

    print(f"\n  STATISTICS:")
    print(f"    Total CalcUsage outputs (N): {N}")
    print(f"    Unique output names (M): {M}")
    print(f"    Ambiguous bare names (K): {K}")

    # --- List ambiguous names ---
    if ambiguous:
        print(f"\n  AMBIGUOUS NAMES:")
        for name, producers in sorted(ambiguous.items()):
            print(f"    \"{name}\" produced by {len(producers)} CalcUsages:")
            for p in producers:
                is_virtual = "__" in p
                label = " [VIRTUAL]" if is_virtual else ""
                print(f"      - {p}{label}")
    else:
        print(f"\n  AMBIGUOUS NAMES: (none)")

    # --- Check downstream bare-name references ---
    print(f"\n  DOWNSTREAM BARE-NAME REFERENCES:")
    bare_ref_counts: dict[str, int] = defaultdict(int)
    dotted_ref_counts: dict[str, int] = defaultdict(int)

    for usage in usages:
        for b in usage.bindings:
            if b.source_path is None:
                continue
            # A bare-name reference has no dots and no ::
            if "." not in b.source_path and "::" not in b.source_path:
                # Check if this bare name is an output name
                if b.source_path in output_name_to_usages:
                    bare_ref_counts[b.source_path] += 1
            elif "." in b.source_path and "::" not in b.source_path:
                # Dotted reference -- extract output segment
                parts = b.source_path.split(".")
                if len(parts) == 2:
                    out_name = parts[1]
                    if out_name in output_name_to_usages:
                        dotted_ref_counts[out_name] += 1

    if ambiguous:
        for name in sorted(ambiguous.keys()):
            bare_count = bare_ref_counts.get(name, 0)
            dotted_count = dotted_ref_counts.get(name, 0)
            print(
                f"    \"{name}\": bare-name refs={bare_count}, "
                f"dotted refs={dotted_count}"
            )
    else:
        print("    (no ambiguous names to check)")

    # Also show ALL bare-name references (not just ambiguous)
    all_bare = {k: v for k, v in bare_ref_counts.items()}
    if all_bare:
        print(f"\n  ALL BARE-NAME OUTPUT REFERENCES:")
        for name, count in sorted(all_bare.items()):
            is_ambig = "AMBIGUOUS" if name in ambiguous else "unique"
            print(f"    \"{name}\": {count} refs ({is_ambig})")
    else:
        print(f"\n  ALL BARE-NAME OUTPUT REFERENCES: (none found)")

    # --- Recommendation ---
    print(f"\n  RECOMMENDATION:")
    if K == 0:
        print(f"    K=0 -- bare-name registration is safe (no collisions)")
    elif K <= 3:
        print(f"    K={K} -- bare-name registration needs collision handling")
        print(f"    Recommend: remove-on-conflict policy (Option B from design comments)")
    else:
        print(f"    K={K} -- significant ambiguity, consider skipping bare-name registration")

    return {
        "N": N, "M": M, "K": K,
        "ambiguous": ambiguous,
        "bare_refs": dict(bare_ref_counts),
    }


def main() -> None:
    print_section("SPIKE 4: Bare-Name Ambiguity")

    # Use solar_battery and catf_mfe per the plan
    suites = [s for s in EXTENDED_SUITES if s[0] in ("solar_battery", "catf_mfe")]
    if len(sys.argv) > 1:
        paths = [Path(p) for p in sys.argv[1].split(",")]
        suites = [("cli_model", paths)]

    all_stats: list[tuple[str, dict]] = []
    for suite_name, model_paths in suites:
        stats = run_spike_for_model(suite_name, model_paths)
        if stats:
            all_stats.append((suite_name, stats))

    # --- Cross-model summary ---
    if all_stats:
        print_section("CROSS-MODEL SUMMARY")
        summary_rows = []
        for name, s in all_stats:
            summary_rows.append([
                name, str(s["N"]), str(s["M"]), str(s["K"]),
            ])
        print_table(["Model", "N (total)", "M (unique)", "K (ambiguous)"], summary_rows)

        # Overall recommendation
        total_k = sum(s["K"] for _, s in all_stats)
        total_bare_refs = sum(
            sum(s.get("bare_refs", {}).values()) for _, s in all_stats
        )
        print(f"\n  Total ambiguous names across all models: {total_k}")
        print(f"  Total bare-name references to output names: {total_bare_refs}")

        if total_bare_refs == 0:
            print(f"\n  POLICY RECOMMENDATION: Bare-name registration is OPTIONAL.")
            print(f"    No binding source_paths use bare output names.")
            print(f"    All references use dotted (instance.output) or SysML QN format.")
            print(f"    Safe to skip bare-name registration entirely.")
        elif total_k > 0:
            print(f"\n  POLICY RECOMMENDATION: Use remove-on-conflict for bare names.")
        else:
            print(f"\n  POLICY RECOMMENDATION: Bare-name registration is safe.")


if __name__ == "__main__":
    main()
