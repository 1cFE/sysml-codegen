"""S4 probe B — snapshot leg: rebuild offline, lower from sidecar, byte-compare.

License-free (loads the snapshot, never invokes the parser), but run in the same
env as probe A for identical library versions:

    UV_CACHE_DIR=/tmp/agentic-mbse-uv-cache \
    PYTHONPATH=/home/reid/1cfe/sysml-codegen/src \
    uv run --directory /home/reid/1cfe/agentic-mbse python \
      /home/reid/1cfe/sysml-codegen/.project/active/spike-vertical-slice-constraint-execution/probe_b_snapshot.py

Checks:
1. Missing-sidecar refusal (strict boundary, S3 lesson).
2. Snapshot-leg generation completes from snapshot + sidecar alone.
3. package_snapshot/ is byte-identical to package_live/.
"""

from __future__ import annotations

import json
import logging
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import s4_lib
from s4_lib import SPIKE_DIR, SidecarError

OUT = SPIKE_DIR / "out"


def compare_trees(a: Path, b: Path) -> list[str]:
    def files(root: Path) -> dict[str, Path]:
        return {
            str(p.relative_to(root)): p
            for p in root.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts
        }

    fa, fb = files(a), files(b)
    diffs = []
    for rel in sorted(set(fa) - set(fb)):
        diffs.append(f"only in {a.name}: {rel}")
    for rel in sorted(set(fb) - set(fa)):
        diffs.append(f"only in {b.name}: {rel}")
    for rel in sorted(set(fa) & set(fb)):
        if fa[rel].read_bytes() != fb[rel].read_bytes():
            diffs.append(f"differs: {rel}")
    return diffs


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    failures: list[str] = []
    snap_dir = OUT / "snapshot"
    snapshot = snap_dir / "extraction_snapshot.json"

    # --- 1. strict boundary: a snapshot dir without the sidecar refuses ----
    print("=== missing-sidecar refusal ===")
    bare_dir = OUT / "snapshot_no_sidecar"
    bare_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(snapshot, bare_dir / "extraction_snapshot.json")
    try:
        s4_lib.load_sidecar(bare_dir)
        failures.append("missing sidecar was NOT refused")
    except SidecarError as e:
        print(f"  refused as required: {e}")

    # --- 2. snapshot-leg generation ----------------------------------------
    print("=== generate (snapshot leg) ===")
    components = s4_lib.components_from_snapshot(snapshot)
    facts_doc = s4_lib.load_sidecar(snap_dir)
    summary = s4_lib.generate_s4_package(components, facts_doc, OUT / "package_snapshot")
    print(json.dumps(summary, indent=2))
    (OUT / "summary_snapshot.json").write_text(json.dumps(summary, indent=2) + "\n")

    live_summary = json.loads((OUT / "summary_live.json").read_text())
    for key in (
        "control_modules",
        "extended_modules",
        "root_channels",
        "constraint_ids",
        "entry_point_qns",
        "catalog_fingerprint",
        "executable_fingerprint",
    ):
        if summary[key] != live_summary[key]:
            failures.append(
                f"summary mismatch on {key}: live={live_summary[key]} snap={summary[key]}"
            )

    # --- 3. byte identity ----------------------------------------------------
    print("=== byte-compare live vs snapshot packages ===")
    diffs = compare_trees(OUT / "package_live", OUT / "package_snapshot")
    for d in diffs:
        failures.append(d)
    print(f"  {len(diffs)} differing file(s)")

    print(f"\n{'FAILURES:' if failures else 'PROBE B PASSED'}")
    for f in failures:
        print(f"  - {f}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
