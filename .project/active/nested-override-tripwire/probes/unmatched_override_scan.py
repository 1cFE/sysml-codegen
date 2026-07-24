"""Phase-0 false-fire scan for the [NESTED-OCCURRENCE-OVERRIDE] tripwire predicate.

Runs the candidate predicate — "a demand fell through silently AND an extracted
override exists for the same leaf attribute name" — across every committed snapshot
fixture the conformance suite registers (`tests/conformance/conftest.py::SNAPSHOT_MODELS`),
plus the recorded nested-occurrence probe fixture, which is the shape the warning must
catch. Every clean fixture must fire zero times; the probe fixture must fire.

Reads only committed snapshots, so it needs no syside license.

    uv run python .project/active/nested-override-tripwire/probes/unmatched_override_scan.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from sysml_codegen.analysis.constraint_lowering import prepare_constraint_usages  # noqa: E402
from sysml_codegen.analysis.part_instance_index import FrozenOccurrenceIndex  # noqa: E402
from sysml_codegen.extraction.data_models import RedefinitionData  # noqa: E402
from sysml_codegen.resolution.supplied_values import (  # noqa: E402
    _BindingTarget,
    _logical_demands,
    resolve_logical_demand,
)
from sysml_codegen.snapshot import CONSTRAINT_LOWERING_MODE_APPLIED  # noqa: E402
from sysml_codegen.snapshot.loader import load_extraction_snapshot  # noqa: E402
from tests.conformance.conftest import SNAPSHOT_MODELS  # noqa: E402

FIXTURES = REPO / "tests" / "fixtures"

# The recorded failure coordinate (`tests/fixtures/nested_occurrence_override_probe/`) has
# no committed extraction snapshot — it is expected to halt, so it was never captured. It
# therefore cannot be scanned here; the positive case is pinned by the Phase-1 unit test,
# which constructs the coordinate from the BACKLOG entry directly.


def unmatched_override_scopes(
    target: _BindingTarget,
    records: list[RedefinitionData],
) -> list[str]:
    """Candidate predicate: captured scopes of overrides sharing the demand's leaf name.

    Name-only variant (widest). The part-usage-leaf tightening is applied by
    `unmatched_override_scopes_tight` below; the scan reports both.
    """
    return sorted(
        {
            record.owning_part_qn
            for record in records
            if record.attribute_name == target.attr and record.owning_part_qn
        }
    )


def unmatched_override_scopes_tight(
    target: _BindingTarget,
    records: list[RedefinitionData],
) -> list[str]:
    """Narrower variant: the override's captured scope must also mention the part usage.

    Either the override's owning QN ends in the demanded part-usage leaf (the
    definition-relative capture of `Design__panel` against a demanded
    `the_design__panel`), or its dotted target_path names the part usage.
    """
    # Shape gate: only an instance-relative dotted demand can suffer the
    # occurrence-vs-definition scope mismatch. The clean-corpus false-fire set was
    # entirely `::` reference-form demands naming library defs.
    if target.form != "dotted":
        return []
    scopes: set[str] = set()
    for record in records:
        if record.attribute_name != target.attr or not record.owning_part_qn:
            continue
        owner_leaf = record.owning_part_qn.rsplit("__", 1)[-1]
        path = list(record.target_path or [])
        if owner_leaf == target.part_usage or target.part_usage in path:
            scopes.add(record.owning_part_qn)
    return sorted(scopes)


def scan(model: str) -> dict:
    snap = load_extraction_snapshot(FIXTURES / model / "extraction_snapshot.json")
    hierarchy = snap["hierarchy_data"]
    prepared = (
        prepare_constraint_usages(
            snap["constraint_facts"],
            occ_index=FrozenOccurrenceIndex(snap["part_occurrences"]),
            calc_usages=snap["calc_usages"],
            source_location_mode="snapshot",
            source_roots=[],
        )
        if snap["constraint_lowering_mode"] == CONSTRAINT_LOWERING_MODE_APPLIED
        and snap["constraint_facts"].usages
        else None
    )
    records = list(hierarchy.design_overrides) + list(hierarchy.redefinitions)

    wide: list[tuple[str, list[str]]] = []
    tight: list[tuple[str, list[str]]] = []
    demands = _logical_demands(snap["calc_usages"], prepared)
    for demand in demands:
        resolved = resolve_logical_demand(
            demand,
            redefinitions=hierarchy.redefinitions,
            design_overrides=hierarchy.design_overrides,
            usage_type_map=hierarchy.usage_type_map,
            exact_real_sources={},
        )
        if resolved.value is not None or resolved.nonliteral or resolved.malformed_literal:
            continue
        scopes = unmatched_override_scopes(demand.target, records)
        if scopes:
            wide.append((demand.target.qn, scopes))
        scopes_tight = unmatched_override_scopes_tight(demand.target, records)
        if scopes_tight:
            tight.append((demand.target.qn, scopes_tight))
    return {"model": model, "demands": len(demands), "wide": wide, "tight": tight}


def main() -> int:
    results = [scan(model) for model in SNAPSHOT_MODELS]

    print(f"{'fixture':<34} {'demands':>7} {'wide':>5} {'tight':>5}")
    for row in results:
        print(
            f"{row['model']:<34} {row['demands']:>7} "
            f"{len(row['wide']):>5} {len(row['tight']):>5}"
        )
    print()
    for row in results:
        for qn, scopes in row["tight"]:
            print(f"  TIGHT FIRE  {row['model']}: {qn} <- {scopes}")
        for qn, scopes in row["wide"]:
            print(f"  WIDE  FIRE  {row['model']}: {qn} <- {scopes}")

    clean_wide = sum(len(row["wide"]) for row in results)
    clean_tight = sum(len(row["tight"]) for row in results)
    print()
    print(f"clean-corpus fires: wide={clean_wide} tight={clean_tight}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
