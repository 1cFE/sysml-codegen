#!/usr/bin/env python3
"""Check a committed study record against runbook steps 14 and 15 (design DD12, Appendix H2 step 4).

Evidence for the SC4 dry run, not a shipped tool. It reads the record on its own, not through the
installed runbook's Check lines, so that a disagreement between the two is visible. It applies
the five conditions those lines state and names every one that fails:

1. step 14: every § 15 finding id has a row in the studies directory's DISCOVERY_LOG.md, and
   every log row for this study names a § 15 id;
2. step 15: record.md holds no unreplaced placeholder, that is, no opening angle bracket;
3. step 15: every name under the snapshot's manifest.content_used.fingerprint_names is a key
   under fingerprints;
4. step 15: every arms[].store_id resolves into stores[];
5. step 15: every arms[].artifacts[] entry has a sha256.

Usage: check_record.py RECORD_DIR

The study id is RECORD_DIR's name, and the discovery log is RECORD_DIR/../DISCOVERY_LOG.md.
Exits 0 when all five hold, 1 when any fails, and 2 when RECORD_DIR has no record.md or no
readable snapshot.json.
"""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any


def table_rows(lines: list[str]) -> Iterator[list[str]]:
    """The data rows of every markdown table in ``lines``, each as its stripped cells."""
    in_table = False
    seen_separator = False
    for line in lines:
        if not line.startswith("|"):
            in_table = seen_separator = False
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not in_table:
            in_table = True  # the header row
            continue
        if not seen_separator and all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            seen_separator = True
            continue
        yield cells


def section(text: str, number: int) -> list[str]:
    """The lines of record.md's ``## <number>.`` section, up to the next ``## `` heading."""
    lines = text.splitlines()
    start = next(
        (i for i, line in enumerate(lines) if line.startswith(f"## {number}.")), None
    )
    if start is None:
        return []
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines)
    )
    return lines[start + 1 : end]


def check_join(record: str, log_path: Path, study_id: str) -> list[str]:
    """Step 14: § 15's ids and this study's discovery-log rows are the same set."""
    pattern = re.compile(rf"{re.escape(study_id)}#\d+")
    ids: set[str] = set()
    problems: list[str] = []
    for cells in table_rows(section(record, 15)):
        finding = cells[0].strip("`")
        if pattern.fullmatch(finding):
            ids.add(finding)
        else:
            problems.append(f"§ 15 row id {finding!r} is not of the form {study_id}#<n>")
    if not log_path.is_file():
        return [*problems, f"no discovery log at {log_path}"]
    logged = {
        cells[2].strip("`")
        for cells in table_rows(log_path.read_text().splitlines())
        if len(cells) > 2 and cells[2].strip("`").startswith(f"{study_id}#")
    }
    if missing := sorted(ids - logged):
        problems.append(f"§ 15 ids with no discovery-log row: {missing}")
    if orphans := sorted(logged - ids):
        problems.append(f"discovery-log rows naming no § 15 id: {orphans}")
    return problems


def check_placeholders(record: str) -> list[str]:
    """Step 15: no opening angle bracket is left in record.md."""
    lines = [n for n, line in enumerate(record.splitlines(), start=1) if "<" in line]
    if not lines:
        return []
    count = record.count("<")
    return [f"record.md has {count} unreplaced placeholder bracket(s), on lines {lines}"]


def check_fingerprints(snapshot: dict[str, Any]) -> list[str]:
    """Step 15: every declared fingerprint name is a key under ``fingerprints``."""
    try:
        names = snapshot["manifest"]["content_used"]["fingerprint_names"]
    except (KeyError, TypeError):
        return ["snapshot.json has no manifest.content_used.fingerprint_names"]
    if missing := sorted(set(names) - set(snapshot.get("fingerprints", {}))):
        return [f"fingerprint names with no key under fingerprints: {missing}"]
    return []


def check_stores(snapshot: dict[str, Any]) -> list[str]:
    """Step 15: every arm's store id resolves into ``stores[]``."""
    stores = {store.get("store_id") for store in snapshot.get("stores", [])}
    arms = snapshot.get("arms", [])
    if unresolved := sorted({str(arm.get("store_id")) for arm in arms} - {str(s) for s in stores}):
        return [f"arm store ids not in stores[]: {unresolved}"]
    return []


def check_artifact_digests(snapshot: dict[str, Any]) -> list[str]:
    """Step 15: every result artifact of every arm has a digest."""
    undigested = [
        artifact.get("path")
        for arm in snapshot.get("arms", [])
        for artifact in arm.get("artifacts", [])
        if not artifact.get("sha256")
    ]
    if undigested:
        return [f"result artifacts with no sha256: {undigested}"]
    return []


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: check_record.py RECORD_DIR", file=sys.stderr)
        return 2
    record_dir = Path(argv[0]).resolve()
    study_id = record_dir.name
    try:
        record = (record_dir / "record.md").read_text()
        snapshot = json.loads((record_dir / "snapshot.json").read_text())
    except (OSError, json.JSONDecodeError) as error:
        print(f"check_record: cannot read the record in {record_dir}: {error}", file=sys.stderr)
        return 2
    checks = [
        ("1 step 14: § 15 and the discovery log join", check_join(
            record, record_dir.parent / "DISCOVERY_LOG.md", study_id)),
        ("2 step 15: no unreplaced placeholder", check_placeholders(record)),
        ("3 step 15: every fingerprint name has a key", check_fingerprints(snapshot)),
        ("4 step 15: every arm's store resolves", check_stores(snapshot)),
        ("5 step 15: every result artifact has a digest", check_artifact_digests(snapshot)),
    ]
    print(f"check_record: {study_id}")
    for name, problems in checks:
        print(f"{'FAIL' if problems else 'PASS'} {name}")
        for problem in problems:
            print(f"     {problem}")
    return 1 if any(problems for _, problems in checks) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
