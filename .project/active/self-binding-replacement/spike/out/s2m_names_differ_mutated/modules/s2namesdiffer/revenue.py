"""RevenueModule Module Wrapper

TEAx module for Revenue calculation.

Inputs:
    - availability_in: availability_in parameter

Outputs:
    - revenue: revenue result

SysML Source: root-0/model.sysml:5

SysML Source: root-0/model.sysml:5

GAP: Code generator does NOT implement calc logic - only wrapper structure.
Handwritten implementation required in handwritten/s2namesdiffer/revenue_impl.py
"""

from pydantic import BaseModel, Field, RootModel
from simkit.core.base import ModuleBase, ModuleResult

from spike_pkg.primitives import Float


class RevenueInput(BaseModel):
    """Input model for RevenueModule.

    Attributes:
        availability_in: availability_in input
    """
    availability_in: float = Field(..., description="availability_in input")


class RevenueModule(ModuleBase[RevenueInput, Float]):
    """TEAx module for Revenue calculation.

Inputs:
    - availability_in: availability_in parameter

Outputs:
    - revenue: revenue result

SysML Source: root-0/model.sysml:5

    SysML Source: root-0/model.sysml:5

    Calculation Specification:
        revenue = availability_in * 100.0

    IMPLEMENTATION: See spike_pkg.handwritten.s2namesdiffer.revenue_impl
    for manual implementation.

    NOTE: Single-output module - returns Float directly (no MultiOutput needed).
    """

    name: str = "RevenueModule"
    version: str = "v0.1"

    def validate_and_fill_default(
        self, availability_in: float    ) -> RevenueInput:
        """Validate inputs and fill defaults.

        Args:
            availability_in: availability_in input

        Returns:
            Validated input model
        """
        return RevenueInput(availability_in=availability_in)

    def run(
        self, availability_in: float    ) -> ModuleResult[Float]:
        """Execute calculation.

        Args:
            availability_in: availability_in input

        Returns:
            Module result with Float (single-output mode)
        """
        # Validate inputs
        validated_inputs = self.validate_and_fill_default(availability_in)

        # Import handwritten implementation
        from spike_pkg.handwritten.s2namesdiffer.revenue_impl import (
            run_revenue,
        )

        # Execute implementation - returns single value
        revenue = run_revenue(validated_inputs)

        # Single output - return Float directly (RootModel[float])
        # TEAx assigns entire return value to the one channel declared in YAML
        return ModuleResult(data=Float(revenue))
