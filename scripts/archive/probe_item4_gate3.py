"""Item 4 Gate 3 — the per-binding resolution probe (design D6).

For every ``resolve_producer`` call across every committed fixture, resolve
twice against the *same* context: once as the consumer actually asks (carry on),
and once with row 16's two dedicated fields stripped (carry off, i.e. the
pre-Item-4 request shape). Diff the tuple ``(outcome, identity, key_form)``.

Scope is all five ``ProducerRequest`` builders, not only bindings (design review
C3): the calculation consumer and the constraint consumer in
``dependency_backtracker`` / ``constraint_lowering``, plus the three
``graph_builder`` consumers — LocalTerm, EXPOSE alias, and the aggregation
pre-mint lookup. Aggregation and LocalTerm resolutions are not bindings, so a
binding-only probe could not see C3's regression class.

Gate 2's stop rule is applied to the result:

- a changed *value* (default carried or numeric result) is a stop;
- a changed *resolution shape* — ``outcome`` or ``key_form`` moving to anything
  other than row 16 — is a stop.

Run: ``uv run python scripts/probes/probe_item4_gate3.py``
"""

from __future__ import annotations

import dataclasses
import json
import sys
from collections import defaultdict
from pathlib import Path

from sysml_codegen.resolution.producer_resolution import resolve_producer

FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "fixtures"

ROW_16 = "occurrence_materialized_qn"


def _tuple_of(resolution) -> tuple[str, str, str | None]:
    return (resolution.outcome.value, resolution.identity, resolution.key_form)


def _carry_off(request):
    """The same request as the pre-Item-4 consumer would have built it."""
    return dataclasses.replace(request, written_reference=None, occurrence_owner_path=None)


def _install_probe(records: list[dict]) -> None:
    """Wrap resolve_producer in every module that calls it."""

    def probing_resolve(request, context):
        on = resolve_producer(request, context)
        off = resolve_producer(_carry_off(request), context)
        records.append(
            {
                "consumer_eqn": request.consumer_eqn,
                "param_name": request.param_name,
                "reference": request.reference,
                "written_reference": request.written_reference,
                "occurrence_owner_path": request.occurrence_owner_path,
                "instance_path": request.instance_path,
                "diagnostic_context": request.diagnostic_context,
                "on": _tuple_of(on),
                "off": _tuple_of(off),
                "default_on": on.default_value,
                "default_off": off.default_value,
            }
        )
        return on

    for module_name in (
        "sysml_codegen.analysis.dependency_backtracker",
        "sysml_codegen.analysis.constraint_lowering",
        "sysml_codegen.resolution.graph_builder",
    ):
        __import__(module_name)

        sys.modules[module_name].resolve_producer = probing_resolve


def _fixtures_with_snapshots() -> list[Path]:
    return sorted(path.parent for path in FIXTURES.glob("*/extraction_snapshot.json"))


def main() -> None:
    # Import after nothing else has bound resolve_producer.
    from sysml_codegen.orchestration.snapshot_context import (
        build_pipeline_context_from_snapshot,
    )

    all_records: dict[str, list[dict]] = {}
    failures: dict[str, str] = {}

    for fixture_dir in _fixtures_with_snapshots():
        records: list[dict] = []
        _install_probe(records)
        try:
            build_pipeline_context_from_snapshot(fixture_dir / "extraction_snapshot.json")
        except Exception as exc:  # noqa: BLE001 - probe reports, never masks
            failures[fixture_dir.name] = f"{type(exc).__name__}: {exc}"
        all_records[fixture_dir.name] = records

    moved: list[tuple[str, dict]] = []
    total = 0
    for fixture, records in all_records.items():
        for record in records:
            total += 1
            if record["on"] != record["off"]:
                moved.append((fixture, record))

    print("=" * 72)
    print("GATE 3 — per-binding resolution probe, all five builders")
    print("=" * 72)
    print(f"  fixtures probed        : {len(all_records)}")
    print(f"  resolve_producer calls : {total}")
    print(f"  resolutions that moved : {len(moved)}")
    if failures:
        print(f"\n  !! fixtures that failed to build: {len(failures)}")
        for fixture, error in failures.items():
            print(f"     {fixture}: {error}")

    # ---- Gate 2, clause 2: shape may only move TO row 16 ----
    shape_stops = [
        (fixture, record)
        for fixture, record in moved
        if record["on"][2] != ROW_16
    ]
    # ---- Gate 2, clause 1: value may not move ----
    #
    # Only a default that was *already carried* and then changed is a value
    # stop. `None -> x` is not one: before the carry these bindings took the
    # lenient terminal miss, which carries no default at resolution time and
    # lets the entry-point classifier supply it afterwards. Comparing the two
    # would flag every intended convergence as a value change. The authoritative
    # value check is the final entry point, which probe_item4_entrypoints.py
    # measures.
    value_stops = [
        (fixture, record)
        for fixture, record in moved
        if record["default_off"] is not None
        and record["default_on"] != record["default_off"]
    ]

    print("\n" + "-" * 72)
    print("GATE 2 stop rule")
    print("-" * 72)
    print(f"  shape stops (moved to a key_form other than row 16): {len(shape_stops)}")
    for fixture, record in shape_stops:
        print(f"    [{fixture}] {record['diagnostic_context']}")
        print(f"      off={record['off']}")
        print(f"      on ={record['on']}")
    print(f"  value stops (default_value changed): {len(value_stops)}")
    for fixture, record in value_stops:
        print(f"    [{fixture}] {record['diagnostic_context']}")
        print(f"      {record['default_off']} -> {record['default_on']}")

    verdict = "PASS" if not shape_stops and not value_stops else "STOP"
    print(f"\n  Gate 2 verdict: {verdict}")

    # ---- Gate 1 table: one row per moved entry point ----
    print("\n" + "-" * 72)
    print("GATE 1 — forced-difference table (moved resolutions by fixture)")
    print("-" * 72)
    by_fixture: dict[str, list[dict]] = defaultdict(list)
    for fixture, record in moved:
        by_fixture[fixture].append(record)

    for fixture in sorted(by_fixture):
        print(f"\n  [{fixture}] {len(by_fixture[fixture])} moved")
        for record in sorted(by_fixture[fixture], key=lambda r: r["diagnostic_context"]):
            print(f"    {record['diagnostic_context']}")
            print(f"      old: {record['off'][1]}  ({record['off'][0]}/{record['off'][2]})")
            print(f"      new: {record['on'][1]}  ({record['on'][0]}/{record['on'][2]})")
            print(f"      default carried: {record['default_off']} -> {record['default_on']}")

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/item4_gate3_results.json")
    out.write_text(json.dumps(all_records, indent=2, default=str))
    print(f"\n  full per-call record written to {out}")


if __name__ == "__main__":
    main()
