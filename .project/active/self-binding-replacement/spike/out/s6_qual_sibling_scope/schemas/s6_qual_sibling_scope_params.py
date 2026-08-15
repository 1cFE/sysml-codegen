from pydantic import BaseModel, Field


class S6QualSiblingScopeParams(BaseModel):
    """Parameters from s6_qual_sibling_scope.

    Generated from SysML calculation definitions.
    """
    S6QualSiblingScope__plant__bop__the_unit__cost: float = Field(default=7.0, description="Entry point: cost")

    model_config = {"frozen": True, "extra": "forbid"}
