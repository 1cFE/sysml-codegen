from pydantic import BaseModel, Field


class U1UsageQualSelfParams(BaseModel):
    """Parameters from u1_usage_qual_self.

    Generated from SysML calculation definitions.
    """
    U1UsageQualSelf__component__length: float = Field(default=3.0, description="Entry point: length")
    U1UsageQualSelf__component__width: float = Field(default=4.0, description="Entry point: width")

    model_config = {"frozen": True, "extra": "forbid"}
