"""Throwaway: how long does fact extraction add to `sysml-codegen snapshot` capture?

Usage (licensed; from the sysml-codegen repo root):

    uv run --extra dev python .project/active/subset-profile-screen/spike-snapshot/time_capture.py

For each of the 23 committed snapshots' source trees (`sources.json`): runs today's
`capture_instance_graph_snapshot` into a temp file (best of 3), then, on the same staged model
capture would parse, times `extract_subset_facts` (best of 3). The extraction runs on the
model capture loaded, by wrapping `elaborate_admitted_sources`, so it is the real added cost,
not a second load. One warm-up capture first (SysIDE loads its standard library once).
"""

from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]

from agentic_mbse.sysml.subset_extraction import extract_subset_facts  # noqa: E402

import sysml_codegen.orchestration.elaborated_pipeline as ep  # noqa: E402
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot  # noqa: E402

EXTRACT_TIMES: list[float] = []
_original = ep.SysMLDataExtractor


class _TimingExtractor(_original):  # type: ignore[misc,valid-type]
    """Times extract_subset_facts on the model capture just loaded, then carries on."""

    def load_models(self):  # type: ignore[no-untyped-def]
        ok = super().load_models()
        if ok:
            best = float("inf")
            for _ in range(3):
                t0 = time.perf_counter()
                extract_subset_facts(self.model)
                best = min(best, time.perf_counter() - t0)
            EXTRACT_TIMES.append(best)
        return ok


def main() -> None:
    sources = json.loads((HERE / "sources.json").read_text())
    with tempfile.TemporaryDirectory() as tmp:
        capture_instance_graph_snapshot([REPO / "tests/fixtures/sample_model"], Path(tmp) / "w.json")
        print("| snapshot | capture today, s (best of 3) | extraction, s (best of 3) | added |")
        print("|---|---:|---:|---:|")
        tc = te = 0.0
        for snap, root in sources.items():
            name = Path(snap).parent.name
            ep.SysMLDataExtractor = _original
            best = float("inf")
            for _ in range(3):
                t0 = time.perf_counter()
                capture_instance_graph_snapshot([REPO / root], Path(tmp) / f"{name}.json")
                best = min(best, time.perf_counter() - t0)
            EXTRACT_TIMES.clear()
            ep.SysMLDataExtractor = _TimingExtractor
            capture_instance_graph_snapshot([REPO / root], Path(tmp) / f"{name}.x.json")
            ext = EXTRACT_TIMES[0]
            tc += best
            te += ext
            print(f"| {name} | {best:.3f} | {ext:.3f} | {ext / best:+.0%} |", flush=True)
        print(f"| **total** | {tc:.2f} | {te:.2f} | {te / tc:+.0%} |")


if __name__ == "__main__":
    sys.exit(main())
