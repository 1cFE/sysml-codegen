"""Constraint module for PumpStation__station__pump_fit__aa8dd6c31b6b238a (Item 7 / D2/D3/D9).

Effective predicate: PumpStation::station::pump_fit in owner instance PumpStation__station.
Three-valued (Kleene) semantics. A verdict against the assertion does not itself raise (INV-3).
"""

from pydantic import BaseModel
from simkit.config.schema import MultiOutput
from simkit.core.base import ModuleBase, ModuleResult

from station_study.schemas.constraint_types import ConstraintEvaluation
from station_study.modules.constraints.predicates import _finalize_assertion, constraint_pred_definition_pumpstation__capacitycoversdemand


class StationPumpFitConstraintInput(BaseModel):
    """Exact input schema: one field per resolved formal."""
    capacity: float
    demand_flow: float


class StationPumpFitConstraintOutput(MultiOutput):
    evaluation: ConstraintEvaluation


class StationPumpFitConstraintModule(ModuleBase[StationPumpFitConstraintInput, StationPumpFitConstraintOutput]):
    name: str = "pumpstation__station__pump_fit__aa8dd6c31b6b238a"
    version: str = "v0.1"

    CONSTRAINT_ID = "PumpStation__station__pump_fit__aa8dd6c31b6b238a"

    def run(self, capacity: float, demand_flow: float) -> ModuleResult[StationPumpFitConstraintOutput]:
        StationPumpFitConstraintInput(capacity=capacity, demand_flow=demand_flow)  # validate every resolved formal
        body = constraint_pred_definition_pumpstation__capacitycoversdemand(capacity=capacity, demand_flow=demand_flow)
        verdict = _finalize_assertion(
            body,
            is_negated=False,
            expected_value=True,
        )
        return ModuleResult(
            data=StationPumpFitConstraintOutput(
                evaluation=ConstraintEvaluation(
                    constraint_id=self.CONSTRAINT_ID,
                    actual_value=verdict.actual_value,
                    status=verdict.status,
                    margin=verdict.margin,
                    observed={"capacity": float(capacity), "demand_flow": float(demand_flow)},
                )
            )
        )
