"""The derivative's integrity check, and proof that it fails closed.

`catf_mfe_gated` deliberately differs from `catf_mfe_d5`, so the byte-reversal proof that pins
the other d5 variants cannot transfer to it. `scripts/check_gated_manifest.py` replaces it with
an accounting identity — ``65 = 58 carriers + 7 named deletions`` — joined from committed
artifacts, license-free.

**A check nobody has seen fail is not yet a check.** The identity would close vacuously if the
`renamed_from:` bridge were dropped or pointed somewhere a deletion already claims, so both of
those mutations are exercised here for real, against a temporary copy of the fixture, and the
check must refuse each one by name.

The same standard applies to the **deletion** side (audit A-3). A deletion record used to be
accepted on the strength of citing an authorizing row, so nothing tied it to the derivation it
promises — which is how two derivations shipped without the relation intent the owner ruled must
survive the deletion. `check_derivations` reads the `.sysml`, and both of its failure modes are
exercised here: the documentation stripped, and the initializer itself gone.
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts/check_gated_manifest.py"

_spec = importlib.util.spec_from_file_location("check_gated_manifest", SCRIPT)
assert _spec is not None and _spec.loader is not None
check_gated_manifest = importlib.util.module_from_spec(_spec)
sys.modules["check_gated_manifest"] = check_gated_manifest
_spec.loader.exec_module(check_gated_manifest)

ManifestError = check_gated_manifest.ManifestError


@pytest.fixture
def provenance_text() -> str:
    return check_gated_manifest.PROVENANCE.read_text()


@pytest.fixture
def mutated_provenance(provenance_text, monkeypatch, tmp_path):
    """Rewrite PROVENANCE into a temp file and point the check at it.

    The committed fixture is never edited — a falsification that mutates a committed artifact
    and relies on a revert is one interrupted run away from corrupting the tree.
    """

    def _apply(before: str, after: str):
        assert before in provenance_text, f"anchor not in PROVENANCE: {before!r}"
        path = tmp_path / "PROVENANCE.md"
        path.write_text(provenance_text.replace(before, after, 1))
        monkeypatch.setattr(check_gated_manifest, "PROVENANCE", path)

    return _apply


def test_the_identity_closes():
    result = check_gated_manifest.run()
    assert result.authored == 65
    assert result.carriers == 58
    assert result.deletions == 7
    assert result.matched_by_name == 56
    assert result.matched_by_renamed_from == 2


def test_every_deletion_cites_an_authorizing_table_row(provenance_text):
    deletions = check_gated_manifest.parse_deletions(provenance_text)
    assert len(deletions) == 7
    assert {record.table_row for record in deletions} == {
        "A1", "A4", "A7", "A8", "C37", "C21", "C28"
    }
    for record in deletions:
        assert "owner-disposition.md" in record.authorizing_row, record


def test_an_unmatched_carrier_fails_closed(mutated_provenance):
    """Drop a `renamed_from:` and the carrier it bridged becomes unaccountable."""
    mutated_provenance(
        "- **`renamed_from:` `CATFMFEPhysics::catf_physics::ViabilityCheck`**",
        "- **was once called** `CATFMFEPhysics::catf_physics::ViabilityCheck`",
    )
    with pytest.raises(ManifestError) as failure:
        check_gated_manifest.run()
    assert "renamed_from" in str(failure.value)


def test_a_renamed_from_claimed_by_a_deletion_fails(mutated_provenance):
    """Point a `renamed_from:` at a row a deletion record already claims."""
    mutated_provenance(
        "- **`renamed_from:` `CATFMFEPhysics::catf_physics::ViabilityCheck`**",
        "- **`renamed_from:` `CATFMFEPhysics::catf_physics::PowerBalanceConsistency`**",
    )
    with pytest.raises(ManifestError) as failure:
        check_gated_manifest.run()
    message = str(failure.value)
    assert "a deletion record also claims" in message
    assert "PowerBalanceConsistency" in message


def test_every_derive_instead_row_has_its_derivation_in_source():
    """The deletion side's outside evidence (audit A-3).

    The document join alone accepted a deletion record on the strength of citing an authorizing
    row. Whether the derivation it promises exists, and whether it carries the relation intent
    the owner ruled must survive the deletion, went unchecked — which is how two bare
    initializers rode through four phases of gates.
    """
    assert check_gated_manifest.check_derivations(check_gated_manifest.FIXTURE_ROOT) == []


def test_a_derivation_missing_its_basis_comment_fails_closed(tmp_path, monkeypatch):
    """Strip A7's relation + chosen-basis block and the check must name that row."""
    root = tmp_path / "catf_mfe_gated"
    shutil.copytree(check_gated_manifest.FIXTURE_ROOT, root)
    shield = root / "designs/catf_mfe/shield.sysml"
    stripped = [
        line
        for line in shield.read_text().splitlines(keepends=True)
        if "Relation (undirected): neutron_shield" not in line
        and "CHOSEN BASIS, not physics: neutron_shield" not in line
    ]
    shield.write_text("".join(stripped))

    problems = check_gated_manifest.check_derivations(root)
    assert len(problems) == 1
    assert "CompositionConsistency" in problems[0]
    assert "the undirected relation" in problems[0]
    assert "the chosen-basis statement" in problems[0]


def test_a_missing_derivation_fails_closed(tmp_path):
    """The other half: the initializer itself gone, not just its documentation."""
    root = tmp_path / "catf_mfe_gated"
    shutil.copytree(check_gated_manifest.FIXTURE_ROOT, root)
    vacuum = root / "designs/catf_mfe/vacuum.sysml"
    vacuum.write_text(
        vacuum.read_text().replace(
            "attribute outer_radius : Real = inner_radius + wall_thickness;",
            "attribute outer_radius : Real = 6.5 [m];",
        )
    )

    problems = check_gated_manifest.check_derivations(root)
    assert len(problems) == 1
    assert "ThicknessConsistency" in problems[0]
    assert "not found" in problems[0]


def test_a_deletion_without_an_authorizing_row_fails(mutated_provenance):
    """The other way an unauthorized change could slip through."""
    mutated_provenance(
        "- **Authorizing row:** `owner-disposition.md` Group A, A4 (`derive-instead`)",
        "- **Reason:** it looked redundant",
    )
    with pytest.raises(ManifestError) as failure:
        check_gated_manifest.run()
    assert "cites no authorizing table row" in str(failure.value)
