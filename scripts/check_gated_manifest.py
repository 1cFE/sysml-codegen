#!/usr/bin/env python3
"""Prove the CATF derivative's accounting identity closes: ``65 = 56 carriers + 9 deletions``.

`catf_mfe_gated` deliberately differs from `catf_mfe_d5`, so the byte-reversal check that pins
the other d5 variants cannot transfer to it (`scripts/make_d5_variant.py`). This is its
replacement, and it proves a stronger thing than "what changed": it proves **every change was
authorized**.

The join, over committed artifacts and nothing else — **license-free by construction**:

=================================================================  =============================
`tests/expectations/constraint_population/catf_mfe_d5.json`        the 65 authored usages
`tests/expectations/constraint_population/catf_mfe_gated.json`     the 56 carriers
`tests/fixtures/catf_mfe_gated/PROVENANCE.md`                      renames + deletion records
`tests/expectations/gated_manifest/catf_mfe_gated.json`            the ruled table's counts
`tests/fixtures/catf_mfe_gated/**/*.sysml`                         the replacing derivations
=================================================================  =============================

**The fifth source is the deletion side's outside evidence.** The first four are all documents,
so a deletion record used to be accepted on the strength of citing an authorizing row — whether
the derivation it promises exists in source, and whether it carries the relation intent the
owner ruled must survive the deletion, went unchecked. Two bare initializers rode that gap
through four phases of gates (audit finding A-1). `check_derivations` closes it, which turns the
owner's documentation obligation from a claim into a gated property.

Every d5 usage must be **either** a carrier — matched by qualified name, or through the
``renamed_from:`` field on a carrier's per-change record — **or** a named deletion record citing
an authorizing table row. Nothing may be both, and nothing may be neither.

**The rename is why the join needs `renamed_from:` at all.** The two asserted gates were renamed
by the rewrite (`…::ViabilityCheck` → `…::net_power_viable`), so a plain name join would read
each as one deletion plus one addition and the identity would close for the wrong reason.
Joining on `declaration_id` cannot bridge it either — that key is content-derived, so a
rewritten usage does not keep it.

The check fails closed in both directions: a carrier matching neither by name nor by
``renamed_from:`` fails, and a ``renamed_from:`` naming a d5 row that a deletion record also
claims fails.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
D5_POPULATION = REPO / "tests/expectations/constraint_population/catf_mfe_d5.json"
GATED_POPULATION = REPO / "tests/expectations/constraint_population/catf_mfe_gated.json"
GATED_MANIFEST = REPO / "tests/expectations/gated_manifest/catf_mfe_gated.json"
FIXTURE_ROOT = REPO / "tests/fixtures/catf_mfe_gated"
PROVENANCE = FIXTURE_ROOT / "PROVENANCE.md"

#: One per-change record's rename pair, written as two adjacent bullet lines:
#:     - **`renamed_from:` `<d5 qualified name>`** (d5 `physics.sysml:134`)
#:     - **now:** `<derivative qualified name>`
RENAME_PAIR = re.compile(
    r"^- \*\*`renamed_from:`\s*`(?P<before>[^`]+)`.*?^- \*\*now:\*\*\s*`(?P<after>[^`]+)`",
    re.DOTALL | re.MULTILINE,
)

#: The same field, matched on its own so a record missing its `**now:**` partner is counted
#: and refused rather than silently skipped. Anchored to the bullet form so the file's prose
#: mentions of the field name are not mistaken for records.
RENAME_FIELD = re.compile(r"^- \*\*`renamed_from:`", re.MULTILINE)

#: One deletion record's heading:
#:     ### D3 — A7 `CATFMFEShield::catf_shield::CompositionConsistency`
DELETION_HEADING = re.compile(r"^### D\d+ — (\S+) `([^`]+)`\s*$", re.MULTILINE)

#: The citation every deletion record must carry:
#:     - **Authorizing row:** owner-disposition.md Group A, A7 (`derive-instead`)
AUTHORIZING_ROW = re.compile(r"^- \*\*Authorizing row:\*\*\s*(.+?)\s*$", re.MULTILINE)


class ManifestError(Exception):
    """The identity does not close. Carries every failing row by name."""


@dataclass(frozen=True)
class DeletionRecord:
    """One named deletion in the derivative's PROVENANCE."""

    table_row: str
    usage_qualified_name: str
    authorizing_row: str


