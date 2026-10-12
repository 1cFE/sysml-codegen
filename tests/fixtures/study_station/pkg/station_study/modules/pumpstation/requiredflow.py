"""RequiredFlowModule Module Wrapper

TEAx module for RequiredFlow calculation.

Inputs:
    - rise_rate: rise_rate parameter
    - inflow: inflow parameter
    - area: area parameter

Outputs:
    - required_flow: required_flow result

SysML Source: root-0/station.sysml:9

SysML Source: root-0/station.sysml:9

GAP: Code generator does NOT implement calc logic - only wrapper structure.
Handwritten implementation required in handwritten/pumpstation/requiredflow_impl.py
"""

from pydantic import BaseModel, Field, RootModel
from simkit.core.base import ModuleBase, ModuleResult

from station_study.primitives import Float


class RequiredFlowInput(BaseModel):
    """Input model for RequiredFlowModule.

    Attributes:
        rise_rate: rise_rate input
        inflow: inflow input
        area: area input
    """
    rise_rate: float = Field(..., description="rise_rate input")
    inflow: float = Field(..., description="inflow input")
    area: float = Field(..., description="area input")


class RequiredFlowModule(ModuleBase[RequiredFlowInput, Float]):
    """TEAx module for RequiredFlow calculation.

Inputs:
    - rise_rate: rise_rate parameter
    - inflow: inflow parameter
    - area: area parameter

Outputs:
    - required_flow: required_flow result

SysML Source: root-0/station.sysml:9

    SysML Source: root-0/station.sysml:9

    Calculation Specification:
        required_flow = inflow - rise_rate * area

    IMPLEMENTATION: See station_study.handwritten.pumpstation.requiredflow_impl
    for manual implementation.

    NOTE: Single-output module - returns Float directly (no MultiOutput needed).
    """

    name: str = "RequiredFlowModule"
    version: str = "v0.1"

    def validate_and_fill_default(
        self, rise_rate: float, inflow: float, area: float    ) -> RequiredFlowInput:
        """Validate inputs and fill defaults.

        Args:
            rise_rate: rise_rate input
            inflow: inflow input
            area: area input

        Returns:
            Validated input model
        """
        return RequiredFlowInput(rise_rate=rise_rate, inflow=inflow, area=area)

    def run(
        self, rise_rate: float, inflow: float, area: float    ) -> ModuleResult[Float]:
        """Execute calculation.

        Args:
            rise_rate: rise_rate input
            inflow: inflow input
            area: area input

        Returns:
            Module result with Float (single-output mode)
        """
        # Validate inputs
        validated_inputs = self.validate_and_fill_default(rise_rate, inflow, area)

        # Import handwritten implementation
        from station_study.handwritten.pumpstation.requiredflow_impl import (
            run_requiredflow,
        )

        # Execute implementation - returns single value
        required_flow = run_requiredflow(validated_inputs)

        # Single output - return Float directly (RootModel[float])
        # TEAx assigns entire return value to the one channel declared in YAML
        return ModuleResult(data=Float(required_flow))
