"""The station's independent oracle: its two calculations, recomputed from the model text.

Written for study-layer-to-codegen, as the neutral fixture's oracle. ``verify`` imports it
through the manifest's ``oracle`` block and calls :func:`evaluate` with each sampled case's
swept inputs. The design values below are the ones ``models/station.sysml`` declares, and the
arithmetic is the model's, written out again here rather than read from the generated
package, so that agreement between the two means something.

:func:`operand_bindings` publishes where each operand of the one constraint takes its value
from, because a generic verifier does not guess bindings by name.
"""

from __future__ import annotations

from collections.abc import Mapping

STATION = "PumpStation__station__"
REQUIRED_FLOW = STATION + "demand__required_flow"
ANNUAL_COST = STATION + "pumping__annual_cost"
PUMP_FIT = STATION + "pump_fit__aa8dd6c31b6b238a"

#: The station's design attributes, as ``models/station.sysml`` declares them.
DESIGN = {
    STATION + "design_inflow": 0.30,
    STATION + "basin_area": 12.0,
    STATION + "allowed_rise_rate": 0.005,
    STATION + "installed_capacity": 0.25,
    STATION + "pump_head": 8.0,
    STATION + "energy_price": 0.10,
}


def evaluate(point: Mapping[str, float]) -> dict[str, float]:
    """The two calculated channels at ``point``, which overrides any of :data:`DESIGN`."""
    unmodelled = sorted(set(point) - set(DESIGN))
    if unmodelled:
        raise ValueError(f"the station oracle models no input named {unmodelled}")
    values = {**DESIGN, **point}
    required_flow = (
        values[STATION + "design_inflow"]
        - values[STATION + "allowed_rise_rate"] * values[STATION + "basin_area"]
    )
    annual_cost = (
        required_flow * values[STATION + "pump_head"] * values[STATION + "energy_price"] * 1000.0
    )
    return {REQUIRED_FLOW: required_flow, ANNUAL_COST: annual_cost}


def operand_bindings() -> dict[str, dict[str, dict[str, str]]]:
    """Each pump-fit operand's source: the installed capacity input, the required-flow channel."""
    return {
        PUMP_FIT: {
            "capacity": {"kind": "input", "key": STATION + "installed_capacity"},
            "demand_flow": {"kind": "channel", "key": REQUIRED_FLOW},
        }
    }
