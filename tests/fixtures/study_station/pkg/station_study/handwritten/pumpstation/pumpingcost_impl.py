"""Auto-generated implementation for PumpingCost.

AUTO_IMPLEMENTED = True

SysML Source: root-0/station.sysml:16

SysML Expressions:
    annual_cost = flow_rate * head * price * 1000.0
"""

AUTO_IMPLEMENTED = True

from station_study.modules.pumpstation.pumpingcost import PumpingCostInput


def run_pumpingcost(inputs: PumpingCostInput) -> float:
    """Execute PumpingCost calculation.

SysML Source: root-0/station.sysml:16

SysML Expressions:
    annual_cost = flow_rate * head * price * 1000.0

Args:
    inputs: Input parameters validated against PumpingCostInput schema

Returns:
    float: annual_cost

Example:
    >>> inputs = PumpingCostInput(...)
    >>> result = run_pumpingcost(inputs)
    """
    return (((inputs.flow_rate * inputs.head) * inputs.price) * 1000.0)
