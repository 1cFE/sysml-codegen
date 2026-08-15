"""Auto-generated implementation for UnitCost.

AUTO_IMPLEMENTED = True

SysML Source: root-0/model.sysml:7

SysML Expressions:
    total_cost = unit_cost * 2.0
"""

AUTO_IMPLEMENTED = True

from spike_pkg.modules.s6qualsiblingscope.unitcost import UnitCostInput


def run_unitcost(inputs: UnitCostInput) -> float:
    """Execute UnitCost calculation.

SysML Source: root-0/model.sysml:7

SysML Expressions:
    total_cost = unit_cost * 2.0

Args:
    inputs: Input parameters validated against UnitCostInput schema

Returns:
    float: total_cost

Example:
    >>> inputs = UnitCostInput(...)
    >>> result = run_unitcost(inputs)
    """
    return (inputs.unit_cost * 2.0)
