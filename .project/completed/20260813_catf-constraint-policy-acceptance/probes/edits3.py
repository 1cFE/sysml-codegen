"""THROWAWAY (Item 5 Phase 1). The edits P7 never tested, group by group.

P7 proved the library + A2 + A3 + A7 + A8 + the axis leg. It deleted nothing, kept all 65
usage rows, and derived the axis leg the D-S2 ruling drops. This module carries the rest of
the ruled shape so B2 can be tested at full scope before the fixture exists:

    group 3 — A1 + C37, the AlphaNeutronSplit derivation and its two deleted usages
    group 4 — the A4, C21, C28 deletions
    group 5 — the five `@inapplicable:` markers on B1-B5
    group 6 — the axis-leg reversal (P7 had it; the ruling drops it)

Nothing here touches a committed fixture. Authority is `owner-disposition.md`.
"""

from __future__ import annotations

from pathlib import Path

from edits import replace

#: The ruled library (D5). `ProductWithinBand` is deliberately absent - its only consumer
#: (A9) is parked by the D-S1 ruling, so authoring it would ship an unused definition.
GATE_LIBRARY = '''/*
 * Constraint-definition library for the CATF gated derivative.
 *
 * Two forms, both over bare `Real` formals with predicates written over formals only
 * (the blessed bindings-only gate shape, rulings-20260812 Q4). Neither carries a `[unit]`
 * literal: the toolchain does not check units on constraint bindings at all, so the unit
 * correctness of every binding here is human-owned (owner-disposition.md, unit-check column).
 */
package CATFGateForms {
    public import ScalarValues::*;

    constraint def PositiveQuantity {
        in value : Real;
        value > 0
    }

    constraint def FractionWithinBand {
        in part_power : Real;
        in whole_power : Real;
        in lower_frac : Real;
        in upper_frac : Real;
        part_power > whole_power * lower_frac and part_power < whole_power * upper_frac
    }
}
'''


def write_library(root: Path) -> None:
    target = root / "library" / "constraints"
    target.mkdir(parents=True, exist_ok=True)
    (target / "gate_forms.sysml").write_text(GATE_LIBRARY)


def _delete(path: Path, block: str) -> None:
    """Remove an authored constraint usage, and the blank line it left behind."""
    text = path.read_text()
    assert block in text, f"anchor not found in {path}:\n{block[:160]}"
    assert text.count(block) == 1, f"anchor is not unique in {path}"
    path.write_text(text.replace(block, "", 1))


# --------------------------------------------------------------- group 3: A1 + C37
A1_BLOCK = """        // Energy conservation constraint
        constraint PowerBalanceConsistency {
            doc /*
            Verify energy conservation through the entire power chain.
            Alpha + Neutron should equal fusion power within 0.1%
            */
            alpha_neutron_split.p_alpha + alpha_neutron_split.p_neutron > p_fusion * 0.999 and
            alpha_neutron_split.p_alpha + alpha_neutron_split.p_neutron < p_fusion * 1.001
        }

"""

C37_BLOCK = """        // Energy conservation check
        constraint EnergyConservation {
            doc /* Verify alpha + neutron = total fusion power (within 0.001%) */
            p_alpha + p_neutron > p_fusion * 0.99999 and
            p_alpha + p_neutron < p_fusion * 1.00001
        }

"""

C37_OLD_DERIVATION = (
    "        out attribute p_neutron : Real = p_fusion * 14.06 / 17.58;"
    "  // MW - Neutron power (80%)"
)

#: The undirected relation and the chosen-basis statement the owner's structural amendment
#: requires, carried in source beside the derivation and repeated in PROVENANCE.
C37_NEW_DERIVATION = """        // Relation (undirected): p_alpha + p_neutron = p_fusion. The DT branching ratios
        // 3.52/17.58 and 14.06/17.58 sum to exactly 1, so this holds by construction.
        // Direction is a CHOSEN BASIS, not physics: p_alpha is taken as the free branch and
        // p_neutron derived as the remainder. The reverse basis is equally valid.
        // Authority: owner-disposition.md Group C, C37 (derive-instead); pairs with A1.
        out attribute p_neutron : Real = p_fusion - p_alpha;  // MW - Neutron power (80%)"""


def apply_group3(root: Path) -> None:
    _delete(root / "designs" / "catf_mfe" / "physics.sysml", A1_BLOCK)
    power_balance = root / "library" / "physics" / "power_balance.sysml"
    _delete(power_balance, C37_BLOCK)
    replace(power_balance, C37_OLD_DERIVATION, C37_NEW_DERIVATION)


# ------------------------------------------------- group 4: A4, C21, C28 deletions
A4_BLOCK = """        // Radial Build Consistency Constraints
        constraint TotalRadiusConsistency {
            doc /* Total outer radius must equal sum of all layer thicknesses */

            // Total from PyFECONS: 3.0 + 1.1 + 0.1 + 0.2 + 0.8 + 0.2 + 0.2 + 0.2 + 0.5 + 0.2 + 0.25 + 0.5 + 0.3 + 1.0 = 8.55 m
            bioshield.outer_radius == 8.55 [m]
        }

"""

