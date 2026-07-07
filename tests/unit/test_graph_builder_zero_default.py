"""INV-6 / F2: a `0.0`-valued design attribute must classify to a `0.0` entry point,
not `None`.

`_classify_entry_points` filled the default with a truthiness test (`if
attr.default_value:`), which drops `"0.0"` (and `""`) to `None`. A Step-3-resolved
entry point is NOT in the fell-through set, so `collect_uncovered_params` (V11) never
inspects it — a `0.0` silently dropped to `None` would emit `null` and escape V11, the
exact failure the epic kills. The fix is `is not None`.
"""

from __future__ import annotations

from pathlib import Path

from sysml_codegen.analysis.parameter_groups import DesignAttributeData
from sysml_codegen.resolution.graph_builder import _classify_entry_points


def _attr(qn: str, default: str | None) -> DesignAttributeData:
    return DesignAttributeData(
        name=qn.split("__")[-1],
        sysml_type="Real",
        default_value=default,
        unit=None,
        source_file=Path("unknown"),
        source_line=0,
        parent_part="",
        qualified_name=qn,
    )


def test_zero_valued_design_attr_classifies_to_zero_not_null():
    qn = "Lib__Plant__driver__efficiency"
    eps = _classify_entry_points(
        entry_point_names={qn},
        entry_point_sources={},
        design_attrs={Path("d.sysml"): [_attr(qn, "0.0")]},
        usages=[],
        calc_def_map={},
        group_deriver=None,
    )
    ep = eps[qn]
    assert ep.entry_type.value == "design_attribute"
    assert ep.default_value == 0.0  # NOT None — the INV-6 hazard


def test_nonzero_valued_design_attr_still_carries():
    qn = "Lib__Plant__driver__efficiency"
    eps = _classify_entry_points(
        entry_point_names={qn},
        entry_point_sources={},
        design_attrs={Path("d.sysml"): [_attr(qn, "0.35")]},
        usages=[],
        calc_def_map={},
        group_deriver=None,
    )
    assert eps[qn].default_value == 0.35


def test_none_valued_design_attr_stays_none():
    qn = "Lib__Plant__driver__efficiency"
    eps = _classify_entry_points(
        entry_point_names={qn},
        entry_point_sources={},
        design_attrs={Path("d.sysml"): [_attr(qn, None)]},
        usages=[],
        calc_def_map={},
        group_deriver=None,
    )
    assert eps[qn].default_value is None
