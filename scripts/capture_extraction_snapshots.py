#!/usr/bin/env python3
"""Capture extraction snapshots for all fixture models.

Runs extraction on each fixture model and serializes the output to JSON.
These snapshots enable downstream conformance tests (C03+) to run without
the JVM/SysIDE parser.

Models that can run the full pipeline use build_pipeline_context().
Models with unsupported binding types (e.g., EXPRESSION) use extraction-only
capture via _capture_extraction_only().

Usage:
    uv run python scripts/capture_extraction_snapshots.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path so tests.helpers is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from sysml_codegen.generation.initialization import (
    build_pipeline_context,
    extract_calculation_usages,
    extract_design_attributes,
    _extract_hierarchy_and_rewrite_bindings,
    _extract_and_filter_computed_attributes,
)
from tests.helpers.snapshot_serializer import serialize_extraction_snapshot, snapshot_to_json

FIXTURES_DIR = Path(__file__).parent.parent / "tests" / "fixtures"

# Models that support the full pipeline (build_pipeline_context)
MODELS = {
    "sample_model": FIXTURES_DIR / "sample_model",
    "solar_battery_model": FIXTURES_DIR / "solar_battery_model",
    "catf_mfe_model": FIXTURES_DIR / "catf_mfe_model",
    "attr_expr_probe": FIXTURES_DIR / "attr_expr_probe",
    "chain_spike_model": FIXTURES_DIR / "chain_spike_model",
    "issue22_model": FIXTURES_DIR / "issue22_model",
    "alias_agg_probe": FIXTURES_DIR / "alias_agg_probe",
}

# Models that need extraction-only capture (pipeline fails on unsupported binding types
# or CHAIN overrides that produce unresolvable source paths)
EXTRACTION_ONLY_MODELS = {
    "expression_binding_probe": FIXTURES_DIR / "expression_binding_probe",
    "chain_override_probe": FIXTURES_DIR / "chain_override_probe",
    "unresolvable_attr_probe": FIXTURES_DIR / "unresolvable_attr_probe",
}


def _capture_extraction_only(model_name: str, model_path: Path) -> dict:
    """Capture extraction data without building the full pipeline.

    Used for models with EXPRESSION bindings or other constructs that
    the backtracker/graph builder cannot yet resolve.
    """
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    extractor = SysMLDataExtractor([model_path])
    if not extractor.load_models():
        raise RuntimeError(f"Failed to load models from {model_path}")

    calc_defs = extractor.extract_calculation_definitions()
    calc_usages, _report = extract_calculation_usages(
        extractor.model, calc_defs=calc_defs
    )

    hierarchy_data, scoped_agg_data, chain_aliases = _extract_hierarchy_and_rewrite_bindings(
        extractor.model, calc_usages
    )

    design_attrs = extract_design_attributes(extractor.model)

    computed_attrs, expose_aliases = _extract_and_filter_computed_attributes(
        extractor.model, calc_usages, design_attrs
    )

    all_aliases = chain_aliases + expose_aliases

    return serialize_extraction_snapshot(
        model_name=model_name,
        calc_defs=calc_defs,
        calc_usages=calc_usages,
        design_attributes=design_attrs,
        hierarchy_data=hierarchy_data,
        aggregation_expressions=scoped_agg_data,
        computed_attributes=computed_attrs,
        channel_aliases=all_aliases,
        fixtures_dir=FIXTURES_DIR,
    )


def _capture_full_pipeline(model_name: str, model_path: Path) -> dict:
    """Capture extraction data via the full pipeline context."""
    ctx = build_pipeline_context([model_path])

    return serialize_extraction_snapshot(
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


def _save_and_report(model_name: str, model_path: Path, snapshot: dict) -> None:
    """Save snapshot to disk and print summary."""
    output_path = model_path / "extraction_snapshot.json"
    output_path.write_text(snapshot_to_json(snapshot))

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


def main() -> None:
    for model_name, model_path in MODELS.items():
        print(f"Processing {model_name} from {model_path}...")
        snapshot = _capture_full_pipeline(model_name, model_path)
        _save_and_report(model_name, model_path, snapshot)

    for model_name, model_path in EXTRACTION_ONLY_MODELS.items():
        print(f"Processing {model_name} (extraction-only) from {model_path}...")
        snapshot = _capture_extraction_only(model_name, model_path)
        _save_and_report(model_name, model_path, snapshot)

    print(f"\nDone. Snapshots saved to {FIXTURES_DIR}/*/extraction_snapshot.json")


if __name__ == "__main__":
    main()
