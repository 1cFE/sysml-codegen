"""REQ-REG-08: post-alias uniqueness re-check (SC-11 residual grandparent hole).

The class-name collision aliaser keys on the parent segment only, so two modules
with the same class name AND parent but different grandparents alias identically.
The re-check is a hard fail-fast.

Gate 4B-G0 split detection from the raise: the aliaser aliases, ``_residual_collisions``
reports what survived, and the two callers decide. That is what let the generation
boundary run the same check *before* clearing the output tree, with the package's
own error instead of a bare ``ValueError`` (Slice 3E audit F5, second half).
"""

from __future__ import annotations

from sysml_codegen.elaboration.diagnostics import SiteReason
from sysml_codegen.generation import CodeGenerationError
from sysml_codegen.generation.errors import residual_class_name_collision_error
from sysml_codegen.generation.registry import (
    _residual_collisions,
    _resolve_class_name_collisions,
)


def _entry(class_name: str, module_type: str, import_path: str) -> dict:
    """A registry entry as ``_registry_class_entries`` builds it."""
    return {
        "class_name": class_name,
        "module_type": module_type,
        "imported_name": class_name,
        "import_path": import_path,
        "import_group": "formula",
    }


def test_grandparent_collision_survives_aliasing_and_is_refused_by_type():
    """Same class + parent, different grandparent -> alias still collides.

    The refusal is the package's own error, not a bare ``ValueError``: the
    operator reads a code-generation failure, and the CLI's boundary handler
    catches it instead of the bottom "Unexpected error" arm.
    """
    all_modules = [
        _entry("Pump", "a.pump.Pump", "a.pump"),
        _entry("Pump", "b.pump.Pump", "b.pump"),
    ]
    aliased = _resolve_class_name_collisions(all_modules)
    residual = _residual_collisions(aliased)
    assert sorted(residual) == ["Pump_Pump"]

    error = residual_class_name_collision_error(
        residual, reason=SiteReason.GENERATION_REGISTRY_RENDER_CLASS_NAME_COLLISION
    )
    assert isinstance(error, CodeGenerationError)
    assert error.reason is SiteReason.GENERATION_REGISTRY_RENDER_CLASS_NAME_COLLISION
    assert "grandparent collision" in str(error)
    assert "'Pump_Pump'" in str(error)


def test_distinct_parents_alias_cleanly():
    """Same class, different parents -> distinct aliases -> no residual, no raise."""
    all_modules = [
        _entry("Pump", "a.foo.Pump", "a.foo"),
        _entry("Pump", "a.bar.Pump", "a.bar"),
    ]
    resolved = _resolve_class_name_collisions(all_modules)
    aliases = sorted(m["class_name"] for m in resolved)
    assert aliases == ["Bar_Pump", "Foo_Pump"]
    assert _residual_collisions(resolved) == {}
