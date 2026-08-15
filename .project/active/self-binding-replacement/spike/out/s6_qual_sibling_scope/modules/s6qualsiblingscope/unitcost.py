"""UnitCostModule Module Wrapper

TEAx module for UnitCost calculation.

Inputs:
    - unit_cost: unit_cost parameter

Outputs:
    - total_cost: total_cost result

SysML Source: root-0/model.sysml:7

SysML Source: root-0/model.sysml:7

GAP: Code generator does NOT implement calc logic - only wrapper structure.
Handwritten implementation required in handwritten/s6qualsiblingscope/unitcost_impl.py
"""

from pydantic import BaseModel, Field, RootModel
from simkit.core.base import ModuleBase, ModuleResult

from spike_pkg.primitives import Float


class UnitCostInput(BaseModel):
    """Input model for UnitCostModule.

    Attributes:
        unit_cost: unit_cost input
    """
    unit_cost: float = Field(..., description="unit_cost input")


class UnitCostModule(ModuleBase[UnitCostInput, Float]):
    """TEAx module for UnitCost calculation.

Inputs:
    - unit_cost: unit_cost parameter

Outputs:
    - total_cost: total_cost result

SysML Source: root-0/model.sysml:7

    SysML Source: root-0/model.sysml:7

    Calculation Specification:
        total_cost = unit_cost * 2.0

    IMPLEMENTATION: See spike_pkg.handwritten.s6qualsiblingscope.unitcost_impl
    for manual implementation.

    NOTE: Single-output module - returns Float directly (no MultiOutput needed).
    """

    name: str = "UnitCostModule"
    version: str = "v0.1"

    def validate_and_fill_default(
        self, unit_cost: float    ) -> UnitCostInput:
        """Validate inputs and fill defaults.

        Args:
            unit_cost: unit_cost input

        Returns:
            Validated input model
        """
        return UnitCostInput(unit_cost=unit_cost)

    def run(
        self, unit_cost: float    ) -> ModuleResult[Float]:
        """Execute calculation.

        Args:
            unit_cost: unit_cost input

        Returns:
            Module result with Float (single-output mode)
        """
        # Validate inputs
        validated_inputs = self.validate_and_fill_default(unit_cost)

        # Import handwritten implementation
        from spike_pkg.handwritten.s6qualsiblingscope.unitcost_impl import (
            run_unitcost,
        )

        # Execute implementation - returns single value
        total_cost = run_unitcost(validated_inputs)

        # Single output - return Float directly (RootModel[float])
        # TEAx assigns entire return value to the one channel declared in YAML
        return ModuleResult(data=Float(total_cost))
