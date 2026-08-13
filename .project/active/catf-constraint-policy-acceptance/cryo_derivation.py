#!/usr/bin/env python3
"""The source-derived Carnot computation behind finding 6-D. Runnable, and self-checking.

This is the **basis** for the amended expectation cells (`expected-coverage.md`'s headline and
`gated_manifest`'s `expected_study_outcomes`). Those cells are not transcribed from an observed
run — they are derived here from the model's own source constants and formulas, and the
derivation is then checked against what the executed package produced. Bit-exact agreement is
what licenses using it as the basis.

Every constant below is quoted from `tests/fixtures/catf_mfe_gated/` source with its location.
The two geometry inputs are model-computed outputs of the same package, cited as such.

Run: python .project/active/catf-constraint-policy-acceptance/cryo_derivation.py
"""

from __future__ import annotations

# --- inputs to `calc cryo_load : MagnetCryogenicLoad` (designs/catf_mfe/magnets.sysml:86-94)

#: `in magnet_volume = catf_radial_build.magnet_volume_total` -> `tf_coil.volume`
#: (radial_build.sysml:582). Model-computed geometry output, m^3.
MAGNET_VOLUME = 2334.4698659954747

#: `in magnet_surface_area = catf_radial_build.magnet_surface_area` (radial_build.sysml:602), m^2.
MAGNET_SURFACE_AREA = 15.31526418625125

#: `in first_wall_area = catf_radial_build.first_wall_area` (radial_build.sysml:592), m^2.
FIRST_WALL_AREA = 31.101767270540993

#: `in p_neutron = 2079.41;` — an authored literal (magnets.sysml:90), MW.
P_NEUTRON = 2079.41

#: `in operating_temp = temperature_operating`, and
#: `attribute temperature_operating : Real = 20 [K];` (magnets.sysml:66). **20 K, not 4.5 K** —
#: an earlier hand estimate in this item assumed a 4.5 K system and was wrong by that factor.
OPERATING_TEMP = 20.0

#: `carnot_efficiency` is not bound, so it takes the calc def default
#: `in attribute carnot_efficiency : Real = 0.3;` (library/analyses/thermal_loads.sysml:52).
CARNOT_EFFICIENCY = 0.3

#: What the sealed package actually produced through real TEAx at the authored inputs.
EXECUTED_COOLING_POWER = 8396.054399837172

#: Same run, for the ratio that makes the candidate gate-infeasible.
EXECUTED_GROSS_ELECTRIC = 1546.723690193402


def cooling_power() -> tuple[float, dict[str, float]]:
    """`MagnetCryogenicLoad.cooling_power`, transcribed from thermal_loads.sysml:55-66."""
    nuclear_heating = 0.05 * P_NEUTRON * (MAGNET_SURFACE_AREA / FIRST_WALL_AREA)
    ac_losses = 0.0
    heat_leak = MAGNET_VOLUME * 0.05
    thermal_load_cryo = nuclear_heating + ac_losses + heat_leak
    power = (thermal_load_cryo / OPERATING_TEMP) * (300.0 / CARNOT_EFFICIENCY)
    return power, {
        "nuclear_heating": nuclear_heating,
        "ac_losses": ac_losses,
        "heat_leak": heat_leak,
        "thermal_load_cryo": thermal_load_cryo,
        "amplification": 300.0 / (OPERATING_TEMP * CARNOT_EFFICIENCY),
    }


def main() -> int:
    power, terms = cooling_power()
    print(f"nuclear_heating   = {terms['nuclear_heating']:.6f} MW")
    print(f"ac_losses         = {terms['ac_losses']:.6f} MW")
    print(f"heat_leak         = {terms['heat_leak']:.6f} MW   <- magnet_volume * 0.05")
    print(f"thermal_load_cryo = {terms['thermal_load_cryo']:.6f} MW at {OPERATING_TEMP} K")
    print(
        f"amplification     = 300/({OPERATING_TEMP}*{CARNOT_EFFICIENCY}) "
        f"= {terms['amplification']:.1f}x"
    )
    print(f"cooling_power     = {power!r} MW")
    print(f"executed          = {EXECUTED_COOLING_POWER!r} MW")

    assert power == EXECUTED_COOLING_POWER, (
        "the source-derived computation does not reproduce the executed value; "
        "the derivation, not the run, is what the amended expectations rest on"
    )
    print("\nREPRODUCES THE EXECUTED VALUE EXACTLY.")
    print(f"heat_leak is {terms['heat_leak'] / terms['thermal_load_cryo']:.1%} of the cryo load")
    print(f"cryo / gross = {power / EXECUTED_GROSS_ELECTRIC:.2f}x  -> net power is negative")
    print("\n=> the authored CATF design point is GATE-INFEASIBLE under the model as authored.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
