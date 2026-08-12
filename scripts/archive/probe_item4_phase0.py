"""Item 4 Phase 0 probes — no production change, snapshot-only measurement.

Answers the three questions design.md's Phase 0 exit names, before the carry
(Phase 1) touches any production code:

1. **B2 equality.** Does the loader-visible ``source_attribute_name`` on a calc
   binding equal the constraint side's ``FeatureReferenceFact.source_name`` for
   the same shared attribute? Measured on ``shared_producer``'s ``gain``.

2. **Owner-path parity, both shapes.** The calc consumer would derive its owner
   path as ``usage.qualified_name.rsplit("__", 1)[0]``. For the unbracketed
   shape that must equal the constraint side's ``owner_instance_path``; for a
   bracketed (occurrence-indexed ``part_def``) owner it must NOT, and row 16
   must miss rather than hit a wrong key.

3. **The prospective rename set.** For every calc binding in every committed
   fixture, what row-16 key would the carry construct, and does it hit
   ``design_attr_by_qn``? A hit is a binding that moves; a miss is one that
   keeps today's lenient terminal mint. This is Phase 0's static forecast of
   the set Gate 3's live per-binding probe must reproduce in Phase 1.

Run: ``uv run python scripts/probes/probe_item4_phase0.py``
"""

from __future__ import annotations

import json
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "fixtures"


def _load(fixture_dir: Path) -> dict:
    return json.loads((fixture_dir / "extraction_snapshot.json").read_text())


def _design_attr_qns(snapshot: dict) -> set[str]:
    """Every design-attribute QN, flattened across the per-file index."""
    return {
        attr["qualified_name"]
        for attrs in snapshot.get("design_attributes", {}).values()
        for attr in attrs
    }


def _calc_owner_path(usage_qn: str) -> str:
    """The owner path the carry would derive for a calc consumer.

    Mirrors what Phase 1 will supply as ``occurrence_owner_path``: the calc
    usage's QN minus its own trailing segment.
    """
    return usage_qn.rsplit("__", 1)[0]


def _row16_key(owner_path: str, written_name: str) -> str:
    """Row 16's key form, ``_occurrence_materialized_qn``'s construction."""
    return f"{owner_path}__{'__'.join(written_name.split('.'))}"


def _constraint_source_names(snapshot: dict) -> dict[str, str]:
    """Map ``{constraint usage QN}.{actual name}`` -> the reference's source_name."""
    out: dict[str, str] = {}
    for usage in snapshot.get("constraint_facts", {}).get("usages", []):
        usage_qn = usage["identity"]["qualified_name"]
        for actual in usage.get("actuals", []):
            value = actual.get("value") or {}
            reference = value.get("reference") or {}
            source_name = reference.get("source_name")
            if source_name:
                out[f"{usage_qn}.{actual['name']}"] = source_name
    return out


def probe_b2_equality() -> None:
    print("=" * 72)
    print("PROBE 1 — B2: written reference, both sides, shared_producer::gain")
    print("=" * 72)

    snapshot = _load(FIXTURES / "shared_producer")

    calc_names = {
        binding["param_name"]: binding.get("source_attribute_name")
        for usage in snapshot.get("calc_usages", [])
        for binding in usage.get("bindings", [])
    }
    constraint_names = _constraint_source_names(snapshot)

    calc_side = calc_names.get("gain")
    constraint_side = constraint_names.get("SharedProducer::the_rig::floor_check.gain")

    print(f"  calc binding    source_attribute_name = {calc_side!r}")
    print(f"  constraint fact source_name           = {constraint_side!r}")
    verdict = "EQUAL — B2 holds" if calc_side == constraint_side else "DIVERGENT — B2 LOSES"
    print(f"  -> {verdict}")


def probe_owner_path_parity() -> None:
    print()
    print("=" * 72)
    print("PROBE 2 — owner-path parity, unbracketed and bracketed shapes")
    print("=" * 72)

    for fixture, shape in (
        ("shared_producer", "unbracketed (PartUsage owner) — expect PARITY"),
        ("constraint_multi_instance", "bracketed (part_def occurrence) — expect MISS"),
    ):
        snapshot = _load(FIXTURES / fixture)
        attr_qns = _design_attr_qns(snapshot)
        print(f"\n  [{fixture}] {shape}")

        constraint_owners = sorted(
            {
                usage["identity"]["qualified_name"].replace("::", "__")
                for usage in snapshot.get("constraint_facts", {}).get("usages", [])
            }
        )
        print(f"    constraint usage QNs: {constraint_owners}")

        for usage in snapshot.get("calc_usages", []):
            usage_qn = usage["qualified_name"]
            owner_path = _calc_owner_path(usage_qn)
            print(f"    calc usage      : {usage_qn}")
            print(f"    derived owner   : {owner_path}  (brackets: {'[' in owner_path})")
            for binding in usage.get("bindings", []):
                written = binding.get("source_attribute_name")
                if not written:
                    continue
                key = _row16_key(owner_path, written)
                hit = key in attr_qns
                print(f"      {binding['param_name']}: row16 key = {key}")
                print(f"        -> {'HIT' if hit else 'MISS'} against design_attr_by_qn")


def probe_rename_forecast() -> None:
    print()
    print("=" * 72)
    print("PROBE 3 — prospective rename set across all committed fixtures")
    print("=" * 72)

    moved: list[tuple[str, str, str]] = []
    unchanged = 0
    unnamed = 0

    for fixture_dir in sorted(FIXTURES.glob("*/extraction_snapshot.json")):
        fixture = fixture_dir.parent.name
        snapshot = _load(fixture_dir.parent)
        attr_qns = _design_attr_qns(snapshot)

        for usage in snapshot.get("calc_usages", []):
            usage_qn = usage["qualified_name"]
            owner_path = _calc_owner_path(usage_qn)
            for binding in usage.get("bindings", []):
                if binding.get("source_path") is None:
                    continue
                written = binding.get("source_attribute_name")
                if not written:
                    unnamed += 1
                    continue
                key = _row16_key(owner_path, written)
                if key in attr_qns:
                    old = f"{usage_qn}__{binding['param_name']}"
                    moved.append((fixture, old, key))
                else:
                    unchanged += 1

    print(f"  bindings whose row-16 key HITS (would move): {len(moved)}")
    print(f"  bindings whose row-16 key MISSES (unchanged): {unchanged}")
    print(f"  bound bindings with no written name: {unnamed}")

    by_fixture: dict[str, list[tuple[str, str]]] = {}
    for fixture, old, new in moved:
        by_fixture.setdefault(fixture, []).append((old, new))

    print(f"\n  fixtures affected: {len(by_fixture)}")
    for fixture in sorted(by_fixture):
        print(f"\n  [{fixture}] {len(by_fixture[fixture])} moved")
        for old, new in sorted(by_fixture[fixture]):
            print(f"    {old}")
            print(f"      -> {new}")


if __name__ == "__main__":
    probe_b2_equality()
    probe_owner_path_parity()
    probe_rename_forecast()
