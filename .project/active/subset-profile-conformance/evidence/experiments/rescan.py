"""E5 rescan of sysml-codegen (Item 2a P7): which sites each 2a commit added or removed.

    uv run --extra dev python .project/active/subset-profile-conformance/evidence/experiments/rescan.py \
        ITEM1_SCAN_CSV OUT_DIR REV [REV ...]

Scans `src/` of each revision, read from a `git archive` export, with the scanner in this
checkout (`tests/helpers/subset_profile/site_scan.py`) and the installed agentic-mbse source for
the factory search. The first revision is the 2a base; the scan of it is also compared with
Item 1's final scan (`ITEM1_SCAN_CSV`, `scan_sites/1`), so a difference the scanner port made is
told apart from one the code made. Writes `<OUT_DIR>/rescan.json`: per consecutive pair, the
site IDs added and removed.
"""

from __future__ import annotations

import csv
import io
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO))

from tests.helpers.subset_profile import site_scan  # noqa: E402


def export_src(rev: str, dest: Path) -> Path:
    archive = subprocess.run(
        ["git", "-C", str(REPO), "archive", rev, "src"], check=True, capture_output=True
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(dest, filter="data")
    return dest / "src"


def item1_codegen_ids(path: Path) -> set[str]:
    rows = [line for line in path.read_text().splitlines() if not line.startswith("#")]
    return {r["site_id"] for r in csv.DictReader(rows) if r["site_id"].startswith("sysml_codegen")}


def main() -> int:
    item1, out, revs = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:]
    scans: list[tuple[str, dict[str, site_scan.Site]]] = []
    with tempfile.TemporaryDirectory(prefix="rescan-") as tmp:
        for rev in revs:
            src = export_src(rev, Path(tmp) / rev)
            found = site_scan.scan(src)
            scans.append((rev, {s.site_id: s for s in found.codegen()}))
    base_rev, base = scans[0]
    port = {
        "base": base_rev,
        "only_in_item1_scan": sorted(item1_codegen_ids(item1) - set(base)),
        "only_in_port": sorted(set(base) - item1_codegen_ids(item1)),
        "only_in_port_channels": sorted(
            {base[i].channel for i in set(base) - item1_codegen_ids(item1)}
        ),
    }
    steps = []
    for (rev_a, a), (rev_b, b) in zip(scans, scans[1:], strict=False):
        steps.append(
            {
                "from": rev_a,
                "to": rev_b,
                "added": [
                    {"site_id": i, "line": b[i].line, "channel": b[i].channel}
                    for i in sorted(set(b) - set(a))
                ],
                "removed": [
                    {"site_id": i, "line": a[i].line, "channel": a[i].channel}
                    for i in sorted(set(a) - set(b))
                ],
            }
        )
    out.mkdir(parents=True, exist_ok=True)
    summary = {
        "port": port,
        "steps": steps,
        "final": {"rev": scans[-1][0], "sites": len(scans[-1][1])},
    }
    (out / "rescan.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(f"base {base_rev[:8]}: {len(base)} sites; item1 {len(item1_codegen_ids(item1))}")
    print(f"  only in Item 1 scan: {len(port['only_in_item1_scan'])}; only in port: "
          f"{len(port['only_in_port'])} {port['only_in_port_channels']}")
    for s in steps:
        print(f"{s['from'][:8]} -> {s['to'][:8]}: +{len(s['added'])} -{len(s['removed'])}")
    print(f"final {scans[-1][0][:8]}: {len(scans[-1][1])} sites")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
