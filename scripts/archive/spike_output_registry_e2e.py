#!/usr/bin/env python3
"""Spike 8: OutputRegistry End-to-End Key Format Validation.

Builds a prototype OutputRegistry from real model data following the Phase 1-4
registration protocol from 08_algorithm_revised.md Section 12. Validates that
every alias and backtracker resolution produces the correct result.

Addresses design_revision_comments_v3.md Issues 15, 16, 17, 20.

Usage:
    uv run python scripts/spikes/spike_output_registry_e2e.py
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _helpers import (
    DEFAULT_SUITES,
    load_model,
    print_section,
    print_subsection,
    print_table,
)
from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
from sysml_codegen.analysis.parameter_groups import (
    DesignAttributeData,
    extract_design_attributes,
)
from sysml_codegen.core.models import BindingResolution, BindingResolutionType
from sysml_codegen.core.qualified_names import get_channel_name, sysml_to_python_qualified_name
from sysml_codegen.extraction.data_models import (
    ComputedAttributeClassification,
    ComputedAttributeData,
    HierarchyExtractionResult,
    RedefinitionType,
    ScopedAggregationData,
)
from sysml_codegen.extraction.expression_compiler import Compilability
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
# Model suites for this spike (only solar_battery and e2e_attr_expr)
# ---------------------------------------------------------------------------

SPIKE_SUITES = [s for s in DEFAULT_SUITES if s[0] in ("solar_battery", "e2e_attr_expr")]


# ---------------------------------------------------------------------------
# Prototype OutputRegistry
# ---------------------------------------------------------------------------

class PrototypeRegistry:
    """Dict-based prototype of the OutputRegistry for spike validation.

    Tracks every registration key, its source description, and detects
    key collisions (same key -> different channels).
    """

    def __init__(self) -> None:
        self.registry: dict[str, str] = {}        # key -> channel
        self.key_source: dict[str, str] = {}       # key -> description
        self.collisions: list[tuple[str, str, str, str]] = []  # (key, old_ch, new_ch, source)

    def register(self, channel: str, keys: list[tuple[str, str]]) -> None:
        """Register a channel under multiple keys.

        Args:
            channel: The output channel name (PQN format).
            keys: List of (key, source_description) tuples.
        """
        for key, source in keys:
            if key in self.registry:
                if self.registry[key] != channel:
                    self.collisions.append((key, self.registry[key], channel, source))
                # Don't overwrite -- first registration wins
                continue
            self.registry[key] = channel
            self.key_source[key] = source

    def resolve(self, key: str) -> str | None:
        """Exact-match resolution (per design: no normalization)."""
        return self.registry.get(key)


# ---------------------------------------------------------------------------
# Data Extraction (shared pipeline through Step 4.5+scoping)
# ---------------------------------------------------------------------------

def extract_all_data(
    suite_name: str,
    model_paths: list[Path],
) -> dict[str, Any] | None:
    """Run full extraction pipeline for one model suite.

    Returns dict with all extracted data, or None on failure.
    """
    model, adapter, extractor = load_model(model_paths)
    if model is None:
        print("  SKIPPED: model failed to load")
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

    # Step 4.5: Computed attributes (modifies design_attrs in-place)
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
        "model": model,
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
# Phase 1: Registration
# ---------------------------------------------------------------------------

def build_phase1_registry(
    data: dict[str, Any],
    suite_name: str,
) -> PrototypeRegistry:
    """Build Phase 1 prototype OutputRegistry from extracted data.

    Registers:
      - Phase 1A: CalcUsage outputs (concrete + virtual)
      - Phase 1B: Aggregation outputs + aliases
      - Phase 1C: FORMULA computed attribute outputs
    """
    registry = PrototypeRegistry()

    calc_usages: list[CalcUsageData] = data["calc_usages"]
    calc_def_by_name: dict[str, Any] = data["calc_def_by_name"]
    scoped_agg: list[ScopedAggregationData] = data["scoped_agg"]
    computed_attrs: list[ComputedAttributeData] = data["computed_attrs"]

    # Counts for reporting
    concrete_count = 0
    virtual_count = 0
    agg_count = 0
    formula_count = 0

    # ── Phase 1A: CalcUsage outputs ──

    print_subsection("Phase 1A: CalcUsage Outputs")

    for usage in calc_usages:
        if usage.is_template:
            continue
        cd = calc_def_by_name.get(usage.calc_def_name)
        if not cd:
            continue

        is_virtual = usage.instance_name == usage.qualified_name
        tag = "virtual" if is_virtual else "concrete"

        for out_attr in cd.output_attributes:
            channel = get_channel_name(usage.qualified_name, out_attr.name)

            # Key A: instance_name.output
            key_a = f"{usage.instance_name}.{out_attr.name}"
            # Key B: EQN__output (full qualified)
            key_b = f"{usage.qualified_name}__{out_attr.name}"
            # Key C: dotted hierarchy path (Issue 15 fix candidate)
            segments = usage.qualified_name.split("__")
            dotted_path = ".".join(segments[1:])  # drop design prefix
            key_c = f"{dotted_path}.{out_attr.name}"

            keys: list[tuple[str, str]] = [
                (key_a, f"CalcUsage.Key_A({tag})"),
                (key_b, f"CalcUsage.Key_B({tag})"),
            ]
            # Only add Key_C if different from Key_A
            key_c_is_new = key_c != key_a
            if key_c_is_new:
                keys.append((key_c, f"CalcUsage.Key_C({tag})"))

            registry.register(channel, keys)

            # Print details
            print(f"  {tag} | {usage.instance_name}")
            print(f"    channel: {channel}")
            print(f"    Key_A: {key_a}")
            print(f"    Key_B: {key_b}")
            if key_c_is_new:
                print(f"    Key_C: {key_c}  (NEW -- different from Key_A)")
            else:
                print(f"    Key_C: == Key_A (same)")

            if is_virtual:
                virtual_count += 1
            else:
                concrete_count += 1

    # ── Phase 1B: Aggregation outputs + aliases ──

    print_subsection("Phase 1B: Aggregation Outputs")

    for agg in scoped_agg:
        channel = get_channel_name(agg.module_eqn, agg.expression.attribute_name)
        instance_parts = agg.instance_path.split("__")
        part_usage_name = instance_parts[-1] if instance_parts else agg.expression.owning_part_name

        # Key D: part_usage_name.attribute
        key_d = f"{part_usage_name}.{agg.expression.attribute_name}"
        # Key E: full instance dotted path
        key_e = ".".join(instance_parts + [agg.expression.attribute_name])

        keys: list[tuple[str, str]] = [
            (key_d, "Aggregation.Key_D(short)"),
            (key_e, "Aggregation.Key_E(full_dotted)"),
        ]

        # Aliases from hierarchy extractor
        for alias_name in agg.expression.aliases:
            key_alias_d = f"{part_usage_name}.{alias_name}"
            key_alias_e = ".".join(instance_parts + [alias_name])
            keys.append((key_alias_d, f"Aggregation.Alias_D({alias_name})"))
            keys.append((key_alias_e, f"Aggregation.Alias_E({alias_name})"))

        registry.register(channel, keys)

        print(f"  {agg.module_eqn}")
        print(f"    channel:      {channel}")
        print(f"    instance_path: {agg.instance_path}")
        print(f"    Key_D: {key_d}")
        print(f"    Key_E: {key_e}")
        if agg.expression.aliases:
            print(f"    aliases: {agg.expression.aliases}")
            for alias_name in agg.expression.aliases:
                print(f"      Alias_D: {part_usage_name}.{alias_name}")
                print(f"      Alias_E: {'.'.join(instance_parts + [alias_name])}")
        agg_count += 1

    # ── Phase 1C: FORMULA computed attribute outputs ──

    print_subsection("Phase 1C: FORMULA Outputs")

    for ca in computed_attrs:
        if ca.classification != ComputedAttributeClassification.FORMULA:
            continue
        if ca.compilability != Compilability.FULLY_COMPILABLE:
            continue

        part_qn_python = sysml_to_python_qualified_name(ca.owning_part_qualified_name)
        module_eqn = f"{part_qn_python}__{ca.python_name}"
        channel = get_channel_name(module_eqn, ca.python_name)
        # Key F: owning_part_name.python_name
        key_f = f"{ca.owning_part_name}.{ca.python_name}"

        registry.register(channel, [(key_f, "FORMULA.Key_F")])

        print(f"  {ca.python_name} on {ca.owning_part_name}")
        print(f"    channel:  {channel}")
        print(f"    Key_F:    {key_f}")
        print(f"    module_eqn: {module_eqn}")
        print(f"    owning_part_qn: {ca.owning_part_qualified_name}")
        formula_count += 1

    # ── Phase 1 Summary ──

    print_subsection("Phase 1 Summary")

    total_keys = len(registry.registry)
    total_channels = len(set(registry.registry.values()))
    total_collisions = len(registry.collisions)

    print(f"  Concrete CalcUsage outputs: {concrete_count}")
    print(f"  Virtual CalcUsage outputs:  {virtual_count}")
    print(f"  Aggregation outputs:        {agg_count}")
    print(f"  FORMULA outputs:            {formula_count}")
    print(f"  Total channels:             {total_channels}")
    print(f"  Total keys:                 {total_keys}")
    print(f"  Collisions:                 {total_collisions}")

    if registry.collisions:
        print(f"\n  COLLISIONS:")
        for key, old_ch, new_ch, source in registry.collisions:
            print(f"    key: {key}")
            print(f"      existing channel: {old_ch}")
            print(f"      new channel:      {new_ch}")
            print(f"      source:           {source}")

    return registry


# ---------------------------------------------------------------------------
# Instance path finder (for Phase 2 CHAIN alias scoping)
# ---------------------------------------------------------------------------

def find_instance_paths_for_partdef(
    owning_part_qn: str,
    calc_usages: list[CalcUsageData],
    hierarchy_data: HierarchyExtractionResult,
) -> list[str]:
    """Find all design instance paths where a PartDef is instantiated.

    Mirrors the logic in _scope_aggregation_expressions: virtual CalcUsages
    owned by this PartDef reveal instance paths via their parent QN segments.

    Returns dotted instance paths (__ converted to .) with design prefix dropped.
    """
    # Strategy 1: direct virtual CalcUsages on this PartDef
    instance_paths: set[str] = set()
    for usage in calc_usages:
        if usage.is_template or not usage.owning_part_def_qn:
            continue
        if usage.owning_part_def_qn == owning_part_qn:
            parent = usage.qualified_name.rsplit("__", 1)[0]
            # Convert to dotted, drop design prefix
            segments = parent.split("__")
            dotted = ".".join(segments[1:])  # drop design prefix
            instance_paths.add(dotted)

    # Strategy 2: child-walk (matching _scope_aggregation_expressions BF-6)
    if not instance_paths:
        children = {
            name.lower()
            for name in hierarchy_data.part_usage_names.get(owning_part_qn, set())
        }
        if children:
            for usage in calc_usages:
                if usage.is_template or not usage.owning_part_def_qn:
                    continue
                segments = usage.qualified_name.split("__")
                for i, seg in enumerate(segments):
                    if seg.lower() in children and i > 0:
                        parent_path = "__".join(segments[:i])
                        parent_segments = parent_path.split("__")
                        dotted = ".".join(parent_segments[1:])
                        instance_paths.add(dotted)
                        break

    return sorted(instance_paths)


# ---------------------------------------------------------------------------
# Phase 2: CHAIN Alias Validation
# ---------------------------------------------------------------------------

def validate_phase2_chain_aliases(
    data: dict[str, Any],
    registry: PrototypeRegistry,
    suite_name: str,
) -> list[dict[str, Any]]:
    """Validate Phase 2 CHAIN alias resolution against the Phase 1 registry.

    For each CHAIN-type redefinition with a DOTTED source_path, build the
    alias and canonical keys, attempt resolution, and report results.
    """
    hierarchy_data: HierarchyExtractionResult = data["hierarchy_data"]
    calc_usages: list[CalcUsageData] = data["calc_usages"]

    print_subsection("Phase 2: CHAIN Alias Validation")

    results: list[dict[str, Any]] = []
    total_chain = 0
    total_dotted = 0

    for redef in hierarchy_data.redefinitions:
        if redef.redefinition_type != RedefinitionType.CHAIN:
            continue
        total_chain += 1

        if not redef.source_path or "." not in redef.source_path:
            continue  # Skip BARE CAS codes
        total_dotted += 1

        # Find instance paths for this PartDef
        inst_paths = find_instance_paths_for_partdef(
            redef.owning_part_qn, calc_usages, hierarchy_data,
        )

        if not inst_paths:
            results.append({
                "alias_key": f"<no_instance>.{redef.attribute_name}",
                "canonical_key": f"<no_instance>.{redef.source_path}",
                "resolved_channel": None,
                "would_fix_key": None,
                "owning_part_qn": redef.owning_part_qn,
                "note": "NO INSTANCE PATH FOUND",
            })
            continue

        for inst_path in inst_paths:
            inst_parts = inst_path.split(".")
            alias_key = ".".join(inst_parts + [redef.attribute_name])
            source_parts = redef.source_path.split(".")
            canonical_key = ".".join(inst_parts + source_parts)

            resolved_channel = registry.resolve(canonical_key)

            # If failed, check what key WOULD work
            would_fix_key = None
            if resolved_channel is None:
                # Search for a Key_C that ends with the source path's last segment
                target_suffix = "." + source_parts[-1]
                for key, ch in registry.registry.items():
                    if key.endswith(target_suffix) and registry.key_source.get(key, "").startswith("CalcUsage.Key_C"):
                        # Check if the dotted path matches structurally
                        key_parts = key.split(".")
                        if len(key_parts) >= len(source_parts):
                            # Does the tail of the key match source_parts?
                            if key_parts[-len(source_parts):] == source_parts:
                                # Does the prefix match the instance path?
                                key_prefix = ".".join(key_parts[:-len(source_parts)])
                                if key_prefix == inst_path or inst_path.endswith(key_prefix):
                                    would_fix_key = key
                                    break

                # Also try exact match against all registry keys
                if would_fix_key is None:
                    for key, ch in registry.registry.items():
                        key_parts = key.split(".")
                        if len(key_parts) >= len(source_parts) and key_parts[-len(source_parts):] == source_parts:
                            would_fix_key = key
                            break

            # Track which key source resolved this canonical
            resolved_via = registry.key_source.get(canonical_key, "") if resolved_channel else ""

            results.append({
                "alias_key": alias_key,
                "canonical_key": canonical_key,
                "resolved_channel": resolved_channel,
                "resolved_via": resolved_via,
                "would_fix_key": would_fix_key,
                "owning_part_qn": redef.owning_part_qn,
                "note": "",
            })

    # Report
    resolved_count = sum(1 for r in results if r["resolved_channel"] is not None)
    failed_count = sum(1 for r in results if r["resolved_channel"] is None)

    print(f"  Total CHAIN redefs:              {total_chain}")
    print(f"  DOTTED CHAIN redefs (in scope):  {total_dotted}")
    print(f"  Alias attempts (with instances): {len(results)}")
    print(f"  Resolved:                        {resolved_count} / {len(results)}")
    print(f"  Failed:                          {failed_count} / {len(results)}")

    if resolved_count > 0:
        # Key source distribution
        source_counts: dict[str, int] = defaultdict(int)
        for r in results:
            if r["resolved_channel"] is not None:
                source_counts[r["resolved_via"]] += 1
        print(f"\n  Resolved via key source:")
        for src, count in sorted(source_counts.items()):
            print(f"    {src}: {count}")

        print(f"\n  SUCCESSES (first 5):")
        for r in results[:5]:
            if r["resolved_channel"] is not None:
                print(f"    alias:     {r['alias_key']}")
                print(f"    canonical: {r['canonical_key']}")
                print(f"    via:       {r['resolved_via']}")
                print(f"    channel:   {r['resolved_channel']}")

    if failed_count > 0:
        print(f"\n  FAILURES:")
        for r in results:
            if r["resolved_channel"] is None:
                print(f"    alias:     {r['alias_key']}")
                print(f"    canonical: {r['canonical_key']}")
                print(f"    would-fix: {r['would_fix_key']}")
                if r["note"]:
                    print(f"    note:      {r['note']}")

    return results


# ---------------------------------------------------------------------------
# Phase 3: EXPOSE_PURE Alias Validation
# ---------------------------------------------------------------------------

def validate_phase3_expose_pure(
    data: dict[str, Any],
    registry: PrototypeRegistry,
    suite_name: str,
) -> list[dict[str, Any]]:
    """Validate Phase 3 EXPOSE_PURE alias resolution against the registry.

    For each EXPOSE_PURE computed attribute, build canonical_name from
    references field and attempt resolution.
    """
    computed_attrs: list[ComputedAttributeData] = data["computed_attrs"]

    print_subsection("Phase 3: EXPOSE_PURE Alias Validation")

    results: list[dict[str, Any]] = []
    total_expose = 0

    for ca in computed_attrs:
        if ca.classification != ComputedAttributeClassification.EXPOSE_PURE:
            continue
        total_expose += 1

        if len(ca.references) < 2:
            results.append({
                "scoped_alias": f"{ca.owning_part_name}.{ca.python_name}",
                "canonical_name": "<insufficient_refs>",
                "resolved_channel": None,
                "note": f"Only {len(ca.references)} references (need 2+)",
            })
            continue

        # references[1] = CalcUsage instance, references[0] = output attribute
        instance_name = ca.references[1].name
        output_name = ca.references[0].name
        canonical_name = f"{instance_name}.{output_name}"

        resolved_channel = registry.resolve(canonical_name)
        scoped_alias = f"{ca.owning_part_name}.{ca.python_name}"

        results.append({
            "scoped_alias": scoped_alias,
            "canonical_name": canonical_name,
            "resolved_channel": resolved_channel,
            "note": "",
        })

    resolved_count = sum(1 for r in results if r["resolved_channel"] is not None)
    failed_count = sum(1 for r in results if r["resolved_channel"] is None)

    print(f"  EXPOSE_PURE computed attrs: {total_expose}")
    print(f"  Resolved:                   {resolved_count} / {len(results)}")
    print(f"  Failed:                     {failed_count} / {len(results)}")

    for r in results:
        status = "RESOLVED" if r["resolved_channel"] else "FAILED"
        print(f"\n    {r['scoped_alias']} -> {r['canonical_name']} -> {status}")
        if r["resolved_channel"]:
            print(f"      channel: {r['resolved_channel']}")
        if r["note"]:
            print(f"      note: {r['note']}")

    return results


# ---------------------------------------------------------------------------
# Phase 4: Transitive Default Validation
# ---------------------------------------------------------------------------

def validate_phase4_transitive_defaults(
    data: dict[str, Any],
    registry: PrototypeRegistry,
    suite_name: str,
) -> list[dict[str, Any]]:
    """Validate Phase 4 transitive default resolution against the registry.

    For each design attribute with a dotted-path default_value (not a float),
    attempt resolution against the registry.
    """
    design_attrs: dict[Path, list[DesignAttributeData]] = data["design_attrs"]

    print_subsection("Phase 4: Transitive Default Validation")

    results: list[dict[str, Any]] = []

    for file_path, attrs in design_attrs.items():
        for attr in attrs:
            if attr.default_value is None:
                continue
            val = str(attr.default_value)
            if "." not in val:
                continue
            # Skip numeric floats (e.g., "3.14")
            try:
                float(val)
                continue
            except ValueError:
                pass

            resolved_channel = registry.resolve(val)
            scoped_key = f"{attr.parent_part}.{attr.name}" if attr.parent_part else attr.name

            results.append({
                "scoped_key": scoped_key,
                "default_value": val,
                "resolved_channel": resolved_channel,
            })

    resolved_count = sum(1 for r in results if r["resolved_channel"] is not None)
    failed_count = sum(1 for r in results if r["resolved_channel"] is None)

    print(f"  Dotted-path defaults found: {len(results)}")
    print(f"  Resolved:                   {resolved_count} / {len(results)}")
    print(f"  Failed:                     {failed_count} / {len(results)}")

    for r in results:
        status = "RESOLVED" if r["resolved_channel"] else "FAILED"
        print(f"\n    {r['scoped_key']} -> {r['default_value']} -> {status}")
        if r["resolved_channel"]:
            print(f"      channel: {r['resolved_channel']}")

    return results


# ---------------------------------------------------------------------------
# CHAIN Binding Validation (ground truth comparison)
# ---------------------------------------------------------------------------

def validate_chain_bindings(
    data: dict[str, Any],
    registry: PrototypeRegistry,
    suite_name: str,
) -> list[dict[str, Any]]:
    """Compare prototype registry CHAIN binding resolution against backtracker ground truth.

    For each CHAIN binding, attempts registry.resolve(source_path) and compares
    against the backtracker's binding_resolutions.
    """
    calc_usages: list[CalcUsageData] = data["calc_usages"]
    bt_result = data["bt_result"]
    binding_resolutions: dict[str, BindingResolution] = bt_result.binding_resolutions

    print_subsection("CHAIN Binding Validation (vs Ground Truth)")

    results: list[dict[str, Any]] = []

    for usage in calc_usages:
        if usage.is_template:
            continue
        for binding in usage.bindings:
            if binding.binding_type != BindingType.CHAIN:
                continue
            if not binding.source_path:
                continue

            mapping_key = f"{usage.qualified_name}|{binding.param_name}"
            ground_truth = binding_resolutions.get(mapping_key)

            prototype_channel = registry.resolve(binding.source_path)

            gt_type = ground_truth.resolution_type.value if ground_truth else "MISSING"
            gt_channel = ground_truth.qualified_name if ground_truth else "MISSING"

            match = False
            if ground_truth is None:
                match = False
            elif ground_truth.resolution_type == BindingResolutionType.MODULE_OUTPUT:
                match = (prototype_channel == gt_channel)
            elif ground_truth.resolution_type == BindingResolutionType.ENTRY_POINT:
                # Correct: entry points should NOT resolve in the output registry
                match = (prototype_channel is None)

            # Track which registry key was used
            resolved_via = registry.key_source.get(binding.source_path, "") if prototype_channel else ""

            results.append({
                "usage_qn": usage.qualified_name,
                "param_name": binding.param_name,
                "source_path": binding.source_path,
                "gt_type": gt_type,
                "gt_channel": gt_channel,
                "proto_channel": prototype_channel,
                "resolved_via": resolved_via,
                "match": match,
            })

    match_count = sum(1 for r in results if r["match"])
    mismatch_count = sum(1 for r in results if not r["match"])

    print(f"  Total CHAIN bindings:       {len(results)}")
    print(f"  Matches ground truth:       {match_count} / {len(results)}")
    print(f"  Mismatches:                 {mismatch_count} / {len(results)}")

    # Print table
    if results:
        headers = ["Usage (short)", "Param", "source_path", "GT Type", "Match"]
        rows = []
        for r in results:
            usage_short = r["usage_qn"].split("__")[-1]
            rows.append([
                usage_short,
                r["param_name"],
                r["source_path"],
                r["gt_type"],
                "YES" if r["match"] else "NO",
            ])
        print_table(headers, rows)

    if mismatch_count > 0:
        print(f"\n  MISMATCHES:")
        for r in results:
            if not r["match"]:
                print(f"    {r['usage_qn']}|{r['param_name']}")
                print(f"      source_path:     {r['source_path']}")
                print(f"      GT type:         {r['gt_type']}")
                print(f"      GT channel:      {r['gt_channel']}")
                print(f"      Proto channel:   {r['proto_channel']}")
                print(f"      Proto via:       {r['resolved_via']}")

    return results


# ---------------------------------------------------------------------------
# REFERENCE Secondary Resolution Validation
# ---------------------------------------------------------------------------

def validate_reference_secondary_resolution(
    data: dict[str, Any],
    registry: PrototypeRegistry,
    suite_name: str,
) -> list[dict[str, Any]]:
    """Validate REFERENCE binding secondary resolution logic.

    For each REFERENCE binding that resolves to MODULE_OUTPUT in the ground truth,
    try multiple parent_part candidates and determine which produces the correct
    channel. This empirically determines _get_parent_part_for_usage() logic.
    """
    calc_usages: list[CalcUsageData] = data["calc_usages"]
    bt_result = data["bt_result"]
    binding_resolutions: dict[str, BindingResolution] = bt_result.binding_resolutions

    print_subsection("REFERENCE Secondary Resolution Validation")

    results: list[dict[str, Any]] = []

    for usage in calc_usages:
        if usage.is_template:
            continue
        for binding in usage.bindings:
            if binding.binding_type != BindingType.REFERENCE:
                continue
            if not binding.source_path:
                continue

            mapping_key = f"{usage.qualified_name}|{binding.param_name}"
            ground_truth = binding_resolutions.get(mapping_key)

            if not ground_truth or ground_truth.resolution_type != BindingResolutionType.MODULE_OUTPUT:
                continue  # Only care about REF -> MODULE_OUTPUT cases

            # Extract leaf name from SYSML_QN source_path
            leaf_name = binding.source_path.rsplit("::", 1)[-1].strip("'")
            segments = usage.qualified_name.split("__")

            # Try single-segment candidates (each segment individually)
            candidates: dict[str, dict[str, Any]] = {}
            for i in range(1, len(segments)):
                candidate_part = segments[i]
                candidate_key = f"{candidate_part}.{leaf_name}"
                resolved = registry.resolve(candidate_key)
                label = f"segments[{i}]={candidate_part}"
                candidates[label] = {
                    "key": candidate_key,
                    "channel": resolved,
                    "match": resolved == ground_truth.qualified_name if resolved else False,
                }

            # Try dotted combinations (e.g., "solar_battery_plant.p_net_kw")
            for i in range(1, len(segments)):
                candidate_part = ".".join(segments[1:i+1])
                candidate_key = f"{candidate_part}.{leaf_name}"
                resolved = registry.resolve(candidate_key)
                label = f"dotted[1:{i+1}]={candidate_part}"
                candidates[label] = {
                    "key": candidate_key,
                    "channel": resolved,
                    "match": resolved == ground_truth.qualified_name if resolved else False,
                }

            # Find winners
            winners = [label for label, c in candidates.items() if c["match"]]

            results.append({
                "usage_qn": usage.qualified_name,
                "param_name": binding.param_name,
                "source_path": binding.source_path,
                "leaf_name": leaf_name,
                "gt_channel": ground_truth.qualified_name,
                "candidates": candidates,
                "winners": winners,
            })

    print(f"  REFERENCE -> MODULE_OUTPUT cases: {len(results)}")

    for r in results:
        usage_short = r["usage_qn"].split("__")[-1]
        print(f"\n  Usage: {usage_short} | Param: {r['param_name']} | Leaf: {r['leaf_name']}")
        print(f"  source_path: {r['source_path']}")
        print(f"  Ground truth channel: {r['gt_channel']}")
        print(f"  Candidate parent_parts:")
        for label, c in r["candidates"].items():
            status = "MATCH" if c["match"] else ("resolved-wrong" if c["channel"] else "None")
            print(f"    {label} -> {c['key']} -> {status}")
            if c["channel"]:
                print(f"      channel: {c['channel']}")
        if r["winners"]:
            print(f"  WINNER(S): {', '.join(r['winners'])}")
        else:
            print(f"  WINNER(S): NONE -- no candidate matches ground truth!")

    # Summary: what's the consistent winning pattern?
    if results:
        print(f"\n  PATTERN ANALYSIS:")
        winner_patterns: dict[str, int] = defaultdict(int)
        for r in results:
            for w in r["winners"]:
                # Normalize to pattern
                if w.startswith("segments["):
                    # Extract the index
                    idx = w.split("=")[0]
                    winner_patterns[idx] += 1
                else:
                    winner_patterns[w.split("=")[0]] += 1
        for pattern, count in sorted(winner_patterns.items(), key=lambda x: -x[1]):
            print(f"    {pattern}: wins {count} / {len(results)} cases")

        # Check if segments[-2] always wins
        seg_minus_2_wins = 0
        for r in results:
            segments = r["usage_qn"].split("__")
            seg_minus_2 = segments[-2] if len(segments) >= 2 else ""
            for w in r["winners"]:
                if seg_minus_2 in w:
                    seg_minus_2_wins += 1
                    break
        print(f"\n    segments[-2] (immediate parent) wins: {seg_minus_2_wins} / {len(results)}")

    return results


# ---------------------------------------------------------------------------
# instance_path Documentation
# ---------------------------------------------------------------------------

def document_instance_paths(
    data: dict[str, Any],
    registry: PrototypeRegistry,
    suite_name: str,
) -> None:
    """Document the instance_path format from ScopedAggregationData.

    Prints the raw instance_path, its segments, dotted form, and whether
    the design prefix is included. Also checks if the dotted form matches
    any Phase 1 CalcUsage Key_C prefix.
    """
    scoped_agg: list[ScopedAggregationData] = data["scoped_agg"]
    calc_usages: list[CalcUsageData] = data["calc_usages"]

    print_subsection("instance_path Documentation")

    if not scoped_agg:
        print("  (no scoped aggregation data for this model)")
        return

    # Collect unique instance_paths
    seen: set[str] = set()
    unique_aggs: list[ScopedAggregationData] = []
    for agg in scoped_agg:
        if agg.instance_path not in seen:
            seen.add(agg.instance_path)
            unique_aggs.append(agg)

    for i, agg in enumerate(unique_aggs):
        inst_parts = agg.instance_path.split("__")
        dotted_form = ".".join(inst_parts)
        dotted_no_prefix = ".".join(inst_parts[1:]) if len(inst_parts) > 1 else dotted_form

        print(f"  ScopedAggregation #{i+1}:")
        print(f"    instance_path:     {agg.instance_path}")
        print(f"    split('__'):       {inst_parts}")
        print(f"    dotted form:       {dotted_form}")
        print(f"    dotted (no prefix): {dotted_no_prefix}")
        print(f"    module_eqn:        {agg.module_eqn}")
        print(f"    attribute:         {agg.expression.attribute_name}")

        # Does instance_path include design prefix?
        # Check: is first segment a PartDef name (PascalCase) or PartUsage (snake_case)?
        first_seg = inst_parts[0] if inst_parts else ""
        is_design_prefix = any(c.isupper() for c in first_seg) and not first_seg.islower()
        print(f"    first_segment:     {first_seg} ({'DESIGN PREFIX (PascalCase)' if is_design_prefix else 'part_usage (snake_case)'})")

        # Check if dotted_no_prefix matches any Key_C prefix in the registry
        key_c_prefix_match = False
        for key, source in registry.key_source.items():
            if source.startswith("CalcUsage.Key_C") and key.startswith(dotted_no_prefix + "."):
                key_c_prefix_match = True
                break
        print(f"    Key_C prefix match: {'YES' if key_c_prefix_match else 'NO'}")

    # Overall observation
    includes_prefix = all(
        any(c.isupper() for c in agg.instance_path.split("__")[0])
        for agg in unique_aggs
    )

    print(f"\n  OBSERVATION:")
    print(f"    instance_path INCLUDES design prefix: {'YES' if includes_prefix else 'NO'}")
    print(f"    Separator: '__' (double underscore)")
    if includes_prefix:
        print(f"    Phase 1 aggregation Key_E uses instance_parts DIRECTLY (includes prefix)")
        print(f"    -> Key_E dotted form includes design prefix in first segment")
        print(f"    -> CHAIN binding source_paths do NOT include design prefix")
        print(f"    -> Key_E with prefix will NOT match CHAIN binding source_paths directly")
        print(f"    -> Phase 2 CHAIN alias scoping uses find_instance_paths_for_partdef()")
        print(f"       which strips the design prefix -> compatible with Key_C format")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print_section("SPIKE 8: OutputRegistry E2E Key Format Validation")

    suites = SPIKE_SUITES
    if len(sys.argv) > 1:
        paths = [Path(p) for p in sys.argv[1].split(",")]
        suites = [("cli_model", paths)]

    for suite_name, model_paths in suites:
        print_subsection(f"Model: {suite_name}")

        data = extract_all_data(suite_name, model_paths)
        if data is None:
            continue

        registry = build_phase1_registry(data, suite_name)

        # Phase 2/3/4 alias validation
        validate_phase2_chain_aliases(data, registry, suite_name)
        validate_phase3_expose_pure(data, registry, suite_name)
        validate_phase4_transitive_defaults(data, registry, suite_name)

        # Backtracker comparison + instance_path docs
        validate_chain_bindings(data, registry, suite_name)
        validate_reference_secondary_resolution(data, registry, suite_name)
        document_instance_paths(data, registry, suite_name)


if __name__ == "__main__":
    main()
