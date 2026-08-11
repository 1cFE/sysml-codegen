"""Shared fail-loud error construction for generation seams (Item 6)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sysml_codegen.core.errors import CodeGenerationError
    from sysml_codegen.generation.constraint_name_safety import ConstraintNameViolation
    from sysml_codegen.resolution.models import ComputationGraph, PipelineModule


def constraint_name_safety_error(
    violation: ConstraintNameViolation,
) -> CodeGenerationError:
    """Adapt one pure name-safety record to the package's public error."""
    from sysml_codegen.generation import CodeGenerationError
    from sysml_codegen.generation.constraint_name_safety import format_name_safety_violation

    return CodeGenerationError(
        format_name_safety_violation(violation), name_safety_violation=violation
    )


def validate_constraint_graph_or_raise(graph: ComputationGraph) -> None:
    """Raise the public package error for the selected graph violation."""
    from sysml_codegen.generation.constraint_name_safety import (
        select_graph_name_safety_violation,
    )

    violation = select_graph_name_safety_violation(graph)
    if violation is not None:
        raise constraint_name_safety_error(violation)


def residual_class_name_collision_error(
    residual: dict[str, list[str]],
) -> CodeGenerationError:
    """The refusal for registry class names that survive parent-segment aliasing.

    One message for the two places that can detect it — the generation boundary,
    which runs before the output tree is touched, and ``generate_registry``
    itself for callers that reach it directly.
    """
    from sysml_codegen.generation import CodeGenerationError

    return CodeGenerationError(
        "Module class name collision survives aliasing (grandparent collision): "
        + "; ".join(f"{name!r} <- {sorted(mts)}" for name, mts in sorted(residual.items()))
        + ". The parent-segment alias cannot disambiguate these; rename one scope."
    )


def unrenderable_module_kind_error(module: PipelineModule, seam_name: str) -> CodeGenerationError:
    """Build the uniform refusal for a module_kind with no rendering at a seam."""
    # Lazy import mirrors the proven pattern at cli/__init__.py:195 (avoids any import cycle).
    from sysml_codegen.generation import CodeGenerationError

    return CodeGenerationError(
        f"Module {module.name!r} (module_kind={module.module_kind.value!r}) reached the "
        f"{seam_name} seam, which has no rendering for this kind yet (wired in Item 7). "
        f"Refusing rather than mis-rendering it as a calculation."
    )
