"""Supplied-value materializer seams (REQ-SVM-01..04): precedence, 0.0-carry (F2),
collision guard (F3), non-literal loud skip (F5).

These pin the mechanism's sharp behaviors directly on the enrichment seam,
independent of any fixture snapshot. `_enrich` returns only the newly synthesized
attributes so each behavioral assertion below reads exactly as it did against the
route-based materializer it replaced.
"""

from __future__ import annotations

import logging
from pathlib import Path

from sysml_codegen.analysis.parameter_groups import DesignAttributeData
from sysml_codegen.extraction.data_models import RedefinitionData, RedefinitionType
from sysml_codegen.extraction.usage_extractor import BindingInfo, BindingType, CalcUsageData
from sysml_codegen.resolution.supplied_values import enrich_graph_design_attributes

_SCOPE = "Scope__plant"
_SOURCE = Path("design.sysml")


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
        source_file=_SOURCE,
    )


def _override(owner: str, attr: str, value, target_path=None, kind=RedefinitionType.LITERAL):
    return RedefinitionData(
        owning_part_qn=owner,
        attribute_name=attr,
        redefinition_type=kind,
        literal_value=value,
        target_path=target_path or [],
    )


def _enrich(
    calc_usages,
    *,
    redefinitions,
    design_overrides,
    usage_type_map,
    real_design_attrs,
) -> list[DesignAttributeData]:
    """Run the enrichment seam and return only what it synthesized.

    The seam is copy-on-write and returns real plus synthetic attributes together;
    these tests assert on the synthetic set, so the real inputs are subtracted back out.
    """
    before = {id(attr) for attrs in real_design_attrs.values() for attr in attrs}
    enriched = enrich_graph_design_attributes(
        real_design_attrs,
        calc_usages=calc_usages,
        prepared=None,
        redefinitions=redefinitions,
        design_overrides=design_overrides,
        usage_type_map=usage_type_map,
    )
    return [
        attr for attrs in enriched.values() for attr in attrs if id(attr) not in before
    ]


def _synth_by_qn(attrs: list[DesignAttributeData]) -> dict[str, DesignAttributeData]:
    return {a.qualified_name: a for a in attrs}


def test_dotted_override_synthesizes_source_qn():
    """(c) dotted override → one synth attr keyed by the source QN."""
    out = _enrich(
        [_usage("driver.efficiency")],
        redefinitions=[],
        design_overrides=[
            _override(_SCOPE, "efficiency", 0.35, target_path=["driver", "efficiency"])
        ],
        usage_type_map={},
        real_design_attrs={},
    )
    by_qn = _synth_by_qn(out)
    assert "Scope__plant__driver__efficiency" in by_qn
    assert by_qn["Scope__plant__driver__efficiency"].default_value == "0.35"


def test_renamed_consumers_dedup_to_one_synth_attr():
    """INV-2: two differently-named consumers of one source produce ONE synthetic
    attribute (deduped by source QN), so they collapse onto one entry point downstream."""
    u1 = CalcUsageData(
        instance_name="lcoe", calc_def_name="C", calc_def_qualified_name="Lib::C",
        module_type="Lib__C",
        bindings=[BindingInfo(param_name="driver_efficiency", source_path="driver.efficiency",
                              binding_type=BindingType.CHAIN)],
        qualified_name=f"{_SCOPE}__lcoe",
        source_file=_SOURCE,
    )
    u2 = CalcUsageData(
        instance_name="recirc", calc_def_name="C", calc_def_qualified_name="Lib::C",
        module_type="Lib__C",
        bindings=[BindingInfo(param_name="eta", source_path="driver.efficiency",
                              binding_type=BindingType.CHAIN)],
        qualified_name=f"{_SCOPE}__recirc",
        source_file=_SOURCE,
    )
    out = _enrich(
        [u1, u2],
        redefinitions=[],
        design_overrides=[
            _override(_SCOPE, "efficiency", 0.35, target_path=["driver", "efficiency"])
        ],
        usage_type_map={},
        real_design_attrs={},
    )
    assert len(out) == 1  # one synth attr, not one-per-consumer
    assert out[0].qualified_name == "Scope__plant__driver__efficiency"


