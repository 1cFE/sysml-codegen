"""THROWAWAY (Item 5 Phase 2). Derive the 58-carrier expectation from the RULED TABLE.

Not from a dump. The construction is:

    d5's 65-row expectation  −  the 7 named deletions  +  the 2 renames  =  the 58 carriers

and that construction is then cross-checked against a source scan of what the author will
write. The scan supplies line numbers (deletions above a row shift it) and is a *check* on
the membership, never its source — Item 3's PD2/DR-6 rule. A disagreement is a triage, not a
quiet edit.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path("/home/reid/1cfe/sysml-codegen-item7-rebuild")
sys.path.insert(0, str(REPO))
from tests.helpers.constraint_source_scan import scan_constraint_declarations  # noqa: E402

D5 = json.loads(
    (REPO / "tests/expectations/constraint_population/catf_mfe_d5.json").read_text()
)

#: The 7 named deletions, each with its authorizing row in `owner-disposition.md`.
DELETIONS = {
    "CATFMFEPhysics::catf_physics::PowerBalanceConsistency": "A1 (derive-instead)",
    "CATFMFERadialBuild::catf_radial_build::TotalRadiusConsistency": "A4 (derive-instead)",
    "CATFMFEShield::catf_shield::CompositionConsistency": "A7 (derive-instead)",
    "CATFMFEVacuum::catf_vacuum_vessel::ThicknessConsistency": "A8 (derive-instead)",
    "FusionPhysics_PowerBalance::AlphaNeutronSplit::EnergyConservation": "C37 (derive-instead)",
    "FusionPhysics_Confinement::PlasmaConfinement::Phase2PlasmaParametersPhysical": "C21 (O2)",
    "FusionPhysics_Neutronics::TritiumBreedingRatio::Phase2SelfSufficiency": "C28 (O2)",
}

#: The 2 renamed carriers: d5 qualified name -> derivative qualified name.
RENAMES = {
    "CATFMFEPhysics::catf_physics::ViabilityCheck": (
        "CATFMFEPhysics::catf_physics::net_power_viable"
    ),
    "CATFMFEPhysics::catf_physics::ReasonableParasiticTotal": (
        "CATFMFEPhysics::catf_physics::parasitic_fraction_ok"
    ),
}


def main(source_root: Path, out_path: Path) -> None:
    rows = D5["constraint_usages"]
    assert len(rows) == 65, len(rows)

    qns = {row["usage_qualified_name"] for row in rows}
    assert not set(DELETIONS) - qns, f"deletion names not in d5's 65: {set(DELETIONS) - qns}"
    assert not set(RENAMES) - qns, f"rename sources not in d5's 65: {set(RENAMES) - qns}"

    derived = [r for r in rows if r["usage_qualified_name"] not in DELETIONS]
    assert len(derived) == 58, f"65 - 7 = {len(derived)}"
    print(f"identity: 65 = {len(derived)} carriers + {len(DELETIONS)} named deletions")

    scanned = {
        item.as_row()["usage_qualified_name"]: item.as_row()
        for item in scan_constraint_declarations(source_root)
    }
    expected = {
        RENAMES.get(r["usage_qualified_name"], r["usage_qualified_name"]) for r in derived
    }
    assert expected == set(scanned), (
        "derivation vs source disagree\n"
        f"  in derivation only: {sorted(expected - set(scanned))}\n"
        f"  in source only:     {sorted(set(scanned) - expected)}"
    )
    print(f"cross-check: derivation and source agree on all {len(expected)} identities")

    document = {
        "constraint_usages": sorted(
            (scanned[name] for name in expected),
            key=lambda r: (r["source_file"], r["source_line"]),
        ),
        "fixture": "catf_mfe_gated",
    }
    out_path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(f"wrote {out_path} with {len(document['constraint_usages'])} rows")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
