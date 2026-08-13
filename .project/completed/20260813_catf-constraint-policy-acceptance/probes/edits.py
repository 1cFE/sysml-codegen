"""THROWAWAY (Item 5 design stage). Apply probe edits to a scratch copy of catf_mfe_d5.

Nothing here touches a committed fixture. `setup_probe.py` makes the scratch copies under
/tmp/item5probe/; this module rewrites them in place. No output is authority — the findings
land in `design.md`.
"""

from __future__ import annotations

from pathlib import Path

GATE_LIBRARY = '''/*
 * THROWAWAY PROBE - fixture-local constraint-definition library.
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

    constraint def ProductWithinBand {
        in observed : Real;        // m^3/s
        in count : Real;           // Dimensionless
        in each_capacity : Real;   // m^3/s
        in rel_tol : Real;         // Dimensionless
        observed >= count * each_capacity * (1.0 - rel_tol) and
        observed <= count * each_capacity * (1.0 + rel_tol)
    }
}
'''


def write_library(root: Path) -> None:
    target = root / "library" / "constraints"
    target.mkdir(parents=True, exist_ok=True)
    (target / "gate_forms.sysml").write_text(GATE_LIBRARY)


def replace(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    assert old in text, f"anchor not found in {path}:\n{old[:120]}"
    assert text.count(old) == 1, f"anchor is not unique in {path}"
    path.write_text(text.replace(old, new))


# --------------------------------------------------------------------------- A2
A2_OLD = """        constraint ViabilityCheck {
            doc /*
            Net power must be positive for viable power plant.
            This ensures Q_eng > 1.0
            */
            p_electric_net_out > 0
        }"""

A2_NEW = """        assert constraint net_power_viable : PositiveQuantity {
            doc /*
            Net power must be positive for viable power plant.
            This ensures Q_eng > 1.0
            */
            in value = p_electric_net_out;
        }"""

# --------------------------------------------------------------------------- A3
A3_OLD = """        constraint ReasonableParasiticTotal {
            doc /*
            Total parasitic loads should be reasonable (10-90% of gross).
            Upper bound ensures Q_eng > 1.1 (CATF minimum)
            */
            net_electric.p_parasitic_total > gross_electric.p_electric_gross * 0.10 and
            net_electric.p_parasitic_total < gross_electric.p_electric_gross * 0.90
        }"""

A3_NEW = """        assert constraint parasitic_fraction_ok : FractionWithinBand {
            doc /*
            Total parasitic loads should be reasonable (10-90% of gross).
            Upper bound ensures Q_eng > 1.1 (CATF minimum)
            */
            in part_power = net_electric.p_parasitic_total;
            in whole_power = gross_electric.p_electric_gross;
            in lower_frac = 0.10;
            in upper_frac = 0.90;
        }"""

# --------------------------------------------------------------------------- A9
A9_OLD = """        constraint PumpingSpeedConsistency {
            doc /* Total pumping speed should match sum of pump capacities */
            pumping_speed_total == n_pumps * pump_capacity_each
        }"""

A9_NEW = """        assert constraint pumping_speed_agrees : ProductWithinBand {
            doc /* Total pumping speed should match sum of pump capacities */
            in observed = pumping_speed_total;
            in count = n_pumps;
            in each_capacity = pump_capacity_each;
            in rel_tol = 0.01;
        }"""


def apply_a2(root: Path) -> None:
    physics = root / "designs" / "catf_mfe" / "physics.sysml"
    replace(physics, A2_OLD, A2_NEW)
    replace(
        physics,
        "    private import FusionPhysics::AlphaNeutronSplit;",
        "    private import CATFGateForms::PositiveQuantity;\n"
        "    private import CATFGateForms::FractionWithinBand;\n"
        "    private import FusionPhysics::AlphaNeutronSplit;",
    )


def apply_a3(root: Path) -> None:
    replace(root / "designs" / "catf_mfe" / "physics.sysml", A3_OLD, A3_NEW)


# ------------------------------------------------------- P4: derivation legs (O6)
def apply_derive_intra(root: Path) -> None:
    """Leg (a): outer_radius derived from inner_radius + thickness, inside one part."""
    replace(
        root / "designs" / "catf_mfe" / "radial_build.sysml",
        "            attribute outer_radius : Real = 4.1 [m];",
        "            attribute outer_radius : Real = inner_radius + thickness;",
    )


def apply_derive_cross(root: Path) -> None:
    """Leg (b): the next layer's inner_radius derived from the previous outer_radius."""
    replace(
        root / "designs" / "catf_mfe" / "radial_build.sysml",
        "            attribute inner_radius : Real = 4.1 [m];",
        "            attribute inner_radius : Real = plasma_region.outer_radius;",
    )


def apply_derive_cross_qualified(root: Path) -> None:
    """Leg (b), fallback spelling: qualified-name reference rather than dot-chain."""
    replace(
        root / "designs" / "catf_mfe" / "radial_build.sysml",
        "            attribute inner_radius : Real = 4.1 [m];",
        "            attribute inner_radius : Real = catf_radial_build::plasma_region::outer_radius;",
    )


def apply_derive_both_unitless(root: Path) -> None:
    """Both legs, with the `[m]` literals stripped from the three attributes involved.

    Tests the hypothesis that the collision is a unit-text disagreement between the
    unit-carrying entry point and the unit-free computed-expression consumer.
    """
    path = root / "designs" / "catf_mfe" / "radial_build.sysml"
    replace(
        path,
        "            attribute inner_radius : Real = 3.0 [m];",
        "            attribute inner_radius : Real = 3.0;  // m",
    )
    replace(
        path,
        "            attribute thickness : Real = 1.1 [m];  // From line 74",
        "            attribute thickness : Real = 1.1;  // m - From line 74",
    )
    replace(
        path,
        "            attribute outer_radius : Real = 4.1 [m];",
        "            attribute outer_radius : Real = inner_radius + thickness;  // m",
    )
    replace(
        path,
        "            attribute inner_radius : Real = 4.1 [m];",
        "            attribute inner_radius : Real = plasma_region.outer_radius;  // m",
    )


def apply_a9(root: Path) -> None:
    vacuum = root / "designs" / "catf_mfe" / "vacuum.sysml"
    replace(vacuum, A9_OLD, A9_NEW)
    replace(
        vacuum,
        "    private import FusionAnalysesThermalLoads::VacuumPumpPower;",
        "    private import CATFGateForms::ProductWithinBand;\n"
        "    private import FusionAnalysesThermalLoads::VacuumPumpPower;",
    )
