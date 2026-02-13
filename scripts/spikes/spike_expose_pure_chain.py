#!/usr/bin/env python3
"""Spike 3: EXPOSE_PURE Transitive Resolution Chain.

Traces the full Bug 2 resolution chain with actual data from e2e_attr_expr
and solar_battery models. Identifies the exact key format mismatch point
that causes EXPOSE_PURE bindings to fail.

Answers design_revision_comments.md Issues 1 + 3
(virtual instance_name + design attr two-hop).

Usage:
    uv run python scripts/spikes/spike_expose_pure_chain.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

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
    CalcUsageData,
    extract_calculation_usages,
)
from sysml_codegen.extraction.data_models import (
    ComputedAttributeClassification,
    ComputedAttributeData,
)
from sysml_codegen.analysis.parameter_groups import (
    DesignAttributeData,
    extract_design_attributes,
)
from sysml_codegen.generation.initialization import (
    _extract_and_filter_computed_attributes,
)
from agentic_mbse.sysml.types import BindingType


# ---------------------------------------------------------------------------
# Index Builders (replicate backtracker logic for diagnostic purposes)
# ---------------------------------------------------------------------------

def build_computed_attr_index(
    computed_attrs: list[ComputedAttributeData],
) -> dict[str, ComputedAttributeData]:
    """Build computed attribute index matching backtracker's logic.

    Keys: "part.attr" (dotted), "attr" (bare), "Part::attr" (SysML QN).
    Only indexes ALL classifications (not just FORMULA) for diagnostic purposes.
    """
    index: dict[str, ComputedAttributeData] = {}
    for ca in computed_attrs:
        dotted = f"{ca.owning_part_name}.{ca.python_name}"
        index[dotted] = ca
        index[ca.python_name] = ca
        if ca.owning_part_qualified_name:
            sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
            index[sysml_qn] = ca
    return index


def build_design_attr_binding_index(
    design_attrs: dict[Path, list[DesignAttributeData]],
) -> dict[str, str]:
    """Build design attribute binding index matching backtracker's logic.

    Maps "parent_part.attr_name" -> default_value for path references.
    """
    index: dict[str, str] = {}
    for _path, attrs in design_attrs.items():
        for attr in attrs:
            if not attr.default_value:
                continue
            if not _is_path_reference(attr.default_value):
                continue
            key = f"{attr.parent_part}.{attr.name}"
            index[key] = attr.default_value
    return index


def _is_path_reference(value: str) -> bool:
    """Check if a default value is a path reference vs a literal."""
    if not value or "." not in value:
        return False
    try:
        float(value)
        return False
    except ValueError:
        pass
    if value.lower() in ("true", "false"):
        return False
    return True


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
            # Short key
            short_inst = usage.instance_name.rsplit("__", 1)[-1] if "__" in usage.instance_name else usage.instance_name
            short_key = f"{short_inst}.{attr.name}"
            full_key = f"{usage.instance_name}.{attr.name}"
            catalog[short_key] = channel
            catalog[full_key] = channel
    return catalog


# ---------------------------------------------------------------------------
# Chain Tracer
# ---------------------------------------------------------------------------

def trace_chain(
    chain_label: str,
    consumer_name: str,
    param_name: str,
    usages: list[CalcUsageData],
    computed_attr_index: dict[str, ComputedAttributeData],
    design_attr_index: dict[str, str],
    output_catalog: dict[str, str],
) -> None:
    """Trace the resolution chain for a specific binding."""
    print(f"\n  CHAIN TRACE: {chain_label}")

    # Find the consumer CalcUsage
    consumer = next((u for u in usages if u.instance_name == consumer_name), None)
    if consumer is None:
        # Try matching by short name
        consumer = next(
            (u for u in usages if u.instance_name.rsplit("__", 1)[-1] == consumer_name),
            None,
        )
    if consumer is None:
        print(f"    ERROR: Consumer CalcUsage '{consumer_name}' not found")
        return

    # Find the binding
    binding = next((b for b in consumer.bindings if b.param_name == param_name), None)
    if binding is None:
        print(f"    ERROR: Binding '{param_name}' not found on {consumer_name}")
        return

    # Step A: The binding itself
    print(f"\n    Step A: Binding")
    print(f"      param_name: {binding.param_name}")
    print(f"      binding_type: {binding.binding_type.name}")
    print(f"      source_path: {binding.source_path!r}")
    if binding.literal_value is not None:
        print(f"      literal_value: {binding.literal_value!r}")

    source_path = binding.source_path or ""

    # Step B: Computed attribute index lookup
    print(f"\n    Step B: Computed Attribute Index Lookup")
    ca = computed_attr_index.get(source_path)
    # Also try dotted normalization from SysML QN
    ca_via_dotted = None
    ca_via_bare = None
    if ca is None and "::" in source_path:
        parts = source_path.split("::")
        if len(parts) >= 2:
            dotted = f"{parts[-2]}.{parts[-1]}"
            ca_via_dotted = computed_attr_index.get(dotted)
            if ca_via_dotted:
                print(f"      source_path not in index directly")
                print(f"      :: normalized to: {dotted!r}")
                ca = ca_via_dotted
        bare = parts[-1]
        ca_via_bare = computed_attr_index.get(bare)
        if ca is None and ca_via_bare:
            print(f"      :: bare name: {bare!r}")
            ca = ca_via_bare

    if ca is not None:
        print(f"      FOUND in computed_attr_index: YES")
        print(f"      classification: {ca.classification.value}")
        print(f"      expression_text: {ca.expression_text!r}")
        print(f"      owning_part: {ca.owning_part_name} ({ca.owning_part_qualified_name})")
        if ca.references:
            for ref in ca.references:
                print(f"      reference: name={ref.name!r} qualified={ref.qualified_name!r}")
    else:
        print(f"      FOUND in computed_attr_index: NO")
        print(f"      Tried keys: {source_path!r}")
        if "::" in source_path:
            parts = source_path.split("::")
            print(f"        also tried dotted: {parts[-2]}.{parts[-1]!r}")
            print(f"        also tried bare: {parts[-1]!r}")

    # Step C: EXPOSE_PURE target
    print(f"\n    Step C: EXPOSE_PURE Target")
    if ca is not None and ca.classification == ComputedAttributeClassification.EXPOSE_PURE:
        print(f"      IS EXPOSE_PURE: YES")
        print(f"      canonical_target: {ca.expression_text!r}")
    elif ca is not None:
        print(f"      IS EXPOSE_PURE: NO (classification={ca.classification.value})")
        print(f"      expression_text: {ca.expression_text!r}")
    else:
        print(f"      N/A (not in computed_attr_index)")

    # Step D: Design attribute binding index lookup
    print(f"\n    Step D: Design Attribute Binding Index")
    # Try several key formats
    da_keys_tried = []
    da_target = None
    # Direct source_path
    da_keys_tried.append(source_path)
    if source_path in design_attr_index:
        da_target = design_attr_index[source_path]

    # :: normalized to dotted
    if da_target is None and "::" in source_path:
        parts = source_path.split("::")
        if len(parts) >= 2:
            dotted = f"{parts[-2]}.{parts[-1]}"
            da_keys_tried.append(dotted)
            if dotted in design_attr_index:
                da_target = design_attr_index[dotted]

    if da_target is not None:
        print(f"      FOUND: YES")
        print(f"      key: {da_keys_tried[-1]!r}")
        print(f"      target: {da_target!r}")
    else:
        print(f"      FOUND: NO")
        print(f"      keys tried: {da_keys_tried}")

    # Step E: CalcUsage output resolution
    print(f"\n    Step E: CalcUsage Output Resolution")
    resolve_target = None
    if ca is not None and ca.classification == ComputedAttributeClassification.EXPOSE_PURE:
        resolve_target = ca.expression_text
    elif da_target is not None:
        resolve_target = da_target

    if resolve_target:
        print(f"      resolve_target: {resolve_target!r}")
        # Find the producer
        if "." in resolve_target:
            inst_seg = resolve_target.split(".")[0]
            out_seg = resolve_target.split(".", 1)[1]
            matching = [
                u for u in usages
                if u.instance_name == inst_seg
                or u.instance_name.rsplit("__", 1)[-1] == inst_seg
            ]
            if matching:
                producer = matching[0]
                print(f"      producer instance_name: {producer.instance_name!r}")
                print(f"      producer is_virtual: {'__' in producer.instance_name}")
                # Check output catalog
                if resolve_target in output_catalog:
                    print(f"      output_catalog[{resolve_target!r}] = {output_catalog[resolve_target]!r}")
                    print(f"      RESOLUTION: SUCCESS")
                else:
                    print(f"      output_catalog[{resolve_target!r}] = NOT FOUND")
                    # Try full key
                    full_key = f"{producer.instance_name}.{out_seg}"
                    if full_key in output_catalog:
                        print(f"      output_catalog[{full_key!r}] = {output_catalog[full_key]!r}")
                        print(f"      RESOLUTION: REQUIRES FULL KEY (short key failed)")
                    else:
                        print(f"      output_catalog[{full_key!r}] = NOT FOUND")
                        print(f"      RESOLUTION: FAILURE -- key format mismatch")
            else:
                print(f"      No CalcUsage found with instance segment {inst_seg!r}")
                print(f"      RESOLUTION: FAILURE -- producer not found")
        else:
            print(f"      resolve_target has no dot -- bare name: {resolve_target!r}")
            if resolve_target in output_catalog:
                print(f"      output_catalog[{resolve_target!r}] = {output_catalog[resolve_target]!r}")
            else:
                print(f"      output_catalog[{resolve_target!r}] = NOT FOUND")
    else:
        print(f"      No resolve target available (neither EXPOSE_PURE nor design attr)")

    # Step F: Prototype OutputRegistry test
    print(f"\n    Step F: Prototype OutputRegistry Resolution")
    # Test resolving the original source_path through the catalog
    test_keys = [source_path]
    if "::" in source_path:
        parts = source_path.split("::")
        test_keys.append(f"{parts[-2]}.{parts[-1]}")
        test_keys.append(parts[-1])
    if resolve_target:
        test_keys.append(resolve_target)

    for tk in test_keys:
        result = output_catalog.get(tk)
        print(f"      registry.resolve({tk!r}) = {result!r}")

    # Diagnosis
    print(f"\n    DIAGNOSIS:")
    if resolve_target and resolve_target in output_catalog:
        print(f"      Chain resolves successfully via {resolve_target!r}")
        print(f"      OutputRegistry would need EXPOSE_PURE alias: {source_path!r} -> {output_catalog[resolve_target]!r}")
    elif resolve_target:
        print(f"      Chain BREAKS: {resolve_target!r} not in output catalog")
        if "." in resolve_target:
            inst = resolve_target.split(".")[0]
            matching = [u for u in usages if u.instance_name.rsplit("__", 1)[-1] == inst]
            if matching and "__" in matching[0].instance_name:
                full = f"{matching[0].instance_name}.{resolve_target.split('.', 1)[1]}"
                print(f"      Root cause: EXPOSE_PURE uses short instance name {inst!r}")
                print(f"        but output catalog registers full qualified name")
                print(f"        Proposed fix: also register short key {resolve_target!r} -> channel")
                if full in output_catalog:
                    print(f"        Full key exists: {full!r} -> {output_catalog[full]!r}")
    else:
        print(f"      Chain does not go through EXPOSE_PURE or design attr")
        print(f"      This binding resolves directly (or fails to resolve)")


# ---------------------------------------------------------------------------
# Spike Logic
# ---------------------------------------------------------------------------

def run_spike_for_model(
    suite_name: str,
    model_paths: list[Path],
    chains_to_trace: list[tuple[str, str, str]],
) -> None:
    """Run Spike 3 on a single model.

    Args:
        chains_to_trace: List of (label, consumer_name, param_name) tuples.
    """
    print_subsection(f"Model: {suite_name}")

    model, adapter, extractor = load_model(model_paths)
    if model is None:
        print("  SKIPPED: model failed to load")
        return

    # Step 1: Extract everything
    calc_defs = extractor.extract_calculation_definitions()
    calc_def_map = {cd.name: cd for cd in calc_defs}
    print(f"  CalcDefs: {len(calc_defs)}")

    usages, _ = extract_calculation_usages(
        model, calc_defs=calc_defs, expand_templates=True,
    )
    print(f"  CalcUsages (expanded): {len(usages)}")

    design_attrs = extract_design_attributes(model)
    total_da = sum(len(v) for v in design_attrs.values())
    print(f"  DesignAttributes: {total_da} across {len(design_attrs)} files")

    computed_attrs = _extract_and_filter_computed_attributes(model, usages, design_attrs)
    print(f"  ComputedAttributes: {len(computed_attrs)}")

    # Classify computed attrs
    by_class: dict[str, int] = {}
    for ca in computed_attrs:
        by_class[ca.classification.value] = by_class.get(ca.classification.value, 0) + 1
    print(f"  Classifications: {by_class}")

    # Step 2: Build indexes
    computed_attr_index = build_computed_attr_index(computed_attrs)
    design_attr_index = build_design_attr_binding_index(design_attrs)
    output_catalog = build_output_catalog(usages, calc_def_map)

    # Dump indexes for diagnostic visibility
    print(f"\n  COMPUTED ATTRIBUTE INDEX ({len(computed_attr_index)} keys):")
    seen_cas: set[str] = set()
    for key, ca in sorted(computed_attr_index.items()):
        ca_id = f"{ca.owning_part_name}.{ca.name}"
        if ca_id not in seen_cas:
            seen_cas.add(ca_id)
            # Show all keys for this attr
            keys_for_this = [k for k, v in computed_attr_index.items() if v is ca]
            print(f"    {ca_id} [{ca.classification.value}]")
            print(f"      keys: {keys_for_this}")
            print(f"      expression: {ca.expression_text!r}")

    print(f"\n  DESIGN ATTRIBUTE BINDING INDEX ({len(design_attr_index)} entries):")
    for key, target in sorted(design_attr_index.items()):
        print(f"    {key!r} -> {target!r}")

    print(f"\n  OUTPUT CATALOG ({len(output_catalog)} keys):")
    # Group by channel
    channels: dict[str, list[str]] = {}
    for key, channel in sorted(output_catalog.items()):
        channels.setdefault(channel, []).append(key)
    for channel, keys in sorted(channels.items()):
        print(f"    channel: {channel}")
        for k in keys:
            print(f"      key: {k!r}")

    # Step 3: Trace each chain
    for label, consumer, param in chains_to_trace:
        trace_chain(
            label, consumer, param,
            usages, computed_attr_index, design_attr_index, output_catalog,
        )


def main() -> None:
    print_section("SPIKE 3: EXPOSE_PURE Transitive Resolution Chain")

    # e2e_attr_expr: the Bug 2 model
    e2e_suite = next((s for s in DEFAULT_SUITES if s[0] == "e2e_attr_expr"), None)
    if e2e_suite:
        run_spike_for_model(
            e2e_suite[0],
            e2e_suite[1],
            chains_to_trace=[
                ("financial.total_capex", "financial", "total_capex"),
                ("lcoe.annual_om", "lcoe", "annual_om"),
                ("lcoe.annualized_capital", "lcoe", "annualized_capital"),
            ],
        )

    # solar_battery: traces annualized_financial.total_capex (aggregation path)
    sb_suite = next((s for s in DEFAULT_SUITES if s[0] == "solar_battery"), None)
    if sb_suite:
        run_spike_for_model(
            sb_suite[0],
            sb_suite[1],
            chains_to_trace=[
                ("annualized_financial.total_capex", "annualized_financial", "total_capex"),
                ("lcoe.annualized_capital_cost", "lcoe", "annualized_capital_cost"),
            ],
        )


if __name__ == "__main__":
    main()