#: Each `derive-instead` row, and how to find the derivation that replaces it in the
#: derivative's source. Keyed by the deleted usage's qualified name.
#:
#: The ruled table (`owner-disposition.md`) names all five. Two of them — A1 and A4 — are
#: deletions with no derivation of their own: A1 is the instance-level restatement of C37's
#: identity, and A4 asserted a literal against itself. The other three must exist in source
#: **and** carry the owner-required relation + chosen-basis statement.
DERIVATIONS: dict[str, tuple[str, str] | None] = {
    "CATFMFEPhysics::catf_physics::PowerBalanceConsistency": None,
    "CATFMFERadialBuild::catf_radial_build::TotalRadiusConsistency": None,
    "CATFMFEShield::catf_shield::CompositionConsistency": (
        "designs/catf_mfe/shield.sysml",
        "attribute fraction_volume : Real = 1.0 - neutron_shield.fraction_volume;",
    ),
    "CATFMFEVacuum::catf_vacuum_vessel::ThicknessConsistency": (
        "designs/catf_mfe/vacuum.sysml",
        "attribute outer_radius : Real = inner_radius + wall_thickness;",
    ),
    "FusionPhysics_PowerBalance::AlphaNeutronSplit::EnergyConservation": (
        "library/physics/power_balance.sysml",
        "out attribute p_neutron : Real = p_fusion - p_alpha;",
    ),
}

#: The two statements the owner's structural amendment requires beside every derivation
#: (`owner-disposition.md:37-41`). Matched case-insensitively on the comment block above the
#: initializer, because the point is that the statements are *there*, not their capitalization.
RELATION_MARKER = "relation (undirected):"
BASIS_MARKER = "chosen basis, not physics"

#: How far above an initializer the comment block may start. Generous enough for the longest
#: authored block (A7's seven lines, which also carries the O3 debt pointer).
COMMENT_WINDOW = 12


@dataclass(frozen=True)
class Result:
    """What the join proved. Every field is a count a caller can assert on."""

    authored: int
    carriers: int
    deletions: int
    matched_by_name: int
    matched_by_renamed_from: int


def usage_names(path: Path) -> set[str]:
    """The qualified names in a population expectation file."""
    document = json.loads(path.read_text())
    return {row["usage_qualified_name"] for row in document["constraint_usages"]}


def parse_renames(provenance: str) -> dict[str, str]:
    """Map each renamed carrier's new qualified name to the d5 name it came from.

    A ``renamed_from:`` with no ``**now:**`` beside it is a failure rather than a half-record:
    a rename the check cannot resolve is exactly how the identity would close vacuously.
    """
    renames = {
        match.group("after"): match.group("before")
        for match in RENAME_PAIR.finditer(provenance)
    }
    declared = len(RENAME_FIELD.findall(provenance))
    if declared != len(renames):
        raise ManifestError(
            f"{declared} renamed_from: field(s) in PROVENANCE but {len(renames)} resolved to a "
            "carrier — every renamed_from: needs a `**now:** `<qualified name>`` beside it"
        )
    return renames


def parse_deletions(provenance: str) -> list[DeletionRecord]:
    """The named deletion records, each with the table row it cites.

    A record whose section carries no ``Authorizing row:`` line is a failure, not a record with
    a blank field — an unauthorized deletion is what this check exists to catch.
    """
    headings = list(DELETION_HEADING.finditer(provenance))
    records = []
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(provenance)
        cite = AUTHORIZING_ROW.search(provenance[heading.start() : end])
        if cite is None:
            raise ManifestError(
                f"deletion record {heading.group(1)} ({heading.group(2)}) cites no "
                "authorizing table row"
            )
        records.append(
            DeletionRecord(
                table_row=heading.group(1),
                usage_qualified_name=heading.group(2),
                authorizing_row=cite.group(1),
            )
        )
    return records


def _comment_block_above(lines: list[str], index: int) -> str:
    """The contiguous `//` comment block immediately above `lines[index]`."""
    block = []
    cursor = index - 1
    while cursor >= 0 and index - cursor <= COMMENT_WINDOW:
        stripped = lines[cursor].strip()
        if not stripped.startswith("//"):
            break
        block.append(stripped)
        cursor -= 1
    return "\n".join(reversed(block)).lower()