def test_zero_literal_carries_as_string_zero_not_dropped():
    """F2/INV-6: a supplied 0.0 materializes as `"0.0"`, never dropped."""
    out = _enrich(
        [_usage("driver.efficiency")],
        redefinitions=[],
        design_overrides=[
            _override(_SCOPE, "efficiency", 0.0, target_path=["driver", "efficiency"])
        ],
        usage_type_map={},
        real_design_attrs={},
    )
    assert _synth_by_qn(out)["Scope__plant__driver__efficiency"].default_value == "0.0"


def test_precedence_usage_override_beats_specialized_def():
    """INV-3 / SC-2: tier 1 (usage override 0.99) beats tier 2a (spec-def :>> 0.35)."""
    out = _enrich(
        [_usage("driver.efficiency")],
        redefinitions=[_override("Lib__Hif_Driver", "efficiency", 0.35)],
        design_overrides=[
            _override(_SCOPE, "efficiency", 0.99, target_path=["driver", "efficiency"])
        ],
        usage_type_map={(_SCOPE, "driver"): "Lib__Hif_Driver"},
        real_design_attrs={},
    )
    assert _synth_by_qn(out)["Scope__plant__driver__efficiency"].default_value == "0.99"


def test_three_tier_precedence_ladder():
    """SC-2 / INV-3: the full ladder with distinct values at each tier. Tier 1 (usage
    override 0.99) > tier 2 (specialized-def :>> 0.35) > tier 3 (base def → no synthesis).
    A tier-skip or tier-reorder would flip an assertion below."""
    tier2 = [_override("Lib__Hif_Driver", "efficiency", 0.35)]
    tier1 = [_override(_SCOPE, "efficiency", 0.99, target_path=["driver", "efficiency"])]
    utm = {(_SCOPE, "driver"): "Lib__Hif_Driver"}

    def resolve(redefs, overrides):
        out = _enrich(
            [_usage("driver.efficiency")],
            redefinitions=redefs,
            design_overrides=overrides,
            usage_type_map=utm,
            real_design_attrs={},
        )
        return out[0].default_value if out else None

    assert resolve(tier2, tier1) == "0.99"  # tier 1 wins over tier 2
    assert resolve(tier2, []) == "0.35"      # tier 2 wins when tier 1 absent
    assert resolve([], []) is None           # tier 3: base def carries, no synthesis


def test_specialized_def_resolves_when_no_override():
    """Tier 2a alone: spec-def :>> via usage_type_map (Strategy 1)."""
    out = _enrich(
        [_usage("driver.efficiency")],
        redefinitions=[_override("Lib__Hif_Driver", "efficiency", 0.35)],
        design_overrides=[],
        usage_type_map={(_SCOPE, "driver"): "Lib__Hif_Driver"},
        real_design_attrs={},
    )
    assert _synth_by_qn(out)["Scope__plant__driver__efficiency"].default_value == "0.35"


def test_in_part_direct_owner_leg_resolves_bare_name():
    """(d)/F4: a bare in-part binding resolves via tier-2b direct-owner match on the
    consuming calc's own part def."""
    usage = _usage("throughput", owning_part_def_qn="Lib__Flow_Sub")
    out = _enrich(
        [usage],
        redefinitions=[_override("Lib__Flow_Sub", "throughput", 8.0)],
        design_overrides=[],
        usage_type_map={},
        real_design_attrs={},
    )
    assert _synth_by_qn(out)["Scope__plant__throughput"].default_value == "8.0"


def test_in_part_leg_scoped_by_owner_no_cross_wire():
    """INV-4: tier-2b matches only the consuming calc's OWN part def. A same-named
    redefinition owned by an unrelated part def does not cross-wire."""
    usage = _usage("throughput", owning_part_def_qn="Lib__Flow_Sub")
    out = _enrich(
        [usage],
        redefinitions=[_override("Lib__Other_Part", "throughput", 99.0)],
        design_overrides=[],
        usage_type_map={},
        real_design_attrs={},
    )
    assert out == []  # unrelated owner → no synthesis, no cross-wire


