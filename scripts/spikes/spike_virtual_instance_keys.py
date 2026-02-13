#!/usr/bin/env python3
"""Spike 2: Virtual CalcUsage Instance Names and Output Keys.

For virtual (template-expanded) CalcUsages, determines what lookup keys
downstream CHAIN bindings use to reference their outputs, and whether
those keys match short or qualified instance_name forms.

Answers design_revision_comments.md Issue 1
(OutputRegistry doesn't solve virtual instance_name problem).

Usage:
    uv run python scripts/spikes/spike_virtual_instance_keys.py
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _helpers import (
    DEFAULT_SUITES,
    load_model,
    print_section,
    print_subsection,
    print_table,
)
from sysml_codegen.extraction.usage_extractor import (
    CalcUsageData,
    extract_calculation_usages,
)
from agentic_mbse.sysml.types import BindingType


# ---------------------------------------------------------------------------
# Key Building
# ---------------------------------------------------------------------------

def short_instance_name(instance_name: str) -> str:
    """Extract the short (leaf) instance name from a qualified name."""
    if "__" in instance_name:
        return instance_name.rsplit("__", 1)[-1]
    return instance_name


def build_output_keys(
    usage: CalcUsageData,
    output_names: list[str],
) -> list[dict[str, str]]:
    """Build short_key and full_key for each output of a CalcUsage."""
    short = short_instance_name(usage.instance_name)
    result = []
    for out_name in output_names:
        result.append({
            "output_name": out_name,
            "short_key": f"{short}.{out_name}",
            "full_key": f"{usage.instance_name}.{out_name}",
            "short_instance": short,
            "full_instance": usage.instance_name,
        })
    return result


# ---------------------------------------------------------------------------
# Spike Logic
# ---------------------------------------------------------------------------

def run_spike_for_model(
    suite_name: str,
    model_paths: list[Path],
) -> None:
    """Run Spike 2 on a single model suite."""
    print_subsection(f"Model: {suite_name}")

    model, adapter, extractor = load_model(model_paths)
    if model is None:
        print("  SKIPPED: model failed to load")
        return

    # Extract CalcDefs and build lookup
    calc_defs = extractor.extract_calculation_definitions()
    calc_def_map = {cd.name: cd for cd in calc_defs}
    print(f"  CalcDefs: {len(calc_defs)}")

    # Extract expanded CalcUsages
    usages, _ = extract_calculation_usages(
        model, calc_defs=calc_defs, expand_templates=True,
    )
    print(f"  CalcUsages (expanded): {len(usages)}")

    # --- Part 1: Build output key catalog ---
    # Maps each possible key -> (usage instance_name, output_name)
    key_catalog: dict[str, tuple[str, str]] = {}
    # All output keys per usage
    usage_output_keys: dict[str, list[dict[str, str]]] = {}

    print("\n  PRODUCER OUTPUT KEYS:")

    for usage in usages:
        cd = calc_def_map.get(usage.calc_def_name)
        if cd is None:
            print(f"\n    CalcUsage: {usage.instance_name} -- CalcDef {usage.calc_def_name!r} NOT FOUND")
            continue

        output_names = [attr.name for attr in cd.output_attributes]
        if not output_names:
            continue

        keys = build_output_keys(usage, output_names)
        usage_output_keys[usage.instance_name] = keys

        is_virtual = "__" in usage.instance_name
        label = "VIRTUAL" if is_virtual else "concrete"

        print(f"\n    CalcUsage [{label}]: {usage.instance_name}")
        if is_virtual:
            print(f"      short_instance: {short_instance_name(usage.instance_name)}")

        for k in keys:
            print(f"      Output: {k['output_name']}")
            print(f"        short_key: {k['short_key']}")
            if is_virtual:
                print(f"        full_key:  {k['full_key']}")

            # Register both keys in catalog
            key_catalog[k["short_key"]] = (usage.instance_name, k["output_name"])
            key_catalog[k["full_key"]] = (usage.instance_name, k["output_name"])

    # --- Part 2: Match consumer CHAIN bindings against producer keys ---
    print("\n  CONSUMER BINDING -> PRODUCER KEY MATCHING:")

    match_rows: list[list[str]] = []
    mismatch_rows: list[list[str]] = []

    for usage in usages:
        chain_bindings = [b for b in usage.bindings if b.binding_type == BindingType.CHAIN]
        if not chain_bindings:
            continue

        print(f"\n    Consumer: {usage.instance_name}")

        for b in chain_bindings:
            source_path = b.source_path or ""

            # Try to match against catalog
            match_type = "NO_MATCH"
            matched_producer = ""

            if source_path in key_catalog:
                matched_producer = key_catalog[source_path][0]
                # Determine if it matched via short or full key
                if "__" in matched_producer and not source_path.startswith(matched_producer):
                    match_type = "SHORT_KEY"
                else:
                    match_type = "FULL_KEY"

            # Also try extracting the instance segment and matching
            if "." in source_path:
                instance_seg = source_path.split(".")[0]
                # Check if instance_seg matches any usage's short or full instance_name
                matching_usages = [
                    u for u in usages
                    if u.instance_name == instance_seg
                    or short_instance_name(u.instance_name) == instance_seg
                ]
                if matching_usages:
                    producer = matching_usages[0]
                    is_short_match = (
                        producer.instance_name != instance_seg
                        and short_instance_name(producer.instance_name) == instance_seg
                    )
                    if match_type == "NO_MATCH":
                        match_type = "SHORT_INSTANCE" if is_short_match else "FULL_INSTANCE"
                    matched_producer = producer.instance_name

            print(
                f"      Binding: {b.param_name} <- source_path={b.source_path!r}"
                f"  match={match_type}"
            )
            if matched_producer:
                print(f"        producer: {matched_producer}")

            row = [
                suite_name, usage.instance_name, b.param_name,
                source_path, match_type, matched_producer,
            ]
            match_rows.append(row)
            if match_type == "NO_MATCH":
                mismatch_rows.append(row)

    # --- Part 3: Summary ---
    print_subsection(f"Match Summary for {suite_name}")
    print_table(
        ["Model", "Consumer", "Param", "source_path", "Match", "Producer"],
        match_rows,
    )

    if mismatch_rows:
        print_subsection(f"MISMATCHES for {suite_name} (source_path matches neither key format)")
        print_table(
            ["Model", "Consumer", "Param", "source_path", "Match", "Producer"],
            mismatch_rows,
        )
    else:
        print(f"\n  No mismatches found for {suite_name}.")


def main() -> None:
    print_section("SPIKE 2: Virtual Instance Names and Output Keys")

    suites = [s for s in DEFAULT_SUITES if s[0] in ("solar_battery", "e2e_attr_expr")]
    if len(sys.argv) > 1:
        paths = [Path(p) for p in sys.argv[1].split(",")]
        suites = [("cli_model", paths)]

    for suite_name, model_paths in suites:
        run_spike_for_model(suite_name, model_paths)


if __name__ == "__main__":
    main()
