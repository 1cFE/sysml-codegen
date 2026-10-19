"""Shared fail-loud error construction for generation seams (Item 6)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sysml_codegen.core.errors import CodeGenerationError
    from sysml_codegen.elaboration.diagnostics import SiteReason
    from sysml_codegen.generation.constraint_name_safety import ConstraintNameViolation
    from sysml_codegen.resolution.models import (
        ComputationGraph,
        ModuleOutput,
        PipelineModule,
    )


def constraint_name_safety_error(
    violation: ConstraintNameViolation,
    *,
    reason: SiteReason,
) -> CodeGenerationError:
    """Adapt one pure name-safety record to the package's public error.

    ``reason`` names the caller's site: the graph preflight and the per-module render check
    report the same kind of violation from different places.
    """
    from sysml_codegen.core.errors import GenerationCode
    from sysml_codegen.generation import CodeGenerationError
    from sysml_codegen.generation.constraint_name_safety import format_name_safety_violation

    return CodeGenerationError(
        format_name_safety_violation(violation),
        code=GenerationCode.CONSTRAINT_NAME_UNSAFE,
        reason=reason,
        name_safety_violation=violation,
    )


def validate_constraint_graph_or_raise(graph: ComputationGraph) -> None:
    """Raise the public package error for the selected graph violation."""
    from sysml_codegen.elaboration.diagnostics import SiteReason
    from sysml_codegen.generation.constraint_name_safety import (
        select_graph_name_safety_violation,
    )

    violation = select_graph_name_safety_violation(graph)
    if violation is not None:
        raise constraint_name_safety_error(
            violation, reason=SiteReason.GENERATION_CONSTRAINT_NAME_UNSAFE
        )


def residual_class_name_collision_error(
    residual: dict[str, list[str]],
    *,
    reason: SiteReason,
) -> CodeGenerationError:
    """The refusal for registry class names that survive parent-segment aliasing.

    One message for the two places that can detect it — the generation boundary,
    which runs before the output tree is touched, and ``generate_registry``
    itself for callers that reach it directly.
    """
    from sysml_codegen.core.errors import GenerationCode
    from sysml_codegen.generation import CodeGenerationError

    return CodeGenerationError(
        "REGISTRY_CLASS_NAME_COLLISION: module class name collision survives aliasing "
        "(grandparent collision): "
        + "; ".join(f"{name!r} <- {sorted(mts)}" for name, mts in sorted(residual.items()))
        + ". The parent-segment alias cannot disambiguate these; rename one scope.",
        code=GenerationCode.REGISTRY_CLASS_NAME_COLLISION,
        reason=reason,
    )


def unsupported_exit_point_type_error(
    module: PipelineModule,
    output: ModuleOutput,
) -> CodeGenerationError:
    """Build the public refusal for a root output with no TEAx wrapper."""
    from sysml_codegen.core.errors import GenerationCode
    from sysml_codegen.generation import CodeGenerationError

    source_file = module.source_file or "unknown"
    source_line = module.source_line if module.source_line is not None else 0
    return CodeGenerationError(
        "EXIT_POINT_TYPE_UNSUPPORTED: "
        f"module={module.name!r} "
        f"output={f'{output.field_name}/{output.channel_name}'!r} "
        f"python_type={output.python_type!r} "
        f"source={f'{source_file}:{source_line}'!r}",
        code=GenerationCode.EXIT_POINT_TYPE_UNSUPPORTED,
    )


def unrenderable_module_kind_error(module: PipelineModule, seam_name: str) -> CodeGenerationError:
    """Build the uniform refusal for a module_kind with no rendering at a seam."""
    # Lazy import mirrors the proven pattern at cli/__init__.py:195 (avoids any import cycle).
    from sysml_codegen.core.errors import GenerationCode
    from sysml_codegen.generation import CodeGenerationError

    return CodeGenerationError(
        f"Module {module.name!r} (module_kind={module.module_kind.value!r}) reached the "
        f"{seam_name} seam, which has no rendering for this kind yet (wired in Item 7). "
        f"Refusing rather than mis-rendering it as a calculation.",
        code=GenerationCode.MODULE_KIND_UNRENDERABLE,
    )
