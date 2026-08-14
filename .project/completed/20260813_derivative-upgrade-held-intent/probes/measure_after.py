"""Measure the projected shape of an edited fixture against the baseline.

Reports the facts the design has to record: the entry-point key set that leaves and arrives,
the minted `unit_text` on the new constraint and derived-attribute ports, the module count,
and the coverage account / disposition histogram.

The coverage numbers here are a CONFIRMATION of what the spec fixed from the ruled table in
advance; they are not the source of the committed expectations (SC-6).

Usage:  python measure_after.py <baseline-root> <edited-root>
"""

from __future__ import annotations

import sys
from pathlib import Path

from sysml_codegen.elaboration import project
from sysml_codegen.generation.coverage import coverage_account
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths


def _entry_units(graph) -> dict[str, str | None]:
    return {
        parameter.qualified_name: parameter.unit_text
        for group in graph.entry_point_groups
        for parameter in group.parameters
    }


def _projected(root: Path):
    return project(elaborate_model_paths([root]))


def main() -> int:
    baseline = _projected(Path(sys.argv[1]))
    edited = _projected(Path(sys.argv[2]))

    before, after = _entry_units(baseline), _entry_units(edited)
    left, arrived = sorted(set(before) - set(after)), sorted(set(after) - set(before))

    print(f"modules: {len(baseline.modules)} -> {len(edited.modules)}")
    print(f"entry points: {len(before)} -> {len(after)}")

    print(f"\nkeys that LEFT ({len(left)}):")
    for key in left:
        print(f"  {key}   (was unit={before[key]!r})")
    print(f"\nkeys that ARRIVED ({len(arrived)}):")
    for key in arrived:
        print(f"  {key}   (unit={after[key]!r})")

    print("\nunit_text on surviving radial-build free parameters:")
    for key, unit in sorted(after.items()):
        if "catf_radial_build" in key and ("thickness" in key or "inner_radius" in key):
            print(f"  {key:70} unit={unit!r}")

    print("\nunit_text on the A9 entry points:")
    for key, unit in sorted(after.items()):
        if "catf_vacuum_pumping" in key and "cryo_pumps" not in key:
            print(f"  {key:70} unit={unit!r}")

    catalog = edited.constraint_catalog
    assert catalog is not None
    print(f"\ncoverage account: {coverage_account(catalog).as_mapping()}")
    histogram: dict[str, int] = {}
    for row in catalog.usage_records:
        histogram[str(row.disposition_kind)] = histogram.get(str(row.disposition_kind), 0) + 1
    print(f"disposition histogram: {histogram}")
    print(f"catalog usage rows: {len(catalog.usage_records)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
