"""Auto-generated implementation for RequiredFlow.

AUTO_IMPLEMENTED = True

SysML Source: root-0/station.sysml:9

SysML Expressions:
    required_flow = inflow - rise_rate * area
"""

AUTO_IMPLEMENTED = True

from station_study.modules.pumpstation.requiredflow import RequiredFlowInput


def run_requiredflow(inputs: RequiredFlowInput) -> float:
    """Execute RequiredFlow calculation.

SysML Source: root-0/station.sysml:9

SysML Expressions:
    required_flow = inflow - rise_rate * area

Args:
    inputs: Input parameters validated against RequiredFlowInput schema

Returns:
    float: required_flow

Example:
    >>> inputs = RequiredFlowInput(...)
    >>> result = run_requiredflow(inputs)
    """
    return (inputs.inflow - (inputs.rise_rate * inputs.area))
