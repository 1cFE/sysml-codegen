"""Phase 2: strict resolver seam + shared terminal-disposition switch (offline).

Hand-built facts + a real OutputRegistry (registered directly, no live model) —
pins the occurrence-scope->ScopedKey transform and the strict ladder without
needing a licensed model load.
"""

import pytest
from agentic_mbse.sysml.expression_facts import FeatureReferenceFact, IdentityFact

from sysml_codegen.analysis.constraint_lowering import (
    guard_polarity,
    occurrence_scope,
    resolve_actual,
)
from sysml_codegen.analysis.dependency_backtracker import terminal_disposition
from sysml_codegen.analysis.parameter_groups import DesignAttributeData
from sysml_codegen.core.identifier_types import CanonicalChannel, ScopedKey
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError


def _reference(source_name=None, target_qn=None, chain_segments=None):
    target = (
        IdentityFact(kind="AttributeUsage", name=None, qualified_name=target_qn)
        if target_qn
        else None
    )
    return FeatureReferenceFact(
        source_name=source_name,
        target=target,
        target_types=[],
        chain_segments=chain_segments or [],
    )


def test_occurrence_scope_transform_strips_root_and_keeps_brackets():
    assert occurrence_scope("the_design__c__cell[0]") == "c.cell[0]"
    assert occurrence_scope("the_design__c__cell") == "c.cell"


def test_ladder_scoped_hit_wins():
    registry = OutputRegistry()
    registry.register_scoped(ScopedKey("c.cell.power_calc.p"), CanonicalChannel("Chan__p"))
    ref = _reference(chain_segments=["power_calc", "p"])
    result = resolve_actual(
        reference=ref,
        occ_scope="c.cell",
        formal_name="p",
        usage_qualified_name="Design__c__cell__nonneg",
        registry=registry,
        design_attr_by_qn={},
    )
    assert result.resolution == "module_output"
    assert result.bound_channel == "Chan__p"


def test_occurrence_key_first_then_deindexed_shared_binding():
    """B1: registry holds only the de-indexed key; the occurrence-scoped key
    (with brackets) misses, so resolution falls through to the shared channel
    and records it (INV-3) — not an error."""
    registry = OutputRegistry()
    registry.register_scoped(
        ScopedKey("the_design.c.cell.power_calc.p"),
        CanonicalChannel("MultiChan__the_design__c__cell__power_calc__p"),
    )
    ref = _reference(chain_segments=["power_calc", "p"])
    result = resolve_actual(
        reference=ref,
        occ_scope="the_design.c.cell[0]",
        formal_name="p",
        usage_qualified_name="Design__c__cell0__bound",
        registry=registry,
        design_attr_by_qn={},
    )
    assert result.resolution == "module_output"
    assert result.bound_channel == "MultiChan__the_design__c__cell__power_calc__p"


def test_ladder_falls_to_alias_lookup():
    registry = OutputRegistry()
    registry.register_scoped(ScopedKey("elsewhere.chan"), CanonicalChannel("Real__chan"))
    registry.register_alias(ScopedKey("c.cell.aliased"), CanonicalChannel("Real__chan"))
    ref = _reference(chain_segments=["aliased"])
    result = resolve_actual(
        reference=ref,
        occ_scope="c.cell",
        formal_name="a",
        usage_qualified_name="Design__c__cell__nonneg",
        registry=registry,
        design_attr_by_qn={},
    )
    assert result.resolution == "module_output"
    assert result.bound_channel == "Real__chan"


def test_ladder_falls_to_design_attribute():
    registry = OutputRegistry()
    attr = DesignAttributeData(
        name="threshold",
        sysml_type="Real",
        default_value="10.0",
        unit=None,
        source_file=None,
        source_line=1,
        parent_part="Design",
        qualified_name="Design__threshold",
    )
    # target_qn is SysML `::`-form (per-segment quoted) -- exactly what the live
    # reference.target.qualified_name carries; resolve_actual sanitizes it to
    # the EQN `__`-form before matching design_attr_by_qn.
    ref = _reference(source_name="threshold", target_qn="Design::threshold")
    result = resolve_actual(
        reference=ref,
        occ_scope="c.cell",
        formal_name="threshold",
        usage_qualified_name="Design__c__cell__nonneg",
        registry=registry,
        design_attr_by_qn={"Design__threshold": attr},
    )
    assert result.resolution == "design_attribute"
    assert result.design_attribute_qn == "Design__threshold"


def test_strict_terminal_raises_never_synthesizes():
    registry = OutputRegistry()
    ref = _reference(source_name="unresolvable_actual_name")
    with pytest.raises(CodeGenerationError) as exc_info:
        resolve_actual(
            reference=ref,
            occ_scope="c.cell",
            formal_name="unresolvable_actual_name",
            usage_qualified_name="Design__c__cell__nonneg",
            registry=registry,
            design_attr_by_qn={},
        )
    assert "unresolvable_actual_name" in str(exc_info.value)


def test_switch_shared_lenient_path_still_synthesizes():
    """Same terminal switch, strict=False -> the calc path's unchanged
    fallback-EP synthesis (byte-identical to pre-extraction behavior)."""
    fallback = terminal_disposition(
        usage_qualified_name="Design__plant__cost_calc",
        param_name="rate",
        source_path="unresolved.rate",
        strict=False,
    )
    assert fallback == "Design__plant__cost_calc__rate"


def test_switch_strict_raises_naming_actual():
    with pytest.raises(CodeGenerationError, match="my_param"):
        terminal_disposition(
            usage_qualified_name="Design__c__cell__nonneg",
            param_name="my_param",
            source_path="my_param",
            strict=True,
        )


def test_polarity_guard_raises_on_none_is_negated():
    with pytest.raises(CodeGenerationError, match="is_negated"):
        guard_polarity(is_negated=None, usage_qualified_name="Design__c__nonneg")


def test_polarity_guard_passes_through_when_present():
    assert guard_polarity(is_negated=False, usage_qualified_name="Design__c__nonneg") is False
