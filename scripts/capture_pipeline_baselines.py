#!/usr/bin/env python3
"""Capture pipeline baselines: ComputationGraph JSON and registry __init__.py.

Captures deterministic pipeline output for diff-based regression detection.
These baselines sit alongside the existing YAML baselines.

Baselines are captured through the SNAPSHOT serialization boundary — the same
path the byte-exact conformance tests use (test_factory_purity rebuilds graphs
from committed extraction snapshots and compares raw model_dump against these
files).

Item 2 (snapshot-driven generation) revved the snapshot format: the loader now
re-absolutizes `source_file` and deserializes `compilation_results`. Two
deliberate, reviewed effects on these baselines follow, and are EXPECTED when
regenerating after re-capturing the extraction snapshots:
  - `compilability` flips from "unknown" to its real value and `auto_impl_context`
    becomes non-null for expression-bearing CalcUsage modules (SC-10).
  - `source_file` is relativized to the snapshot's own directory (basenames),
    stripped of the machine-specific absolute prefix so baselines stay portable.
Any OTHER field changing is an unintended output shift — investigate before
committing.

Requires no syside license (reads committed extraction snapshots).

Usage:
    uv run python scripts/capture_pipeline_baselines.py
"""

from __future__ import annotations

import ast as python_ast
import sys
from pathlib import Path

# Add project root to sys.path for template + tests package access
sys.path.insert(0, str(Path(__file__).parent.parent))

import jinja2

from sysml_codegen.generation.registry import (
    _collect_exit_point_primitive_types,
    generate_registry,
)

from sysml_codegen.snapshot import build_full_graph_from_snapshot

FIXTURES_DIR = Path(__file__).parent.parent / "tests" / "fixtures"
OUTPUT_DIR = FIXTURES_DIR / "baseline_outputs"

# baseline dir name -> extraction snapshot name
MODELS = {
    "solar_battery": "solar_battery_model",
    "catf_mfe": "catf_mfe_model",
    "attr_expr_probe": "attr_expr_probe",
    "chain_spike": "chain_spike_model",
    "sample_model": "sample_model",
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

    for model_name, snapshot_name in MODELS.items():
        print(f"Processing {model_name} from snapshot {snapshot_name}...")
        snapshot_path = FIXTURES_DIR / snapshot_name / "extraction_snapshot.json"
        graph, _inputs = build_full_graph_from_snapshot(snapshot_path)

        # Create output directory
        model_output_dir = OUTPUT_DIR / model_name
        model_output_dir.mkdir(parents=True, exist_ok=True)

        # 1. ComputationGraph JSON
        graph_json = graph.model_dump_json(indent=2) + "\n"
        # The loader re-absolutizes source_file to a machine-specific absolute
        # path (Item 2 D1). Strip the snapshot's own-directory prefix so the
        # committed baseline stays portable — relative basenames matching the
        # snapshot's stored form (no /home/... paths). source_file is the only
        # absolute path in the graph.
        graph_json = graph_json.replace(str(snapshot_path.parent) + "/", "")
        graph_path = model_output_dir / "computation_graph.json"
        graph_path.write_text(graph_json)

        n_modules = len(graph.modules)
        n_exec = len(graph.execution_order)
        print(f"  -> computation_graph.json ({n_modules} modules, {n_exec} exec_order)")

        # 2. Registry __init__.py
        exit_point_types = _collect_exit_point_primitive_types(graph.modules)
        registry_code = generate_registry(
            graph=graph,
            package_name=model_name,
            template_env=template_env,
            output_path=model_output_dir,
            exit_point_primitive_types=exit_point_types,
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
