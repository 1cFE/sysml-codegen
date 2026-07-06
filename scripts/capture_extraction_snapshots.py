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
    uv run python scripts/capture_extraction_snapshots.py --fixtures NAME[,NAME...]

``--fixtures`` restricts the run to the named fixtures (keyed by MODEL NAME — the
keys of MODELS / EXTRACTION_ONLY_MODELS), so each capture step touches exactly the
fixtures it names and byte-identity of the rest is checkable via ``git status``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to sys.path so tests.helpers is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

import json

from scripts.capture_filter import select_fixtures

from sysml_codegen.analysis.parameter_groups import extract_design_attributes
from sysml_codegen.extraction.usage_extractor import extract_calculation_usages
from sysml_codegen.orchestration.pipeline_builder import (
    _extract_and_filter_computed_attributes,
    _extract_hierarchy_and_rewrite_bindings,
)
from sysml_codegen.snapshot import (
    capture_snapshot,
    serialize_extraction_snapshot,
    snapshot_to_json,
)

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
    "return_styles": FIXTURES_DIR / "return_styles",
    "retype_model": FIXTURES_DIR / "retype_model",
    # Plant-idiom conformance fixtures (Item 8, UPSTREAM-FINDINGS). Both build the
    # full graph — the unresolved cross-part inputs fall to Step-4 fallbacks rather
    # than stopping assembly (like catf_mfe's dangling cryo_load.magnet_volume).
    "wi014_toy": FIXTURES_DIR / "wi014_toy",
    "ife_plant": FIXTURES_DIR / "ife_plant",
    # Registered so the capture script can reproduce this snapshot (Item 5
    # committed it without registering it here — permanent fixture drift). Its
    # committed paths are repo-relative; re-capture brings it to the canonical
    # script form (absolute design_attributes keys, model-relative source_file).
    "quoted_owner_formula": FIXTURES_DIR / "quoted_owner_formula",
    # Stage-(b) companion fixtures (Item 10, UPSTREAM-FINDINGS). Each isolates one
    # cross-part channel mechanism the Phase-7 precedence resolver flips (D8):
    #   spec_chain_channel      — specialized-def :>> nested calc output -> cross-part
    #                             consumer (the gamma -> lcoe edge, SC-2)
    #   sibling_channel_ambiguity — two same-type siblings; consumer disambiguates to
    #                             the correct instance-scoped channel (SC-3)
    #   self_named_rescue       — self-named `in x = x` with a resolvable upstream (SC-4)
    # Captured current-incomplete FIRST (Item 8 pattern) so each Phase-7 flip is a
    # separately-attributable diff. They carry `reference_chain` (recapture set, M6).
    "spec_chain_channel": FIXTURES_DIR / "spec_chain_channel",
    "sibling_channel_ambiguity": FIXTURES_DIR / "sibling_channel_ambiguity",
    "self_named_rescue": FIXTURES_DIR / "self_named_rescue",
    # Two-level specialization fixture (Item 10 Phase 8, C-then-B ruling). Reproduces
    # the REAL fusion-tea hif_plant shape: a part USAGE typed by the BASE def
    # ('IFE Power Plant') with an inline `part :>> driver : 'HIF Driver'` retype on the
    # usage; lcoe_calc inherited from the base. The usage-level retype is NOT indexed in
    # usage_type_map (keyed by part-DEF QN), so the declaring-base-def type-select misses
    # 'HIF Driver' -> the gamma -> lcoe edge stays unwired. This is the WI-015 gap.
    "spec_chain_twolevel": FIXTURES_DIR / "spec_chain_twolevel",
    # Plant-Value & Blind-Spot fixtures (PIPELINE-TRUTH Item 1). All three build a
    # full graph:
    #   plant_values          — the headline; its 3 cross-part plant-calc inputs fall
    #                           to valueless Step-4 EPs and trip V11 on all three
    #                           value-provision mechanisms (the "before" state Item 2 flips).
    #   plant_value_shapes    — 9 secondary fusion-tea syntactic shapes (SC-3).
    #   deep_cross_scope_probe — committed for the first time (D1-F6 drift); full-pipeline.
    "plant_values": FIXTURES_DIR / "plant_values",
    "plant_value_shapes": FIXTURES_DIR / "plant_value_shapes",
    "deep_cross_scope_probe": FIXTURES_DIR / "deep_cross_scope_probe",
}

# Models that need extraction-only capture (pipeline fails on unsupported binding types
# or CHAIN overrides that produce unresolvable source paths)
EXTRACTION_ONLY_MODELS = {
    "expression_binding_probe": FIXTURES_DIR / "expression_binding_probe",
    "chain_override_probe": FIXTURES_DIR / "chain_override_probe",
    "unresolvable_attr_probe": FIXTURES_DIR / "unresolvable_attr_probe",
    # Self-named-binding trap (Item 8, mechanism D). Extraction-only: the degenerate
    # self-reference is fully visible in extraction; no pipeline baseline is needed.
    # Kept isolated (own fixture dir) so its failure mode cannot poison ife_plant.
    "self_named_binding_trap": FIXTURES_DIR / "self_named_binding_trap",
    # Aggregation-literal dispatch probe (PIPELINE-TRUTH Item 8, Row D / REQ-AST-10).
    # Extraction-only: the literal-bearing aggregation is fully visible in extraction;
    # no pipeline baseline is needed. Isolated so its shape cannot poison other fixtures.
    "agg_literal_probe": FIXTURES_DIR / "agg_literal_probe",
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
        compilation_results={},  # extraction-only: no graph, no compilation
        # Manifest is model-wide and does not need the graph, so the
        # extraction-only path must carry it too — otherwise a constraint-bearing
        # extraction-only fixture would diverge live-vs-snapshot (INV-B, Item 4).
        constraint_manifest=extractor.collect_constraint_manifest(),
        output_dir=model_path,
    )


def _report(model_path: Path, snapshot: dict) -> None:
    """Print a one-model capture summary."""
    output_path = model_path / "extraction_snapshot.json"
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


def main(requested: str | None = None) -> None:
    # `--fixtures` restricts the run; unknown names fail loud before any capture.
    selected = select_fixtures(list(MODELS) + list(EXTRACTION_ONLY_MODELS), requested)

    # Full-pipeline models go through the promoted, supported capture path so
    # there is no second copy of the capture logic (INV-3 spirit).
    for model_name, model_path in MODELS.items():
        if model_name not in selected:
            continue
        print(f"Processing {model_name} from {model_path}...")
        out = capture_snapshot([model_path], model_path / "extraction_snapshot.json")
        _report(model_path, json.loads(out.read_text()))

    # Extraction-only fixtures cannot build the full pipeline; capture directly
    # and write the summary here.
    for model_name, model_path in EXTRACTION_ONLY_MODELS.items():
        if model_name not in selected:
            continue
        print(f"Processing {model_name} (extraction-only) from {model_path}...")
        snapshot = _capture_extraction_only(model_name, model_path)
        (model_path / "extraction_snapshot.json").write_text(snapshot_to_json(snapshot))
        _report(model_path, snapshot)

    print(f"\nDone. Snapshots saved to {FIXTURES_DIR}/*/extraction_snapshot.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixtures",
        help="comma-separated fixture MODEL names to capture (default: all)",
    )
    args = parser.parse_args()
    try:
        main(args.fixtures)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
