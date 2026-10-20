"""Throwaway: find each committed snapshot's source tree by the sha256s its envelope seals.

For each of the 23 committed v6 envelopes, every `sources.files[].referent` is
`root-0/<rel>`. A candidate directory D is the source root when, for every file,
`D/<rel>` exists with the sealed sha256 and D holds no other .sysml file. Candidates:
the snapshot's own folder, every tests/fixtures/* folder, and the scratch d5 variants
this spike regenerates under `spike-snapshot/regen/`.

Writes `sources.json`: {snapshot: root-or-null, ...}.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
FIX = REPO / "tests" / "fixtures"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def matches(root: Path, files: list[dict]) -> bool:
    want = {f["referent"].split("/", 1)[1]: f["sha256"] for f in files}
    have = {str(p.relative_to(root)) for p in root.rglob("*.sysml")}
    if have != set(want):
        return False
    return all(sha(root / rel) == digest for rel, digest in want.items())


def main() -> None:
    snaps = sorted(FIX.glob("*/instance_graph_snapshot.json")) + [
        FIX / "study_station" / "station.snapshot.json"
    ]
    candidates = sorted(p for p in FIX.iterdir() if p.is_dir())
    candidates += sorted(p for p in (HERE / "regen").glob("*") if p.is_dir())
    candidates += [FIX / "study_station" / "models"]
    out: dict[str, str | None] = {}
    for snap in snaps:
        doc = json.loads(snap.read_text())
        files = doc["sources"]["files"]
        found = None
        for cand in [snap.parent, *candidates]:
            if cand.is_dir() and matches(cand, files):
                found = str(cand.relative_to(REPO))
                break
        out[str(snap.relative_to(REPO))] = found
        print(f"{'OK ' if found else 'MISSING'} {snap.parent.name:45s} -> {found}", file=sys.stderr)
    (HERE / "sources.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
