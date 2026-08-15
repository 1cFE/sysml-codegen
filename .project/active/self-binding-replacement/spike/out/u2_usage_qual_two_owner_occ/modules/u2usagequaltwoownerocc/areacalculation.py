"""AreaCalculationModule Module Wrapper

TEAx module for AreaCalculation calculation.

Inputs:
    - length: length parameter

Outputs:
    - area: area result

SysML Source: root-0/model.sysml:7

SysML Source: root-0/model.sysml:7

GAP: Code generator does NOT implement calc logic - only wrapper structure.
Handwritten implementation required in handwritten/u2usagequaltwoownerocc/areacalculation_impl.py
"""

from pydantic import BaseModel, Field, RootModel
from simkit.core.base import ModuleBase, ModuleResult

from spike_pkg.primitives import Float


class AreaCalculationInput(BaseModel):
    """Input model for AreaCalculationModule.

    Attributes:
        length: length input
    """
    length: float = Field(..., description="length input")


class AreaCalculationModule(ModuleBase[AreaCalculationInput, Float]):
    """TEAx module for AreaCalculation calculation.

Inputs:
    - length: length parameter

Outputs:
    - area: area result

SysML Source: root-0/model.sysml:7

    SysML Source: root-0/model.sysml:7

    Calculation Specification:
        area = length * 2.0

    IMPLEMENTATION: See spike_pkg.handwritten.u2usagequaltwoownerocc.areacalculation_impl
    for manual implementation.

    NOTE: Single-output module - returns Float directly (no MultiOutput needed).
    """

    name: str = "AreaCalculationModule"
    version: str = "v0.1"

    def validate_and_fill_default(
        self, length: float    ) -> AreaCalculationInput:
        """Validate inputs and fill defaults.

        Args:
            length: length input

        Returns:
            Validated input model
        """
        return AreaCalculationInput(length=length)

    def run(
        self, length: float    ) -> ModuleResult[Float]:
        """Execute calculation.

        Args:
            length: length input

        Returns:
            Module result with Float (single-output mode)
        """
        # Validate inputs
        validated_inputs = self.validate_and_fill_default(length)

        # Import handwritten implementation
        from spike_pkg.handwritten.u2usagequaltwoownerocc.areacalculation_impl import (
            run_areacalculation,
        )

        # Execute implementation - returns single value
        area = run_areacalculation(validated_inputs)

        # Single output - return Float directly (RootModel[float])
        # TEAx assigns entire return value to the one channel declared in YAML
        return ModuleResult(data=Float(area))
