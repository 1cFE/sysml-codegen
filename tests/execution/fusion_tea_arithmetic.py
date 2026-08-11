"""Hand transcription of the Fusion Tea equations, independent of any executor.

Every number below is read off the SysML and typed out here; nothing is read
back from a generated package, a snapshot, or a previous run (epic R1). The
transcription is the oracle the real-TEAx lane compares against, so it must be
derivable from the model files alone:

- ``library/analyses/hif_economics.sysml`` — Meier driver cost, reactor cost,
  total capital cost, COE.
- ``library/analyses/fusion_cycle.sysml`` — recirculating power fraction.
- ``library/analyses/ife_lcoe.sysml`` — the Hawker LCOE chain.

The design-point inputs come from the design files:
``designs/hif_ife/hif_plant.sysml`` (availability 0.9, gain 80.0, thermal
efficiency 0.43, frequency 3.5, discount rate 0.08, O&M 65.0, plant cost 2000.0,
net electric 1.0 GW, thermal power 2.054 GW), ``designs/hif_ife/hif_driver.sysml``
(beam energy 5.0 MJ, efficiency 0.35, energy 14286000.0 J, 1 chamber, pulse rate
3.5 Hz, lifetime 6e9 shots), and ``designs/generic_ife/ife_subsystems.sysml``
(blanket multiple 1.15, yield cost 5e6, target cost 10.0, target factory 0.1).
"""

from __future__ import annotations

from typing import Final

# --- design point -------------------------------------------------------
AVAILABILITY: Final = 0.9
GAIN: Final = 80.0
THERMAL_EFFICIENCY: Final = 0.43
FREQUENCY: Final = 3.5
DISCOUNT_RATE: Final = 0.08
OM_COST_CONSTANT: Final = 65.0
PLANT_COST_CONSTANT: Final = 2000.0
NET_ELECTRIC_POWER_GW: Final = 1.0
THERMAL_POWER_GW: Final = 2.054
BEAM_ENERGY_MJ: Final = 5.0
NUM_CHAMBERS: Final = 1.0
REP_RATE: Final = 3.5
DRIVER_EFFICIENCY: Final = 0.35
DRIVER_ENERGY: Final = 14286000.0
DRIVER_LIFETIME_SHOTS: Final = 6.0e9
BLANKET_ENERGY_MULTIPLE: Final = 1.15
YIELD_COST_CONSTANT: Final = 5.0e6
TARGET_COST_CONSTANT: Final = 10.0
TARGET_FACTORY_COST: Final = 0.1
NUM_UNITS: Final = 1.0
CONSTRUCTION_YEARS: Final = 5.0
OPERATIONAL_YEARS: Final = 40.0
VIABILITY_THRESHOLD: Final = 10.0


def driver_cost_billions(
    beam_energy_mj: float = BEAM_ENERGY_MJ,
    num_chambers: float = NUM_CHAMBERS,
    rep_rate: float = REP_RATE,
) -> float:
    """`Meier HIF Driver Cost`.cost_billions (hif_economics.sysml, Meier Eq. 5)."""
    return (
        (0.32 + 0.088 * beam_energy_mj)
        * (1.25 + 0.05 * num_chambers)
        * (1.0 + 0.0088 * (rep_rate - 5.0))
    )


def driver_gamma(driver_efficiency: float = DRIVER_EFFICIENCY) -> float:
    """`Meier HIF Driver Cost`.gamma — cost per joule of bank energy."""
    bank_energy_joules = BEAM_ENERGY_MJ * 1.0e6 / driver_efficiency
    return driver_cost_billions() * 1.0e9 / bank_energy_joules


def reactor_cost_billions(thermal_power_gw: float = THERMAL_POWER_GW) -> float:
    """`Meier Reactor Cost`.reactor_cost_billions."""
    return 0.66 * (thermal_power_gw / 1.67) ** 0.49 * (0.72 * NUM_UNITS + 0.28)


def total_capital_billions() -> float:
    """`Meier Total Capital Cost`.total_capital_billions (1.83 indirect multiplier)."""
    return 1.83 * (
        reactor_cost_billions() + driver_cost_billions() + TARGET_FACTORY_COST
    )


def meier_coe_cents_kwh(availability: float = AVAILABILITY) -> float:
    """`Meier COE`.coe_cents_kwh."""
    return (0.113 * total_capital_billions()) / (
        0.0876 * availability * NET_ELECTRIC_POWER_GW
    )


def recirculating_fraction(
    gain: float = GAIN, thermal_efficiency: float = THERMAL_EFFICIENCY
) -> float:
    """`Recirculating Power Fraction`.f_recirc."""
    return 1.0 / (DRIVER_EFFICIENCY * gain * BLANKET_ENERGY_MULTIPLE * thermal_efficiency)


def lcoe(
    gain: float = GAIN,
    availability: float = AVAILABILITY,
    thermal_efficiency: float = THERMAL_EFFICIENCY,
) -> float:
    """`IFE LCOE`.lcoe, the full Hawker chain (ife_lcoe.sysml Eqs. 2.2-2.16).

    ``driver_cost_constant`` is not an entry point: the model wires it to the
    Meier gamma channel, so it is computed here the same way.
    """
    driver_cost_constant = driver_gamma()
    energy_on_target = DRIVER_EFFICIENCY * DRIVER_ENERGY
    fusion_energy_per_shot = gain * energy_on_target
    net_electric_power = (
        DRIVER_ENERGY
        * FREQUENCY
        * (thermal_efficiency * BLANKET_ENERGY_MULTIPLE * gain * DRIVER_EFFICIENCY - 2.0)
    )
    net_electric_kw = net_electric_power / 1000.0
    shots_per_year = 31557600.0 * FREQUENCY * availability
    driver_lifetime_years = DRIVER_LIFETIME_SHOTS / shots_per_year
    annual_capital_cost = (
        PLANT_COST_CONSTANT * net_electric_kw
        + YIELD_COST_CONSTANT * fusion_energy_per_shot / 1.0e9
        + driver_cost_constant * DRIVER_ENERGY
    ) / CONSTRUCTION_YEARS
    annual_operating_cost = (
        TARGET_COST_CONSTANT * shots_per_year
        + OM_COST_CONSTANT * net_electric_kw
        + driver_cost_constant * DRIVER_ENERGY / driver_lifetime_years
    )
    annual_energy = 8760.0 * net_electric_kw * availability / 1000.0
    discount_factor_con = (1.0 + DISCOUNT_RATE) ** CONSTRUCTION_YEARS
    pvf_construction = (1.0 - 1.0 / discount_factor_con) / DISCOUNT_RATE
    discount_factor_op = (1.0 + DISCOUNT_RATE) ** OPERATIONAL_YEARS
    pvf_operation = (
        (1.0 / discount_factor_con) * (1.0 - 1.0 / discount_factor_op) / DISCOUNT_RATE
    )
    return (
        annual_capital_cost * pvf_construction + annual_operating_cost * pvf_operation
    ) / (annual_energy * pvf_operation)


#: The epic's headline value, and the number the recovery plan names as the
#: target to re-prove. Written out so a change in the transcription above fails
#: against a constant rather than silently redefining the target.
RUN_C_LCOE: Final = 270.1211779380445
