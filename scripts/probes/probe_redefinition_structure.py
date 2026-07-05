#!/usr/bin/env python3
"""Probe 2: Map :>> redefinition ReferenceUsage structure across all PartDefs.

For all PartDefinitions in solar_battery, finds ReferenceUsage members with
owned_redefinitions. Prints the complete structure including:
- The owning PartDef name
- The redefined feature name and chaining_features (deep-path)
- Whether feature_value_expression exists and its type
- The value if it's a literal
- The source_path if it's a chain/reference

Focus on finding two patterns:
1. :>> total_capex = capital_cost (ALIAS pattern)
2. :>> capital_cost = sum(...) (AGGREGATION pattern)

Usage:
    uv run python scripts/probes/probe_redefinition_structure.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.syside_adapter import SysideAdapter
from sysml_codegen.extraction.extractor import SysMLDataExtractor

from sysml_codegen.extraction.expression_utils import (
    extract_feature_chain_name,
    extract_feature_reference_name,
    is_literal_expression,
    extract_literal_value,
    reconstruct_expression,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_attr(obj: Any, attr: str, default: Any = "<missing>") -> Any:
    """Safely access attribute."""
    try:
        return getattr(obj, attr, default)
    except Exception:
        return default


def type_name(obj: Any) -> str:
    """Return type(obj).__name__."""
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


def classify_expression(expr: Any) -> str:
    """Classify a feature_value_expression into a human-readable category."""
    if expr is None:
        return "NONE"
    if is_literal_expression(expr):
        return f"LITERAL({extract_literal_value(expr)})"
    if SysideAdapter.is_instance(expr, "FeatureChainExpression"):
        return f"CHAIN({extract_feature_chain_name(expr)})"
    if SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
        return f"REFERENCE({extract_feature_reference_name(expr)})"
    if SysideAdapter.is_instance(expr, "OperatorExpression"):
        op = safe_attr(expr, "operator", "?")
        return f"OPERATOR({op})"
    func = safe_attr(expr, "function", None)
    if func not in (None, "<missing>"):
        func_name = safe_attr(func, "name", "?")
        return f"INVOCATION({func_name})"
    return f"UNKNOWN({type_name(expr)})"


def has_sum_invocation(node: Any, depth: int = 0) -> bool:
    """Check if expression tree contains a sum() invocation."""
    if node is None or depth > 10:
        return False
    func = safe_attr(node, "function", None)
    if func not in (None, "<missing>"):
        if safe_attr(func, "name", None) == "sum":
            return True
    try:
        for op in getattr(node, "operands", []):
            if has_sum_invocation(op, depth + 1):
                return True
    except (TypeError, AttributeError):
        pass
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("Probe 2: :>> Redefinition Structure on All PartDefs")
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

    total_redefs = 0
    alias_candidates = []
    aggregation_candidates = []

    for part_def in SysideAdapter.elements_of_type(model, "PartDefinition"):
        part_name = sanitize_name(safe_attr(part_def, "name", ""))

        # Collect all redefinitions on this PartDef
        redefs_on_part = []

        for member in getattr(part_def, "owned_members", []):
            if not SysideAdapter.is_instance(member, "ReferenceUsage"):
                continue

            owned_redefs = getattr(member, "owned_redefinitions", None)
            if not owned_redefs:
                continue

            owned_redefs_list = list(owned_redefs)
            if not owned_redefs_list:
                continue

            redef = owned_redefs_list[0]
            redefined_feature = safe_attr(redef, "redefined_feature", None)

            # Get chaining_features for deep-path detection
            chaining = []
            try:
                chaining = list(getattr(redefined_feature, "chaining_features", []))
            except (TypeError, AttributeError):
                pass

            if chaining:
                target_path = [sanitize_name(safe_attr(c, "name", "?")) for c in chaining]
                attr_name = target_path[-1]
                is_deep_path = True
            else:
                attr_name = sanitize_name(safe_attr(redefined_feature, "name", None)) or \
                            sanitize_name(safe_attr(member, "name", None))
                target_path = []
                is_deep_path = False

            expr = getattr(member, "feature_value_expression", None)
            expr_class = classify_expression(expr)

            # Check for sum() in expression
            contains_sum = has_sum_invocation(expr) if expr else False

            # Try to reconstruct expression text
            expr_text = ""
            if expr is not None:
                try:
                    expr_text = reconstruct_expression(expr)
                except Exception:
                    expr_text = "<reconstruction failed>"

            redef_info = {
                "part_name": part_name,
                "attr_name": attr_name,
                "member_name": sanitize_name(safe_attr(member, "name", "")),
                "member_type": type_name(member),
                "redef_feature_name": sanitize_name(safe_attr(redefined_feature, "name", "")),
                "redef_feature_type": type_name(redefined_feature),
                "chaining": target_path,
                "is_deep_path": is_deep_path,
                "expr_type": type_name(expr),
                "expr_class": expr_class,
                "expr_text": expr_text,
                "contains_sum": contains_sum,
            }

            redefs_on_part.append(redef_info)
            total_redefs += 1

            # Classify for special patterns
            if expr_class.startswith("CHAIN(") or expr_class.startswith("REFERENCE("):
                alias_candidates.append(redef_info)
            if contains_sum:
                aggregation_candidates.append(redef_info)

        # Print per-PartDef summary
        if redefs_on_part:
            print(f"\n{'=' * 60}")
            print(f"PartDef: {part_name} ({len(redefs_on_part)} redefinitions)")
            print(f"{'=' * 60}")

            for r in redefs_on_part:
                deep_marker = " [DEEP-PATH]" if r["is_deep_path"] else ""
                sum_marker = " [HAS SUM()]" if r["contains_sum"] else ""
                print(f"\n  :>> {r['attr_name']}{deep_marker}{sum_marker}")
                print(f"    member: {r['member_type']} name={r['member_name']!r}")
                print(f"    redefined_feature: {r['redef_feature_type']} name={r['redef_feature_name']!r}")
                if r["is_deep_path"]:
                    print(f"    chaining_features: {r['chaining']}")
                print(f"    expression type: {r['expr_type']}")
                print(f"    classification: {r['expr_class']}")
                if r["expr_text"]:
                    # Truncate long expressions
                    display = r["expr_text"][:100]
                    if len(r["expr_text"]) > 100:
                        display += "..."
                    print(f"    reconstructed: {display}")

    # Summary section
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"Total :>> redefinitions found: {total_redefs}")

    # Alias pattern analysis
    print(f"\n--- ALIAS candidates (CHAIN/REFERENCE expressions) ---")
    print(f"Count: {len(alias_candidates)}")
    for ac in alias_candidates:
        print(f"  {ac['part_name']}.{ac['attr_name']} => {ac['expr_class']}")

    # Look specifically for the pattern where attr_name != source_path
    # e.g., :>> total_capex = capital_cost
    print(f"\n--- Potential ALIAS rewrites (attr != source) ---")
    for ac in alias_candidates:
        source = ac["expr_class"]
        # Extract the source name from the classification
        if source.startswith("CHAIN("):
            source_name = source[6:-1]
        elif source.startswith("REFERENCE("):
            source_name = source[10:-1]
        else:
            continue
        if ac["attr_name"] != source_name:
            print(f"  {ac['part_name']}: :>> {ac['attr_name']} = {source_name}")
            print(f"    => '{ac['attr_name']}' is an ALIAS for '{source_name}'")

    # Aggregation pattern analysis
    print(f"\n--- AGGREGATION candidates (contain sum()) ---")
    print(f"Count: {len(aggregation_candidates)}")
    for ag in aggregation_candidates:
        display = ag["expr_text"][:80] if ag["expr_text"] else "<no text>"
        print(f"  {ag['part_name']}.{ag['attr_name']}: {display}")

    # Also scan design PartUsages for deep-path overrides
    print(f"\n{'=' * 70}")
    print("Design PartUsage :>> Overrides (deep-path)")
    print(f"{'=' * 70}")

    design_redef_count = 0
    for usage in SysideAdapter.elements_of_type(model, "PartUsage"):
        usage_name = sanitize_name(safe_attr(usage, "name", ""))
        owned_redefs = getattr(usage, "owned_redefinitions", None)
        if not owned_redefs or not list(owned_redefs):
            continue

        # This is a "part redefines" usage
        members_with_redefs = []
        for member in getattr(usage, "owned_members", []):
            if not SysideAdapter.is_instance(member, "ReferenceUsage"):
                continue
            mr = getattr(member, "owned_redefinitions", None)
            if not mr or not list(mr):
                continue
            members_with_redefs.append(member)

        if members_with_redefs:
            print(f"\n  PartUsage: {usage_name} (part redefines)")
            for member in members_with_redefs:
                design_redef_count += 1
                redef = list(member.owned_redefinitions)[0]
                rf = safe_attr(redef, "redefined_feature", None)
                chaining = []
                try:
                    chaining = list(getattr(rf, "chaining_features", []))
                except (TypeError, AttributeError):
                    pass

                if chaining:
                    chain_names = [sanitize_name(safe_attr(c, "name", "?")) for c in chaining]
                    path_str = ".".join(chain_names)
                else:
                    path_str = sanitize_name(safe_attr(rf, "name", "?"))

                expr = getattr(member, "feature_value_expression", None)
                expr_class = classify_expression(expr)

                print(f"    :>> {path_str} = {expr_class}")

    print(f"\n  Total design :>> overrides: {design_redef_count}")


if __name__ == "__main__":
    main()
