"""REQ-REG-08: post-alias uniqueness re-check (SC-11 residual grandparent hole).

The class-name collision aliaser keys on the parent segment only, so two modules
with the same class name AND parent but different grandparents alias identically.
The Item-5 static scan proved no committed model hits this, so the re-check lands
as a hard fail-fast (Phase-0 gate: CLEAN).

Gate 4B-G0 split detection from the raise: the aliaser aliases, ``_residual_collisions``
reports what survived, and the two callers decide. That is what let the generation
boundary run the same check *before* clearing the output tree, with the package's
own error instead of a bare ``ValueError`` (Slice 3E audit F5, second half).
"""

from __future__ import annotations

from sysml_codegen.generation import CodeGenerationError
from sysml_codegen.generation.errors import residual_class_name_collision_error
from sysml_codegen.generation.registry import (
    _residual_collisions,
    _resolve_class_name_collisions,
)


def test_grandparent_collision_survives_aliasing_and_is_refused_by_type():
    """Same class + parent, different grandparent -> alias still collides.

    The refusal is the package's own error, not a bare ``ValueError``: the
    operator reads a code-generation failure, and the CLI's boundary handler
    catches it instead of the bottom "Unexpected error" arm.
    """
    all_modules = [
        {"class_name": "Pump", "module_type": "a.pump.Pump"},
        {"class_name": "Pump", "module_type": "b.pump.Pump"},
    ]
    imports = [
        "from pkg.modules.a.pump import Pump",
        "from pkg.modules.b.pump import Pump",
    ]
    aliased, _ = _resolve_class_name_collisions(all_modules, imports)
    residual = _residual_collisions(aliased)
    assert sorted(residual) == ["Pump_Pump"]

    error = residual_class_name_collision_error(residual)
    assert isinstance(error, CodeGenerationError)
    assert "grandparent collision" in str(error)
    assert "'Pump_Pump'" in str(error)


def test_distinct_parents_alias_cleanly():
    """Same class, different parents -> distinct aliases -> no residual, no raise."""
    all_modules = [
        {"class_name": "Pump", "module_type": "a.foo.Pump"},
        {"class_name": "Pump", "module_type": "a.bar.Pump"},
    ]
    imports = [
        "from pkg.modules.a.foo import Pump",
        "from pkg.modules.a.bar import Pump",
    ]
    resolved, _ = _resolve_class_name_collisions(all_modules, imports)
    aliases = sorted(m["class_name"] for m in resolved)
    assert aliases == ["Bar_Pump", "Foo_Pump"]
    assert _residual_collisions(resolved) == {}
