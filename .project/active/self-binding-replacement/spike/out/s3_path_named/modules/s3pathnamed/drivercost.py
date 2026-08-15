"""DriverCostModule Module Wrapper

TEAx module for DriverCost calculation.

Inputs:
    - driver_cost: driver_cost parameter

Outputs:
    - total_cost: total_cost result

SysML Source: root-0/model.sysml:5

SysML Source: root-0/model.sysml:5

GAP: Code generator does NOT implement calc logic - only wrapper structure.
Handwritten implementation required in handwritten/s3pathnamed/drivercost_impl.py
"""

from pydantic import BaseModel, Field, RootModel
from simkit.core.base import ModuleBase, ModuleResult

from spike_pkg.primitives import Float


class DriverCostInput(BaseModel):
    """Input model for DriverCostModule.

    Attributes:
        driver_cost: driver_cost input
    """
    driver_cost: float = Field(..., description="driver_cost input")


class DriverCostModule(ModuleBase[DriverCostInput, Float]):
    """TEAx module for DriverCost calculation.

Inputs:
    - driver_cost: driver_cost parameter

Outputs:
    - total_cost: total_cost result

SysML Source: root-0/model.sysml:5

    SysML Source: root-0/model.sysml:5

    Calculation Specification:
        total_cost = driver_cost * 3.0

    IMPLEMENTATION: See spike_pkg.handwritten.s3pathnamed.drivercost_impl
    for manual implementation.

    NOTE: Single-output module - returns Float directly (no MultiOutput needed).
    """

    name: str = "DriverCostModule"
    version: str = "v0.1"

    def validate_and_fill_default(
        self, driver_cost: float    ) -> DriverCostInput:
        """Validate inputs and fill defaults.

        Args:
            driver_cost: driver_cost input

        Returns:
            Validated input model
        """
        return DriverCostInput(driver_cost=driver_cost)

    def run(
        self, driver_cost: float    ) -> ModuleResult[Float]:
        """Execute calculation.

        Args:
            driver_cost: driver_cost input

        Returns:
            Module result with Float (single-output mode)
        """
        # Validate inputs
        validated_inputs = self.validate_and_fill_default(driver_cost)

        # Import handwritten implementation
        from spike_pkg.handwritten.s3pathnamed.drivercost_impl import (
            run_drivercost,
        )

        # Execute implementation - returns single value
        total_cost = run_drivercost(validated_inputs)

        # Single output - return Float directly (RootModel[float])
        # TEAx assigns entire return value to the one channel declared in YAML
        return ModuleResult(data=Float(total_cost))
