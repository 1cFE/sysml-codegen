#!/usr/bin/env python3
"""Spike Q1: AST Extraction Coverage.

For each CalcDef output attribute, report whether feature_value_expression exists,
its root node type, traversal depth, all node types encountered, and all operators.

Usage:
    uv run python scripts/spike_extract_expression_asts.py [model_path ...]
    (defaults to all 4 model suites if no args given)

Multi-directory models can be passed as comma-separated paths:
    uv run python scripts/spike_extract_expression_asts.py path/a,path/b
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

from agentic_mbse.sysml.expression import extract_operators, traverse_expression

from sysml_codegen.extraction.extractor import SysMLDataExtractor


# -- Data classes --

@dataclass
class OutputASTInfo:
    calc_name: str
    output_name: str
    has_expression: bool
    root_node_type: str = ""
    depth: int = 0
    node_types: list[str] = field(default_factory=list)
    operators: list[str] = field(default_factory=list)


# -- Helpers --

def sanitize_name(name: str | None) -> str:
    """Strip quotes, replace spaces (matches extractor._sanitize_name)."""
    if not name:
        return ""
    name = name.strip("'\"")
    name = name.replace(" ", "_")
    return name


def measure_depth(expr, depth: int = 0) -> int:
    """Measure max depth of expression AST via operands recursion."""
    if expr is None:
        return depth
    max_d = depth
    if hasattr(expr, "operands"):
        try:
            for operand in expr.operands:
                child_d = measure_depth(operand, depth + 1)
                if child_d > max_d:
                    max_d = child_d
        except (TypeError, AttributeError):
            pass
    return max_d


def collect_node_types(expr) -> list[str]:
    """Collect all node type names via traverse_expression."""
    return traverse_expression(expr, lambda node: type(node).__name__)


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


def analyze_calc_def(raw_elem, calc_def, adapter) -> list[OutputASTInfo]:
    """Analyze a single CalcDef's output attributes for AST info."""
    results = []
    output_names = {attr.name for attr in calc_def.output_attributes}

    for member in raw_elem.owned_members:
        if not adapter.is_instance(member, "AttributeUsage"):
            continue

        # Check direction
        is_output = False
        if hasattr(member, "direction"):
            direction_str = str(member.direction)
            if "Out" in direction_str or "Return" in direction_str:
                is_output = True

        if not is_output:
            continue

        member_name = sanitize_name(member.name)
        # Only analyze outputs that the structured extractor also found
        if member_name not in output_names:
            continue

        has_expr = (
            hasattr(member, "feature_value_expression")
            and member.feature_value_expression is not None
        )

        info = OutputASTInfo(
            calc_name=calc_def.name,
            output_name=member_name,
            has_expression=has_expr,
        )

        if has_expr:
            expr = member.feature_value_expression
            info.root_node_type = type(expr).__name__
            info.depth = measure_depth(expr)
            info.node_types = collect_node_types(expr)
            info.operators = extract_operators(expr)

        results.append(info)

    return results


# -- Suite definitions --
# Each suite is (label, [list of model paths]).
# Multi-directory models (e.g. CATF) list all directories needed for loading.

DEFAULT_SUITES: list[tuple[str, list[Path]]] = [
    ("chain_spike_model", [Path("tests/fixtures/chain_spike_model")]),
    ("sample_model", [Path("tests/fixtures/sample_model")]),
    ("solar_battery_model", [Path("tests/fixtures/solar_battery_model")]),
    ("catf_mfe", [
        Path("/home/reid/fusion_modeling/models/library"),
        Path("/home/reid/fusion_modeling/models/designs/catf_mfe"),
    ]),
]


def run_suite(label: str, model_paths: list[Path]) -> list[OutputASTInfo]:
    """Run analysis on a single model suite."""
    print(f"\n{'='*70}")
    print(f"Suite: {label}")
    paths_str = ", ".join(str(p) for p in model_paths)
    print(f"Paths: {paths_str}")
    print(f"{'='*70}")

    raw_elems, calc_defs, adapter = load_and_extract(model_paths)
    if adapter is None:
        return []

    # Build name -> calc_def lookup
    calc_def_by_name = {cd.name: cd for cd in calc_defs}

    all_results: list[OutputASTInfo] = []

    for raw_elem in raw_elems:
        name = sanitize_name(raw_elem.name)
        calc_def = calc_def_by_name.get(name)
        if calc_def is None:
            print(f"  WARN: Raw element '{name}' not found in structured extraction")
            continue
        results = analyze_calc_def(raw_elem, calc_def, adapter)
        all_results.extend(results)

    # Print table
    print(f"\n{'CalcDef':<30} {'Output':<25} {'HasAST':<8} {'RootType':<30} {'Depth':<6} {'Operators':<20} NodeTypes")
    print("-" * 150)
    for r in all_results:
        node_types_str = ", ".join(sorted(set(r.node_types))) if r.node_types else "-"
        ops_str = ", ".join(sorted(set(r.operators))) if r.operators else "-"
        print(
            f"{r.calc_name:<30} {r.output_name:<25} {str(r.has_expression):<8} "
            f"{r.root_node_type:<30} {r.depth:<6} {ops_str:<20} {node_types_str}"
        )

    return all_results


def main():
    if len(sys.argv) > 1:
        # CLI args: each arg is a path or comma-separated paths for multi-dir models
        suites = []
        for arg in sys.argv[1:]:
            paths = [Path(p.strip()) for p in arg.split(",")]
            label = paths[0].name if len(paths) == 1 else "+".join(p.name for p in paths)
            suites.append((label, paths))
    else:
        suites = DEFAULT_SUITES

    grand_total = 0
    grand_with_ast = 0
    all_node_types: set[str] = set()
    all_operators: set[str] = set()

    for label, model_paths in suites:
        results = run_suite(label, model_paths)
        total = len(results)
        with_ast = sum(1 for r in results if r.has_expression)
        grand_total += total
        grand_with_ast += with_ast
        for r in results:
            all_node_types.update(r.node_types)
            all_operators.update(r.operators)

        pct = (with_ast / total * 100) if total > 0 else 0
        print(f"\n  Suite summary: {with_ast}/{total} outputs have ASTs ({pct:.1f}%)")

    # Grand summary
    print(f"\n{'='*70}")
    print("GRAND SUMMARY")
    print(f"{'='*70}")
    pct = (grand_with_ast / grand_total * 100) if grand_total > 0 else 0
    print(f"Total outputs: {grand_total}")
    print(f"With AST:      {grand_with_ast} ({pct:.1f}%)")
    print(f"Without AST:   {grand_total - grand_with_ast}")
    print(f"\nNode type inventory ({len(all_node_types)} types):")
    for nt in sorted(all_node_types):
        print(f"  - {nt}")
    print(f"\nOperator inventory ({len(all_operators)} operators):")
    for op in sorted(all_operators):
        print(f"  - {op!r}")


if __name__ == "__main__":
    main()
