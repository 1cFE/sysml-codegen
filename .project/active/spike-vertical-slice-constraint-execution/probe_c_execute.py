"""S4 probe C — execute the sealed package under the REAL TEAx runtime (simkit).

simkit code comes from the teax working tree; the host venv is agentic-mbse's
(it carries pydantic/yaml/pandas/dotenv/pyarrow — teax's own .venv is not
provisioned and `uv run` fails on the workspace root build):

    UV_CACHE_DIR=/tmp/agentic-mbse-uv-cache \
    uv run --directory /home/reid/1cfe/agentic-mbse python \
      /home/reid/1cfe/sysml-codegen/.project/active/spike-vertical-slice-constraint-execution/probe_c_execute.py

Checks (S4 pass criteria 1):
- seal verifies before execution;
- satisfied point (budget 5000): run completes, report all_satisfied, margin +2000;
- violated point (budget 2500): run COMPLETES (violation is evidence, not an
  exception), report violation, margin -500;
- ordinary outputs (area 12, cost 3000) identical across both points;
- report artifact is written beside the ordinary outputs on the file-backed run;
- aggregator exact schema: a missing per-assertion field is a schema failure.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

SPIKE_DIR = Path(__file__).resolve().parent
OUT = SPIKE_DIR / "out"
TEAX_SIMKIT = Path("/home/reid/1cfe/teax/packages/teax-simkit")
PACKAGE_NAME = "wi014_s4"

sys.path.insert(0, str(TEAX_SIMKIT))


def verify_seal(out_dir: Path) -> None:
    """Verify the PackageContract on load (inlined from s4_lib to keep this
    probe free of codegen imports — the study side must not import codegen)."""
    seal_path = out_dir / "contracts" / "package_contract.json"
    seal = json.loads(seal_path.read_text())
    for rel, expected in seal["artifact_hashes"].items():
        actual = hashlib.sha256((out_dir / rel).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f"seal violation: {rel} hash mismatch")
    extras = {
        str(p.relative_to(out_dir))
        for p in out_dir.rglob("*")
        if p.is_file() and p != seal_path and "__pycache__" not in p.parts
    } - set(seal["artifact_hashes"])
    if extras:
        raise RuntimeError(f"seal violation: unhashed files present: {sorted(extras)}")

BUDGET_QN = "toy_plant__Toy_Plant__plant_budget"
AREA_CH = "toy_plant__demo_plant__area_calc__area"
COST_CH = "toy_plant__demo_plant__cost_calc__cost"
EVAL_CH = "toy_plant__demo_plant__affordable__evaluation"
REPORT_CH = "constraint_report"


def stage_package(src: Path, dest: Path, budget: float | None) -> Path:
    """Copy the sealed package for one run; optionally override plant_budget."""
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    if budget is not None:
        for jf in (dest / "inputs").glob("*.json"):
            data = json.loads(jf.read_text())
            if BUDGET_QN in data:
                data[BUDGET_QN] = budget
                jf.write_text(json.dumps(data, indent=2) + "\n")
                break
        else:
            raise RuntimeError(f"{BUDGET_QN} not found in any inputs JSON")
    return dest


def run_point(pkg_dir: Path, out_dir: Path):
    import importlib

    parent = str(pkg_dir.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    # fresh import per staged copy is unnecessary: both copies are byte-identical
    # modulo the inputs JSON, which is read at execution time, not import time.
    pkg = importlib.import_module(pkg_dir.name)

    from simkit.core.pipeline import execute_pipeline

    registry = getattr(pkg, f"create_{PACKAGE_NAME}_registry")()
    yaml_path = pkg_dir / "pipelines" / "pipeline.yaml"
    return execute_pipeline(
        yaml_path,
        out_dir,
        registry=registry,
        custom_schema_types=list(pkg.CUSTOM_SCHEMA_TYPES),
    )


def main() -> int:
    failures: list[str] = []
    ok = lambda cond, msg: None if cond else failures.append(msg)  # noqa: E731

    sealed = OUT / "package_live"
    print("=== seal verification ===")
    verify_seal(sealed)
    print("  seal intact")

    stage_root = OUT / "exec"
    stage_root.mkdir(parents=True, exist_ok=True)
    # Both truth points execute ONE package (same import); only the inputs
    # JSON differs — the false point overrides plant_budget to 2500.
    pkg_dir = stage_package(sealed, stage_root / PACKAGE_NAME, budget=None)

    print("=== satisfied point (budget 5000) ===")
    res_true = run_point(pkg_dir, stage_root / "run_true")
    outs_true = dict(res_true.outputs)
    print("  channels:", sorted(outs_true))

    ev = outs_true[EVAL_CH]
    rep = outs_true[REPORT_CH]
    ok(outs_true[AREA_CH].root == 12.0, f"area={outs_true[AREA_CH]}")
    ok(outs_true[COST_CH].root == 3000.0, f"cost={outs_true[COST_CH]}")
    ok(ev.status == "satisfied" and ev.actual_value is True, f"eval={ev}")
    ok(ev.margin == 2000.0, f"margin={ev.margin}")
    ok(ev.observed == {"cost": 3000.0, "budget": 5000.0}, f"observed={ev.observed}")
    ok(rep.headline == "all_satisfied" and rep.assessed_count == 1, f"report={rep}")
    ok(
        rep.results[0].constraint_id == "toy_plant__demo_plant__affordable",
        f"report ids={[r.constraint_id for r in rep.results]}",
    )
    print(f"  eval: {ev.status} margin={ev.margin}; headline={rep.headline}")

    print("=== violated point (budget 2500) ===")
    stage_package(sealed, stage_root / PACKAGE_NAME, budget=2500.0)
    try:
        res_false = run_point(pkg_dir, stage_root / "run_false")
    except Exception as e:  # noqa: BLE001
        failures.append(f"violated point RAISED (must complete as evidence): {e!r}")
        res_false = None

    if res_false is not None:
        outs_false = dict(res_false.outputs)
        ev_f = outs_false[EVAL_CH]
        rep_f = outs_false[REPORT_CH]
        ok(ev_f.status == "violated" and ev_f.actual_value is False, f"eval={ev_f}")
        ok(ev_f.margin == -500.0, f"margin={ev_f.margin}")
        ok(rep_f.headline == "violation", f"headline={rep_f.headline}")
        # ordinary outputs identical across truth values
        ok(
            outs_false[AREA_CH].root == outs_true[AREA_CH].root
            and outs_false[COST_CH].root == outs_true[COST_CH].root,
            "ordinary outputs differ across truth values",
        )
        print(f"  eval: {ev_f.status} margin={ev_f.margin}; headline={rep_f.headline}")

        # report artifact persisted beside ordinary outputs (file-backed run)
        manifest = res_false.manifest
        by_channel = {a.channel: a for a in manifest.artifacts}
        ok(
            by_channel.get(REPORT_CH) is not None and by_channel[REPORT_CH].produced,
            f"report artifact not persisted: {manifest}",
        )
        run_dirs = list((stage_root / "run_false").glob("*/constraint_report.json"))
        ok(bool(run_dirs), "constraint_report.json not found in run dir")
        if run_dirs:
            written = json.loads(run_dirs[0].read_text())
            ok(
                written["headline"] == "violation"
                and written["results"][0]["status"] == "violated",
                f"persisted report wrong: {written}",
            )

    print("=== aggregator exact-schema negative check ===")
    import importlib

    agg_mod = importlib.import_module(
        f"{PACKAGE_NAME}.modules.constraints.constraint_report_aggregator"
    )
    try:
        agg_mod.ConstraintReportAggregatorInput()
        failures.append("aggregator accepted a MISSING assertion result")
    except Exception as e:  # pydantic.ValidationError
        print(f"  missing result is a schema failure as required: {type(e).__name__}")

    print(f"\n{'FAILURES:' if failures else 'PROBE C PASSED'}")
    for f in failures:
        print(f"  - {f}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
