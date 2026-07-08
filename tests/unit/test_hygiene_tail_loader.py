"""D3 Hygiene Tail Site 1 — loud load-bearing-field diagnostics in the snapshot
loader (TRUTH-DEBT Item 6).

`snapshot/loader.py` deserializes snapshot dicts with `.get(field, default)`.
Most defaults are benign; a load-bearing subset (`python_type`, `binding_type`,
`parent_part_path`, `owning_part_def_qn`, `qualified_name`) masked a missing or
corrupt field with no diagnostic. `qualified_name` is a keying field — a silent
default would mis-key the output registry — so it raises; the rest warn and
degrade. Expectations are anchored to hand-edited malformed dicts, never
computed by the code under test (R1).
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from sysml_codegen.snapshot import SnapshotFormatError
from sysml_codegen.snapshot.loader import (
    _deserialize_attribute_info,
    _deserialize_calc_usage,
    _deserialize_design_attribute,
)


def _warns(caplog):
    return [r.message for r in caplog.records if r.levelno >= logging.WARNING]


def _valid_attr() -> dict:
    return {
        "name": "cost",
        "sysml_type": "ScalarValues::Real",
        "default_value": "1.0",
        "binding_type": "unbound",
        "is_input": True,
        "is_output": False,
        "python_type": "float",
        "description": "",
        "unit": None,
        "source_line": 12,
        "is_optional": False,
    }


def _valid_usage() -> dict:
    return {
        "instance_name": "calc1",
        "calc_def_name": "CalcDef",
        "calc_def_qualified_name": "Pkg::CalcDef",
        "module_type": "CalcDefModule",
        "bindings": [],
        "unbound_params": [],
        "source_file": "model.sysml",
        "source_line": 3,
        "parent_part_path": "Pkg::Part1",
        "qualified_name": "Pkg::Part1::calc1",
        "is_template": False,
        "owning_part_def_qn": "Pkg::PartDef1",
    }


def _valid_design_attribute() -> dict:
    return {
        "name": "misc_cost",
        "sysml_type": "ScalarValues::Real",
        "default_value": "1.0",
        "unit": None,
        "source_file": "design.sysml",
        "source_line": 1,
        "parent_part": "Design__plant",
        "qualified_name": "Design__plant__misc_cost",
    }


# --- AttributeInfo: python_type, binding_type -----------------------------------


def test_missing_python_type_warns(caplog):
    d = _valid_attr()
    del d["python_type"]
    with caplog.at_level(logging.WARNING):
        info = _deserialize_attribute_info(d)
    assert info.python_type == "Any"  # degraded default preserved
    assert any("python_type" in w for w in _warns(caplog))


def test_missing_binding_type_warns(caplog):
    d = _valid_attr()
    del d["binding_type"]
    with caplog.at_level(logging.WARNING):
        info = _deserialize_attribute_info(d)
    assert info.binding_type.value == "unbound"
    assert any("binding_type" in w for w in _warns(caplog))


def test_clean_attr_dict_no_warn(caplog):
    with caplog.at_level(logging.WARNING):
        info = _deserialize_attribute_info(_valid_attr())
    assert info.python_type == "float"
    assert _warns(caplog) == []


# --- CalcUsageData: parent_part_path, owning_part_def_qn (WARN) -----------------


def test_missing_parent_part_path_warns(caplog):
    d = _valid_usage()
    del d["parent_part_path"]
    with caplog.at_level(logging.WARNING):
        usage = _deserialize_calc_usage(d)
    assert usage.parent_part_path == ""
    assert any("parent_part_path" in w for w in _warns(caplog))


def test_missing_owning_part_def_qn_warns(caplog):
    d = _valid_usage()
    del d["owning_part_def_qn"]
    with caplog.at_level(logging.WARNING):
        usage = _deserialize_calc_usage(d)
    assert usage.owning_part_def_qn is None
    assert any("owning_part_def_qn" in w for w in _warns(caplog))


def test_clean_usage_dict_no_warn(caplog):
    with caplog.at_level(logging.WARNING):
        _deserialize_calc_usage(_valid_usage())
    assert _warns(caplog) == []


# --- CalcUsageData / DesignAttributeData: qualified_name (RAISE, keying) --------


def test_missing_usage_qualified_name_raises():
    d = _valid_usage()
    del d["qualified_name"]
    with pytest.raises(SnapshotFormatError, match="qualified_name"):
        _deserialize_calc_usage(d)


def test_missing_design_attribute_qualified_name_raises():
    d = _valid_design_attribute()
    del d["qualified_name"]
    with pytest.raises(SnapshotFormatError, match="qualified_name"):
        _deserialize_design_attribute(d)


def test_clean_design_attribute_no_warn(caplog):
    with caplog.at_level(logging.WARNING):
        attr = _deserialize_design_attribute(_valid_design_attribute())
    assert attr.qualified_name == "Design__plant__misc_cost"
    assert _warns(caplog) == []
