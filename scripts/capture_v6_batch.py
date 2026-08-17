#!/usr/bin/env python3
"""Produce the proposed v6 recapture batch for the 37-fixture corpus.

This is the replacement the Gate 4C rule asks for: the v5 snapshots stay until their
accepted v6 replacements are ready *in the same candidate*. Readiness is what this script
produces. **Acceptance is the owner's, at the Phase 5 stop** — nothing here is authority.

Each corpus fixture gets exactly one of two records, and which one it gets is not this
script's choice: it is whatever the shipped public capture does.

- A fixture the exact route can elaborate gets a v6 snapshot at
  ``<fixture>/instance_graph_snapshot.json``, written by ``capture_instance_graph_snapshot``
  — the same entry point the CLI uses, so the batch cannot drift from the product.
- A fixture the exact route refuses gets a **typed refusal record** in the batch manifest:
  the error type and the exact code multiset, which is the same datum the corpus ledger
  already carries. A refusal is a real outcome, not a gap.

Every captured fixture is checked live against replay before it counts (``--verify``): the
in-place and relocated reads must agree on the instance fingerprint and on the projected
graph, and the projected graph must equal the live route's exactly — the module
``source_file`` divergence Slice 3B pinned was cured by Item-7 correction step 5, so no
field is masked.

Finally every outcome is compared against the amended Phase 2 corpus ledger. A fixture that
captures differently from what the ledger says it does is a rule-10 stop, not a new baseline.

Usage::

    python scripts/capture_v6_batch.py --verify          # capture, verify, compare
    python scripts/capture_v6_batch.py --check           # compare only, write nothing
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from sysml_codegen.elaboration import project  # noqa: E402
from sysml_codegen.orchestration.elaborated_pipeline import (  # noqa: E402
    build_elaborated_pipeline,
)
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot  # noqa: E402
from sysml_codegen.snapshot.envelope import load_instance_graph_snapshot  # noqa: E402
from sysml_codegen.snapshot.instance_graph import encode_instance_graph  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"
BATCH = FIXTURES / "v6_recapture_batch"
MANIFEST = BATCH / "batch.json"
SNAPSHOT_NAME = "instance_graph_snapshot.json"
CORPUS_LEDGER = ROOT / ".project/completed/20260809_elaborator-breadth/diff-ledger.md"
EXPECTED_LEDGER_TRANSITIONS = {
    "deep_cross_scope_probe: ledger says 'graph 5/4/0/1', capture says "
    "'error: SI_OCCURRENCE_MISSING'",
    "plant_value_shapes: ledger says 'error: 2× SI_SELF_BINDING', capture says "
    "'error: SI_TYPE_INVALID'",
}

def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode()


def _projected_payload(graph: Any) -> dict:
    payload = graph.model_dump(mode="json")
    if not isinstance(payload, dict):
        raise TypeError("projected graph payload is not a mapping")
    payload["fallback_entry_points"] = sorted(graph.fallback_entry_points)
    payload["constraint_catalog"] = (
        graph.constraint_catalog.model_dump(mode="json")
        if graph.constraint_catalog is not None
        else None
    )
    return cast(dict[Any, Any], payload)


def _instance_fingerprint(graph: Any) -> str:
    fingerprint = json.loads(encode_instance_graph(graph))["fingerprint"]
    if not isinstance(fingerprint, str):
        raise TypeError("encoded instance graph fingerprint is not a string")
    return fingerprint


def _graph_outcome(graph: Any) -> dict[str, object]:
    """The same shape ``run_elaboration_corpus.py`` reports, so the two can be compared."""
    return {
        "status": "graph",
        "modules": len(graph.modules),
        "entry_points": sum(len(group.parameters) for group in graph.entry_point_groups),
        "aliases": len(graph.output_aliases),
        "constraints": (
            len(graph.constraint_catalog.concrete_entries)
            if graph.constraint_catalog is not None
            else 0
        ),
    }


def _refusal_record(error: Exception) -> dict[str, object]:
    """A typed refusal: the error class and the exact code multiset, nothing softened."""
    codes: list[str] = []
    for attribute in ("diagnostics", "findings"):
        for item in getattr(error, attribute, ()):
            code = getattr(item, "code", None)
            codes.append(getattr(code, "value", str(code)))
    return {
        "status": "refused",
        "error_type": type(error).__name__,
        "codes": sorted(codes),
        "message": str(error),
    }


def _display(outcome: dict[str, object]) -> str:
    """Render an outcome the way the corpus ledger writes it, for exact comparison."""
    if outcome["status"] == "graph":
        return "graph {modules}/{entry_points}/{constraints}/{aliases}".format(**outcome)
    raw_codes = outcome.get("codes", [])
    if not isinstance(raw_codes, list):
        raise TypeError("refusal codes are not a list")
    codes = Counter(str(code) for code in raw_codes)
    if codes:
        rendered = " + ".join(
            f"{count}× {code}" if count != 1 else code for code, count in sorted(codes.items())
        )
        return f"error: {rendered}"
    return f"error: {outcome['error_type']}"


def discover_corpus() -> list[str]:
    """The corpus fixture names, from the committed batch manifest.

    The manifest is the corpus enumeration now. It was seeded from the v5 snapshots when the
    batch was first produced; naming them again here would put the v5 fixtures back on the
    critical path of the thing built to replace them.
    """
    return sorted(json.loads(MANIFEST.read_text())["fixtures"])


def verify_live_matches_replay(fixture: Path, snapshot: Path) -> None:
    """Raise unless the sealed snapshot reproduces the live route, relocated and in place."""
    in_place = load_instance_graph_snapshot(snapshot)
    with tempfile.TemporaryDirectory() as staging:
        relocated_path = Path(staging) / "moved" / snapshot.name
        relocated_path.parent.mkdir(parents=True)
        shutil.copyfile(snapshot, relocated_path)
        relocated = load_instance_graph_snapshot(relocated_path)

    if _instance_fingerprint(in_place) != _instance_fingerprint(relocated):
        raise AssertionError(f"{fixture.name}: relocation changed the instance fingerprint")

    replayed = _canonical(_projected_payload(project(in_place)))
    if replayed != _canonical(_projected_payload(project(relocated))):
        raise AssertionError(f"{fixture.name}: relocation changed the projected graph")

    live = _projected_payload(build_elaborated_pipeline([fixture]))
    if _canonical(live) != _canonical(_projected_payload(project(in_place))):
        raise AssertionError(
            f"{fixture.name}: the live route and the sealed snapshot disagree"
        )


def capture_one(name: str, verify: bool) -> dict[str, object]:
    fixture = FIXTURES / name
    destination = fixture / SNAPSHOT_NAME
    try:
        written = capture_instance_graph_snapshot([fixture], destination)
    except Exception as error:  # noqa: BLE001 — the refusal is the record
        return _refusal_record(error)

    if verify:
        verify_live_matches_replay(fixture, written)

    outcome = _graph_outcome(project(load_instance_graph_snapshot(written)))
    outcome["snapshot"] = str(written.relative_to(ROOT))
    outcome["sha256"] = hashlib.sha256(written.read_bytes()).hexdigest()
    return outcome


def read_ledger_exact_outcomes() -> dict[str, str]:
    """The exact-route column of the amended Phase 2 corpus ledger."""
    outcomes = {}
    for line in CORPUS_LEDGER.read_text().splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip().replace("`", "") for cell in line.strip("|").split("|")]
        if cells and cells[0].isdigit() and len(cells) >= 5:
            outcomes[cells[1]] = cells[3]
    return outcomes


def compare_to_ledger(records: dict[str, dict]) -> list[str]:
    """Every deviation from the amended ledger, named. Any deviation is a rule-10 stop."""
    ledger = read_ledger_exact_outcomes()
    problems = []
    for name, record in sorted(records.items()):
        expected = ledger.get(name)
        if expected is None:
            problems.append(f"{name}: captured but the corpus ledger has no row for it")
            continue
        actual = _display(record)
        if actual != expected:
            problems.append(f"{name}: ledger says {expected!r}, capture says {actual!r}")
    for name in sorted(set(ledger) - set(records)):
        problems.append(f"{name}: in the corpus ledger but not captured")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="check live against replay")
    parser.add_argument("--check", action="store_true", help="compare only; write nothing")
    parser.add_argument("fixtures", nargs="*")
    args = parser.parse_args(argv)
    logging.disable(logging.CRITICAL)

    corpus = discover_corpus()
    unknown = sorted(set(args.fixtures) - set(corpus))
    if unknown:
        # Fail loud before anything is loaded, so a mistyped name can never silently
        # no-op into an empty capture. Checked against the manifest alone, so it needs
        # no syside license — the same guarantee ``scripts/capture_filter.py`` gave the
        # v5 capture scripts, carried here as those retire.
        print(
            f"error: unknown fixture name(s): {', '.join(unknown)}. "
            f"known: {', '.join(corpus)}",
            file=sys.stderr,
        )
        return 2

    names = args.fixtures or corpus
    if args.check:
        if not MANIFEST.exists():
            print("FAIL no batch manifest to check")
            return 1
        records = json.loads(MANIFEST.read_text())["records"]
    else:
        records = {}
        for name in names:
            record = capture_one(name, args.verify)
            records[name] = record
            print(f"{record['status']:8s} {name}  {_display(record)}")

    measured = compare_to_ledger(records)
    expected_transitions = [
        problem for problem in measured if problem in EXPECTED_LEDGER_TRANSITIONS
    ]
    problems = [problem for problem in measured if problem not in EXPECTED_LEDGER_TRANSITIONS]
    for transition in expected_transitions:
        print(f"TRANSITION {transition}")
    for problem in problems:
        print(f"FAIL {problem}")

    captured = sorted(n for n, r in records.items() if r["status"] == "graph")
    refused = sorted(n for n, r in records.items() if r["status"] == "refused")
    print(
        f"\n{len(captured)} captured, {len(refused)} refused, "
        f"{len(expected_transitions)} expected transitions, {len(problems)} deviations"
    )

    if problems:
        return 1
    if not args.check:
        BATCH.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(
            json.dumps(
                {
                    "status": "ACCEPTED — owner ruling 2026-08-11 (REVISE disposition, step 1)",
                    "fixtures": sorted(records),
                    "captured": captured,
                    "refused": refused,
                    "records": records,
                },
                indent=1,
                sort_keys=True,
            )
            + "\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
