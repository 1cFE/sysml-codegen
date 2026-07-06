"""Unit tests for the Item 7 resolution matcher fixes (SC-8).

Covers the two ``_resolve_to_design_attribute`` corrections and the A1 pool
restriction:

- Bug A (REQ-BT-09): the ``::``-QN branch sanitizes per segment, so a quoted-owner
  reference matches the per-segment-sanitized design-attribute qualified_name.
- Bug B (REQ-BT-10): a design attribute owned by a part *def* (empty parent_part)
  resolves via a leaf-unique fallback when exactly one design-part attribute carries
  the leaf; ambiguity (0 or >1) refuses (returns None -> Step-4, kept loud). INV-2.
- A1: the leaf-unique pool excludes calc-def I/O attributes (which leak into
  ``_design_attributes``), so a dotted calc-output reference is never cross-wired
  into a DESIGN_ATTRIBUTE entry point.

Real data objects, no mocks (R1): a real OutputRegistry plus synthetic
DesignAttributeData / CalcUsageData, calling the real backtracker method.
"""

from dataclasses import dataclass, field
from pathlib import Path

from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
from sysml_codegen.analysis.parameter_groups import DesignAttributeData
from sysml_codegen.extraction.usage_extractor import CalcUsageData


@dataclass
class _SimpleCalcDef:
    name: str
    qualified_name: str
    output_attributes: list = field(default_factory=list)
    input_attributes: list = field(default_factory=list)


_F = Path("/models/design.sysml")


def _attr(name: str, qn: str, parent_part: str = "", default: str | None = None):
    return DesignAttributeData(
        name=name,
        sysml_type="Real",
        default_value=default,
        unit=None,
        source_file=_F,
        source_line=1,
        parent_part=parent_part,
        qualified_name=qn,
    )


def _usage() -> CalcUsageData:
    return CalcUsageData(
        instance_name="consumer",
        calc_def_name="ConsumerCalc",
        calc_def_qualified_name="Lib::ConsumerCalc",
        module_type="ConsumerCalcModule",
        bindings=[],
        unbound_params=[],
        qualified_name="Design__plant__consumer",
        source_file=_F,
    )


def _backtracker(attrs: list[DesignAttributeData], calc_defs=None) -> DependencyBacktracker:
    from sysml_codegen.orchestration.output_registry_builder import build_output_registry

    registry = build_output_registry(
        calc_usages=[], calc_defs=[], aggregation_data=[],
        computed_attributes=[], channel_aliases=[], design_attributes={},
    )
    return DependencyBacktracker(
        all_usages=[],
        calc_defs=calc_defs or [],
        design_attributes={_F: attrs},
        output_registry=registry,
    )


def test_def_owned_leaf_unique_resolves():
    """Bug B: a dotted ref to a def-owned (parent_part='') design attr resolves by
    unique leaf even though the exact parent_part match fails."""
    attr = _attr("magnet_vol", "Lib__MagnetPartDef__magnet_vol", parent_part="")
    bt = _backtracker([attr])
    # dotted source_path: parent is the usage name, leaf is the def-owned attr
    qn = bt._resolve_to_design_attribute("magnet_holder.magnet_vol", _usage())
    assert qn == "Lib__MagnetPartDef__magnet_vol"


def test_def_owned_leaf_ambiguous_refuses():
    """INV-2: two design attributes share the leaf -> refuse (None), never guess."""
    a1 = _attr("shared", "Lib__PartA__shared", parent_part="")
    a2 = _attr("shared", "Design__part_b__shared", parent_part="part_b")
    bt = _backtracker([a1, a2])
    assert bt._resolve_to_design_attribute("some_part.shared", _usage()) is None


def test_leaf_unique_excludes_calc_def_io():
    """A1: a leaf that only names a calc-def I/O attribute is NOT a match — the
    calc-output attribute is filtered out of the leaf-unique pool, so the dotted
    reference falls through (kept loud) rather than cross-wiring."""
    calc_out = _attr("calc_out", "Lib__SomeCalc__calc_out", parent_part="")
    bt = _backtracker([calc_out], calc_defs=[_SimpleCalcDef("SomeCalc", "Lib::SomeCalc")])
    assert bt._resolve_to_design_attribute("some_calc.calc_out", _usage()) is None


def test_leaf_unique_ignores_calc_io_collision():
    """A1: when a real design-part attr and a calc-def I/O attr share a leaf, the
    calc-def one is filtered, leaving exactly one design-part candidate -> resolves
    (the collision does not force a refuse)."""
    design_attr = _attr("power", "Lib__DriverDef__power", parent_part="")
    calc_io = _attr("power", "Lib__PowerCalc__power", parent_part="")
    bt = _backtracker(
        [design_attr, calc_io],
        calc_defs=[_SimpleCalcDef("PowerCalc", "Lib::PowerCalc")],
    )
    assert bt._resolve_to_design_attribute("driver.power", _usage()) == "Lib__DriverDef__power"


def test_quoted_owner_reference_matches_after_flip():
    """Bug A: a quoted-owner ``::`` reference resolves to the per-segment-sanitized
    design-attribute QN. A bare ::->__ swap would keep the quote/space and miss."""
    attr = _attr("power", "RetypeLibrary__IFE_Driver__power", parent_part="")
    bt = _backtracker([attr])
    qn = bt._resolve_to_design_attribute("RetypeLibrary::'IFE Driver'::power", _usage())
    assert qn == "RetypeLibrary__IFE_Driver__power"


def test_quoted_owner_reference_no_false_match():
    """Bug A sanitize does not over-match: a ``::`` ref whose sanitized QN names no
    design attribute returns None."""
    attr = _attr("power", "RetypeLibrary__IFE_Driver__power", parent_part="")
    bt = _backtracker([attr])
    assert bt._resolve_to_design_attribute("RetypeLibrary::'HIF Driver'::torque", _usage()) is None
