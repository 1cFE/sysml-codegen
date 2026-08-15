from pydantic import BaseModel, Field


class S4AQualOneOccParams(BaseModel):
    """Parameters from s4_a_qual_one_occ.

    Generated from SysML calculation definitions.
    """
    S4AQualOneOcc__plant__availability: float = Field(default=0.85, description="Entry point: availability")

    model_config = {"frozen": True, "extra": "forbid"}
