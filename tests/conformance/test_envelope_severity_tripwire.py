"""REQ-DIAG-04 tripwire: no diagnostic severity crosses the snapshot boundary.

The requirement (severity skew fails closed in both directions) was recorded
UNTESTED-by-construction at CONSTRAINT-SEMANTICS Item 7's audit: no *diagnostic*
severity is written to disk, so there was nothing to assert — but nothing would
have failed if the v6 envelope started carrying one again. This is that missing
tripwire, at the public on-disk boundary (narrow-correction step 4, rev-2 brief).

The envelope legitimately carries one severity field: the **disposition**
severity at ``constraint_usages[].disposition.severity``
(`snapshot/instance_graph.py` — a different field with a different writer, not
what REQ-DIAG-04 is about). So the pin is exact: across every committed v6
snapshot, the set of JSON paths whose key is ``severity`` is exactly that one.
A diagnostic severity (or any new severity-bearing field) surfacing anywhere in
a captured envelope adds a path and flips this red, which converts the row's
"impossible rather than guarded" state into a guarded one.

License-free: reads the committed snapshots, captures nothing.
"""

from __future__ import annotations

import json
import re

from tests.conftest import FIXTURES_DIR

DISPOSITION_SEVERITY = "$.instance_graph.graph.constraint_usages[].disposition.severity"


def _severity_paths(value: object, path: str, hits: set[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key == "severity":
                hits.add(child_path)
            _severity_paths(child, child_path, hits)
    elif isinstance(value, list):
        for child in value:
            _severity_paths(child, f"{path}[]", hits)


def test_the_only_severity_on_disk_is_the_disposition_severity() -> None:
    snapshots = sorted(FIXTURES_DIR.glob("*/instance_graph_snapshot.json"))
    assert snapshots, "no committed v6 snapshots found; re-anchor this tripwire"

    offenders: dict[str, set[str]] = {}
    disposition_seen = False
    for snapshot in snapshots:
        hits: set[str] = set()
        _severity_paths(json.loads(snapshot.read_text()), "$", hits)
        normalized = {re.sub(r"\[\]+", "[]", h) for h in hits}
        if DISPOSITION_SEVERITY in normalized:
            disposition_seen = True
        extra = normalized - {DISPOSITION_SEVERITY}
        if extra:
            offenders[str(snapshot.relative_to(FIXTURES_DIR))] = extra

    assert offenders == {}, (
        "a severity field beyond the disposition severity reached the v6 "
        f"envelope (REQ-DIAG-04 guards against diagnostic severity on disk): {offenders}"
    )
    assert disposition_seen, (
        "no committed snapshot carries the disposition severity path any more; "
        "this tripwire's exact-set premise needs re-anchoring"
    )
