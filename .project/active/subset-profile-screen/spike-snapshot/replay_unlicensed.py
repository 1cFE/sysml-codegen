"""Throwaway: re-run the screen from dumped facts with SysIDE unimportable and no license.

Usage (from the sysml-codegen repo root, license NOT set):

    env -u SYSIDE_LICENSE_KEY uv run --extra dev python \
        .project/active/subset-profile-screen/spike-snapshot/replay_unlicensed.py OUT_DIR

Reads every `OUT_DIR/*.facts.json` that `probe_roundtrip.py ... --dump-facts` wrote, decodes it,
runs `evaluate_subset_profile`, normalizes the root path exactly as the probe did, and compares
with `OUT_DIR/*.result.json` (the live, licensed screen result). Blocks `syside` first, so a
hidden live dependency raises.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Blocking the SysIDE-side agentic-mbse modules too fails: `IdentifiedConstraintFacts` (the
# `constraints` field) lives in `constraint_extraction.py`, which imports `reference_use` and
# `syside_adapter`. Those import `syside` lazily, so blocking `syside` itself is the real test.
sys.modules["syside"] = None  # type: ignore[assignment]

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import factcodec  # noqa: E402
from agentic_mbse.sysml.subset_profile import evaluate_subset_profile  # noqa: E402


def main() -> None:
    assert "SYSIDE_LICENSE_KEY" not in os.environ, "run without the license"
    out = Path(sys.argv[1])
    rows = {f"{r['group']}__{r['name']}": r for r in json.loads((out / "summary.json").read_text())}
    same = differ = 0
    for facts_path in sorted(out.glob("*.facts.json")):
        key = facts_path.name.removesuffix(".facts.json")
        facts = factcodec.decode(facts_path.read_text())
        result = factcodec.encode(evaluate_subset_profile(facts)).replace(rows[key]["prefix"], "<ROOT>")
        live = (out / f"{key}.result.json").read_text()
        if result == live:
            same += 1
        else:
            differ += 1
            print("DIFFER", key)
    print(f"replayed {same + differ}: {same} byte-identical, {differ} differ")
    print("syside imported:", "syside" in sys.modules and sys.modules["syside"] is not None)


if __name__ == "__main__":
    main()
