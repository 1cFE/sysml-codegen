#!/usr/bin/env python3
"""Capture pipeline baselines: ComputationGraph JSON and registry __init__.py.

Captures deterministic pipeline output for diff-based regression detection.
These baselines sit alongside the existing YAML baselines.

Usage:
    uv run python scripts/capture_pipeline_baselines.py
"""

from __future__ import annotations

import ast as python_ast
import sys
from pathlib import Path

# Add project root to sys.path for template access
sys.path.insert(0, str(Path(__file__).parent.parent))

import jinja2

from sysml_codegen.generation.initialization import build_pipeline_context
from sysml_codegen.generation.registry import generate_registry_function

FIXTURES_DIR = Path(__file__).parent.parent / "tests" / "fixtures"
OUTPUT_DIR = FIXTURES_DIR / "baseline_outputs"

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
    template_env = _get_template_env()

    for model_name, model_path in MODELS.items():
        print(f"Processing {model_name} from {model_path}...")
        ctx = build_pipeline_context([model_path])

        # Create output directory
        model_output_dir = OUTPUT_DIR / model_name
        model_output_dir.mkdir(parents=True, exist_ok=True)

        # 1. ComputationGraph JSON
        graph_json = ctx.computation_graph.model_dump_json(indent=2)
        graph_path = model_output_dir / "computation_graph.json"
        graph_path.write_text(graph_json)

        n_modules = len(ctx.computation_graph.modules)
        n_exec = len(ctx.computation_graph.execution_order)
        print(f"  -> computation_graph.json ({n_modules} modules, {n_exec} exec_order)")

        # 2. Registry __init__.py
        registry_code = generate_registry_function(
            calc_defs=ctx.calc_defs,
            package_name=model_name,
            template_env=template_env,
            output_path=model_output_dir,
            entry_point_groups=ctx.computation_graph.entry_point_groups,
            exit_point_primitive_types=None,
            computed_attributes=ctx.computed_attributes,
            aggregation_data=ctx.aggregation_expressions,
        )
        registry_path = model_output_dir / "registry_init.py"
        registry_path.write_text(registry_code)

        # Verify syntactically valid Python
        try:
            python_ast.parse(registry_code)
            syntax_ok = "valid"
        except SyntaxError as e:
            syntax_ok = f"INVALID: {e}"

        print(f"  -> registry_init.py ({len(registry_code)} bytes, syntax: {syntax_ok})")

    print(f"\nDone. Baselines saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
