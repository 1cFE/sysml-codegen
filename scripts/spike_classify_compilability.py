#!/usr/bin/env python3
"""Spike Q4: Compilability Classification & Cross-Reference.

Classifies every CalcDef across all model suites as FULLY_COMPILABLE,
PARTIALLY_COMPILABLE, or MANUAL_REQUIRED. Cross-references against Q3
compilation results to verify zero false positives.

Usage:
    uv run python scripts/spike_classify_compilability.py [model_path ...]
    (defaults to all 4 model suites if no args given)
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.expression import extract_feature_refs
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.extraction.extractor import SysMLDataExtractor

# Reuse infrastructure from Q3 script
from spike_compile_expressions import (
    compile_expression,
    sanitize_name,
    load_and_extract,
    get_all_member_names,
    get_output_expression,
    build_dependency_graph,
    topological_sort,
    compile_calc_def_body,
    generate_test_inputs,
    compare_compiled_vs_handwritten,
    HANDWRITTEN_IMPL_DIR,
)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class OutputClassification:
    output_name: str
    verdict: str  # "compilable" or "not_compilable"
    reason: str | None = None
    compiled_expression: str | None = None


@dataclass
class CalcDefClassification:
    calc_name: str
    suite: str
    verdict: str  # FULLY_COMPILABLE, PARTIALLY_COMPILABLE, MANUAL_REQUIRED
    reason: str | None = None
    output_details: list[OutputClassification] = field(default_factory=list)
    outputs_compilable: int = 0
    outputs_total: int = 0
    # Q3 cross-reference
    q3_body_valid: bool | None = None
    q3_all_outputs_ast_pass: bool | None = None
    cross_ref_ok: bool | None = None
    false_positive: bool = False


# ---------------------------------------------------------------------------
# Classification logic
# ---------------------------------------------------------------------------

def classify_output(
    output_name: str,
    raw_elem: Any,
    calc_def: Any,
    adapter: Any,
) -> OutputClassification:
    """Classify a single output attribute's compilability."""
    input_names = {attr.name for attr in calc_def.input_attributes}
    output_names = {attr.name for attr in calc_def.output_attributes}
    all_member_names = get_all_member_names(raw_elem)

    # Step 1: Check if expression AST exists
    expr = get_output_expression(raw_elem, output_name, adapter)
    if expr is None:
        return OutputClassification(
            output_name=output_name,
            verdict="not_compilable",
            reason="missing expression AST",
        )

    # Step 2: Check if all refs resolve
    refs = extract_feature_refs(expr, ignore_std_lib=True)
    for ref in refs:
        ref_name = sanitize_name(ref.name)
        if ref_name not in input_names and ref_name not in output_names:
            # Check extended resolution (undeclared intermediates)
            if ref_name not in all_member_names:
                return OutputClassification(
                    output_name=output_name,
                    verdict="not_compilable",
                    reason=f"unresolvable ref: {ref_name}",
                )

    # Step 3: Try to compile and validate syntax
    context: dict = {
        "node_types": [],
        "literal_value_type": None,
        "has_unary_negation": False,
        "undeclared_intermediates": [],
    }
    compiled = compile_expression(expr, input_names, output_names, all_member_names, context)

    if "UNRESOLVED_" in compiled or "UNSUPPORTED_" in compiled or "UNKNOWN_" in compiled:
        return OutputClassification(
            output_name=output_name,
            verdict="not_compilable",
            reason=f"compilation produced unresolvable token: {compiled[:80]}",
        )

    # Step 4: Validate syntax
    try:
        ast.parse(compiled, mode="eval")
    except SyntaxError as e:
        return OutputClassification(
            output_name=output_name,
            verdict="not_compilable",
            reason=f"syntax error: {e}",
            compiled_expression=compiled,
        )

    return OutputClassification(
        output_name=output_name,
        verdict="compilable",
        compiled_expression=compiled,
    )


