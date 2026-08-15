"""THROWAWAY (Item 5 design stage). Elaborate a scratch fixture and report the outcome.

Usage:  probes/licensed.sh probes/run_probe.py /tmp/item5probe/p1
"""

from __future__ import annotations

import sys
from pathlib import Path

from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline


def main(root: Path) -> None:
    print(f"=== {root}")
    try:
        graph = build_elaborated_pipeline([root])
    except Exception as error:  # noqa: BLE001 - a probe reports whatever it gets
        print(f"RESULT: REFUSED -> {type(error).__name__}")
        text = str(error)
        print(text[:5000])
        if len(text) > 5000:
            print(f"... [{len(text) - 5000} more chars]")
        return

    print(f"RESULT: ADMITTED -> {len(graph.modules)} modules")
    catalog = graph.constraint_catalog
    if catalog is None:
        print("catalog: None")
        return
    rows = catalog.usage_records
    kinds: dict[str, int] = {}
    for row in rows:
        kinds[row.disposition_kind] = kinds.get(row.disposition_kind, 0) + 1
    print(f"usage_records: {len(rows)}  dispositions: {kinds}")
    print(f"concrete_entries: {len(catalog.concrete_entries)}")
    print(f"excluded_records: {len(catalog.excluded_records)}")
    print(f"source_records: {[s.definition_qualified_name for s in catalog.source_records]}")
    for entry in catalog.concrete_entries:
        print(f"  ENTRY {entry.usage_qualified_name}")
        print(f"        ir={entry.predicate_ir}")
        print(f"        channel={entry.evaluation_channel}")
    for row in rows:
        if row.disposition_kind == "eligible":
            print(f"  ELIGIBLE {row.usage_qualified_name} occ={row.occurrence_count}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
