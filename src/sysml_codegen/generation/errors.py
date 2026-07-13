"""Shared fail-loud error construction for generation seams (Item 6)."""


def unrenderable_module_kind_error(module, seam_name):
    """Build the uniform refusal for a module_kind with no rendering at a seam."""
    # Lazy import mirrors the proven pattern at cli/__init__.py:195 (avoids any import cycle).
    from sysml_codegen.generation import CodeGenerationError

    return CodeGenerationError(
        f"Module {module.name!r} (module_kind={module.module_kind.value!r}) reached the "
        f"{seam_name} seam, which has no rendering for this kind yet (wired in Item 7). "
        f"Refusing rather than mis-rendering it as a calculation."
    )
