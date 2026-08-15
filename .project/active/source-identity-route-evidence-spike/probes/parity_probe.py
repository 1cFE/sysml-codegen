#!/usr/bin/env python3
"""Live vs snapshot vs relocated-snapshot parity for the source-identity routes.

SOURCE-IDENTITY Item 2, licensed leg. For each parity fixture, builds the pipeline
three ways and compares the public entry-point topology (qualified name, entry
type, default) plus the state of the known fan-out bindings:

  live       build_pipeline_context([tests/fixtures/<name>])
  snapshot   build_pipeline_context_from_snapshot(committed snapshot, in place)
  relocated  same snapshot copied alone into a temp dir, rebuilt from there

Run (license required for the live leg):
    set -a; source ~/1cfe/agentic-mbse/.env; set +a
    uv run python .project/active/source-identity-route-evidence-spike/probes/parity_probe.py

Writes raw per-fixture evidence to probes/raw/parity_<fixture>.json.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tests"))

import logging

logging.disable(logging.WARNING)

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.orchestration.snapshot_context import (
    build_pipeline_context_from_snapshot,
)

FIXTURES = ["fusion_tea", "ife_plant", "shared_producer", "solar_battery_model"]
RAW_DIR = Path(__file__).parent / "raw"

# The fan-out cells whose binding state must agree across routes.
WATCHED_BINDINGS = {
    "fusion_tea": [
        ("hif_plant_pkg__hif_plant__lcoe_calc", "gain"),
        ("hif_plant_pkg__hif_plant__recirc_calc", "gain"),
    ],
    "ife_plant": [
        ("IfePlantDesign__baseline_plant__lcoe_calc", "gain"),
        ("IfePlantDesign__hif_plant__driver__base_power_calc", "bank_energy"),
    ],
    "shared_producer": [("SharedProducer__the_rig__scaler", "gain")],
    "solar_battery_model": [
        (
            "SolarBatteryDesign__solar_battery_plant__battery_system__battery_bos"
            "__cost_model",
            "pack_count",
        ),
    ],
}


def topology(ctx) -> dict[str, tuple[str, object]]:
    return {
        ep.qualified_name: (str(ep.entry_type), ep.default_value)
        for gr in ctx.computation_graph.entry_point_groups
        for ep in gr.parameters
    }


def binding_states(ctx, name: str) -> dict[str, dict]:
    out = {}
    for usage_qn, param in WATCHED_BINDINGS.get(name, []):
        for cu in ctx.calc_usages:
            if cu.qualified_name == usage_qn:
                for b in cu.bindings:
                    if b.param_name == param:
                        out[f"{usage_qn}|{param}"] = {
                            "binding_type": str(b.binding_type),
                            "source_path": b.source_path,
                            "literal_value": b.literal_value,
                            "written_reference": b.written_reference,
                        }
    return out


def main() -> int:
    RAW_DIR.mkdir(exist_ok=True)
    failures = 0
    for name in FIXTURES:
        fixture_dir = REPO / "tests" / "fixtures" / name
        snap_path = fixture_dir / "extraction_snapshot.json"

        live_ctx = build_pipeline_context([fixture_dir])
        snap_ctx = build_pipeline_context_from_snapshot(snap_path)
        with tempfile.TemporaryDirectory(prefix=f"reloc_{name}_") as td:
            reloc = Path(td) / "extraction_snapshot.json"
            shutil.copy2(snap_path, reloc)
            reloc_ctx = build_pipeline_context_from_snapshot(reloc)

        routes = {"live": live_ctx, "snapshot": snap_ctx, "relocated": reloc_ctx}
        topos = {r: topology(c) for r, c in routes.items()}
        binds = {r: binding_states(c, name) for r, c in routes.items()}

        ok = topos["live"] == topos["snapshot"] == topos["relocated"] and (
            binds["live"] == binds["snapshot"] == binds["relocated"]
        )
        verdict = "PARITY" if ok else "DIVERGED"
        if not ok:
            failures += 1
        print(f"{name:25s} {verdict}  eps={len(topos['live'])}")
        if not ok:
            for r in ("snapshot", "relocated"):
                extra = set(topos[r]) - set(topos["live"])
                missing = set(topos["live"]) - set(topos[r])
                changed = {
                    q
                    for q in set(topos[r]) & set(topos["live"])
                    if topos[r][q] != topos["live"][q]
                }
                if extra or missing or changed:
                    print(f"    vs {r}: +{sorted(extra)} -{sorted(missing)} ~{sorted(changed)}")
                if binds[r] != binds["live"]:
                    print(f"    binding diff vs {r}: {binds[r]} != {binds['live']}")

        (RAW_DIR / f"parity_{name}.json").write_text(
            json.dumps(
                {"fixture": name, "verdict": verdict, "topology": topos, "bindings": binds},
                indent=1,
                default=str,
            )
        )
    print("RESULT:", "ALL PARITY" if failures == 0 else f"{failures} DIVERGED")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
