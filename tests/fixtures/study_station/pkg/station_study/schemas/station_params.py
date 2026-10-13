from pydantic import BaseModel, Field


class StationParams(BaseModel):
    """Parameters from station.

    Generated from SysML calculation definitions.
    """
    PumpStation__station__allowed_rise_rate: float = Field(default=0.005, description="Entry point: allowed_rise_rate")
    PumpStation__station__basin_area: float = Field(default=12.0, description="Entry point: basin_area")
    PumpStation__station__design_inflow: float = Field(default=0.3, description="Entry point: design_inflow")
    PumpStation__station__energy_price: float = Field(default=0.1, description="Entry point: energy_price")
    PumpStation__station__installed_capacity: float = Field(default=0.25, description="Entry point: installed_capacity")
    PumpStation__station__pump_head: float = Field(default=8.0, description="Entry point: pump_head")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}