def test_gain_self_redef_materializes():
    """D2: an instance self-redefinition (`:>> gain = 80.0` owned by the instance
    itself, empty target_path) synthesizes for a bare-name binding (`in gain = gain`),
    the tier fusion_tea's `hif_plant.sysml:87` needs to lower 'Viability Threshold'."""
    usage = _usage("gain")
    out = _enrich(
        [usage],
        redefinitions=[],
        design_overrides=[_override(_SCOPE, "gain", 80.0)],
        usage_type_map={},
        real_design_attrs={},
    )
    assert _synth_by_qn(out)[f"{_SCOPE}__gain"].default_value == "80.0"


def test_gain_self_redef_does_not_shadow_tier1_bare_override():
    """R2: the self-redef tier sits below tier 1 — a genuine bare override block on a
    sub-part instance (`owning_part_qn == f'{instance_scope}__{part_usage}'`) still
    wins when both are present."""
    usage = _usage("gain")
    tier1_override = _override(f"{_SCOPE}__gain", "gain", 1.0)  # bare override block
    self_redef_override = _override(_SCOPE, "gain", 80.0)  # instance self-redef
    out = _enrich(
        [usage],
        redefinitions=[],
        design_overrides=[tier1_override, self_redef_override],
        usage_type_map={},
        real_design_attrs={},
    )
    assert _synth_by_qn(out)[f"{_SCOPE}__gain"].default_value == "1.0"


def test_gain_self_redef_scoped_to_bare_name_binding_only():
    """The self-redef tier is demand-scoped to bare-name bindings (part_usage ==
    attr); a dotted binding to the same instance/attr shape must not match it."""
    usage = _usage("driver.gain")
    out = _enrich(
        [usage],
        redefinitions=[],
        design_overrides=[_override(_SCOPE, "gain", 80.0)],
        usage_type_map={},
        real_design_attrs={},
    )
    assert out == []


def test_collision_guard_real_attr_wins_and_warns(caplog):
    """F3/REQ-SVM-03: a real design attribute covering the source QN is not overwritten;
    the materializer skips synthesis and WARNs."""
    real = DesignAttributeData(
        name="efficiency", sysml_type="Real", default_value="0.5", unit=None,
        source_file=Path("d.sysml"), source_line=1, parent_part="driver",
        qualified_name="Scope__plant__driver__efficiency",
    )
    with caplog.at_level(logging.WARNING):
        out = _enrich(
            [_usage("driver.efficiency")],
            redefinitions=[],
            design_overrides=[
                _override(_SCOPE, "efficiency", 0.35, target_path=["driver", "efficiency"])
            ],
            usage_type_map={},
            real_design_attrs={Path("d.sysml"): [real]},
        )
    assert out == []  # real wins; nothing synthesized
    assert any("already covers" in r.message for r in caplog.records)


def test_non_literal_override_skips_loudly_with_count_summary(caplog):
    """F5/REQ-SVM-04/INV-7: a referenced binding whose only supplied value is non-literal
    (CHAIN) is not synthesized and a count-summary WARN names the deferred shape."""
    with caplog.at_level(logging.WARNING):
        out = _enrich(
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
        _enrich(
            [_usage("driver.efficiency")],
            redefinitions=[],
            design_overrides=[
                _override(_SCOPE, "efficiency", 0.35, target_path=["driver", "efficiency"])
            ],
            usage_type_map={},
            real_design_attrs={},
        )
    assert [r for r in caplog.records if r.levelno >= logging.WARNING] == []


def test_malformed_type_def_literal_does_not_suppress_part_def_literal():
    """Regression (audit F1): a malformed literal at one tier must not consume the tiers
    below it.

    Merging tiers 2a and 2b into a single owner loop made a bad literal on the
    specialized/type def exit the whole loop, so a perfectly good literal on the
    consuming part def was lost — silently, with the seam reporting `0 literal applied,
    0 non-literal skipped`. The predecessor fell through and resolved 42.0.
    """
    out = _enrich(
        [_usage("driver.efficiency", owning_part_def_qn="Design__Plant")],
        redefinitions=[
            _override("Lib__Hif_Driver", "efficiency", "true"),  # malformed, type def
            _override("Design__Plant", "efficiency", 42.0),  # valid, consuming part def
        ],
        design_overrides=[],
        usage_type_map={(_SCOPE, "driver"): "Lib__Hif_Driver"},
        real_design_attrs={},
    )
    assert _synth_by_qn(out)["Scope__plant__driver__efficiency"].default_value == "42.0"
