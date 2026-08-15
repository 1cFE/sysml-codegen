#!/usr/bin/env python3
"""Probe 5: Run the full pipeline and inspect backtracker resolution.

Runs build_pipeline_context() on the solar_battery model and inspects:
1. All modules in the computation graph, including is_aggregation flags
2. All scoped aggregation expressions with instance paths and module EQNs
3. The annualized_financial module's inputs and their source types
4. Specific tracking of "total_capex" and "capital_cost" through the pipeline

This probe helps verify that:
- Aggregation modules are correctly created from sum() expressions
- Alias resolution (total_capex -> capital_cost) is wired correctly
- Entry points from multiplicity attributes are present
- The LCOE pipeline chain is complete

Usage:
    uv run python scripts/probes/probe_backtracker_resolution.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

# Suppress noisy logs from the pipeline
logging.basicConfig(level=logging.WARNING)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_attr(obj: Any, attr: str, default: Any = "<missing>") -> Any:
    """Safely access attribute."""
    try:
        return getattr(obj, attr, default)
    except Exception:
        return default


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("Probe 5: Full Pipeline -- Backtracker & Graph Resolution")
    print("=" * 70)

    model_path = Path(__file__).parent.parent.parent / "tests" / "fixtures" / "solar_battery_model"

    print(f"\nLoading model and building pipeline context from: {model_path}")
    try:
        from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
        ctx = build_pipeline_context([model_path])
        print("  Pipeline context built successfully")
    except Exception as e:
        print(f"  ERROR building pipeline context: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # -----------------------------------------------------------------------
    # Section 1: All Modules in Computation Graph
    # -----------------------------------------------------------------------
    print(f"\n{'=' * 70}")
    print("Section 1: Computation Graph Modules")
    print(f"{'=' * 70}")
    print(f"  Total modules: {len(ctx.computation_graph.modules)}")
    print(f"  Execution order: {ctx.computation_graph.execution_order}")

    for m in ctx.computation_graph.modules:
        agg_marker = " [AGG]" if m.is_aggregation else ""
        comp_marker = " [COMPUTED]" if m.is_computed_attribute else ""
        print(f"\n  Module: {m.name}{agg_marker}{comp_marker}")
        print(f"    module_type: {m.module_type}")
        print(f"    execution_order: {m.execution_order}")
        print(f"    compilability: {m.compilability}")
        if m.compiled_expression:
            display = m.compiled_expression[:80]
            print(f"    compiled_expression: {display}")
        print(f"    inputs ({len(m.inputs)}):")
        for inp in m.inputs:
            src = inp.source
            if src.source_type == "module_output":
                print(f"      {inp.param_name} <- module_output: {src.producer_channel}")
            elif src.source_type == "entry_point":
                print(f"      {inp.param_name} <- entry_point: {src.qualified_name} (group={src.param_group})")
            else:
                print(f"      {inp.param_name} <- {src.source_type}: {src.qualified_name or src.producer_channel}")
        print(f"    outputs ({len(m.outputs)}):")
        for out in m.outputs:
            print(f"      {out.field_name} -> channel: {out.channel_name}")

    # -----------------------------------------------------------------------
    # Section 2: Aggregation Expressions
    # -----------------------------------------------------------------------
    print(f"\n{'=' * 70}")
    print("Section 2: Scoped Aggregation Expressions")
    print(f"{'=' * 70}")
    print(f"  Total scoped aggregations: {len(ctx.aggregation_expressions)}")

    for sa in ctx.aggregation_expressions:
        agg = sa.expression
        print(f"\n  Instance: {sa.instance_path}")
        print(f"    attribute: {agg.attribute_name}")
        print(f"    module_eqn: {sa.module_eqn}")
        print(f"    owning_part_qn: {agg.owning_part_qn}")
        print(f"    aliases: {agg.aliases}")
        print(f"    sum_terms: {[(t.part_usage_name, t.attribute_name, t.multiplicity_attr, t.multiplicity_count) for t in agg.sum_terms]}")
        print(f"    singleton_terms: {[t.source_path for t in agg.singleton_terms]}")
        print(f"    local_terms: {[t.attribute_name for t in agg.local_terms]}")
        print(f"    entry_points: {agg.entry_points}")
        print(f"    input_channels: {agg.input_channels}")
        print(f"    has_unsupported: {agg.has_unsupported_nodes}")
        display = agg.transformed_expression[:80] if agg.transformed_expression else "<none>"
        print(f"    transformed: {display}")

    # -----------------------------------------------------------------------
    # Section 3: annualized_financial Module Deep Dive
    # -----------------------------------------------------------------------
    print(f"\n{'=' * 70}")
    print("Section 3: annualized_financial Module Deep Dive")
    print(f"{'=' * 70}")

    ann_fin_modules = [
        m for m in ctx.computation_graph.modules
        if "annualized_financial" in m.name
    ]

    if not ann_fin_modules:
        print("  WARNING: No module containing 'annualized_financial' found!")
        print("  This means the calc usage is not being picked up by the pipeline.")

        # Check if it's in the calc_usages list
        print(f"\n  Checking calc_usages for annualized_financial...")
        for cu in ctx.calc_usages:
            if "annualized_financial" in cu.qualified_name:
                print(f"    Found calc usage: {cu.qualified_name}")
                print(f"      is_template: {cu.is_template}")
                print(f"      owning_part_def_qn: {cu.owning_part_def_qn}")
                print(f"      bindings:")
                for b in cu.bindings:
                    print(f"        {b.param_name}: type={b.binding_type}, source={b.source_path}, literal={b.literal_value}")
    else:
        for m in ann_fin_modules:
            print(f"\n  Module: {m.name}")
            print(f"    module_type: {m.module_type}")
            print(f"    inputs:")
            for inp in m.inputs:
                src = inp.source
                print(f"      {inp.param_name}:")
                print(f"        source_type: {src.source_type}")
                print(f"        producer_channel: {src.producer_channel}")
                print(f"        qualified_name: {src.qualified_name}")
                print(f"        param_group: {src.param_group}")
            print(f"    outputs:")
            for out in m.outputs:
                print(f"      {out.field_name} -> {out.channel_name}")

    # -----------------------------------------------------------------------
    # Section 4: total_capex and capital_cost Tracking
    # -----------------------------------------------------------------------
    print(f"\n{'=' * 70}")
    print("Section 4: Tracking total_capex and capital_cost")
    print(f"{'=' * 70}")

    print(f"\n  --- Where is 'total_capex' referenced? ---")
    for m in ctx.computation_graph.modules:
        for inp in m.inputs:
            if "total_capex" in inp.param_name.lower():
                print(f"  Input: {m.name}.{inp.param_name}")
                print(f"    source: {inp.source.source_type}")
                print(f"    channel: {inp.source.producer_channel}")
                print(f"    entry: {inp.source.qualified_name}")

    print(f"\n  --- Where is 'capital_cost' referenced? ---")
    for m in ctx.computation_graph.modules:
        for inp in m.inputs:
            if "capital_cost" in inp.param_name.lower():
                print(f"  Input: {m.name}.{inp.param_name}")
                print(f"    source: {inp.source.source_type}")
                print(f"    channel: {inp.source.producer_channel}")
                print(f"    entry: {inp.source.qualified_name}")
        for out in m.outputs:
            if "capital_cost" in out.channel_name.lower():
                print(f"  Output: {m.name}.{out.field_name}")
                print(f"    channel: {out.channel_name}")

    # -----------------------------------------------------------------------
    # Section 5: Entry Point Groups
    # -----------------------------------------------------------------------
    print(f"\n{'=' * 70}")
    print("Section 5: Entry Point Groups")
    print(f"{'=' * 70}")
    print(f"  Total groups: {len(ctx.computation_graph.entry_point_groups)}")

    for group in ctx.computation_graph.entry_point_groups:
        print(f"\n  Group: {group.name} ({group.class_name})")
        print(f"    source_file: {group.source_file}")
        print(f"    parameters ({len(group.parameters)}):")
        for p in group.parameters:
            print(f"      {p.simple_name}: type={p.entry_type.value}, default={p.default_value}")

    # -----------------------------------------------------------------------
    # Section 6: Pipeline Integrity Checks
    # -----------------------------------------------------------------------
    print(f"\n{'=' * 70}")
    print("Section 6: Pipeline Integrity Checks")
    print(f"{'=' * 70}")

    # Check 1: Are all module_output sources resolvable?
    all_output_channels = set()
    for m in ctx.computation_graph.modules:
        for out in m.outputs:
            all_output_channels.add(out.channel_name)

    broken_wires = []
    for m in ctx.computation_graph.modules:
        for inp in m.inputs:
            if inp.source.source_type == "module_output":
                if inp.source.producer_channel not in all_output_channels:
                    broken_wires.append((m.name, inp.param_name, inp.source.producer_channel))

    if broken_wires:
        print(f"\n  BROKEN WIRES ({len(broken_wires)}):")
        for mod_name, param, channel in broken_wires:
            print(f"    {mod_name}.{param} <- {channel} (NOT FOUND in outputs)")
    else:
        print(f"\n  All module_output wires resolve correctly.")

    # Check 2: Are all entry_point sources resolvable?
    all_entry_qns = set()
    for group in ctx.computation_graph.entry_point_groups:
        for p in group.parameters:
            all_entry_qns.add(p.qualified_name)

    missing_entries = []
    for m in ctx.computation_graph.modules:
        for inp in m.inputs:
            if inp.source.source_type == "entry_point":
                if inp.source.qualified_name not in all_entry_qns:
                    missing_entries.append((m.name, inp.param_name, inp.source.qualified_name))

    if missing_entries:
        print(f"\n  MISSING ENTRY POINTS ({len(missing_entries)}):")
        for mod_name, param, qn in missing_entries:
            print(f"    {mod_name}.{param} <- entry:{qn} (NOT in any group)")
    else:
        print(f"\n  All entry_point sources resolve correctly.")

    # Check 3: LCOE chain completeness
    print(f"\n  LCOE Chain Check:")
    lcoe_modules = [m for m in ctx.computation_graph.modules if "lcoe" in m.name.lower()]
    if lcoe_modules:
        for m in lcoe_modules:
            print(f"    LCOE module: {m.name}")
            for inp in m.inputs:
                src_desc = inp.source.producer_channel or inp.source.qualified_name or "?"
                status = "OK"
                if inp.source.source_type == "module_output":
                    if inp.source.producer_channel not in all_output_channels:
                        status = "BROKEN"
                print(f"      {inp.param_name} <- {src_desc} [{status}]")
    else:
        print(f"    WARNING: No LCOE module found!")

    # Check 4: Aggregation module completeness
    print(f"\n  Aggregation Module Check:")
    agg_modules = [m for m in ctx.computation_graph.modules if m.is_aggregation]
    print(f"    Total aggregation modules: {len(agg_modules)}")
    for m in agg_modules:
        has_broken = False
        for inp in m.inputs:
            if inp.source.source_type == "module_output":
                if inp.source.producer_channel not in all_output_channels:
                    has_broken = True
        status = "BROKEN" if has_broken else "OK"
        print(f"    {m.name}: {len(m.inputs)} inputs, {len(m.outputs)} outputs [{status}]")


if __name__ == "__main__":
    main()
