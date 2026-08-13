"""Item 5 Phase 3. Build `tests/fixtures/catf_mfe_gated/` in Phase 1's proven group order.

Same edits, same order, same result — at fixture scale rather than scratch scale. Re-elaborates
after each group, because the landing is atomic: a profile BLOCK or a projection collision halts
the whole model, so a late discovery costs the entire authoring pass.

Run once. The fixture it produces is committed; this script is the record of how, and is not
itself authority — `owner-disposition.md` is.
"""

from __future__ import annotations

import shutil
import sys
from collections import Counter
from pathlib import Path

import edits
import edits2
import edits3

REPO = Path("/home/reid/1cfe/sysml-codegen-item7-rebuild")
SRC = REPO / "tests/fixtures/catf_mfe_d5"
DST = REPO / "tests/fixtures/catf_mfe_gated"

#: Phase 1's proven order. `ruled_lib` first because A2's import references it.
GROUPS: tuple[tuple[str, tuple], ...] = (
    ("library (D5: PositiveQuantity, FractionWithinBand)", (edits3.write_library,)),
    ("A2 assert-one-sided", (edits.apply_a2,)),
    ("A3 assert-band", (edits.apply_a3,)),
    ("A7 + A8 derivations", (edits2.apply_a7, edits2.apply_a8)),
    ("A1 + C37 derivation and their usage deletions", (edits3.apply_group3,)),
    ("A4, C21, C28 deletions", (edits3.apply_group4,)),
    ("A7 + A8 usage deletions", (edits3.apply_group4b,)),
)


def elaborate(label: str) -> None:
    from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline

    graph = build_elaborated_pipeline([DST])
    catalog = graph.constraint_catalog
    assert catalog is not None, f"{label}: no catalog"
    histogram = Counter(row.disposition_kind for row in catalog.usage_records)
    print(
        f"  ADMIT  {len(graph.modules):>2} modules | "
        f"{len(catalog.usage_records):>2} rows | "
        f"{len(catalog.concrete_entries)} concrete | {dict(histogram)}"
    )


def main() -> None:
    assert not DST.exists(), f"{DST} already exists — this script builds it once"
    shutil.copytree(SRC, DST)
    for name in ("instance_graph_snapshot.json", "PROVENANCE.md"):
        (DST / name).unlink()
    print(f"forked {SRC.name} -> {DST.name}")
    elaborate("fork, unedited")

    for label, actions in GROUPS:
        for action in actions:
            action(DST)
        print(f"applied: {label}")
        elaborate(label)


if __name__ == "__main__":
    sys.exit(main())