def check_derivations(fixture_root: Path) -> list[str]:
    """Every `derive-instead` row's replacing derivation, in source, with its statements.

    The identity check joins four documents and never opens a `.sysml`, so a deletion record
    is otherwise accepted on the strength of citing an authorizing row — whether the
    derivation it promises exists, and whether it carries the relation intent the owner ruled
    must survive the deletion, went unchecked. That gap shipped two bare initializers past
    four phases of gates (audit finding A-1). This closes it.
    """
    problems: list[str] = []
    for usage, derivation in DERIVATIONS.items():
        if derivation is None:
            continue
        relative, initializer = derivation
        path = fixture_root / relative
        if not path.exists():
            problems.append(f"{usage}: {relative} does not exist")
            continue
        lines = path.read_text().splitlines()
        matches = [i for i, line in enumerate(lines) if initializer in line]
        if not matches:
            problems.append(
                f"{usage}: derive-instead promises `{initializer}` in {relative}, not found"
            )
            continue
        if len(matches) > 1:
            problems.append(f"{usage}: `{initializer}` is not unique in {relative}")
            continue
        comment = _comment_block_above(lines, matches[0])
        missing = [
            name
            for name, marker in (
                ("the undirected relation", RELATION_MARKER),
                ("the chosen-basis statement", BASIS_MARKER),
            )
            if marker not in comment
        ]
        if missing:
            problems.append(
                f"{usage}: the derivation at {relative}:{matches[0] + 1} is missing "
                f"{' and '.join(missing)} — required by owner-disposition.md:37-41"
            )
    return problems


def run() -> Result:
    """Join the four sources and prove the identity. Raises `ManifestError` on any failure."""
    authored = usage_names(D5_POPULATION)
    carriers = usage_names(GATED_POPULATION)
    provenance = PROVENANCE.read_text()
    renames = parse_renames(provenance)
    deletions = parse_deletions(provenance)

    deleted = {record.usage_qualified_name for record in deletions}
    matched_by_name = carriers & authored
    renamed_carriers = set(carriers) - authored

    problems: list[str] = []

    unknown = deleted - authored
    if unknown:
        problems.append(f"deletion records naming usages absent from d5: {sorted(unknown)}")

    unresolved = renamed_carriers - set(renames)
    if unresolved:
        problems.append(
            f"carriers matching neither by name nor by renamed_from: {sorted(unresolved)}"
        )

    claimed = {renames[name] for name in renamed_carriers & set(renames)}
    unknown = claimed - authored
    if unknown:
        problems.append(f"renamed_from: naming usages absent from d5: {sorted(unknown)}")

    contested = claimed & deleted
    if contested:
        problems.append(
            f"renamed_from: claims a d5 usage a deletion record also claims: {sorted(contested)}"
        )

    unaccounted = authored - matched_by_name - claimed - deleted
    if unaccounted:
        problems.append(
            f"d5 usages that are neither a carrier nor a named deletion: {sorted(unaccounted)}"
        )

    problems.extend(check_derivations(FIXTURE_ROOT))

    if problems:
        raise ManifestError("; ".join(problems))

    result = Result(
        authored=len(authored),
        carriers=len(carriers),
        deletions=len(deletions),
        matched_by_name=len(matched_by_name),
        matched_by_renamed_from=len(claimed),
    )
    if result.carriers + result.deletions != result.authored:
        raise ManifestError(
            f"identity does not close: {result.carriers} carriers + {result.deletions} "
            f"deletions != {result.authored} authored"
        )
    _refuse_disagreement_with_the_ruled_table(result)
    return result


def _refuse_disagreement_with_the_ruled_table(result: Result) -> None:
    """The join must agree with the ruled table's committed counts, field by field."""
    expected = json.loads(GATED_MANIFEST.read_text())
    mismatches = [
        f"{field}: joined {actual}, ruled table says {expected[field]}"
        for field, actual in (
            ("d5_authored_total", result.authored),
            ("carrier_total", result.carriers),
            ("deletion_total", result.deletions),
            ("matched_by_name", result.matched_by_name),
            ("matched_by_renamed_from", result.matched_by_renamed_from),
        )
        if expected[field] != actual
    ]
    if mismatches:
        raise ManifestError("; ".join(mismatches))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="run the join and report")
    parser.parse_args()
    try:
        result = run()
    except ManifestError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(
        f"identity closes: {result.authored} = {result.carriers} carriers "
        f"+ {result.deletions} named deletions"
    )
    print(f"  carriers matched by name:         {result.matched_by_name}")
    print(f"  carriers matched by renamed_from: {result.matched_by_renamed_from}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