C21_BLOCK = """        // Phase 2 constraint placeholder (not enforced in Phase 1)
        constraint Phase2PlasmaParametersPhysical {
            doc /* Phase 2: Will validate plasma parameters are physical */
            true  // Placeholder - implement in Phase 2
        }
"""

C28_BLOCK = """        // Phase 2 constraint placeholder (not enforced in Phase 1)
        constraint Phase2SelfSufficiency {
            doc /* Phase 2: Will check TBR ≥ 1.05 for fuel self-sufficiency */
            true  // Placeholder - implement in Phase 2
        }
"""


def apply_group4(root: Path) -> None:
    _delete(root / "designs" / "catf_mfe" / "radial_build.sysml", A4_BLOCK)
    _delete(root / "library" / "physics" / "confinement.sysml", C21_BLOCK)
    _delete(root / "library" / "physics" / "neutronics.sysml", C28_BLOCK)


# ------------------------------------------ group 5: the five @inapplicable markers
#
# Two authoring traps, both measured by Item 2 fixtures:
#   - the marker is read only on the FIRST line of the joined documentation
#     (`constraint_domain_inapplicable_late_marker`), so it goes at the top of the first
#     `doc` body, not appended to it;
#   - a malformed marker (no colon, no reason) halts generation at `error` whatever the
#     usage's form (`constraint_domain_inapplicable_plain_form`).
#
# The form is copied from `tests/fixtures/constraint_domain_inapplicable/model.sysml:20`.
MARKERS: tuple[tuple[str, str, str, str], ...] = (
    (
        "divertor.sysml",
        "        constraint HeatLoadBalance {\n            doc /*\n",
        "@inapplicable: no divertor part exists in designs/catf_mfe - gating divertor "
        "power exhaust means adding a divertor, which is a modeling decision (O5)",
        "B1",
    ),
    (
        "first_wall.sysml",
        "        constraint TotalThicknessConsistency {\n            doc /*\n",
        "@inapplicable: no structurally matching design part - the design's first_wall is a "
        "radial-build layer with no armor_layer or structural_backing children",
        "B2",
    ),
    (
        "radial_build.sysml",
        "        constraint RadiusConsistency {\n            doc /*\n",
        "@inapplicable: superseded by derivation - each layer's outer_radius is derived from "
        "inner_radius + thickness, so an attached guard would be vacuous (L2-2)",
        "B3",
    ),
    (
        "shield.sysml",
        "        constraint TotalThicknessConsistency {\n            doc /*\n",
        "@inapplicable: superseded by derivation - thickness_total is a composition closure "
        "derived from the layer thicknesses (O3 records the mismatched sets)",
        "B4",
    ),
    (
        "vacuum.sysml",
        "        constraint ThicknessConsistency {\n            doc /*\n",
        "@inapplicable: superseded by derivation - outer_radius is derived from "
        "inner_radius + wall_thickness at A8, so an attached guard would be vacuous",
        "B5",
    ),
)


def apply_group5(root: Path) -> None:
    for filename, anchor, reason, _row in MARKERS:
        replace(
            root / "library" / "components" / filename,
            anchor,
            f"{anchor}            {reason}\n",
        )


# ------------------------------------------------------- group 6: axis-leg reversal
def apply_group6(root: Path) -> None:
    """Undo the one A5/A6 leg P7 derived. The ruling keeps one consistent basis."""
    replace(
        root / "designs" / "catf_mfe" / "radial_build.sysml",
        "            attribute outer_radius : Real = inner_radius + thickness;",
        "            attribute outer_radius : Real = 3.0 [m];  // Calculated",
    )


# ------------------- group 4b: the A7 and A8 usage deletions (derive-instead's other half)
#
# `edits2.apply_a7` / `apply_a8` only author the derivation. `derive-instead` also deletes
# the authored usage the derivation replaces - that is the whole point of the disposition,
# and it is the -2 that takes the probe from 60 rows to the ruled 58.
A7_BLOCK = """        // Shield Composition Fractions (must sum to 1.0)
        constraint CompositionConsistency {
            doc /* Shield composition fractions must sum to 1.0 */
            neutron_shield.fraction_volume + gamma_shield.fraction_volume == 1.0
        }

"""

A8_BLOCK = """        // Constraint for geometry consistency
        constraint ThicknessConsistency {
            doc /* Outer radius must equal inner radius plus wall thickness */
            outer_radius == inner_radius + wall_thickness
        }
"""


def apply_group4b(root: Path) -> None:
    _delete(root / "designs" / "catf_mfe" / "shield.sysml", A7_BLOCK)
    _delete(root / "designs" / "catf_mfe" / "vacuum.sysml", A8_BLOCK)
