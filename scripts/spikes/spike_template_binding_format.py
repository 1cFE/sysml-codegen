#!/usr/bin/env python3
"""Spike 1: Template Binding source_path Format.

Determines what source_path format SysIDE produces for CalcUsage bindings
inside PartDefinitions (templates) vs. concrete CalcUsages, and how those
formats change after template expansion (virtual CalcUsages).

Answers design_revision_comments.md Issue 7 (blocks everything).

Usage:
    uv run python scripts/spikes/spike_template_binding_format.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _helpers import (
    DEFAULT_SUITES,
    load_model,
    print_section,
    print_subsection,
    print_table,
    safe_attr,
)
from sysml_codegen.extraction.usage_extractor import (
    BindingInfo,
    CalcUsageData,
    extract_calculation_usages,
)
from agentic_mbse.sysml.types import BindingType


# ---------------------------------------------------------------------------
# Format Classification
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
    # No dots, no ::, just a plain name
    return "BARE"


# ---------------------------------------------------------------------------
# Spike Logic
# ---------------------------------------------------------------------------

def print_bindings(bindings: list[BindingInfo], indent: str = "    ") -> list[list[str]]:
    """Print binding details and return summary rows for the summary table."""
    rows = []
    for b in bindings:
        fmt = classify_source_path(b.source_path, b.binding_type)
        literal_str = ""
        if b.literal_value is not None:
            literal_str = f" literal={b.literal_value!r}"
        print(
            f"{indent}Binding: {b.param_name} | {b.binding_type.name} | "
            f"source_path={b.source_path!r}{literal_str} | format={fmt}"
        )
        rows.append([b.param_name, b.binding_type.name, repr(b.source_path), fmt])
    return rows


def run_spike_for_model(
    suite_name: str,
    model_paths: list[Path],
) -> list[list[str]]:
    """Run Spike 1 on a single model suite.

    Returns summary rows: [model, usage_name, param, binding_type, source_path, format]
    """
    print_subsection(f"Model: {suite_name}")

    model, adapter, extractor = load_model(model_paths)
    if model is None:
        print("  SKIPPED: model failed to load")
        return []

    # Extract CalcDefs
    calc_defs = extractor.extract_calculation_definitions()
    print(f"  CalcDefs found: {len(calc_defs)}")

    # --- Unexpanded (templates visible) ---
    unexpanded, report_unexp = extract_calculation_usages(
        model, calc_defs=calc_defs, expand_templates=False,
    )
    print(f"  CalcUsages (expand_templates=False): {len(unexpanded)}")

    templates = [u for u in unexpanded if u.is_template]
    concrete_unexp = [u for u in unexpanded if not u.is_template]

    summary_rows: list[list[str]] = []

    if templates:
        print(f"\n  TEMPLATE CALCUSAGES (expand_templates=False): {len(templates)}")
        for usage in templates:
            print(
                f"\n    Template: {usage.instance_name}"
                f" (calc_def={usage.calc_def_name},"
                f" owning={usage.owning_part_def_qn})"
            )
            for b in usage.bindings:
                fmt = classify_source_path(b.source_path, b.binding_type)
                literal_str = ""
                if b.literal_value is not None:
                    literal_str = f" literal={b.literal_value!r}"
                print(
                    f"      Binding: {b.param_name} | {b.binding_type.name} | "
                    f"source_path={b.source_path!r}{literal_str} | format={fmt}"
                )
                summary_rows.append([
                    suite_name, f"TPL:{usage.instance_name}",
                    b.param_name, b.binding_type.name, repr(b.source_path), fmt,
                ])
    else:
        print("\n  TEMPLATE CALCUSAGES: (none found)")

    if concrete_unexp:
        print(f"\n  CONCRETE CALCUSAGES (expand_templates=False): {len(concrete_unexp)}")
        for usage in concrete_unexp:
            print(
                f"\n    Concrete: {usage.instance_name}"
                f" (calc_def={usage.calc_def_name},"
                f" qn={usage.qualified_name})"
            )
            for b in usage.bindings:
                fmt = classify_source_path(b.source_path, b.binding_type)
                literal_str = ""
                if b.literal_value is not None:
                    literal_str = f" literal={b.literal_value!r}"
                print(
                    f"      Binding: {b.param_name} | {b.binding_type.name} | "
                    f"source_path={b.source_path!r}{literal_str} | format={fmt}"
                )
                summary_rows.append([
                    suite_name, f"CONC:{usage.instance_name}",
                    b.param_name, b.binding_type.name, repr(b.source_path), fmt,
                ])

    # --- Expanded (virtual copies) ---
    expanded, report_exp = extract_calculation_usages(
        model, calc_defs=calc_defs, expand_templates=True,
    )
    print(f"\n  CalcUsages (expand_templates=True): {len(expanded)}")

    virtuals = [u for u in expanded if "__" in u.qualified_name]
    concrete_exp = [u for u in expanded if "__" not in u.qualified_name]

    if virtuals:
        print(f"\n  VIRTUAL CALCUSAGES (expand_templates=True): {len(virtuals)}")
        for usage in virtuals:
            print(
                f"\n    Virtual: {usage.instance_name}"
                f"\n      qualified_name={usage.qualified_name}"
            )
            for b in usage.bindings:
                fmt = classify_source_path(b.source_path, b.binding_type)
                literal_str = ""
                if b.literal_value is not None:
                    literal_str = f" literal={b.literal_value!r}"
                print(
                    f"      Binding: {b.param_name} | {b.binding_type.name} | "
                    f"source_path={b.source_path!r}{literal_str} | format={fmt}"
                )
                summary_rows.append([
                    suite_name, f"VIRT:{usage.instance_name}",
                    b.param_name, b.binding_type.name, repr(b.source_path), fmt,
                ])
    else:
        print("\n  VIRTUAL CALCUSAGES: (none found)")

    if concrete_exp:
        print(f"\n  CONCRETE CALCUSAGES (expand_templates=True): {len(concrete_exp)}")
        for usage in concrete_exp:
            # Only print if not already printed in unexpanded concrete
            print(
                f"\n    Concrete: {usage.instance_name}"
                f" (calc_def={usage.calc_def_name},"
                f" qn={usage.qualified_name})"
            )
            for b in usage.bindings:
                fmt = classify_source_path(b.source_path, b.binding_type)
                literal_str = ""
                if b.literal_value is not None:
                    literal_str = f" literal={b.literal_value!r}"
                print(
                    f"      Binding: {b.param_name} | {b.binding_type.name} | "
                    f"source_path={b.source_path!r}{literal_str} | format={fmt}"
                )
                # Don't double-count concrete usages in summary

    return summary_rows


def main() -> None:
    print_section("SPIKE 1: Template Binding source_path Format")

    suites = DEFAULT_SUITES
    if len(sys.argv) > 1:
        paths = [Path(p) for p in sys.argv[1].split(",")]
        suites = [("cli_model", paths)]

    all_summary_rows: list[list[str]] = []

    for suite_name, model_paths in suites:
        rows = run_spike_for_model(suite_name, model_paths)
        all_summary_rows.extend(rows)

    # --- Summary ---
    print_section("SUMMARY: source_path Format Classification")

    if all_summary_rows:
        print_table(
            ["Model", "CalcUsage", "Param", "BindingType", "source_path", "Format"],
            all_summary_rows,
        )

    # Format distribution per model
    print_subsection("Format Distribution by Model")
    from collections import Counter
    models = sorted(set(r[0] for r in all_summary_rows))
    dist_rows = []
    for m in models:
        model_rows = [r for r in all_summary_rows if r[0] == m]
        counts = Counter(r[5] for r in model_rows)
        n_tpl = sum(1 for r in model_rows if r[1].startswith("TPL:"))
        n_virt = sum(1 for r in model_rows if r[1].startswith("VIRT:"))
        n_conc = sum(1 for r in model_rows if r[1].startswith("CONC:"))
        dist_rows.append([
            m, str(len(model_rows)),
            str(n_tpl), str(n_virt), str(n_conc),
            str(counts.get("BARE", 0)),
            str(counts.get("DOTTED", 0)),
            str(counts.get("SYSML_QN", 0)),
            str(counts.get("LITERAL", 0)),
            str(counts.get("EXPRESSION", 0)),
            str(counts.get("NONE", 0)),
        ])
    print_table(
        ["Model", "Total", "TPL", "VIRT", "CONC",
         "BARE", "DOTTED", "SYSML_QN", "LITERAL", "EXPR", "NONE"],
        dist_rows,
    )


if __name__ == "__main__":
    main()
