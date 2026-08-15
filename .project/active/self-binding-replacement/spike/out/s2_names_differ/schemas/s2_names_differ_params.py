from pydantic import BaseModel, Field


class S2NamesDifferParams(BaseModel):
    """Parameters from s2_names_differ.

    Generated from SysML calculation definitions.
    """
    S2NamesDiffer__plant__availability: float = Field(default=0.85, description="Entry point: availability")

    model_config = {"frozen": True, "extra": "forbid"}
