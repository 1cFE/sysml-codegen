#!/usr/bin/env python3
"""Spike Q2: Expression Reference Resolution Rate.

For each output attribute with an AST, extract feature refs and classify each as
input, intermediate (sibling output), or unresolvable. Cross-check against
independent AST node count. Report std_lib filtered ref counts explicitly.

Usage:
    uv run python scripts/spike_resolve_expression_refs.py [model_path ...]
    (defaults to all 4 model suites if no args given)

Multi-directory models can be passed as comma-separated paths:
    uv run python scripts/spike_resolve_expression_refs.py path/a,path/b
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

from agentic_mbse.sysml.expression import extract_feature_refs, traverse_expression

from sysml_codegen.extraction.extractor import SysMLDataExtractor


# -- Data classes --

@dataclass
class RefClassification:
    name: str
    qualified_name: str
    category: str  # "input", "intermediate", "unresolvable"


@dataclass
class OutputRefInfo:
    calc_name: str
    output_name: str
    refs: list[RefClassification] = field(default_factory=list)
    ref_node_count: int = 0  # independent AST count
    extract_count_all: int = 0  # extract_feature_refs(ignore_std_lib=False)
    extract_count_filtered: int = 0  # extract_feature_refs(ignore_std_lib=True)


# -- Helpers --

def sanitize_name(name: str | None) -> str:
    """Strip quotes, replace spaces (matches extractor._sanitize_name)."""
    if not name:
        return ""
    name = name.strip("'\"")
    name = name.replace(" ", "_")
    return name


def count_ref_nodes(expr) -> int:
    """Count FeatureReferenceExpression and FeatureChainExpression nodes in AST."""
    def visitor(node):
        type_name = type(node).__name__
        if "FeatureReference" in type_name or "FeatureChain" in type_name:
            return True
        return None
    return len(traverse_expression(expr, visitor))


def classify_ref(ref, input_names: set[str], output_names: set[str]) -> str:
    """Classify a ref as input, intermediate, or unresolvable."""
    if ref.name in input_names:
        return "input"
    if ref.name in output_names:
        return "intermediate"
    return "unresolvable"


def load_and_extract(model_paths: list[Path]):
    """Load model from one or more directories, return (raw_elements, calc_defs, adapter)."""
    extractor = SysMLDataExtractor(model_paths)
    if not extractor.load_models():
        label = ", ".join(str(p) for p in model_paths)
        print(f"  ERROR: Failed to load models from {label}", file=sys.stderr)
        return [], [], None
    calc_defs = extractor.extract_calculation_definitions()
    raw_elems = list(extractor.adapter.elements_of_type(extractor.model, "CalculationDefinition"))
    return raw_elems, calc_defs, extractor.adapter


def analyze_calc_def_refs(raw_elem, calc_def, adapter) -> list[OutputRefInfo]:
    """Analyze a single CalcDef's output expressions for ref resolution."""
    results = []
    input_names = {attr.name for attr in calc_def.input_attributes}
    output_names = {attr.name for attr in calc_def.output_attributes}

    for member in raw_elem.owned_members:
        if not adapter.is_instance(member, "AttributeUsage"):
            continue

        is_output = False
        if hasattr(member, "direction"):
            direction_str = str(member.direction)
            if "Out" in direction_str or "Return" in direction_str:
                is_output = True

        if not is_output:
            continue

        member_name = sanitize_name(member.name)
        if member_name not in output_names:
            continue

        has_expr = (
            hasattr(member, "feature_value_expression")
            and member.feature_value_expression is not None
        )

        if not has_expr:
            continue

        expr = member.feature_value_expression

        # Extract refs both ways
        refs_filtered = extract_feature_refs(expr, ignore_std_lib=True)
        refs_all = extract_feature_refs(expr, ignore_std_lib=False)
        node_count = count_ref_nodes(expr)

        info = OutputRefInfo(
            calc_name=calc_def.name,
            output_name=member_name,
            ref_node_count=node_count,
            extract_count_all=len(refs_all),
            extract_count_filtered=len(refs_filtered),
        )

        for ref in refs_filtered:
            category = classify_ref(ref, input_names, output_names)
            info.refs.append(RefClassification(
                name=ref.name,
                qualified_name=ref.qualified_name,
                category=category,
            ))

        results.append(info)

    return results


# -- Suite definitions --

DEFAULT_SUITES: list[tuple[str, list[Path]]] = [
    ("chain_spike_model", [Path("tests/fixtures/chain_spike_model")]),
    ("sample_model", [Path("tests/fixtures/sample_model")]),
    ("solar_battery_model", [Path("tests/fixtures/solar_battery_model")]),
    ("catf_mfe", [
        Path("/home/reid/fusion_modeling/models/library"),
        Path("/home/reid/fusion_modeling/models/designs/catf_mfe"),
    ]),
]


