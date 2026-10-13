"""PumpingCostModule Module Wrapper

TEAx module for PumpingCost calculation.

Inputs:
    - head: head parameter
    - price: price parameter
    - flow_rate: flow_rate parameter

Outputs:
    - annual_cost: annual_cost result

SysML Source: root-0/station.sysml:16

SysML Source: root-0/station.sysml:16

GAP: Code generator does NOT implement calc logic - only wrapper structure.
Handwritten implementation required in handwritten/pumpstation/pumpingcost_impl.py
"""

from pydantic import BaseModel, Field, RootModel
from simkit.core.base import ModuleBase, ModuleResult

from station_study.primitives import Float


class PumpingCostInput(BaseModel):
    """Input model for PumpingCostModule.

    Attributes:
        head: head input
        price: price input
        flow_rate: flow_rate input
    """
    head: float = Field(..., description="head input")
    price: float = Field(..., description="price input")
    flow_rate: float = Field(..., description="flow_rate input")


class PumpingCostModule(ModuleBase[PumpingCostInput, Float]):
    """TEAx module for PumpingCost calculation.

Inputs:
    - head: head parameter
    - price: price parameter
    - flow_rate: flow_rate parameter

Outputs:
    - annual_cost: annual_cost result

SysML Source: root-0/station.sysml:16

    SysML Source: root-0/station.sysml:16

    Calculation Specification:
        annual_cost = flow_rate * head * price * 1000.0

    IMPLEMENTATION: See station_study.handwritten.pumpstation.pumpingcost_impl
    for manual implementation.

    NOTE: Single-output module - returns Float directly (no MultiOutput needed).
    """

    name: str = "PumpingCostModule"
    version: str = "v0.1"

    def validate_and_fill_default(
        self, head: float, price: float, flow_rate: float    ) -> PumpingCostInput:
        """Validate inputs and fill defaults.

        Args:
            head: head input
            price: price input
            flow_rate: flow_rate input

        Returns:
            Validated input model
        """
        return PumpingCostInput(head=head, price=price, flow_rate=flow_rate)

    def run(
        self, head: float, price: float, flow_rate: float    ) -> ModuleResult[Float]:
        """Execute calculation.

        Args:
            head: head input
            price: price input
            flow_rate: flow_rate input

        Returns:
            Module result with Float (single-output mode)
        """
        # Validate inputs
        validated_inputs = self.validate_and_fill_default(head, price, flow_rate)

        # Import handwritten implementation
        from station_study.handwritten.pumpstation.pumpingcost_impl import (
            run_pumpingcost,
        )

        # Execute implementation - returns single value
        annual_cost = run_pumpingcost(validated_inputs)

        # Single output - return Float directly (RootModel[float])
        # TEAx assigns entire return value to the one channel declared in YAML
        return ModuleResult(data=Float(annual_cost))
