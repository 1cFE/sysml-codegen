"""AreaCalculationModule Module Wrapper

TEAx module for AreaCalculation calculation.

Inputs:
    - length_in: length_in parameter

Outputs:
    - area: area result

SysML Source: root-0/model.sysml:9

SysML Source: root-0/model.sysml:9

GAP: Code generator does NOT implement calc logic - only wrapper structure.
Handwritten implementation required in handwritten/u6usagequalcrossnamed/areacalculation_impl.py
"""

from pydantic import BaseModel, Field, RootModel
from simkit.core.base import ModuleBase, ModuleResult

from spike_pkg.primitives import Float


class AreaCalculationInput(BaseModel):
    """Input model for AreaCalculationModule.

    Attributes:
        length_in: length_in input
    """
    length_in: float = Field(..., description="length_in input")


class AreaCalculationModule(ModuleBase[AreaCalculationInput, Float]):
    """TEAx module for AreaCalculation calculation.

Inputs:
    - length_in: length_in parameter

Outputs:
    - area: area result

SysML Source: root-0/model.sysml:9

    SysML Source: root-0/model.sysml:9

    Calculation Specification:
        area = length_in * 2.0

    IMPLEMENTATION: See spike_pkg.handwritten.u6usagequalcrossnamed.areacalculation_impl
    for manual implementation.

    NOTE: Single-output module - returns Float directly (no MultiOutput needed).
    """

    name: str = "AreaCalculationModule"
    version: str = "v0.1"

    def validate_and_fill_default(
        self, length_in: float    ) -> AreaCalculationInput:
        """Validate inputs and fill defaults.

        Args:
            length_in: length_in input

        Returns:
            Validated input model
        """
        return AreaCalculationInput(length_in=length_in)

    def run(
        self, length_in: float    ) -> ModuleResult[Float]:
        """Execute calculation.

        Args:
            length_in: length_in input

        Returns:
            Module result with Float (single-output mode)
        """
        # Validate inputs
        validated_inputs = self.validate_and_fill_default(length_in)

        # Import handwritten implementation
        from spike_pkg.handwritten.u6usagequalcrossnamed.areacalculation_impl import (
            run_areacalculation,
        )

        # Execute implementation - returns single value
        area = run_areacalculation(validated_inputs)

        # Single output - return Float directly (RootModel[float])
        # TEAx assigns entire return value to the one channel declared in YAML
        return ModuleResult(data=Float(area))
