"""Auto-generated implementation for AreaCalculation.

AUTO_IMPLEMENTED = True

SysML Source: root-0/model.sysml:9

SysML Expressions:
    area = length_in * 2.0
"""

AUTO_IMPLEMENTED = True

from spike_pkg.modules.u6usagequalcrossnamed.areacalculation import AreaCalculationInput


def run_areacalculation(inputs: AreaCalculationInput) -> float:
    """Execute AreaCalculation calculation.

SysML Source: root-0/model.sysml:9

SysML Expressions:
    area = length_in * 2.0

Args:
    inputs: Input parameters validated against AreaCalculationInput schema

Returns:
    float: area

Example:
    >>> inputs = AreaCalculationInput(...)
    >>> result = run_areacalculation(inputs)
    """
    return (inputs.length_in * 2.0)
