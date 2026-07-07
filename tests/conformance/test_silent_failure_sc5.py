"""SC-5 / D3-12 — non-float entry-point literal is loud, not a silent None-omission.

The hazard-scoped warn fires at JSON-emission time: a param that lands in a group
with no numeric value AND whose input type is non-numeric (a bool/string/enum)
can never be a float entry point, so it is silently omitted. A numeric-typed EP
with no default (a normal user-fill) and a chain-reference design default stay
silent (INV-6). Expectations anchored to the fixture source, not computed (R1).
"""

from __future__ import annotations

import logging

import pytest

from sysml_codegen.analysis.parameter_groups import (
    ParameterGroupDeriver,
    _is_numeric_sysml_type,
    extract_design_attributes,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.usage_extractor import extract_calculation_usages
from tests.conftest import requires_license, snapshot_fixture


def _deriver(fixture: str) -> ParameterGroupDeriver:
    fixture_dir = snapshot_fixture(fixture).parent
    ex = SysMLDataExtractor([fixture_dir])
    assert ex.load_models(), fixture
    defs = ex.extract_calculation_definitions()
    usages, _ = extract_calculation_usages(ex.model, calc_defs=defs)
    dattrs = extract_design_attributes(ex.model)
    return ParameterGroupDeriver(dattrs, usages, defs)


def _warns(caplog):
    return [r.message for r in caplog.records if r.levelno >= logging.WARNING]


# --- unit: the numeric-type discriminator --------------------------------------


@pytest.mark.parametrize(
    "sysml_type,expected",
    [
        ("Real", True), ("Integer", True), ("Power", True), ("Length", True),
        (None, True), ("", True),  # unknown → conservative numeric (no false warn)
        ("'Wall Kind'", False), ("Wall Kind", False), ('"State"', False),
    ],
)
def test_is_numeric_sysml_type(sysml_type, expected):
    assert _is_numeric_sysml_type(sysml_type) is expected


# --- fires-on-shape: the enum EP warns -----------------------------------------


@requires_license
def test_sc5_nonfloat_enum_ep_warns(caplog):
    """`plant_value_shapes` has `wall : 'Wall Kind'` fed the enum literal
    `'Wall Kind'::liquid_wall`; it cannot be a float EP and is omitted — warn."""
    deriver = _deriver("plant_value_shapes")
    with caplog.at_level(logging.WARNING):
        deriver.derive_groups()
    warns = _warns(caplog)
    assert any("SC-5/D3-12" in w and "wall" in w for w in warns), warns


# --- silent-on-clean: a chain-reference default stays silent (INV-6) -----------


@requires_license
def test_sc5_chain_reference_default_stays_silent(caplog):
    """`attr_expr_probe` carries chain-reference design defaults (`half_vol =
    split.half`) and numeric-typed unbound params with no default — none is a
    non-float EP hazard, so SC-5 stays silent (INV-6)."""
    deriver = _deriver("attr_expr_probe")
    with caplog.at_level(logging.WARNING):
        deriver.derive_groups()
    assert not any("SC-5/D3-12" in w for w in _warns(caplog)), _warns(caplog)
