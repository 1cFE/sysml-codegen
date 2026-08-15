from pydantic import BaseModel, Field


class U3BUsageQualSingleOccParams(BaseModel):
    """Parameters from u3_b_usage_qual_single_occ.

    Generated from SysML calculation definitions.
    """
    U3BUsageQualSingleOcc__plant__component_0__length: float = Field(default=3.0, alias="U3BUsageQualSingleOcc__plant__component[0]__length", description="Entry point: length")

    model_config = {"frozen": True, "extra": "forbid"}
