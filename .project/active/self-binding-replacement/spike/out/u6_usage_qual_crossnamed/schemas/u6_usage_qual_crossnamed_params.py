from pydantic import BaseModel, Field


class U6UsageQualCrossnamedParams(BaseModel):
    """Parameters from u6_usage_qual_crossnamed.

    Generated from SysML calculation definitions.
    """
    U6UsageQualCrossnamed__plant__comp_b__length: float = Field(default=7.0, description="Entry point: length")

    model_config = {"frozen": True, "extra": "forbid"}
