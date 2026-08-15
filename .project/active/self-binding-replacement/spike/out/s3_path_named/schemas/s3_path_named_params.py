from pydantic import BaseModel, Field


class S3PathNamedParams(BaseModel):
    """Parameters from s3_path_named.

    Generated from SysML calculation definitions.
    """
    S3PathNamed__plant__driver__cost: float = Field(default=12.5, description="Entry point: cost")

    model_config = {"frozen": True, "extra": "forbid"}
