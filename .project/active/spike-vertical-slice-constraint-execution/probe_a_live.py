"""S4 probe A — live leg: capture facts, lower, generate, prove liveness.

Run from the sysml-codegen repo root via the licensed agentic-mbse venv:

    UV_CACHE_DIR=/tmp/agentic-mbse-uv-cache \
    PYTHONPATH=/home/reid/1cfe/sysml-codegen/src \
    uv run --directory /home/reid/1cfe/agentic-mbse python \
      /home/reid/1cfe/sysml-codegen/.project/active/spike-vertical-slice-constraint-execution/probe_a_live.py

Produces out/snapshot/{extraction_snapshot.json,constraint_facts.s4.json} and
out/package_live/. Exits non-zero on any failed check.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import s4_lib
from s4_lib import FIXTURE, PACKAGE_NAME, SPIKE_DIR

OUT = SPIKE_DIR / "out"


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    failures: list[str] = []
    ok = lambda cond, msg: None if cond else failures.append(msg)  # noqa: E731

    from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
    from sysml_codegen.snapshot.capture import capture_snapshot

    print("=== live extraction ===")
    ctx = build_pipeline_context([FIXTURE])
    components = s4_lib.components_from_live_ctx(ctx)

    print("=== constraint fact capture (live) ===")
    facts_doc = s4_lib.capture_constraint_facts(ctx.extractor.model)
    print(json.dumps(facts_doc, indent=2)[:2000])
    ok(len(facts_doc["facts"]) == 1, "expected exactly one assert fact")
    fact = facts_doc["facts"][0]
    ok(fact["usage_name"] == "affordable", f"usage_name={fact['usage_name']}")
    ok(fact["is_negated"] is False, "polarity should be positive")
    ok(
        [i["instance_eqn"] for i in fact["owner_instances"]] == ["toy_plant__demo_plant"],
        f"owner instances: {fact['owner_instances']}",
    )
    ok(len(fact["formals"]) == 2, f"formals: {fact['formals']}")
    ok(len(fact["actuals"]) == 2, f"actuals: {fact['actuals']}")
    if failures:
        print("CAPTURE FAILURES:", failures)
        return 1

    print("=== snapshot + sidecar capture ===")
    snap_dir = OUT / "snapshot"
    snap_dir.mkdir(parents=True, exist_ok=True)
    capture_snapshot([FIXTURE], snap_dir / "extraction_snapshot.json")
    s4_lib.write_sidecar(facts_doc, snap_dir)

    # Generation consumes the SERIALIZED sidecar on both legs (round-trip
    # exercised here; byte-identity depends on it).
    facts_doc = s4_lib.load_sidecar(snap_dir)

    print("=== generate (live leg) ===")
    summary = s4_lib.generate_s4_package(components, facts_doc, OUT / "package_live")
    print(json.dumps(summary, indent=2))

    # --- liveness: pruning drops cost_calc without the constraint root -----
    control = summary["control_modules"]
    extended = summary["extended_modules"]
    ok(
        control == ["toy_plant__demo_plant__area_calc"],
        f"control graph should contain ONLY area_calc, got {control}",
    )
    ok(
        "toy_plant__demo_plant__cost_calc" in extended,
        f"cost_calc missing from extended graph: {extended}",
    )
    ok(
        summary["root_channels"] == ["toy_plant__demo_plant__cost_calc__cost"],
        f"constraint roots not derived from strict resolution: {summary['root_channels']}",
    )
    ok(
        "toy_plant__demo_plant__affordable" in extended
        and "constraint_report_aggregator" in extended,
        f"constraint/aggregator modules missing: {extended}",
    )
    ok(
        "toy_plant__Toy_Plant__plant_budget" in summary["entry_point_qns"],
        f"budget entry point missing: {summary['entry_point_qns']}",
    )
    ok(
        summary["constraint_ids"] == ["toy_plant__demo_plant__affordable"],
        f"constraint ids: {summary['constraint_ids']}",
    )

    (OUT / "summary_live.json").write_text(json.dumps(summary, indent=2) + "\n")

    print(f"\n{'FAILURES:' if failures else 'PROBE A PASSED'}")
    for f in failures:
        print(f"  - {f}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
