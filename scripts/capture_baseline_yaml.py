#!/usr/bin/env python3
"""Capture baseline pipeline YAML for all 4 models.

One-time script for Item 3 Phase 1: generates pipeline YAML from the current
codebase (pre-integration) and saves to tests/fixtures/baseline_yaml/.

Usage:
    uv run python scripts/capture_baseline_yaml.py
"""

from __future__ import annotations

from pathlib import Path

import jinja2

from sysml_codegen.generation.initialization import build_pipeline_context
from sysml_codegen.generation.pipeline import generate_pipeline_yaml

FIXTURES_DIR = Path(__file__).parent.parent / "tests" / "fixtures"
OUTPUT_DIR = FIXTURES_DIR / "baseline_yaml"

MODELS = {
    "solar_battery": FIXTURES_DIR / "solar_battery_model",
    "attr_expr_probe": FIXTURES_DIR / "attr_expr_probe",
    "chain_spike": FIXTURES_DIR / "chain_spike_model",
    "sample_model": FIXTURES_DIR / "sample_model",
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

    for model_name, model_path in MODELS.items():
        print(f"Processing {model_name} from {model_path}...")
        ctx = build_pipeline_context([model_path])
        yaml_content = generate_pipeline_yaml(
            graph=ctx.computation_graph,
            package_name=model_name,
            template_env=template_env,
        )
        output_path = OUTPUT_DIR / f"{model_name}.yaml"
        output_path.write_text(yaml_content)
        print(f"  -> {output_path} ({len(yaml_content)} bytes, {len(ctx.computation_graph.modules)} modules)")

    print(f"\nDone. Baselines saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
