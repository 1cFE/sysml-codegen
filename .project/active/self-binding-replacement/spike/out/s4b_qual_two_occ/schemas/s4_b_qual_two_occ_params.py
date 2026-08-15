from pydantic import BaseModel, Field


class S4BQualTwoOccParams(BaseModel):
    """Parameters from s4_b_qual_two_occ.

    Generated from SysML calculation definitions.
    """
    S4BQualTwoOcc__plant_a__availability: float = Field(default=0.11, description="Entry point: availability")
    S4BQualTwoOcc__plant_b__availability: float = Field(default=0.99, description="Entry point: availability")

    model_config = {"frozen": True, "extra": "forbid"}
