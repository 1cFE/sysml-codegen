"""Family 3 — Name-keyed lookup uniqueness (PIPELINE-TRUTH Item 5).

INV-3 (uniqueness-or-warn): every name-keyed lookup either keys by QN or warns
when a bare-name lookup is ambiguous — no first-wins collision is silent.

D3-7 is closed-by-construction: the OutputRegistry scoped-key guard raises on a
duplicate key (a regression pin here, not a silent-drop test). D3-10 and D3-11b
warn at the leaf/instance-name lookup. Expectations are anchored to constructed
inputs, never computed by the code under test (R1).
"""

from __future__ import annotations

import logging

import pytest

from sysml_codegen.extraction.data_models import RedefinitionData, RedefinitionType
from sysml_codegen.extraction.usage_extractor import CalcUsageData


def _warns(caplog):
    return [r.message for r in caplog.records if r.levelno >= logging.WARNING]


# --- D3-7: OutputRegistry scoped-key collision guard raises (regression pin) -----


def test_d37_scoped_key_collision_raises_loudly():
    """Two distinct channels under one scoped key (the reachable two-FORMULA
    `Widget.result` shape) raise at registration — the closed-by-construction
    closer for the D3-7 silent-cross-wire claim."""
    from sysml_codegen.core.output_registry import (
        CanonicalChannel,
        OutputRegistry,
        ScopedKey,
    )

    registry = OutputRegistry()
    key = ScopedKey("Widget.result")
    registry.register_scoped(key, CanonicalChannel("pkg_a__widget__result"))
    with pytest.raises(ValueError, match="scoped key collision"):
        registry.register_scoped(key, CanonicalChannel("pkg_b__widget__result"))


def test_d37_same_key_same_channel_is_idempotent():
    """Same key + same channel is not a collision (silently ignored)."""
    from sysml_codegen.core.output_registry import (
        CanonicalChannel,
        OutputRegistry,
        ScopedKey,
    )

    registry = OutputRegistry()
    key = ScopedKey("Widget.result")
    chan = CanonicalChannel("pkg_a__widget__result")
    registry.register_scoped(key, chan)
    registry.register_scoped(key, chan)  # no raise


# --- D3-10: redefinition leaf-name collision warns ------------------------------


def _literal_redef(part_qn: str, attr: str, value: float) -> RedefinitionData:
    return RedefinitionData(
        owning_part_qn=part_qn,
        attribute_name=attr,
        redefinition_type=RedefinitionType.LITERAL,
        literal_value=value,
    )


def test_d310_leaf_redef_collision_refuses_rather_than_guessing(caplog):
    """Two `Motor` partdefs redefine `:>> power` to different literals.

    Declared migration (Item 2, inventory row 4): this used to warn and return the
    first value anyway, which is the "plausible verdict from a guessed binding" that
    contract invariant 26 forbids — the parameter silently acquired 100.0 when 999.0 was
    equally supported. The name-based tier survives, because no exact form covers its
    population, but a collision now refuses: the parameter stays defaultless and
    manual-required, which is loud.
    """
    from sysml_codegen.resolution.graph_builder import _find_literal_redefinition

    redefs = [
        _literal_redef("Pkg__A__Motor", "power", 100.0),
        _literal_redef("Pkg__B__Motor", "power", 999.0),
    ]
    with caplog.at_level(logging.WARNING):
        value = _find_literal_redefinition("motor", "power", redefs, usage_type_map=None)
    assert value is None, "a colliding leaf must not resolve to a guessed default"
    warns = _warns(caplog)
    assert any("power" in w and "leaf collision" in w for w in warns), warns


def test_d310_single_redef_no_warn(caplog):
    """A single matching redef is unambiguous — no warning (INV-6)."""
    from sysml_codegen.resolution.graph_builder import _find_literal_redefinition

    redefs = [_literal_redef("Pkg__A__Motor", "power", 100.0)]
    with caplog.at_level(logging.WARNING):
        value = _find_literal_redefinition("motor", "power", redefs, usage_type_map=None)
    assert value == 100.0
    assert _warns(caplog) == []


# --- D3-11b: user-facing ambiguous instance-name target warns -------------------


def _usage(instance: str, calc_def: str, qn: str) -> CalcUsageData:
    return CalcUsageData(
        instance_name=instance,
        calc_def_name=calc_def,
        calc_def_qualified_name=calc_def,
        module_type=f"{calc_def}Module",
        qualified_name=qn,
        unbound_params=[],
    )


def test_d311b_ambiguous_target_lookup_warns(caplog):
    """`find_required_modules(['power_calc.out'])` with two `power_calc` usages
    resolves first-wins — the user-facing lookup must WARN it is ambiguous."""
    from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
    from sysml_codegen.core.output_registry import OutputRegistry

    usages = [
        _usage("power_calc", "PowerA", "Design__blanket__power_calc"),
        _usage("power_calc", "PowerB", "Design__vacuum__power_calc"),
    ]
    bt = DependencyBacktracker(usages, calc_defs=[], output_registry=OutputRegistry())
    with caplog.at_level(logging.WARNING):
        try:
            bt.find_required_modules(["power_calc.out"])
        except Exception:
            pass  # downstream tracing may fail on the stub usages; the warn is what we pin
    warns = _warns(caplog)
    assert any("power_calc" in w and "ambiguous" in w for w in warns), warns
