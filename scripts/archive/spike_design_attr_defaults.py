#!/usr/bin/env python3
"""Spike 7: DesignAttributeData.default_value Format for Path-Like Defaults.

Classifies every design attribute's default_value to determine:

  - Are transitive defaults (path-like values) identifiable by format?
  - Does registry.resolve(default_value) work with actual data?
  - What filter criteria should Phase 4 transitive alias registration use?

Answers design_revision_comments_v2.md Issue 12.

Usage:
    uv run python scripts/spikes/spike_design_attr_defaults.py
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
)
from sysml_codegen.analysis.parameter_groups import (
    DesignAttributeData,
    extract_design_attributes,
)
from sysml_codegen.extraction.usage_extractor import (
    CalcUsageData,
    extract_calculation_usages,
)


# ---------------------------------------------------------------------------
# Default Value Classification
# ---------------------------------------------------------------------------

def classify_default_value(value: str | None) -> str:
    """Classify the format of a design attribute's default_value.

    Returns one of: NUMERIC, BOOLEAN, SYSML_QN, DOTTED_PATH, AST_TEXT,
    STRING_LITERAL, NONE.
    """
    if value is None or value == "":
        return "NONE"

    # Boolean
    if value.lower() in ("true", "false"):
        return "BOOLEAN"

    # Numeric (int or float)
    try:
        float(value)
        return "NUMERIC"
    except ValueError:
        pass

    # SYSML_QN (contains ::)
    if "::" in value:
        return "SYSML_QN"

    # AST text indicators: starts with ".", contains "(", has operators
    if value.startswith(".") or "(" in value:
        return "AST_TEXT"

    # Dotted path (contains "." and is not numeric -- already ruled out above)
    if "." in value:
        return "DOTTED_PATH"

    # Everything else -- could be a bare name reference or a string literal
    return "STRING_LITERAL"


def _is_potential_reference(value: str) -> bool:
    """Check if a STRING_LITERAL default_value could be a bare-name reference.

    Heuristic: looks like a Python identifier (not a CAS code, not a unit string).
    """
    if not value:
        return False
    # CAS codes are alphanumeric starting with uppercase letters + digits
    # True identifiers are lowercase with underscores
    return "_" in value or value.islower()


# ---------------------------------------------------------------------------
# Output Catalog Builder (reused from Spike 3)
# ---------------------------------------------------------------------------

def build_output_catalog(
    usages: list[CalcUsageData],
    calc_def_map: dict[str, Any],
) -> dict[str, str]:
    """Build output catalog mapping dotted keys -> channel names.

    Registers both short_key and full_key for each output.
    Returns: {key: channel_name}
    """
    catalog: dict[str, str] = {}
    for usage in usages:
        cd = calc_def_map.get(usage.calc_def_name)
        if cd is None:
            continue
        for attr in cd.output_attributes:
            channel = f"{usage.instance_name}__{attr.name}"
            # Short key: last segment of instance_name + output
            short_inst = (
                usage.instance_name.rsplit("__", 1)[-1]
                if "__" in usage.instance_name
                else usage.instance_name
            )
            short_key = f"{short_inst}.{attr.name}"
            full_key = f"{usage.instance_name}.{attr.name}"
            catalog[short_key] = channel
            catalog[full_key] = channel
    return catalog


# ---------------------------------------------------------------------------
# Spike Logic
# ---------------------------------------------------------------------------

def run_spike_for_model(
    suite_name: str,
    model_paths: list[Path],
) -> dict[str, Any] | None:
    """Run Spike 7 on a single model suite."""
    print_subsection(f"Model: {suite_name}")

    model, adapter, extractor = load_model(model_paths)
    if model is None:
        print("  SKIPPED: model failed to load")
        return None

    # Extract design attributes
    design_attrs = extract_design_attributes(model)
    total_attrs = sum(len(v) for v in design_attrs.values())
    print(f"  Design attributes: {total_attrs} across {len(design_attrs)} files")

    # Extract CalcDefs and CalcUsages for output catalog
    calc_defs = extractor.extract_calculation_definitions()
    calc_def_map = {cd.name: cd for cd in calc_defs}
    usages, _ = extract_calculation_usages(
        model, calc_defs=calc_defs, expand_templates=True,
    )
    print(f"  CalcDefs: {len(calc_defs)}, CalcUsages: {len(usages)}")

    # Build output catalog
    output_catalog = build_output_catalog(usages, calc_def_map)
    print(f"  Output catalog: {len(output_catalog)} keys")

    # --- Classify all design attributes ---
    print(f"\n  DESIGN ATTRIBUTES ({total_attrs} total):")

    all_classified: list[dict[str, Any]] = []
    table_rows: list[list[str]] = []

    for source_file, attrs in sorted(design_attrs.items()):
        for attr in attrs:
            classification = classify_default_value(attr.default_value)
            entry = {
                "name": attr.name,
                "parent_part": attr.parent_part,
                "default_value": attr.default_value,
                "qualified_name": attr.qualified_name,
                "sysml_type": attr.sysml_type,
                "classification": classification,
                "source_file": str(source_file),
            }
            all_classified.append(entry)
            table_rows.append([
                attr.name,
                attr.parent_part,
                repr(attr.default_value) if attr.default_value else "(None)",
                classification,
            ])

    print_table(["name", "parent_part", "default_value", "classification"], table_rows)

    # --- Classification distribution ---
    class_counts = Counter(e["classification"] for e in all_classified)
    print(f"\n  CLASSIFICATION DISTRIBUTION:")
    for cls, count in sorted(class_counts.items()):
        print(f"    {cls}: {count}")

    # --- Transitive default resolution ---
    path_like = [
        e for e in all_classified
        if e["classification"] in ("DOTTED_PATH", "SYSML_QN")
    ]
    print(f"\n  TRANSITIVE DEFAULT RESOLUTION ({len(path_like)} path-like defaults):")

    resolved_count = 0
    unresolved_count = 0

    for entry in path_like:
        dv = entry["default_value"]
        parent = entry["parent_part"]
        name = entry["name"]
        print(f"\n    {parent}.{name}: default={dv!r} [{entry['classification']}]")

        # Direct catalog lookup
        channel = output_catalog.get(dv)
        if channel:
            print(f"      output_catalog.get({dv!r}) = {channel!r}")
            print(f"      RESOLVES: YES -> channel {channel!r}")
            resolved_count += 1
            continue

        # If SYSML_QN, try normalization
        if entry["classification"] == "SYSML_QN" and "::" in dv:
            normalized = dv.replace("::", "__")
            channel = output_catalog.get(normalized)
            if channel:
                print(f"      output_catalog.get({normalized!r}) = {channel!r}")
                print(f"      RESOLVES: YES (via :: normalization)")
                resolved_count += 1
                continue
            normalized_lower = normalized.lower()
            channel = output_catalog.get(normalized_lower)
            if channel:
                print(f"      output_catalog.get({normalized_lower!r}) = {channel!r}")
                print(f"      RESOLVES: YES (via :: normalization + lowercase)")
                resolved_count += 1
                continue

        print(f"      output_catalog.get({dv!r}) = NOT FOUND")
        # Show nearby catalog keys for diagnostic
        if "." in dv:
            leaf = dv.rsplit(".", 1)[-1]
            nearby = [k for k in output_catalog if leaf in k]
            if nearby:
                print(f"      Nearby catalog keys containing '{leaf}':")
                for k in nearby[:5]:
                    print(f"        {k!r} -> {output_catalog[k]!r}")
        print(f"      RESOLVES: NO")
        unresolved_count += 1

    # --- Bare-name analysis ---
    bare_names = [
        e for e in all_classified
        if e["classification"] == "STRING_LITERAL"
    ]
    print(f"\n  BARE-NAME ANALYSIS ({len(bare_names)} STRING_LITERAL defaults):")

    potential_refs = []
    for entry in bare_names:
        dv = entry["default_value"]
        is_ref = _is_potential_reference(dv)
        # Check if bare name matches any output name in any CalcUsage
        matching_outputs = []
        for usage in usages:
            cd = calc_def_map.get(usage.calc_def_name)
            if cd:
                for out_attr in cd.output_attributes:
                    if out_attr.name == dv:
                        matching_outputs.append(
                            f"{usage.instance_name}.{out_attr.name}"
                        )

        if is_ref or matching_outputs:
            potential_refs.append(entry)
            print(f"\n    {entry['parent_part']}.{entry['name']}: default={dv!r}")
            print(f"      Looks like identifier: {is_ref}")
            if matching_outputs:
                print(f"      Matches CalcUsage outputs: {matching_outputs}")
            else:
                print(f"      Matches CalcUsage outputs: (none)")

    if not potential_refs and bare_names:
        print(f"  No STRING_LITERAL defaults look like potential references.")
    elif not bare_names:
        print(f"  (no STRING_LITERAL defaults)")

    return {
        "model": suite_name,
        "total_attrs": total_attrs,
        "class_counts": dict(class_counts),
        "path_like_count": len(path_like),
        "resolved_count": resolved_count,
        "unresolved_count": unresolved_count,
        "potential_bare_refs": len(potential_refs),
    }


def main() -> None:
    print_section("SPIKE 7: DesignAttributeData.default_value Format")

    # Run on solar_battery and e2e_attr_expr (per plan)
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
    print_section("SUMMARY: DesignAttributeData.default_value Format")

    if not all_stats:
        print("  No models produced results.")
        return

    # Classification summary table
    all_classes = sorted(
        set(cls for s in all_stats for cls in s["class_counts"].keys())
    )
    headers = ["Model", "Total"] + all_classes
    rows = []
    for s in all_stats:
        row = [s["model"], str(s["total_attrs"])]
        for cls in all_classes:
            row.append(str(s["class_counts"].get(cls, 0)))
        rows.append(row)

    # Totals
    total_row = ["TOTAL", str(sum(s["total_attrs"] for s in all_stats))]
    grand_counts: Counter[str] = Counter()
    for s in all_stats:
        for cls, count in s["class_counts"].items():
            grand_counts[cls] += count
    for cls in all_classes:
        total_row.append(str(grand_counts.get(cls, 0)))
    rows.append(total_row)

    print_table(headers, rows)

    # Transitive defaults summary
    total_path_like = sum(s["path_like_count"] for s in all_stats)
    total_resolved = sum(s["resolved_count"] for s in all_stats)
    total_unresolved = sum(s["unresolved_count"] for s in all_stats)
    total_bare_refs = sum(s["potential_bare_refs"] for s in all_stats)

    print(f"\n  TRANSITIVE DEFAULTS: {total_path_like} found, {total_resolved} resolve, {total_unresolved} fail")
    print(f"  POTENTIAL BARE-NAME REFERENCES: {total_bare_refs}")

    # Verdict
    print(f"\n  VERDICT:")
    if total_path_like == 0:
        print(f"    No path-like default_values found in either model.")
        print(f"    Phase 4 transitive alias registration MAY BE UNNECESSARY")
        print(f"    (or these models don't exercise that pattern)")
    else:
        if total_resolved == total_path_like:
            print(f"    All {total_path_like} path-like defaults resolve successfully")
            print(f"    Phase 4 transitive alias registration WORKS with actual data")
        else:
            print(f"    {total_unresolved}/{total_path_like} path-like defaults FAIL to resolve")
            print(f"    Phase 4 needs investigation for unresolved cases")

    print(f"\n  PROPOSED FILTER for Phase 4:")
    print(f"    def _is_transitive_default(attr: DesignAttributeData) -> bool:")
    print(f"        if attr.default_value is None: return False")
    print(f"        if '.' not in attr.default_value: return False")
    print(f"        try: float(attr.default_value); return False")
    print(f"        except ValueError: pass")
    print(f"        if attr.default_value.lower() in ('true', 'false'): return False")
    print(f"        return True")


if __name__ == "__main__":
    main()