def run_suite(label: str, model_paths: list[Path]) -> list[OutputRefInfo]:
    """Run ref resolution analysis on a single model suite."""
    print(f"\n{'='*70}")
    print(f"Suite: {label}")
    paths_str = ", ".join(str(p) for p in model_paths)
    print(f"Paths: {paths_str}")
    print(f"{'='*70}")

    raw_elems, calc_defs, adapter = load_and_extract(model_paths)
    if adapter is None:
        return []

    calc_def_by_name = {cd.name: cd for cd in calc_defs}
    all_results: list[OutputRefInfo] = []

    for raw_elem in raw_elems:
        name = sanitize_name(raw_elem.name)
        calc_def = calc_def_by_name.get(name)
        if calc_def is None:
            print(f"  WARN: Raw element '{name}' not found in structured extraction")
            continue
        results = analyze_calc_def_refs(raw_elem, calc_def, adapter)
        all_results.extend(results)

    # Print per-output ref table
    print(f"\n{'CalcDef':<30} {'Output':<20} {'Ref':<20} {'QualName':<40} {'Category':<15}")
    print("-" * 130)
    for r in all_results:
        if not r.refs:
            print(f"{r.calc_name:<30} {r.output_name:<20} {'(no refs)':<20} {'':<40} {'literal':<15}")
        else:
            for i, ref in enumerate(r.refs):
                calc_col = r.calc_name if i == 0 else ""
                out_col = r.output_name if i == 0 else ""
                qn_display = ref.qualified_name[:38] if ref.qualified_name else ""
                print(f"{calc_col:<30} {out_col:<20} {ref.name:<20} {qn_display:<40} {ref.category:<15}")

    # Cross-check table (includes std_lib transparency -- issue #4)
    print(f"\n--- Cross-check: AST node count vs extract_feature_refs ---")
    print(f"{'CalcDef':<30} {'Output':<20} {'ASTNodes':<10} {'ExtractAll':<12} {'ExtractFilt':<12} {'StdLibDrop':<11} {'Mismatch?':<10}")
    print("-" * 110)
    mismatches = 0
    stdlib_drops = 0
    for r in all_results:
        mismatch = r.ref_node_count != r.extract_count_all
        if mismatch:
            mismatches += 1
        dropped = r.extract_count_all - r.extract_count_filtered
        if dropped > 0:
            stdlib_drops += dropped
        flag = "YES" if mismatch else ""
        print(
            f"{r.calc_name:<30} {r.output_name:<20} {r.ref_node_count:<10} "
            f"{r.extract_count_all:<12} {r.extract_count_filtered:<12} {dropped:<11} {flag:<10}"
        )

    return all_results


def main():
    if len(sys.argv) > 1:
        suites = []
        for arg in sys.argv[1:]:
            paths = [Path(p.strip()) for p in arg.split(",")]
            label = paths[0].name if len(paths) == 1 else "+".join(p.name for p in paths)
            suites.append((label, paths))
    else:
        suites = DEFAULT_SUITES

    grand_total_refs = 0
    grand_input = 0
    grand_intermediate = 0
    grand_unresolvable = 0
    grand_mismatches = 0
    grand_stdlib_drops = 0

    for label, model_paths in suites:
        results = run_suite(label, model_paths)

        total_refs = sum(len(r.refs) for r in results)
        input_count = sum(1 for r in results for ref in r.refs if ref.category == "input")
        intermediate_count = sum(1 for r in results for ref in r.refs if ref.category == "intermediate")
        unresolvable_count = sum(1 for r in results for ref in r.refs if ref.category == "unresolvable")
        mismatch_count = sum(1 for r in results if r.ref_node_count != r.extract_count_all)
        stdlib_count = sum(r.extract_count_all - r.extract_count_filtered for r in results)

        grand_total_refs += total_refs
        grand_input += input_count
        grand_intermediate += intermediate_count
        grand_unresolvable += unresolvable_count
        grand_mismatches += mismatch_count
        grand_stdlib_drops += stdlib_count

        resolved = input_count + intermediate_count
        pct = (resolved / total_refs * 100) if total_refs > 0 else 100.0
        print(f"\n  Suite summary: {resolved}/{total_refs} refs resolved ({pct:.1f}%)")
        print(f"    input: {input_count}, intermediate: {intermediate_count}, unresolvable: {unresolvable_count}")
        print(f"    cross-check mismatches: {mismatch_count}")
        print(f"    std_lib refs filtered: {stdlib_count}")

    # Grand summary
    print(f"\n{'='*70}")
    print("GRAND SUMMARY")
    print(f"{'='*70}")
    grand_resolved = grand_input + grand_intermediate
    pct = (grand_resolved / grand_total_refs * 100) if grand_total_refs > 0 else 100.0
    print(f"Total refs (filtered): {grand_total_refs}")
    print(f"Resolved:              {grand_resolved} ({pct:.1f}%)")
    print(f"  - input:             {grand_input}")
    print(f"  - intermediate:      {grand_intermediate}")
    print(f"  - unresolvable:      {grand_unresolvable}")
    print(f"Cross-check mismatches: {grand_mismatches}")
    print(f"Std_lib refs filtered: {grand_stdlib_drops}")
    if grand_stdlib_drops > 0:
        print(f"  (These are SI::, ISQ::, ScalarValues::, UnitsAndScales:: refs removed by ignore_std_lib=True)")


if __name__ == "__main__":
    main()
