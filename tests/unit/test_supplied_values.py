"""Supplied-value materializer seams (REQ-SVM-01..04): precedence, 0.0-carry (F2),
collision guard (F3), non-literal loud skip (F5).

These pin the mechanism's sharp behaviors directly on `materialize_supplied_values`,
independent of any fixture snapshot.
"""

from __future__ import annotations

import logging
from pathlib import Path

from sysml_codegen.analysis.parameter_groups import DesignAttributeData
from sysml_codegen.extraction.data_models import RedefinitionData, RedefinitionType
from sysml_codegen.extraction.usage_extractor import BindingInfo, BindingType, CalcUsageData
from sysml_codegen.resolution.supplied_values import materialize_supplied_values

_SCOPE = "Scope__plant"


def _usage(source_path: str, owning_part_def_qn: str | None = None) -> CalcUsageData:
    return CalcUsageData(
        instance_name="cost_calc",
        calc_def_name="CostCalc",
        calc_def_qualified_name="Lib::CostCalc",
        module_type="Lib__CostCalc",
        bindings=[
            BindingInfo(param_name="p", source_path=source_path, binding_type=BindingType.CHAIN)
        ],
        qualified_name=f"{_SCOPE}__cost_calc",
        owning_part_def_qn=owning_part_def_qn,
    )


def _override(owner: str, attr: str, value, target_path=None, kind=RedefinitionType.LITERAL):
    return RedefinitionData(
        owning_part_qn=owner,
        attribute_name=attr,
        redefinition_type=kind,
        literal_value=value,
        target_path=target_path or [],
    )


def _synth_by_qn(attrs: list[DesignAttributeData]) -> dict[str, DesignAttributeData]:
    return {a.qualified_name: a for a in attrs}


def test_dotted_override_synthesizes_source_qn():
    """(c) dotted override → one synth attr keyed by the source QN."""
    out = materialize_supplied_values(
        [_usage("driver.efficiency")],
        redefinitions=[],
        design_overrides=[_override(_SCOPE, "efficiency", 0.35, target_path=["driver", "efficiency"])],
        usage_type_map={},
        real_design_attrs={},
    )
    by_qn = _synth_by_qn(out)
    assert "Scope__plant__driver__efficiency" in by_qn
    assert by_qn["Scope__plant__driver__efficiency"].default_value == "0.35"


def test_zero_literal_carries_as_string_zero_not_dropped():
    """F2/INV-6: a supplied 0.0 materializes as `"0.0"`, never dropped."""
    out = materialize_supplied_values(
        [_usage("driver.efficiency")],
        redefinitions=[],
        design_overrides=[_override(_SCOPE, "efficiency", 0.0, target_path=["driver", "efficiency"])],
        usage_type_map={},
        real_design_attrs={},
    )
    assert _synth_by_qn(out)["Scope__plant__driver__efficiency"].default_value == "0.0"


def test_precedence_usage_override_beats_specialized_def():
    """INV-3 / SC-2: tier 1 (usage override 0.99) beats tier 2a (spec-def :>> 0.35)."""
    out = materialize_supplied_values(
        [_usage("driver.efficiency")],
        redefinitions=[_override("Lib__Hif_Driver", "efficiency", 0.35)],
        design_overrides=[_override(_SCOPE, "efficiency", 0.99, target_path=["driver", "efficiency"])],
        usage_type_map={(_SCOPE, "driver"): "Lib__Hif_Driver"},
        real_design_attrs={},
    )
    assert _synth_by_qn(out)["Scope__plant__driver__efficiency"].default_value == "0.99"


def test_specialized_def_resolves_when_no_override():
    """Tier 2a alone: spec-def :>> via usage_type_map (Strategy 1)."""
    out = materialize_supplied_values(
        [_usage("driver.efficiency")],
        redefinitions=[_override("Lib__Hif_Driver", "efficiency", 0.35)],
        design_overrides=[],
        usage_type_map={(_SCOPE, "driver"): "Lib__Hif_Driver"},
        real_design_attrs={},
    )
    assert _synth_by_qn(out)["Scope__plant__driver__efficiency"].default_value == "0.35"


def test_collision_guard_real_attr_wins_and_warns(caplog):
    """F3/REQ-SVM-03: a real design attribute covering the source QN is not overwritten;
    the materializer skips synthesis and WARNs."""
    real = DesignAttributeData(
        name="efficiency", sysml_type="Real", default_value="0.5", unit=None,
        source_file=Path("d.sysml"), source_line=1, parent_part="driver",
        qualified_name="Scope__plant__driver__efficiency",
    )
    with caplog.at_level(logging.WARNING):
        out = materialize_supplied_values(
            [_usage("driver.efficiency")],
            redefinitions=[],
            design_overrides=[_override(_SCOPE, "efficiency", 0.35, target_path=["driver", "efficiency"])],
            usage_type_map={},
            real_design_attrs={Path("d.sysml"): [real]},
        )
    assert out == []  # real wins; nothing synthesized
    assert any("already covers" in r.message for r in caplog.records)


def test_non_literal_override_skips_loudly_with_count_summary(caplog):
    """F5/REQ-SVM-04/INV-7: a referenced binding whose only supplied value is non-literal
    (CHAIN) is not synthesized and a count-summary WARN names the deferred shape."""
    with caplog.at_level(logging.WARNING):
        out = materialize_supplied_values(
            [_usage("driver.efficiency")],
            redefinitions=[],
            design_overrides=[
                _override(_SCOPE, "efficiency", None, target_path=["driver", "efficiency"],
                          kind=RedefinitionType.CHAIN)
            ],
            usage_type_map={},
            real_design_attrs={},
        )
    assert out == []
    msgs = " ".join(r.message for r in caplog.records)
    assert "non-literal skipped" in msgs and "driver.efficiency" in msgs


def test_clean_run_is_silent_no_warning(caplog):
    """Silent-on-clean (INV-6 conformance): zero non-literal skips → no WARNING."""
    with caplog.at_level(logging.WARNING):
        materialize_supplied_values(
            [_usage("driver.efficiency")],
            redefinitions=[],
            design_overrides=[_override(_SCOPE, "efficiency", 0.35, target_path=["driver", "efficiency"])],
            usage_type_map={},
            real_design_attrs={},
        )
    assert [r for r in caplog.records if r.levelno >= logging.WARNING] == []