def classify_calc_def(
    calc_def: Any,
    raw_elem: Any,
    adapter: Any,
    suite: str,
) -> CalcDefClassification:
    """Classify an entire CalcDef's compilability."""
    output_details: list[OutputClassification] = []

    for attr in calc_def.output_attributes:
        oc = classify_output(attr.name, raw_elem, calc_def, adapter)
        output_details.append(oc)

    compilable_count = sum(1 for o in output_details if o.verdict == "compilable")
    total = len(output_details)

    if compilable_count == total and total > 0:
        # Also check for circular dependencies and undeclared intermediates
        dep_graph, expr_map, undeclared_set = build_dependency_graph(calc_def, raw_elem, adapter)
        order = topological_sort(dep_graph)
        if order is None:
            verdict = "MANUAL_REQUIRED"
            reason = "circular dependency among outputs"
        else:
            # Check that every undeclared intermediate has a compilable expression
            uncompilable_undeclared: list[str] = []
            for ui_name in undeclared_set:
                ui_expr = expr_map.get(ui_name)
                if ui_expr is None:
                    uncompilable_undeclared.append(f"{ui_name}: no expression AST")
                else:
                    input_names = {attr.name for attr in calc_def.input_attributes}
                    output_names = {attr.name for attr in calc_def.output_attributes}
                    all_member_names = get_all_member_names(raw_elem)
                    ctx: dict = {
                        "node_types": [], "literal_value_type": None,
                        "has_unary_negation": False, "undeclared_intermediates": [],
                    }
                    compiled = compile_expression(
                        ui_expr, input_names, output_names, all_member_names, ctx,
                    )
                    if "UNRESOLVED_" in compiled or "UNSUPPORTED_" in compiled or "UNKNOWN_" in compiled:
                        uncompilable_undeclared.append(f"{ui_name}: unresolvable refs in expression")
                    else:
                        try:
                            ast.parse(compiled, mode="eval")
                        except SyntaxError:
                            uncompilable_undeclared.append(f"{ui_name}: syntax error")

            if uncompilable_undeclared:
                verdict = "PARTIALLY_COMPILABLE"
                reason = "undeclared intermediates not compilable: " + "; ".join(uncompilable_undeclared)
            else:
                verdict = "FULLY_COMPILABLE"
                reason = None
    elif compilable_count > 0:
        verdict = "PARTIALLY_COMPILABLE"
        not_compilable = [o for o in output_details if o.verdict != "compilable"]
        reasons = [f"{o.output_name}: {o.reason}" for o in not_compilable]
        reason = "; ".join(reasons)
    else:
        verdict = "MANUAL_REQUIRED"
        reasons = [f"{o.output_name}: {o.reason}" for o in output_details if o.reason]
        reason = "; ".join(reasons) if reasons else "no compilable outputs"

    return CalcDefClassification(
        calc_name=calc_def.name,
        suite=suite,
        verdict=verdict,
        reason=reason,
        output_details=output_details,
        outputs_compilable=compilable_count,
        outputs_total=total,
    )


def cross_reference_q3(
    classifications: list[CalcDefClassification],
    q3_results: dict[str, dict],
) -> list[str]:
    """Cross-reference Q4 classifications against Q3 compilation results.

    For FULLY_COMPILABLE CalcDefs, verifies:
    1. Full body passes ast.parse() (syntax)
    2. All output expressions pass ast.parse() (syntax)
    3. Where ground truth exists, numerical comparison matches (semantic)

    Returns list of false positive CalcDef names (should be empty).
    """
    false_positives: list[str] = []

    for cls in classifications:
        key = f"{cls.suite}::{cls.calc_name}"
        q3 = q3_results.get(key)

        if q3 is None:
            cls.cross_ref_ok = None  # no Q3 data
            continue

        cls.q3_body_valid = q3["body_valid"]
        cls.q3_all_outputs_ast_pass = q3["all_ast_pass"]

        if cls.verdict == "FULLY_COMPILABLE":
            # Must have passed Q3 syntax checks
            if not q3["body_valid"] or not q3["all_ast_pass"]:
                cls.false_positive = True
                cls.cross_ref_ok = False
                false_positives.append(cls.calc_name)
            # If ground truth exists, must also match numerically
            elif q3.get("ground_truth_match") is False:
                cls.false_positive = True
                cls.cross_ref_ok = False
                false_positives.append(cls.calc_name)
            else:
                cls.cross_ref_ok = True
        else:
            cls.cross_ref_ok = True  # non-FULLY verdicts can't be false positives

    return false_positives


# ---------------------------------------------------------------------------
# Suite runner
# ---------------------------------------------------------------------------

