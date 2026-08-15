"""RevenueModule Module Wrapper

TEAx module for Revenue calculation.

Inputs:
    - availability: availability parameter

Outputs:
    - revenue: revenue result

SysML Source: root-0/model.sysml:6

SysML Source: root-0/model.sysml:6

GAP: Code generator does NOT implement calc logic - only wrapper structure.
Handwritten implementation required in handwritten/s4aqualoneocc/revenue_impl.py
"""

from pydantic import BaseModel, Field, RootModel
from simkit.core.base import ModuleBase, ModuleResult

from spike_pkg.primitives import Float


class RevenueInput(BaseModel):
    """Input model for RevenueModule.

    Attributes:
        availability: availability input
    """
    availability: float = Field(..., description="availability input")


class RevenueModule(ModuleBase[RevenueInput, Float]):
    """TEAx module for Revenue calculation.

Inputs:
    - availability: availability parameter

Outputs:
    - revenue: revenue result

SysML Source: root-0/model.sysml:6

    SysML Source: root-0/model.sysml:6

    Calculation Specification:
        revenue = availability * 100.0

    IMPLEMENTATION: See spike_pkg.handwritten.s4aqualoneocc.revenue_impl
    for manual implementation.

    NOTE: Single-output module - returns Float directly (no MultiOutput needed).
    """

    name: str = "RevenueModule"
    version: str = "v0.1"

    def validate_and_fill_default(
        self, availability: float    ) -> RevenueInput:
        """Validate inputs and fill defaults.

        Args:
            availability: availability input

        Returns:
            Validated input model
        """
        return RevenueInput(availability=availability)

    def run(
        self, availability: float    ) -> ModuleResult[Float]:
        """Execute calculation.

        Args:
            availability: availability input

        Returns:
            Module result with Float (single-output mode)
        """
        # Validate inputs
        validated_inputs = self.validate_and_fill_default(availability)

        # Import handwritten implementation
        from spike_pkg.handwritten.s4aqualoneocc.revenue_impl import (
            run_revenue,
        )

        # Execute implementation - returns single value
        revenue = run_revenue(validated_inputs)

        # Single output - return Float directly (RootModel[float])
        # TEAx assigns entire return value to the one channel declared in YAML
        return ModuleResult(data=Float(revenue))
