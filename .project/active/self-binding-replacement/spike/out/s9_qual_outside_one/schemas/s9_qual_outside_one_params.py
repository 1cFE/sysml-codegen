from pydantic import BaseModel, Field


class S9QualOutsideOneParams(BaseModel):
    """Parameters from s9_qual_outside_one.

    Generated from SysML calculation definitions.
    """
    S9QualOutsideOne__fleet__plant_a__availability: float = Field(default=0.11, description="Entry point: availability")

    model_config = {"frozen": True, "extra": "forbid"}
