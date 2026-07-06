#!/usr/bin/env python3
"""Capture baseline pipeline YAML for the tracked models.

Renders pipeline YAML from committed extraction snapshots (the same
snapshot-driven path as ``capture_pipeline_baselines.py``) and saves to
tests/fixtures/baseline_yaml/.

Item 11 (F-B) moved this off the live ``build_pipeline_context`` path onto
``build_full_graph_from_snapshot``: it is now **license-free** and the YAML is
rendered from the exact graph the graph baseline captures, so the two can never
disagree. Verified byte-identical to the prior live-captured baselines for every
unaffected model; the only intended diff is the Item 11 exit-point filename
renames (an aliased channel's output file moves ``{channel}.json`` →
``{instance_path}__{alias_name}.json``).

Usage:
    uv run python scripts/capture_baseline_yaml.py
"""

from __future__ import annotations

from pathlib import Path

import jinja2

from sysml_codegen.generation.pipeline import generate_pipeline_yaml
from sysml_codegen.snapshot import build_full_graph_from_snapshot

FIXTURES_DIR = Path(__file__).parent.parent / "tests" / "fixtures"
OUTPUT_DIR = FIXTURES_DIR / "baseline_yaml"

# display name -> extraction snapshot name. wi014_toy (shape A) added for Item 11
# so the shape-A exit-point rename (total_cost) has a committed YAML baseline.
MODELS = {
    "solar_battery": "solar_battery_model",
    "attr_expr_probe": "attr_expr_probe",
    "chain_spike": "chain_spike_model",
    "sample_model": "sample_model",
    "wi014_toy": "wi014_toy",
}


def _get_template_env() -> jinja2.Environment:
    template_dir = Path(__file__).parent.parent / "src" / "sysml_codegen" / "templates"
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    template_env = _get_template_env()

    for model_name, snapshot_name in MODELS.items():
        print(f"Processing {model_name} from snapshot {snapshot_name}...")
        snapshot_path = FIXTURES_DIR / snapshot_name / "extraction_snapshot.json"
        graph, _inputs = build_full_graph_from_snapshot(snapshot_path)
        yaml_content = generate_pipeline_yaml(
            graph=graph,
            package_name=model_name,
            template_env=template_env,
        )
        output_path = OUTPUT_DIR / f"{model_name}.yaml"
        output_path.write_text(yaml_content)
        print(f"  -> {output_path} ({len(yaml_content)} bytes, {len(graph.modules)} modules)")

    print(f"\nDone. Baselines saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
