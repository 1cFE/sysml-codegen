"""REQ-REG-08: post-alias uniqueness re-check (SC-11 residual grandparent hole).

The class-name collision aliaser keys on the parent segment only, so two modules
with the same class name AND parent but different grandparents alias identically.
The Item-5 static scan proved no committed model hits this, so the re-check lands
as a hard fail-fast (Phase-0 gate: CLEAN).
"""

from __future__ import annotations

import pytest

from sysml_codegen.generation.registry import _resolve_class_name_collisions


def test_grandparent_collision_fails_fast():
    """Same class + parent, different grandparent -> alias still collides -> raise."""
    all_modules = [
        {"class_name": "Pump", "module_type": "a.pump.Pump"},
        {"class_name": "Pump", "module_type": "b.pump.Pump"},
    ]
    imports = [
        "from pkg.modules.a.pump import Pump",
        "from pkg.modules.b.pump import Pump",
    ]
    with pytest.raises(ValueError, match="grandparent collision") as exc:
        _resolve_class_name_collisions(all_modules, imports)
    assert "'Pump_Pump'" in str(exc.value)


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