DEFAULT_SUITES: list[tuple[str, list[Path]]] = [
    ("chain_spike_model", [Path("tests/fixtures/chain_spike_model")]),
    ("sample_model", [Path("tests/fixtures/sample_model")]),
    ("solar_battery_model", [Path("tests/fixtures/solar_battery_model")]),
    ("catf_mfe", [
        Path("/home/reid/fusion_modeling/models/library"),
        Path("/home/reid/fusion_modeling/models/designs/catf_mfe"),
    ]),
]


def run_suite(
    label: str,
    model_paths: list[Path],
) -> tuple[list[CalcDefClassification], dict[str, dict]]:
    """Run classification and Q3 compilation on a single model suite.

    Returns (classifications, q3_results_dict).
    """
    print(f"\n{'='*70}")
    print(f"Suite: {label}")
    paths_str = ", ".join(str(p) for p in model_paths)
    print(f"Paths: {paths_str}")
    print(f"{'='*70}")

    raw_elems, calc_defs, adapter = load_and_extract(model_paths)
    if adapter is None:
        return [], {}

    calc_def_by_name = {cd.name: cd for cd in calc_defs}
    classifications: list[CalcDefClassification] = []
    q3_results: dict[str, dict] = {}

    for raw_elem in raw_elems:
        name = sanitize_name(raw_elem.name)
        calc_def = calc_def_by_name.get(name)
        if calc_def is None:
            continue

        # Q4: classify
        cls = classify_calc_def(calc_def, raw_elem, adapter, label)
        classifications.append(cls)

        # Q3: compile (for cross-reference)
        body, exec_order, output_results, undeclared = compile_calc_def_body(
            calc_def, raw_elem, adapter,
        )
        body_valid = body is not None
        if body_valid:
            import textwrap
            func_code = f"def run(inputs):\n{textwrap.indent(body, '    ')}"
            try:
                ast.parse(func_code)
            except SyntaxError:
                body_valid = False

        all_ast_pass = all(o.ast_valid for o in output_results)

        # Ground truth comparison for solar_battery
        ground_truth_match: bool | None = None  # None = no ground truth available
        if label == "solar_battery_model" and body is not None and exec_order is not None and HANDWRITTEN_IMPL_DIR.exists():
            impl_name = name.lower() + "_impl.py"
            impl_path = HANDWRITTEN_IMPL_DIR / impl_name
            if impl_path.exists():
                input_dict = generate_test_inputs(calc_def)
                # Only use declared output names for return value comparison
                output_names_ordered = [n for n in exec_order if n in {a.name for a in calc_def.output_attributes}]
                cr = compare_compiled_vs_handwritten(
                    calc_def, body, impl_path, input_dict, output_names_ordered,
                )
                if cr.status == "MATCH":
                    ground_truth_match = True
                elif cr.status == "MISMATCH":
                    ground_truth_match = False
                # STUB/EXCLUDED/ERROR -> None (no ground truth available)

        key = f"{label}::{name}"
        q3_results[key] = {
            "body_valid": body_valid,
            "all_ast_pass": all_ast_pass,
            "output_count": len(output_results),
            "valid_count": sum(1 for o in output_results if o.ast_valid),
            "ground_truth_match": ground_truth_match,
        }

    return classifications, q3_results


