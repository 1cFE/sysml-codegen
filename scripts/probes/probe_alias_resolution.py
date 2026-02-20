#!/usr/bin/env python3
"""Probe 3: Verify alias resolution for Solar Battery Plant redefinitions.

Specifically investigates:
1. :>> total_capex = capital_cost -- should create an ALIAS from total_capex to capital_cost
2. How total_capex is named vs how capital_cost is named in the AST
3. Whether the aliases list gets populated in our hierarchy_resolver.py

The critical issue: In design.sysml, the annualized_financial calc usage binds
`in total_capex = capital_cost`. The :>> redefinition on Solar Battery Plant
creates `:>> capital_cost = solar_array.capital_cost + ...`. If the alias
`total_capex -> capital_cost` is not correctly resolved, the pipeline will
have a broken wiring.

Usage:
    uv run python scripts/probes/probe_alias_resolution.py
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


# ---------------------------------------------------------------------------
# Part 1: Raw AST Analysis
# ---------------------------------------------------------------------------

def analyze_raw_ast(model: Any) -> None:
    """Examine the raw AST for alias-related redefinitions on Solar Battery Plant."""
    print("\n" + "=" * 70)
    print("Part 1: Raw AST Analysis -- Solar Battery Plant Redefinitions")
    print("=" * 70)

    # Find Solar Battery Plant PartDef
    sbp_def = None
    for part_def in SysideAdapter.elements_of_type(model, "PartDefinition"):
        if sanitize_name(safe_attr(part_def, "name", "")) == "Solar_Battery_Plant":
            sbp_def = part_def
            break

    if sbp_def is None:
        print("  ERROR: Solar Battery Plant PartDefinition not found!")
        return

    print(f"  Found: {safe_attr(sbp_def, 'name')!r}")

    # Scan ALL ReferenceUsage members with redefinitions
    print(f"\n  All :>> redefinitions on Solar Battery Plant:")
    redef_data = {}  # attr_name -> info dict

    for member in getattr(sbp_def, "owned_members", []):
        if not SysideAdapter.is_instance(member, "ReferenceUsage"):
            continue
        owned_redefs = getattr(member, "owned_redefinitions", None)
        if not owned_redefs:
            continue
        owned_redefs_list = list(owned_redefs)
        if not owned_redefs_list:
            continue

        redef = owned_redefs_list[0]
        rf = safe_attr(redef, "redefined_feature", None)
        attr_name = sanitize_name(safe_attr(rf, "name", None)) or \
                    sanitize_name(safe_attr(member, "name", None))
        member_name = sanitize_name(safe_attr(member, "name", ""))

        expr = getattr(member, "feature_value_expression", None)
        expr_type = type_name(expr)

        # Detailed expression analysis
        expr_text = ""
        is_chain = False
        chain_source = ""
        is_reference = False
        ref_source = ""

        if expr is not None:
            try:
                expr_text = reconstruct_expression(expr)
            except Exception:
                expr_text = "<failed>"

            if SysideAdapter.is_instance(expr, "FeatureChainExpression"):
                is_chain = True
                chain_source = extract_feature_chain_name(expr)
            elif SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
                is_reference = True
                ref_source = extract_feature_reference_name(expr)

        info = {
            "attr_name": attr_name,
            "member_name": member_name,
            "expr_type": expr_type,
            "expr_text": expr_text,
            "is_chain": is_chain,
            "chain_source": chain_source,
            "is_reference": is_reference,
            "ref_source": ref_source,
        }
        redef_data[attr_name] = info

        marker = ""
        if is_chain:
            marker = f" [CHAIN -> {chain_source}]"
        elif is_reference:
            marker = f" [REF -> {ref_source}]"

        display = expr_text[:60] if expr_text else "<no expression>"
        print(f"    :>> {attr_name} = {display}{marker}")

    # Specifically look for alias relationships
    print(f"\n  Alias analysis:")
    print(f"  Looking for patterns where :>> X = Y and Y is another attribute name...")

    for attr_name, info in redef_data.items():
        if info["is_reference"]:
            source = info["ref_source"]
            # Check if source is also a redefined attribute on the same part
            if source in redef_data:
                print(f"    ALIAS FOUND: {attr_name} -> {source}")
                print(f"      {attr_name} (FeatureReferenceExpression) points to {source}")
                print(f"      {source} has expression: {redef_data[source]['expr_text'][:60]}")
            else:
                print(f"    Reference: {attr_name} -> {source} (source not in redef_data)")

        elif info["is_chain"]:
            source = info["chain_source"]
            # Check if source's last segment is a redefined attribute
            source_parts = source.split(".")
            leaf = source_parts[-1] if source_parts else ""
            if leaf in redef_data and attr_name != leaf:
                print(f"    POTENTIAL CHAIN ALIAS: {attr_name} -> {source} (leaf={leaf} is also redefined)")

    # Now check the design-level binding that uses the alias
    print(f"\n  Design-level binding check:")
    print(f"  Looking for `in total_capex = capital_cost` on annualized_financial...")

    for usage in SysideAdapter.elements_of_type(model, "PartUsage"):
        if sanitize_name(safe_attr(usage, "name", "")) != "solar_battery_plant":
            continue

        print(f"  Found design solar_battery_plant PartUsage")

        # Find annualized_financial CalcUsage
        for member in getattr(usage, "owned_members", []):
            if not SysideAdapter.is_instance(member, "CalculationUsage"):
                continue
            if sanitize_name(safe_attr(member, "name", "")) != "annualized_financial":
                continue

            print(f"    Found annualized_financial CalcUsage")

            # Find the total_capex input
            for param in getattr(member, "owned_members", []):
                param_name = sanitize_name(safe_attr(param, "name", ""))
                direction = safe_attr(param, "direction", None)

                if param_name == "total_capex" or param_name == "capital_cost":
                    expr = getattr(param, "feature_value_expression", None)
                    if expr is not None:
                        if SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
                            ref_name = extract_feature_reference_name(expr)
                            referent = safe_attr(expr, "referent", None)
                            ref_owner = safe_attr(referent, "owning_type", None) if referent not in (None, "<missing>") else None
                            ref_owner_name = sanitize_name(safe_attr(ref_owner, "name", "?")) if ref_owner not in (None, "<missing>") else "?"
                            print(f"    param: {param_name} direction={direction}")
                            print(f"      expr type: FeatureReferenceExpression")
                            print(f"      referent name: {ref_name}")
                            print(f"      referent owner: {ref_owner_name}")
                        elif SysideAdapter.is_instance(expr, "FeatureChainExpression"):
                            chain_name = extract_feature_chain_name(expr)
                            print(f"    param: {param_name} direction={direction}")
                            print(f"      expr type: FeatureChainExpression")
                            print(f"      chain name: {chain_name}")
                        else:
                            try:
                                text = reconstruct_expression(expr)
                            except Exception:
                                text = "<failed>"
                            print(f"    param: {param_name} direction={direction}")
                            print(f"      expr type: {type_name(expr)}")
                            print(f"      text: {text}")

            break  # Found annualized_financial


# ---------------------------------------------------------------------------
# Part 2: hierarchy_resolver.py Output
# ---------------------------------------------------------------------------

def analyze_hierarchy_output(model: Any) -> None:
    """Run extract_hierarchy_data() and inspect alias population."""
    print("\n" + "=" * 70)
    print("Part 2: hierarchy_resolver.py Output")
    print("=" * 70)

    try:
        from sysml_codegen.extraction.hierarchy_resolver import extract_hierarchy_data
        hierarchy = extract_hierarchy_data(model)
    except Exception as e:
        print(f"  ERROR running extract_hierarchy_data: {e}")
        import traceback
        traceback.print_exc()
        return

    print(f"\n  Redefinitions: {len(hierarchy.redefinitions)}")
    print(f"  Design overrides: {len(hierarchy.design_overrides)}")
    print(f"  Multiplicities: {len(hierarchy.multiplicities)}")
    print(f"  Aggregation expressions: {len(hierarchy.aggregation_expressions)}")
    print(f"  Warnings: {hierarchy.warnings}")

    # Print all aggregation expressions with alias info
    print(f"\n  --- Aggregation Expressions ---")
    for agg in hierarchy.aggregation_expressions:
        print(f"\n  Aggregation: {agg.owning_part_qn}.{agg.attribute_name}")
        print(f"    owning_part_name: {agg.owning_part_name}")
        print(f"    aliases: {agg.aliases}")
        print(f"    sum_terms: {[(t.part_usage_name, t.attribute_name, t.multiplicity_attr) for t in agg.sum_terms]}")
        print(f"    singleton_terms: {[(t.source_path,) for t in agg.singleton_terms]}")
        print(f"    local_terms: {[(t.attribute_name,) for t in agg.local_terms]}")
        print(f"    has_unsupported: {agg.has_unsupported_nodes}")
        print(f"    input_channels: {agg.input_channels}")
        print(f"    entry_points: {agg.entry_points}")
        display = agg.transformed_expression[:80] if agg.transformed_expression else "<none>"
        print(f"    transformed: {display}")
        raw = agg.raw_expression_text[:80] if agg.raw_expression_text else "<none>"
        print(f"    raw text: {raw}")

    # Focus on capital_cost aggregations that should have aliases
    print(f"\n  --- Alias Population Check ---")
    capital_cost_aggs = [a for a in hierarchy.aggregation_expressions if a.attribute_name == "capital_cost"]
    print(f"  capital_cost aggregation expressions: {len(capital_cost_aggs)}")
    for agg in capital_cost_aggs:
        print(f"    {agg.owning_part_qn}: aliases={agg.aliases}")
        if not agg.aliases:
            print(f"      WARNING: No aliases found! Check if CHAIN redefs point to this attribute.")

    # Show all CHAIN-type redefinitions that could be aliases
    print(f"\n  --- All CHAIN-type redefinitions (potential aliases) ---")
    from sysml_codegen.extraction.data_models import RedefinitionType
    chain_redefs = [r for r in hierarchy.redefinitions if r.redefinition_type == RedefinitionType.CHAIN]
    for cr in chain_redefs:
        print(f"    {cr.owning_part_qn}: :>> {cr.attribute_name} = {cr.source_path}")
        # Check if source_path points to an aggregation attribute
        for agg in hierarchy.aggregation_expressions:
            if (cr.owning_part_qn == agg.owning_part_qn
                    and cr.source_path
                    and cr.source_path.endswith(agg.attribute_name)
                    and cr.attribute_name != agg.attribute_name):
                print(f"      => This is an ALIAS for {agg.attribute_name}!")
                if cr.attribute_name not in agg.aliases:
                    print(f"      => BUG: alias '{cr.attribute_name}' is NOT in agg.aliases!")
                else:
                    print(f"      => OK: alias is correctly populated")


# ---------------------------------------------------------------------------
# Part 3: End-to-End Wiring Check
# ---------------------------------------------------------------------------

def analyze_wiring(model_path: Path) -> None:
    """Check if alias resolution works end-to-end through the pipeline."""
    print("\n" + "=" * 70)
    print("Part 3: End-to-End Wiring Check")
    print("=" * 70)

    try:
        from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
        ctx = build_pipeline_context([model_path])
    except Exception as e:
        print(f"  ERROR building pipeline context: {e}")
        import traceback
        traceback.print_exc()
        return

    # Check if annualized_financial module exists and has correct inputs
    print(f"\n  Looking for annualized_financial module...")
    ann_fin_modules = [
        m for m in ctx.computation_graph.modules
        if "annualized_financial" in m.name
    ]

    if not ann_fin_modules:
        print(f"  WARNING: No module containing 'annualized_financial' found!")
        print(f"  Available modules:")
        for m in ctx.computation_graph.modules:
            print(f"    {m.name} (is_aggregation={m.is_aggregation})")
    else:
        for m in ann_fin_modules:
            print(f"\n  Module: {m.name}")
            print(f"    module_type: {m.module_type}")
            print(f"    is_aggregation: {m.is_aggregation}")
            print(f"    execution_order: {m.execution_order}")
            print(f"    inputs:")
            for inp in m.inputs:
                print(f"      {inp.param_name}: source_type={inp.source.source_type}")
                if inp.source.producer_channel:
                    print(f"        producer_channel: {inp.source.producer_channel}")
                if inp.source.qualified_name:
                    print(f"        qualified_name: {inp.source.qualified_name}")
                if inp.source.param_group:
                    print(f"        param_group: {inp.source.param_group}")
            print(f"    outputs:")
            for out in m.outputs:
                print(f"      {out.field_name}: channel={out.channel_name}")

    # Check for total_capex and capital_cost specifically
    print(f"\n  Searching for 'total_capex' and 'capital_cost' across all modules...")
    for m in ctx.computation_graph.modules:
        for inp in m.inputs:
            if "total_capex" in inp.param_name or "capital_cost" in inp.param_name:
                print(f"  {m.name}.{inp.param_name}: {inp.source.source_type}")
                if inp.source.producer_channel:
                    print(f"    producer_channel: {inp.source.producer_channel}")

        for out in m.outputs:
            if "total_capex" in out.channel_name or "capital_cost" in out.channel_name:
                print(f"  {m.name} output: {out.field_name} channel={out.channel_name}")

    # Check aggregation modules
    print(f"\n  Aggregation modules in graph:")
    for m in ctx.computation_graph.modules:
        if m.is_aggregation:
            print(f"    {m.name}: {len(m.inputs)} inputs, {len(m.outputs)} outputs")
            for out in m.outputs:
                print(f"      output: {out.channel_name}")

    # Check scoped aggregation data
    print(f"\n  Scoped aggregation expressions:")
    for sa in ctx.aggregation_expressions:
        print(f"    {sa.instance_path}.{sa.expression.attribute_name}")
        print(f"      module_eqn: {sa.module_eqn}")
        print(f"      aliases: {sa.expression.aliases}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("Probe 3: Alias Resolution for Solar Battery Plant")
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

    analyze_raw_ast(model)
    analyze_hierarchy_output(model)
    analyze_wiring(model_path)


if __name__ == "__main__":
    main()
