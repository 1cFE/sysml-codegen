#!/usr/bin/env python3
"""Spike 9: Issue 22 Empirical Test -- Aggregation REFERENCE Resolution.

Tests whether a CalcUsage on a PartDef that has a REFERENCE binding to the
same PartDef's :>> EXPRESSION aggregation attribute resolves correctly after
virtual expansion.

The scenario (from design_revision_comments_v3.md Issue 22):
  - WidgetAssembly has :>> total_cost = sum(widget.total_cost)  (aggregation)
  - WidgetAssembly has calc margin_calc : MarginCalc {
        in component_total = total_cost;  // REFERENCE to aggregation attr
    }
  - After virtual expansion, does segments[-2] produce the right parent_part
    to resolve against the aggregation output's Key_D?

Expected: YES -- margin_calc's QN is Issue22Design__plant__assembly__margin_calc,
so segments[-2] = "assembly", and Key_D = "assembly.total_cost".

Usage:
    uv run python scripts/spikes/spike_issue22_agg_ref.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _helpers import (
    load_model,
    print_section,
    print_subsection,
    print_table,
)
from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
from sysml_codegen.analysis.parameter_groups import (
    extract_design_attributes,
)
from sysml_codegen.core.models import BindingResolution, BindingResolutionType
from sysml_codegen.core.qualified_names import get_channel_name
from sysml_codegen.extraction.data_models import (
    ScopedAggregationData,
)
from sysml_codegen.extraction.usage_extractor import (
    CalcUsageData,
    extract_calculation_usages,
)
from sysml_codegen.orchestration.pipeline_builder import (
    _extract_and_filter_computed_attributes,
    _extract_hierarchy_and_rewrite_bindings,
    _scope_aggregation_expressions,
)
from agentic_mbse.sysml.types import BindingType


# ---------------------------------------------------------------------------
# Model path
# ---------------------------------------------------------------------------

ISSUE22_MODEL = [Path("tests/fixtures/issue22_model")]


# ---------------------------------------------------------------------------
# Prototype OutputRegistry (same as Spike 8)
# ---------------------------------------------------------------------------

class PrototypeRegistry:
    """Dict-based prototype of the OutputRegistry for spike validation."""

    def __init__(self) -> None:
        self.registry: dict[str, str] = {}
        self.key_source: dict[str, str] = {}
        self.collisions: list[tuple[str, str, str, str]] = []

    def register(self, channel: str, keys: list[tuple[str, str]]) -> None:
        for key, source in keys:
            if key in self.registry:
                if self.registry[key] != channel:
                    self.collisions.append((key, self.registry[key], channel, source))
                continue
            self.registry[key] = channel
            self.key_source[key] = source

    def resolve(self, key: str) -> str | None:
        return self.registry.get(key)


# ---------------------------------------------------------------------------
# Data Extraction
# ---------------------------------------------------------------------------

def extract_all_data(model_paths: list[Path]) -> dict[str, Any] | None:
    """Run full extraction pipeline for the issue22 model."""
    model, adapter, extractor = load_model(model_paths)
    if model is None:
        print("  ERROR: Failed to load issue22 model")
        return None

    # Step 1-3: CalcDefs + CalcUsages
    calc_defs = extractor.extract_calculation_definitions()
    calc_def_by_name = {cd.name: cd for cd in calc_defs}
    calc_usages, _ = extract_calculation_usages(
        model, calc_defs=calc_defs, expand_templates=True,
    )

    # Step 3.5: Hierarchy extraction + binding rewrite
    hierarchy_data = _extract_hierarchy_and_rewrite_bindings(model, calc_usages)
    _enrich_aliases_from_bindings(hierarchy_data, calc_usages)

    # Step 4: Design attributes
    design_attrs = extract_design_attributes(model)

    # Step 4.5: Computed attributes
    computed_attrs = _extract_and_filter_computed_attributes(
        model, calc_usages, design_attrs,
    )

    # Step 4.7: Scoped aggregation
    scoped_agg = _scope_aggregation_expressions(hierarchy_data, calc_usages)

    # Backtracker for ground truth
    bt = DependencyBacktracker(
        all_usages=calc_usages,
        calc_defs=calc_defs,
        design_attributes=design_attrs,
        computed_attributes=computed_attrs,
        aggregation_data=scoped_agg,
    )
    bt_result = bt.find_required_modules(target_outputs=[], include_all=True)

    return {
        "calc_defs": calc_defs,
        "calc_def_by_name": calc_def_by_name,
        "calc_usages": calc_usages,
        "hierarchy_data": hierarchy_data,
        "design_attrs": design_attrs,
        "computed_attrs": computed_attrs,
        "scoped_agg": scoped_agg,
        "bt_result": bt_result,
    }


# ---------------------------------------------------------------------------
# Check 1: Enumerate CalcUsages
# ---------------------------------------------------------------------------

def check_calc_usages(data: dict[str, Any]) -> None:
    """Print all CalcUsages: template, virtual, and concrete."""
    calc_usages: list[CalcUsageData] = data["calc_usages"]

    print_subsection("Check 1: All CalcUsages")

    headers = ["QN", "Instance", "CalcDef", "Template?", "Category"]
    rows = []
    for u in calc_usages:
        is_virtual = (not u.is_template) and u.instance_name == u.qualified_name
        category = "template" if u.is_template else ("virtual" if is_virtual else "concrete")
        rows.append([
            u.qualified_name,
            u.instance_name,
            u.calc_def_name or "<none>",
            str(u.is_template),
            category,
        ])
    print_table(headers, rows)
    print(f"\n  Total: {len(calc_usages)}")


# ---------------------------------------------------------------------------
# Check 2: margin_calc bindings
# ---------------------------------------------------------------------------

def check_margin_calc_bindings(data: dict[str, Any]) -> CalcUsageData | None:
    """Print all bindings on the virtual margin_calc, confirm REFERENCE type."""
    calc_usages: list[CalcUsageData] = data["calc_usages"]

    print_subsection("Check 2: Virtual margin_calc Bindings")

    margin_calc = None
    for u in calc_usages:
        if u.is_template:
            continue
        if "margin_calc" in u.qualified_name:
            margin_calc = u
            break

    if margin_calc is None:
        print("  ERROR: No virtual margin_calc found!")
        return None

    print(f"  Found: {margin_calc.qualified_name}")
    print(f"  Instance name: {margin_calc.instance_name}")
    print(f"  CalcDef: {margin_calc.calc_def_name}")

    headers = ["Param", "Type", "source_path", "literal"]
    rows = []
    for b in margin_calc.bindings:
        rows.append([
            b.param_name,
            b.binding_type.name if b.binding_type else "<none>",
            b.source_path or "<none>",
            str(b.literal_value) if b.literal_value is not None else "<none>",
        ])
    print_table(headers, rows)

    # Check for the REFERENCE binding to total_cost
    ref_binding = None
    for b in margin_calc.bindings:
        if b.param_name == "component_total":
            ref_binding = b
            break

    if ref_binding is None:
        print("\n  WARNING: No 'component_total' binding found!")
    else:
        is_reference = ref_binding.binding_type == BindingType.REFERENCE
        has_sysml_qn = ref_binding.source_path and "::" in ref_binding.source_path
        print(f"\n  component_total binding:")
        print(f"    type:        {ref_binding.binding_type.name}")
        print(f"    source_path: {ref_binding.source_path}")
        print(f"    is REFERENCE?  {'YES' if is_reference else 'NO'}")
        print(f"    is SYSML_QN?   {'YES' if has_sysml_qn else 'NO'}")

    return margin_calc


# ---------------------------------------------------------------------------
# Check 3: Aggregation outputs
# ---------------------------------------------------------------------------

def check_aggregation_outputs(
    data: dict[str, Any],
    registry: PrototypeRegistry,
) -> None:
    """Print all aggregation outputs and confirm Key_D format."""
    scoped_agg: list[ScopedAggregationData] = data["scoped_agg"]

    print_subsection("Check 3: Aggregation Outputs (registered)")

    if not scoped_agg:
        print("  (no scoped aggregation data)")
        return

    for agg in scoped_agg:
        channel = get_channel_name(agg.module_eqn, agg.expression.attribute_name)
        instance_parts = agg.instance_path.split("__")
        part_usage_name = instance_parts[-1]
        key_d = f"{part_usage_name}.{agg.expression.attribute_name}"

        print(f"  Aggregation: {agg.module_eqn}")
        print(f"    instance_path: {agg.instance_path}")
        print(f"    attribute:     {agg.expression.attribute_name}")
        print(f"    channel:       {channel}")
        print(f"    Key_D:         {key_d}")
        print(f"    Key_D in registry? {registry.resolve(key_d) is not None}")


# ---------------------------------------------------------------------------
# Check 4: Secondary resolution attempt
# ---------------------------------------------------------------------------

def check_secondary_resolution(
    data: dict[str, Any],
    registry: PrototypeRegistry,
    margin_calc: CalcUsageData,
) -> bool:
    """Attempt secondary resolution for the REFERENCE binding on margin_calc."""
    print_subsection("Check 4: Secondary Resolution (segments[-2] + leaf)")

    # Find the component_total binding
    ref_binding = None
    for b in margin_calc.bindings:
        if b.param_name == "component_total":
            ref_binding = b
            break

    if ref_binding is None:
        print("  ERROR: No component_total binding on margin_calc")
        return False

    # Extract leaf name from SYSML_QN
    source_path = ref_binding.source_path or ""
    if "::" in source_path:
        leaf_name = source_path.rsplit("::", 1)[-1].strip("'")
    elif "." in source_path:
        leaf_name = source_path.rsplit(".", 1)[-1]
    else:
        leaf_name = source_path

    # Get segments[-2] (parent part)
    segments = margin_calc.qualified_name.split("__")
    parent_part = segments[-2] if len(segments) >= 2 else "<unknown>"

    # Build resolve key
    resolve_key = f"{parent_part}.{leaf_name}"

    print(f"  margin_calc QN:  {margin_calc.qualified_name}")
    print(f"  segments:        {segments}")
    print(f"  segments[-2]:    {parent_part}")
    print(f"  source_path:     {source_path}")
    print(f"  leaf_name:       {leaf_name}")
    print(f"  resolve_key:     {resolve_key}")

    # Attempt resolution
    resolved_channel = registry.resolve(resolve_key)

    print(f"\n  registry.resolve('{resolve_key}') -> ", end="")
    if resolved_channel:
        print(f"'{resolved_channel}'")
        print(f"  Key source: {registry.key_source.get(resolve_key, '<unknown>')}")
        return True
    else:
        print("None (FAILED)")
        # Print all registry keys for debugging
        print(f"\n  All registry keys ({len(registry.registry)}):")
        for key, ch in sorted(registry.registry.items()):
            print(f"    {key} -> {ch}")
        return False


# ---------------------------------------------------------------------------
# Check 5: Backtracker ground truth comparison
# ---------------------------------------------------------------------------

def check_ground_truth(
    data: dict[str, Any],
    registry: PrototypeRegistry,
    margin_calc: CalcUsageData,
    resolution_succeeded: bool,
) -> bool:
    """Compare prototype resolution against backtracker ground truth."""
    bt_result = data["bt_result"]
    binding_resolutions: dict[str, BindingResolution] = bt_result.binding_resolutions

    print_subsection("Check 5: Backtracker Ground Truth Comparison")

    mapping_key = f"{margin_calc.qualified_name}|component_total"
    ground_truth = binding_resolutions.get(mapping_key)

    if ground_truth is None:
        print(f"  WARNING: No ground truth for {mapping_key}")
        print(f"  Available keys containing 'margin_calc':")
        for k in sorted(binding_resolutions.keys()):
            if "margin_calc" in k:
                print(f"    {k} -> {binding_resolutions[k].resolution_type.value}")
        return False

    print(f"  Ground truth for {mapping_key}:")
    print(f"    resolution_type: {ground_truth.resolution_type.value}")
    print(f"    qualified_name:  {ground_truth.qualified_name}")
    print(f"    source_path:     {ground_truth.source_path}")

    # Check if ground truth says MODULE_OUTPUT (expected if aggregation resolves)
    is_module_output = ground_truth.resolution_type == BindingResolutionType.MODULE_OUTPUT
    print(f"\n  Ground truth is MODULE_OUTPUT? {'YES' if is_module_output else 'NO'}")

    if is_module_output and resolution_succeeded:
        # Both agree: it's a module output and our prototype resolved it
        # Check if channels match
        ref_binding = next(
            (b for b in margin_calc.bindings if b.param_name == "component_total"),
            None,
        )
        if ref_binding:
            source_path = ref_binding.source_path or ""
            if "::" in source_path:
                leaf_name = source_path.rsplit("::", 1)[-1].strip("'")
            else:
                leaf_name = source_path.rsplit(".", 1)[-1] if "." in source_path else source_path

            segments = margin_calc.qualified_name.split("__")
            parent_part = segments[-2] if len(segments) >= 2 else ""
            resolve_key = f"{parent_part}.{leaf_name}"
            proto_channel = registry.resolve(resolve_key)

            channels_match = proto_channel == ground_truth.qualified_name
            print(f"  Prototype channel:    {proto_channel}")
            print(f"  Ground truth channel: {ground_truth.qualified_name}")
            print(f"  Channels match?       {'YES' if channels_match else 'NO'}")
            return channels_match

    elif not is_module_output and not resolution_succeeded:
        # Both agree: it's an entry point (resolution failed in both)
        print(f"  Both agree: ENTRY_POINT (resolution failed as expected)")
        return True

    else:
        print(f"  MISMATCH: prototype={'resolved' if resolution_succeeded else 'failed'}, "
              f"ground_truth={ground_truth.resolution_type.value}")
        return False


# ---------------------------------------------------------------------------
# Build Phase 1 Registry
# ---------------------------------------------------------------------------

def build_phase1_registry(data: dict[str, Any]) -> PrototypeRegistry:
    """Build Phase 1 prototype OutputRegistry from extracted data."""
    registry = PrototypeRegistry()

    calc_usages: list[CalcUsageData] = data["calc_usages"]
    calc_def_by_name: dict[str, Any] = data["calc_def_by_name"]
    scoped_agg: list[ScopedAggregationData] = data["scoped_agg"]

    print_subsection("Phase 1 Registry Build")

    # Phase 1A: CalcUsage outputs
    for usage in calc_usages:
        if usage.is_template:
            continue
        cd = calc_def_by_name.get(usage.calc_def_name)
        if not cd:
            continue

        for out_attr in cd.output_attributes:
            channel = get_channel_name(usage.qualified_name, out_attr.name)

            key_a = f"{usage.instance_name}.{out_attr.name}"
            key_b = f"{usage.qualified_name}__{out_attr.name}"
            segments = usage.qualified_name.split("__")
            key_c = ".".join(segments[1:]) + "." + out_attr.name

            keys: list[tuple[str, str]] = [
                (key_a, "CalcUsage.Key_A"),
                (key_b, "CalcUsage.Key_B"),
            ]
            if key_c != key_a:
                keys.append((key_c, "CalcUsage.Key_C"))

            registry.register(channel, keys)
            print(f"  CalcUsage: {usage.instance_name}.{out_attr.name}")
            print(f"    channel: {channel}")
            print(f"    Key_A: {key_a}")
            if key_c != key_a:
                print(f"    Key_C: {key_c}")

    # Phase 1B: Aggregation outputs
    for agg in scoped_agg:
        channel = get_channel_name(agg.module_eqn, agg.expression.attribute_name)
        instance_parts = agg.instance_path.split("__")
        part_usage_name = instance_parts[-1]

        key_d = f"{part_usage_name}.{agg.expression.attribute_name}"
        key_e = ".".join(instance_parts + [agg.expression.attribute_name])

        keys: list[tuple[str, str]] = [
            (key_d, "Aggregation.Key_D"),
            (key_e, "Aggregation.Key_E"),
        ]

        for alias_name in agg.expression.aliases:
            keys.append((f"{part_usage_name}.{alias_name}", f"Aggregation.Alias({alias_name})"))

        registry.register(channel, keys)
        print(f"  Aggregation: {agg.module_eqn}")
        print(f"    channel: {channel}")
        print(f"    Key_D: {key_d}")
        print(f"    Key_E: {key_e}")

    # Summary
    print(f"\n  Total keys:     {len(registry.registry)}")
    print(f"  Total channels: {len(set(registry.registry.values()))}")
    print(f"  Collisions:     {len(registry.collisions)}")

    if registry.collisions:
        for key, old_ch, new_ch, source in registry.collisions:
            print(f"  COLLISION: {key} -> {old_ch} vs {new_ch} ({source})")

    return registry


# ---------------------------------------------------------------------------
# Print all backtracker resolutions (for diagnostics)
# ---------------------------------------------------------------------------

def print_all_resolutions(data: dict[str, Any]) -> None:
    """Print all backtracker binding resolutions for diagnostics."""
    bt_result = data["bt_result"]
    binding_resolutions: dict[str, BindingResolution] = bt_result.binding_resolutions

    print_subsection("All Backtracker Resolutions")

    headers = ["Mapping Key", "Type", "Channel/QN"]
    rows = []
    for key, res in sorted(binding_resolutions.items()):
        rows.append([
            key,
            res.resolution_type.value,
            res.qualified_name or "<none>",
        ])
    print_table(headers, rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print_section("SPIKE 9: Issue 22 -- Aggregation REFERENCE Resolution")

    model_paths = ISSUE22_MODEL
    if len(sys.argv) > 1:
        model_paths = [Path(p) for p in sys.argv[1].split(",")]

    # Load and extract
    print_subsection("Loading issue22_model")
    data = extract_all_data(model_paths)
    if data is None:
        print("\n  VERDICT: FAIL (model load failed)")
        sys.exit(1)

    # Check 1: Enumerate CalcUsages
    check_calc_usages(data)

    # Build Phase 1 registry
    registry = build_phase1_registry(data)

    # Check 2: margin_calc bindings
    margin_calc = check_margin_calc_bindings(data)
    if margin_calc is None:
        print("\n  VERDICT: FAIL (no margin_calc found)")
        sys.exit(1)

    # Check 3: Aggregation outputs
    check_aggregation_outputs(data, registry)

    # Check 4: Secondary resolution
    resolution_ok = check_secondary_resolution(data, registry, margin_calc)

    # Check 5: Ground truth comparison
    ground_truth_ok = check_ground_truth(data, registry, margin_calc, resolution_ok)

    # Print all resolutions for diagnostics
    print_all_resolutions(data)

    # Final verdict
    print_section("VERDICT")

    if resolution_ok and ground_truth_ok:
        print("  PASS: Secondary resolution succeeds for Issue 22 pattern.")
        print("  segments[-2] produces the correct parent_part for resolving")
        print("  REFERENCE bindings targeting aggregation outputs on the same PartDef.")
        print("  CalcUsage and aggregation share the same instance scope after")
        print("  virtual expansion.")
    elif resolution_ok and not ground_truth_ok:
        print("  PARTIAL: Secondary resolution resolved, but channel doesn't match")
        print("  backtracker ground truth. Investigation needed.")
    elif not resolution_ok and ground_truth_ok:
        print("  PARTIAL: Secondary resolution failed, but backtracker also treats")
        print("  this as ENTRY_POINT. The known limitation note is correct but")
        print("  the scenario doesn't produce a MODULE_OUTPUT in practice.")
    else:
        print("  FAIL: Secondary resolution failed. The known limitation in")
        print("  Section 7 is a real problem for this pattern.")
        print("  segments[-2] does NOT produce the correct parent_part.")


if __name__ == "__main__":
    main()
