"""Shared fail-loud error construction for generation seams (Item 6)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
    from sysml_codegen.resolution.models import PipelineModule


def unrenderable_module_kind_error(module: PipelineModule, seam_name: str) -> CodeGenerationError:
    """Build the uniform refusal for a module_kind with no rendering at a seam."""
    # Lazy import mirrors the proven pattern at cli/__init__.py:195 (avoids any import cycle).
    from sysml_codegen.generation import CodeGenerationError

    return CodeGenerationError(
        f"Module {module.name!r} (module_kind={module.module_kind.value!r}) reached the "
        f"{seam_name} seam, which has no rendering for this kind yet (wired in Item 7). "
        f"Refusing rather than mis-rendering it as a calculation."
    )
