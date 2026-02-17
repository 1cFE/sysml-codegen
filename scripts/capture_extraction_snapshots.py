#!/usr/bin/env python3
"""Capture extraction snapshots for all fixture models.

Runs the full extraction pipeline on each fixture model and serializes
the output to JSON. These snapshots enable downstream conformance tests
(C03+) to run without the JVM/SysIDE parser.

Usage:
    uv run python scripts/capture_extraction_snapshots.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path so tests.helpers is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from sysml_codegen.generation.initialization import build_pipeline_context
from tests.helpers.snapshot_serializer import serialize_extraction_snapshot, snapshot_to_json

FIXTURES_DIR = Path(__file__).parent.parent / "tests" / "fixtures"

MODELS = {
    "sample_model": FIXTURES_DIR / "sample_model",
    "solar_battery_model": FIXTURES_DIR / "solar_battery_model",
    "catf_mfe_model": FIXTURES_DIR / "catf_mfe_model",
    "attr_expr_probe": FIXTURES_DIR / "attr_expr_probe",
    "chain_spike_model": FIXTURES_DIR / "chain_spike_model",
    "issue22_model": FIXTURES_DIR / "issue22_model",
}


def main() -> None:
    for model_name, model_path in MODELS.items():
        print(f"Processing {model_name} from {model_path}...")
        ctx = build_pipeline_context([model_path])

        snapshot = serialize_extraction_snapshot(
            model_name=model_name,
            calc_defs=ctx.calc_defs,
            calc_usages=ctx.calc_usages,
            design_attributes=ctx.design_attributes,
            hierarchy_data=ctx.hierarchy_data,
            aggregation_expressions=ctx.aggregation_expressions,
            computed_attributes=ctx.computed_attributes,
            channel_aliases=ctx.channel_aliases,
            fixtures_dir=FIXTURES_DIR,
        )

        output_path = model_path / "extraction_snapshot.json"
        output_path.write_text(snapshot_to_json(snapshot))

        # Print summary
        n_calc_defs = len(snapshot["calc_defs"])
        n_calc_usages = len(snapshot["calc_usages"])
        n_bindings = sum(len(cu["bindings"]) for cu in snapshot["calc_usages"])
        n_design_attrs = sum(len(v) for v in snapshot["design_attributes"].values())
        n_redefs = len(snapshot["hierarchy_data"]["redefinitions"])
        n_agg = len(snapshot["aggregation_expressions"])
        n_computed = len(snapshot["computed_attributes"])
        n_aliases = len(snapshot["channel_aliases"])

        print(
            f"  -> {output_path.relative_to(FIXTURES_DIR)}\n"
            f"     {n_calc_defs} calc_defs, {n_calc_usages} calc_usages, "
            f"{n_bindings} bindings, {n_design_attrs} design_attrs\n"
            f"     {n_redefs} redefinitions, {n_agg} scoped_agg, "
            f"{n_computed} computed_attrs, {n_aliases} channel_aliases"
        )

    print(f"\nDone. Snapshots saved to {FIXTURES_DIR}/*/extraction_snapshot.json")


if __name__ == "__main__":
    main()
