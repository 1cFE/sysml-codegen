"""Item 8 INV-6 tripwire (codegen side): the catalog producer records semantics, never
re-derives them from strings (spec SC-2, design.md:308).

Codegen holds `source_form`, the owner/definition QNs, and the def->usage join as *recorded*
fields on `ConcreteConstraint` and projects them onto the catalog entry. The alternate system
that Item 8 deleted reconstructed those semantics from strings — splitting a serialized key to
recover a QN, substring-searching predicate text to recover the definition link, or hardcoding a
`source_form` literal. This scan fails loudly if any of those idioms reappears in the catalog
producer.

Scoped to the *reconstruction* anti-pattern (design review F5), not a blanket QN-split ban:
codegen legitimately builds and sanitizes qualified names in many places. The guard targets only
the catalog-producing modules and only the specific string-reconstruction idioms, so legitimate QN
handling stays free. Its TEAx-consumer counterpart is
`teax .../tests/study/test_no_reconstruction.py`; together they cover both sides of spec SC-2.
"""

from __future__ import annotations

import re
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[2] / "src" / "sysml_codegen"

# The modules that assemble the catalog and record its identity fields. A reconstruction
# workaround would live here — this is where the recorded fields are read and projected.
# The lowering module that used to hold the minting half retired with the v5 family
# (retirement step 2); the exact route mints its ``ConcreteConstraint``s in
# ``elaboration/project.py``, off the ``ConstraintNode`` fields ``elaboration/graph.py``
# records, so those two files take its place in the scan set.
CATALOG_PRODUCER_FILES = [
    SRC_DIR / "generation" / "constraint_catalog.py",
    SRC_DIR / "elaboration" / "project.py",
    SRC_DIR / "elaboration" / "graph.py",
    SRC_DIR / "resolution" / "models.py",
]

# Deriving a QN by splitting the serialized predicate source key, instead of reading the recorded
# `definition_qualified_name` / `owner_qualified_name`.
_KEY_SPLIT = re.compile(r"predicate_source_key\s*\.\s*r?split\(")
# Recovering the definition link by searching serialized predicate text.
_PREDICATE_TEXT_SEARCH = re.compile(
    r"predicate_ir\s*\.\s*(?:find|index|split)\(|in\s+\S*predicate_ir"
)
# Hardcoding a source form literal instead of carrying the usage's recorded form.
_HARDCODED_SOURCE_FORM = re.compile(
    r"source_form\s*=\s*['\"](?:inline|definition_typed)['\"]"
)

_IDIOMS = {
    "predicate_source_key string-split (QN reconstruction)": _KEY_SPLIT,
    "predicate_ir text search (definition-link reconstruction)": _PREDICATE_TEXT_SEARCH,
    "hardcoded source_form literal": _HARDCODED_SOURCE_FORM,
}


def _scan(pattern: re.Pattern[str]) -> list[str]:
    offenders: list[str] = []
    for path in CATALOG_PRODUCER_FILES:
        for lineno, line in enumerate(path.read_text().splitlines(), start=1):
            if pattern.search(line):
                offenders.append(f"{path.relative_to(SRC_DIR)}:{lineno}: {line.strip()}")
    return offenders


def test_catalog_producer_does_not_reconstruct_semantics_from_strings():
    all_offenders: list[str] = []
    for label, pattern in _IDIOMS.items():
        for hit in _scan(pattern):
            all_offenders.append(f"[{label}] {hit}")
    assert all_offenders == [], (
        "Catalog reconstruction anti-pattern reappeared (INV-6) — read the recorded field, "
        "do not re-derive it from a string:\n" + "\n".join(all_offenders)
    )


def test_scan_actually_covers_the_catalog_producer():
    """Guard the guard: the scanned files must exist and be the real assembly path, or the
    scan proves nothing."""
    for path in CATALOG_PRODUCER_FILES:
        assert path.is_file(), f"catalog producer file missing from scan set: {path}"
    assembly = (SRC_DIR / "generation" / "constraint_catalog.py").read_text()
    assert "source_form=" in assembly, "scan set no longer covers catalog entry projection"
    minting = (SRC_DIR / "elaboration" / "project.py").read_text()
    assert "source_form=node.source_form" in minting, (
        "scan set no longer covers the exact route's ConcreteConstraint minting"
    )
