"""Where a module's generated class file lives: the one derivation every writer reads.

The module writer, the stencil writer, the module template's own path, the duplicate-path
preflight and the registry's import lines all name a module's file. They read it here, so
every class file written is imported by the registry and every registry import names a
written file (I5 in ``.project/active/repeated-rollup-collision/design.md``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sysml_codegen.core.errors import CodeGenerationError, GenerationCode
from sysml_codegen.core.identifier_types import PythonModulePath, SysMLQualifiedName

if TYPE_CHECKING:
    from sysml_codegen.resolution.models import PipelineModule


def module_python_path(module: PipelineModule) -> PythonModulePath:
    """The package-relative file path of ``module``'s generated class, for every module kind.

    - Calculation: the calc def's qualified name (one file per calc def).
    - Formula: the owning definition's qualified name plus the attribute name (one file
      per definition feature, whichever copy asks).
    - Aggregation: the module's own occurrence path. Only the first copy of a module
      type is written (``registry.class_owners``), so that copy's path is the class's.
    - Constraint and report aggregator: ``module_type`` is already a dotted Python path
      (D9 naming); the file stem is its final segment, lowercased as-is.
    """
    from sysml_codegen.generation.errors import unrenderable_module_kind_error
    from sysml_codegen.resolution.models import ModuleKind

    if module.module_kind in (ModuleKind.CONSTRAINT, ModuleKind.REPORT_AGGREGATOR):
        parts = module.module_type.split(".")
        return PythonModulePath(directory="/".join(parts[:-1]), filename=parts[-1].lower())
    if module.module_kind == ModuleKind.FORMULA:
        sysml_qn = f"{module.calc_def_qualified_name}::{module.calc_def_name}"
    elif module.module_kind == ModuleKind.AGGREGATION:
        sysml_qn = module.name.replace("__", "::")
    elif module.module_kind == ModuleKind.CALCULATION:
        if module.calc_def_qualified_name is None:
            raise CodeGenerationError(
                f"GENERATION_METADATA_MISSING: module {module.name!r} "
                "lacks calc_def_qualified_name",
                code=GenerationCode.GENERATION_METADATA_MISSING,
            )
        sysml_qn = module.calc_def_qualified_name
    else:
        raise unrenderable_module_kind_error(module, "python-path")
    return PythonModulePath.from_sysml(SysMLQualifiedName(sysml_qn))
