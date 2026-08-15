from pydantic import BaseModel, Field


class U2UsageQualTwoOwnerOccParams(BaseModel):
    """Parameters from u2_usage_qual_two_owner_occ.

    Generated from SysML calculation definitions.
    """
    U2UsageQualTwoOwnerOcc__plant_a__component__length: float = Field(default=11.0, description="Entry point: length")
    U2UsageQualTwoOwnerOcc__plant_b__component__length: float = Field(default=99.0, description="Entry point: length")

    model_config = {"frozen": True, "extra": "forbid"}
