#!/usr/bin/env python3
"""Phase 5 scale measurement — the public generation path, timed.

One warm-up plus three measured runs per fixture, on `fusion_tea` and the two
accepted D-5 scale variants. The budget is the Item 7 spec's R10
(`.project/active/elaborator-cutover/spec.md`), whose thresholds are stated for
`fusion_tea`; the D-5 variants are measured against the same shape and reported
as their own declared baseline.

Each run measures, separately:

  live_elaborate  live load + elaboration (``elaborate_model_paths``)
  project         projection onto the ComputationGraph (``project``)
  capture         capture + envelope serialization (``capture_instance_graph_snapshot``)
  generate_live   generation + seal, ``run_codegen`` from ``--models``
  generate_snap   generation + seal, ``run_codegen`` from the sealed v6 snapshot

Nothing is written into the repository: every artifact goes to a temporary
directory that is removed afterwards.
"""

from __future__ import annotations

import json
import resource
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "src"))

from sysml_codegen.cli import GenerationConfig, run_codegen  # noqa: E402
from sysml_codegen.elaboration import project  # noqa: E402
from sysml_codegen.orchestration.elaborated_pipeline import (  # noqa: E402
    elaborate_model_paths,
)
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"
TARGETS = ["fusion_tea", "solar_battery_d5", "catf_mfe_d5"]


def _peak_rss_mib() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def one_run(name: str, workdir: Path) -> dict:
    fixture = FIXTURES / name
    timings: dict[str, float] = {}

    start = time.perf_counter()
    instance_graph = elaborate_model_paths([fixture])
    timings["live_elaborate_s"] = time.perf_counter() - start

    start = time.perf_counter()
    graph = project(instance_graph)
    timings["project_s"] = time.perf_counter() - start

    snapshot = workdir / f"{name}_snapshot.json"
    start = time.perf_counter()
    capture_instance_graph_snapshot([fixture], snapshot)
    timings["capture_s"] = time.perf_counter() - start

    start = time.perf_counter()
    run_codegen(
        GenerationConfig(
            output_path=workdir / f"{name}_live",
            models_path=fixture,
            package_name=f"{name}_pkg",
            overwrite=True,
        )
    )
    timings["generate_live_s"] = time.perf_counter() - start

    start = time.perf_counter()
    run_codegen(
        GenerationConfig(
            output_path=workdir / f"{name}_snap",
            from_snapshot=snapshot,
            package_name=f"{name}_pkg",
            overwrite=True,
        )
    )
    timings["generate_snapshot_s"] = time.perf_counter() - start

    return {
        "timings": {k: round(v, 4) for k, v in timings.items()},
        "counts": {
            "attrs": len(instance_graph.attrs),
            "calcs": len(instance_graph.calcs),
            "constraints": len(instance_graph.constraints),
            "occurrences": len(instance_graph.occurrences),
            "modules": len(graph.modules),
            "entry_points": sum(len(g.parameters) for g in graph.entry_point_groups),
        },
        "envelope_bytes": snapshot.stat().st_size,
        "peak_rss_mib_process_cumulative": round(_peak_rss_mib(), 1),
    }


def main() -> int:
    results: dict[str, dict] = {}
    with tempfile.TemporaryDirectory(prefix="phase5-scale-") as staging:
        workdir = Path(staging)
        for name in TARGETS:
            one_run(name, workdir)  # warm-up, discarded
            results[name] = {"runs": [one_run(name, workdir) for _ in range(3)]}
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
