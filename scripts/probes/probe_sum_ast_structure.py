#!/usr/bin/env python3
"""Probe 1: Map the FULL nesting structure of sum() InvocationExpression nodes.

SysIDE wraps sum() operands in an InvocationExpression(function.name='Evaluation')
node that our code may not handle. This script finds ALL sum() InvocationExpression
nodes in the solar_battery model and recursively prints the EXACT nesting structure
down to the terminal FeatureChainExpression or FeatureReferenceExpression leaf.

Key question: What is the exact AST path from sum() to the actual feature reference?
Is it: sum -> Evaluation -> FeatureChainExpression?
Or:    sum -> collect -> Evaluation -> FeatureChainExpression?
Or:    sum -> FeatureChainExpression directly?

Usage:
    uv run python scripts/probes/probe_sum_ast_structure.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.syside_adapter import SysideAdapter
from sysml_codegen.extraction.extractor import SysMLDataExtractor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_attr(obj: Any, attr: str, default: Any = "<missing>") -> Any:
    """Safely access attribute, returning default if missing or error."""
    try:
        return getattr(obj, attr, default)
    except Exception:
        return default


def type_name(obj: Any) -> str:
    """Return type(obj).__name__ for AST node identification."""
    if obj is None or obj == "<missing>":
        return "<None>"
    return type(obj).__name__


def sanitize_name(name: str | None) -> str:
    """Strip quotes, replace spaces."""
    if not name:
        return ""
    name = name.strip("'\"")
    name = name.replace(" ", "_")
    return name


def print_node_detail(node: Any, indent: int = 0) -> None:
    """Print detailed information about a single AST node."""
    prefix = "  " * indent
    tn = type_name(node)
    name = safe_attr(node, "name", None)
    operator = safe_attr(node, "operator", None)

    info = f"{prefix}{tn}"
    if name not in (None, "<missing>"):
        info += f" name={name!r}"
    if operator not in (None, "<missing>"):
        info += f" operator={operator!r}"

    # For InvocationExpression, show function info
    func = safe_attr(node, "function", None)
    if func not in (None, "<missing>"):
        func_name = safe_attr(func, "name", None)
        if func_name not in (None, "<missing>"):
            info += f" function.name={func_name!r}"

    # For FeatureReferenceExpression, show referent
    referent = safe_attr(node, "referent", None)
    if referent not in (None, "<missing>"):
        ref_name = safe_attr(referent, "name", None)
        if ref_name not in (None, "<missing>"):
            info += f" referent.name={ref_name!r}"

    # For FeatureChainExpression, show target_feature
    target = safe_attr(node, "target_feature", None)
    if target not in (None, "<missing>"):
        target_name = safe_attr(target, "name", None)
        if target_name not in (None, "<missing>"):
            info += f" target_feature.name={target_name!r}"

    # For literals, show value
    value = safe_attr(node, "value", None)
    if value not in (None, "<missing>"):
        info += f" value={value!r}"

    print(info)


def walk_and_print(node: Any, indent: int = 0, max_depth: int = 10) -> None:
    """Recursively walk and print the full AST tree."""
    if node is None or indent > max_depth:
        return

    print_node_detail(node, indent)

    # Recurse into operands
    try:
        operands = list(getattr(node, "operands", []))
        if operands:
            for i, op in enumerate(operands):
                print(f"{'  ' * indent}  [operand {i}]:")
                walk_and_print(op, indent + 2, max_depth)
    except (TypeError, AttributeError):
        pass


def find_sum_invocations_in_expression(expr: Any, depth: int = 0) -> list[Any]:
    """Recursively find all sum() InvocationExpression nodes in an expression tree."""
    results = []
    if expr is None or depth > 15:
        return results

    # Check if this node is a sum() invocation
    func = safe_attr(expr, "function", None)
    if func not in (None, "<missing>"):
        func_name = safe_attr(func, "name", None)
        if func_name == "sum":
            results.append(expr)

    # Recurse into operands
    try:
        for op in getattr(expr, "operands", []):
            results.extend(find_sum_invocations_in_expression(op, depth + 1))
    except (TypeError, AttributeError):
        pass

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("Probe 1: sum() InvocationExpression AST Structure")
    print("=" * 70)

    model_path = Path(__file__).parent.parent.parent / "tests" / "fixtures" / "solar_battery_model"

    print(f"\nLoading model from: {model_path}")
    try:
        extractor = SysMLDataExtractor([model_path])
        if not extractor.load_models():
            print("  ERROR: load_models() returned False", file=sys.stderr)
            sys.exit(1)
        model = extractor.model
        adapter = extractor.adapter
        print("  Model loaded successfully")
    except Exception as e:
        print(f"  ERROR loading model: {e}", file=sys.stderr)
        sys.exit(1)

    # Strategy: Find PartDefinitions with EXPRESSION-type :>> redefinitions
    # that contain sum() calls. These are the assembly parts.
    sum_count = 0

    for part_def in SysideAdapter.elements_of_type(model, "PartDefinition"):
        part_name = sanitize_name(safe_attr(part_def, "name", ""))

        for member in getattr(part_def, "owned_members", []):
            if not SysideAdapter.is_instance(member, "ReferenceUsage"):
                continue

            owned_redefs = getattr(member, "owned_redefinitions", None)
            if not owned_redefs:
                continue

            expr = getattr(member, "feature_value_expression", None)
            if expr is None:
                continue

            # Search for sum() invocations in this expression
            sum_nodes = find_sum_invocations_in_expression(expr)
            if not sum_nodes:
                continue

            attr_name = sanitize_name(safe_attr(member, "name", ""))
            redef = list(owned_redefs)[0]
            redef_feature = safe_attr(redef, "redefined_feature", None)
            redef_name = safe_attr(redef_feature, "name", "?")

            print(f"\n{'=' * 60}")
            print(f"Part: {part_name}")
            print(f"Attribute: {attr_name} (redefines {redef_name})")
            print(f"sum() invocations found: {len(sum_nodes)}")
            print(f"{'=' * 60}")

            # Print the FULL expression tree for context
            print(f"\n--- Full expression tree ---")
            walk_and_print(expr, indent=1)

            # Inspect each sum() node in detail
            for i, sum_node in enumerate(sum_nodes):
                sum_count += 1
                print(f"\n--- sum() invocation [{i}] ---")
                print(f"  sum node type: {type_name(sum_node)}")
                func = safe_attr(sum_node, "function")
                print(f"  sum node function: {type_name(func)} name={safe_attr(func, 'name')!r}")

                try:
                    operands = list(sum_node.operands)
                    print(f"  sum node operand count: {len(operands)}")

                    for j, operand in enumerate(operands):
                        print(f"\n  sum operand [{j}]:")
                        print(f"    type: {type_name(operand)}")

                        # Check if operand is an InvocationExpression (wrapper)
                        op_func = safe_attr(operand, "function", None)
                        if op_func not in (None, "<missing>"):
                            op_func_name = safe_attr(op_func, "name", None)
                            print(f"    function.name: {op_func_name!r}")
                            print(f"    >>> This IS an InvocationExpression wrapper!")

                            # Recurse into wrapper operands
                            try:
                                wrapper_operands = list(operand.operands)
                                print(f"    wrapper operand count: {len(wrapper_operands)}")
                                for k, wop in enumerate(wrapper_operands):
                                    print(f"    wrapper operand [{k}]:")
                                    walk_and_print(wop, indent=4, max_depth=5)
                            except (TypeError, AttributeError):
                                print(f"    wrapper has no operands")
                        else:
                            # Direct feature reference (no wrapper)
                            print(f"    >>> This is NOT an InvocationExpression wrapper")
                            walk_and_print(operand, indent=3, max_depth=5)

                        # Try to extract the chain/reference name regardless
                        print(f"\n    Attempting name extraction:")
                        from sysml_codegen.extraction.expression_utils import (
                            extract_feature_chain_name,
                            extract_feature_reference_name,
                        )

                        if SysideAdapter.is_instance(operand, "FeatureChainExpression"):
                            name = extract_feature_chain_name(operand)
                            print(f"    => FeatureChainExpression: {name}")
                        elif SysideAdapter.is_instance(operand, "FeatureReferenceExpression"):
                            name = extract_feature_reference_name(operand)
                            print(f"    => FeatureReferenceExpression: {name}")
                        else:
                            print(f"    => Not a direct chain/ref, type={type_name(operand)}")
                            # Try unwrapping
                            from sysml_codegen.extraction.hierarchy_resolver import _unwrap_invocation
                            unwrapped = _unwrap_invocation(operand)
                            if unwrapped is not operand:
                                print(f"    => After _unwrap_invocation: {type_name(unwrapped)}")
                                if SysideAdapter.is_instance(unwrapped, "FeatureChainExpression"):
                                    name = extract_feature_chain_name(unwrapped)
                                    print(f"    => Unwrapped chain name: {name}")
                                elif SysideAdapter.is_instance(unwrapped, "FeatureReferenceExpression"):
                                    name = extract_feature_reference_name(unwrapped)
                                    print(f"    => Unwrapped ref name: {name}")
                                else:
                                    print(f"    => Unwrapped but still not chain/ref: {type_name(unwrapped)}")
                            else:
                                print(f"    => _unwrap_invocation returned same node (no wrapper found)")

                except (TypeError, AttributeError) as e:
                    print(f"  ERROR accessing operands: {e}")

    print(f"\n{'=' * 70}")
    print(f"SUMMARY: Found {sum_count} total sum() invocations across all PartDefs")
    print("=" * 70)

    if sum_count == 0:
        print("\nWARNING: No sum() invocations found!")
        print("Possible causes:")
        print("  - sum() may not produce InvocationExpression with function.name='sum'")
        print("  - The expression may be structured differently than expected")
        print("  - Try checking ALL InvocationExpression nodes in the model")

        # Fallback: find ALL InvocationExpression-like nodes
        print("\n--- Fallback: scanning ALL expressions for InvocationExpression ---")
        for part_def in SysideAdapter.elements_of_type(model, "PartDefinition"):
            part_name = sanitize_name(safe_attr(part_def, "name", ""))
            for member in getattr(part_def, "owned_members", []):
                expr = getattr(member, "feature_value_expression", None)
                if expr is None:
                    continue
                _scan_for_invocations(expr, part_name, sanitize_name(safe_attr(member, "name", "")))


def _scan_for_invocations(node: Any, part_name: str, attr_name: str, depth: int = 0) -> None:
    """Scan for any InvocationExpression-like nodes."""
    if node is None or depth > 10:
        return

    func = safe_attr(node, "function", None)
    if func not in (None, "<missing>"):
        func_name = safe_attr(func, "name", "<no name>")
        print(f"  {part_name}.{attr_name}: InvocationExpression function.name={func_name!r} at depth={depth}")
        print(f"    node type: {type_name(node)}")
        try:
            ops = list(node.operands)
            print(f"    operands: {len(ops)}")
            for i, op in enumerate(ops):
                print(f"      [{i}] {type_name(op)}")
        except (TypeError, AttributeError):
            pass

    try:
        for op in getattr(node, "operands", []):
            _scan_for_invocations(op, part_name, attr_name, depth + 1)
    except (TypeError, AttributeError):
        pass


if __name__ == "__main__":
    main()
