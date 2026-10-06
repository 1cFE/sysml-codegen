"""Core data models shared across layers.

These types are used by multiple layers (analysis, resolution, generation)
and are placed here to avoid layer violations.
"""

from pydantic import BaseModel, ConfigDict, model_validator


class AutoImplStep(BaseModel):
    """One assignment rendered into an auto-implemented function body.

    A compiled member becomes a step when something else consumes it, so the
    rendered function never forward-references or recomputes a value.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    expression: str


class AutoImplOutput(BaseModel):
    """One value an auto-implemented function returns, in schema position order.

    ``expression`` is the member's own name when it was already assigned as an
    ``AutoImplStep``, and its compiled expression otherwise.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    expression: str


class AutoImplContext(BaseModel):
    """Everything the auto-implementation template renders, and nothing else.

    This is the whole protocol between the elaborator, which compiles a fully
    compilable calculation, and ``generation/stencils.py``, which renders it.
    It used to be an untyped dictionary merged wholesale into the template
    context, so neither end declared what it carried and the snapshot decoder
    could only check that it was an object.

    ``output_count`` and ``single_output_expression`` are redundant with
    ``output_expressions`` and are kept because they are sealed into every v6
    snapshot written to date. The validator makes the redundancy a checked
    invariant rather than a place two readers can disagree.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    execution_steps: list[AutoImplStep]
    output_expressions: list[AutoImplOutput]
    output_count: int
    single_output_expression: str | None

    @model_validator(mode="after")
    def _derived_fields_agree(self) -> "AutoImplContext":
        if self.output_count != len(self.output_expressions):
            raise ValueError(
                f"output_count {self.output_count} does not match "
                f"{len(self.output_expressions)} output expressions"
            )
        expected = (
            self.output_expressions[0].expression if len(self.output_expressions) == 1 else None
        )
        if self.single_output_expression != expected:
            raise ValueError(
                "single_output_expression must be the one output's expression, "
                "and None when there is not exactly one output"
            )
        return self


__all__ = [
    "AutoImplContext",
    "AutoImplOutput",
    "AutoImplStep",
]