def main():
    args = [a for a in sys.argv[1:]]

    if args:
        suites = []
        for arg in args:
            paths = [Path(p.strip()) for p in arg.split(",")]
            label = paths[0].name if len(paths) == 1 else "+".join(p.name for p in paths)
            suites.append((label, paths))
    else:
        suites = DEFAULT_SUITES

    all_classifications: list[CalcDefClassification] = []
    all_q3_results: dict[str, dict] = {}

    for label, model_paths in suites:
        classifications, q3_results = run_suite(label, model_paths)
        all_classifications.extend(classifications)
        all_q3_results.update(q3_results)

    # Cross-reference Q4 vs Q3
    false_positives = cross_reference_q3(all_classifications, all_q3_results)

    # --- Print Results ---

    # Per-CalcDef classification table
    print(f"\n{'='*70}")
    print("CLASSIFICATION RESULTS")
    print(f"{'='*70}")
    print(
        f"{'Suite':<20} {'CalcDef':<30} {'Verdict':<22} "
        f"{'Compilable':<12} {'CrossRef':<10} {'Reason':<40}"
    )
    print("-" * 140)
    for cls in all_classifications:
        comp_str = f"{cls.outputs_compilable}/{cls.outputs_total}"
        xref_str = ""
        if cls.cross_ref_ok is True:
            xref_str = "OK"
        elif cls.cross_ref_ok is False:
            xref_str = "FAIL!"
        elif cls.cross_ref_ok is None:
            xref_str = "-"
        reason_str = (cls.reason[:38] + "..") if cls.reason and len(cls.reason) > 40 else (cls.reason or "")
        print(
            f"{cls.suite:<20} {cls.calc_name:<30} {cls.verdict:<22} "
            f"{comp_str:<12} {xref_str:<10} {reason_str:<40}"
        )

    # Summary counts per suite
    print(f"\n--- Summary by Suite ---")
    print(f"{'Suite':<20} {'Total':<8} {'FULLY':<8} {'PARTIAL':<10} {'MANUAL':<10}")
    print("-" * 60)

    suite_names = sorted(set(c.suite for c in all_classifications))
    for suite in suite_names:
        suite_cls = [c for c in all_classifications if c.suite == suite]
        total = len(suite_cls)
        fully = sum(1 for c in suite_cls if c.verdict == "FULLY_COMPILABLE")
        partial = sum(1 for c in suite_cls if c.verdict == "PARTIALLY_COMPILABLE")
        manual = sum(1 for c in suite_cls if c.verdict == "MANUAL_REQUIRED")
        print(f"{suite:<20} {total:<8} {fully:<8} {partial:<10} {manual:<10}")

    # Grand totals
    total = len(all_classifications)
    fully = sum(1 for c in all_classifications if c.verdict == "FULLY_COMPILABLE")
    partial = sum(1 for c in all_classifications if c.verdict == "PARTIALLY_COMPILABLE")
    manual = sum(1 for c in all_classifications if c.verdict == "MANUAL_REQUIRED")
    print(f"{'TOTAL':<20} {total:<8} {fully:<8} {partial:<10} {manual:<10}")

    # Cross-reference summary
    print(f"\n--- Cross-Reference Summary ---")
    xref_count = sum(1 for c in all_classifications if c.cross_ref_ok is not None)
    xref_pass = sum(1 for c in all_classifications if c.cross_ref_ok is True)
    xref_fail = sum(1 for c in all_classifications if c.cross_ref_ok is False)

    # Count semantic (ground truth) vs syntax-only validations
    fully_cls = [c for c in all_classifications if c.verdict == "FULLY_COMPILABLE"]
    semantic_count = sum(
        1 for c in fully_cls
        if all_q3_results.get(f"{c.suite}::{c.calc_name}", {}).get("ground_truth_match") is True
    )
    syntax_only = len(fully_cls) - semantic_count

    print(f"Cross-referenced: {xref_count}")
    print(f"Passed: {xref_pass}")
    print(f"Failed (false positives): {xref_fail}")
    print(f"\nFULLY_COMPILABLE validation breakdown:")
    print(f"  Semantic (ground truth match): {semantic_count}")
    print(f"  Syntax-only (no ground truth): {syntax_only}")

    if false_positives:
        print(f"\nFALSE POSITIVES ({len(false_positives)}):")
        for fp in false_positives:
            print(f"  - {fp}")
        print("\nWARNING: False positives found! Classifier is NOT safe.")
    else:
        print(f"\nZero false positives confirmed.")

    # False negative inventory
    print(f"\n--- False Negative Inventory ---")
    print("(MANUAL_REQUIRED CalcDefs that have some compilable outputs)")
    fn_count = 0
    for cls in all_classifications:
        if cls.verdict == "MANUAL_REQUIRED" and cls.outputs_compilable > 0:
            fn_count += 1
            print(
                f"  {cls.calc_name} ({cls.suite}): "
                f"{cls.outputs_compilable}/{cls.outputs_total} outputs compilable"
            )
    if fn_count == 0:
        print("  (none)")

    # Per-output details for non-FULLY CalcDefs
    print(f"\n--- Non-FULLY_COMPILABLE Output Details ---")
    for cls in all_classifications:
        if cls.verdict != "FULLY_COMPILABLE":
            print(f"\n  {cls.calc_name} ({cls.suite}) -- {cls.verdict}:")
            for od in cls.output_details:
                status = "OK" if od.verdict == "compilable" else "FAIL"
                reason = od.reason or ""
                expr = od.compiled_expression or ""
                if len(expr) > 40:
                    expr = expr[:37] + "..."
                print(f"    {od.output_name:<25} {status:<6} {reason:<35} {expr}")


if __name__ == "__main__":
    main()
