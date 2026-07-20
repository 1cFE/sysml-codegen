"""Contract tests: build_output_registry() key format agreement.

TDD Phase 2: These tests define the key format contract between
build_output_registry() and the backtracker's registry queries.
Written BEFORE build_output_registry() exists. Initially skipped
(ImportError), go green when Phase 3 lands.

Contract: for every binding type, the key the backtracker would
construct for registry_resolve(registry,) must exist in a registry built
from the same data.

See: design.md#component-5-contract-tests
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pytest

from sysml_codegen.core.identifier_types import make_scoped_key
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.core.qualified_names import get_channel_name
from sysml_codegen.extraction.data_models import (
    AggregationExpressionData,
    AttributeInfo,
    CalculationDefinitionData,
    ComputedAttributeClassification,
    ComputedAttributeData,
    ScopedAggregationData,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.extraction.usage_extractor import CalcUsageData

try:
    from sysml_codegen.orchestration.output_registry_builder import build_output_registry

    HAS_BUILD_REGISTRY = True
except ImportError:
    HAS_BUILD_REGISTRY = False

from sysml_codegen.core.models import ChannelAlias
from tests.helpers.registry_compat import registry_resolve

pytestmark = pytest.mark.skipif(
    not HAS_BUILD_REGISTRY,
    reason="build_output_registry not yet implemented (TDD Phase 2)",
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


# ---------------------------------------------------------------------------
# Synthetic data factories
# ---------------------------------------------------------------------------


def _make_attr(name: str) -> AttributeInfo:
    """Minimal output attribute."""
    return AttributeInfo(name=name, is_output=True)


def _make_calc_def(name: str, outputs: list[str]) -> CalculationDefinitionData:
    """Minimal calc def with named outputs."""
    return CalculationDefinitionData(
        name=name,
        qualified_name=f"Lib::{name}",
        doc_comment="",
        calc_expressions=[],
        input_attributes=[],
        output_attributes=[_make_attr(o) for o in outputs],
        references=[],
        source_file=Path("test.sysml"),
    )


def _make_usage(
    instance_name: str,
    qualified_name: str,
    calc_def_name: str,
) -> CalcUsageData:
    """Minimal calc usage."""
    return CalcUsageData(
        instance_name=instance_name,
        calc_def_name=calc_def_name,
        calc_def_qualified_name=f"Lib::{calc_def_name}",
        module_type=f"lib.{calc_def_name}Module",
        qualified_name=qualified_name,
        source_file=Path("test.sysml"),
    )


def _make_aggregation(
    instance_path: str,
    owning_part_qn: str,
    owning_part_name: str,
    attribute_name: str,
    aliases: list[str] | None = None,
) -> ScopedAggregationData:
    """Minimal scoped aggregation."""
    return ScopedAggregationData(
        expression=AggregationExpressionData(
            owning_part_qn=owning_part_qn,
            owning_part_name=owning_part_name,
            attribute_name=attribute_name,
            raw_expression_text="sum()",
            transformed_expression="x * n",
            sum_terms=[],
            singleton_terms=[],
            local_terms=[],
            input_channels=[],
            entry_points=[],
            aliases=aliases or [],
        ),
        instance_path=instance_path,
    )


def _make_computed_attr(
    name: str,
    python_name: str,
    owning_part_name: str,
    owning_part_qualified_name: str,
    classification: ComputedAttributeClassification = ComputedAttributeClassification.FORMULA,
    compilability: Compilability = Compilability.FULLY_COMPILABLE,
) -> ComputedAttributeData:
    """Minimal computed attribute."""
    return ComputedAttributeData(
        name=name,
        python_name=python_name,
        owning_part_name=owning_part_name,
        owning_part_qualified_name=owning_part_qualified_name,
        expression_ast=None,
        expression_text=f"{python_name} = ...",
        references=[],
        classification=classification,
        compilability=compilability,
    )


def _make_design_attr(
    name: str, parent_part: str, default_value: str | None = None
):
    """Minimal design attribute. Inline dataclass to avoid importing DesignAttributeData."""
    from sysml_codegen.analysis.parameter_groups import DesignAttributeData

    return DesignAttributeData(
        name=name,
        sysml_type="Real",
        default_value=default_value,
        unit=None,
        source_file=Path("design.sysml"),
        source_line=1,
        parent_part=parent_part,
    )


# ---------------------------------------------------------------------------
# Synthetic data for tests
# ---------------------------------------------------------------------------


def _build_solar_battery_synthetic():
    """Build synthetic data mimicking solar_battery model structure.

    Returns (calc_usages, calc_defs, aggregation_data, computed_attrs,
             channel_aliases, design_attrs).
    """
    # Concrete CalcUsage: lcoe with 2 outputs
    usage_lcoe = _make_usage(
        instance_name="lcoe",
        qualified_name="SolarBatteryDesign__solar_battery_plant__lcoe",
        calc_def_name="LCOECalc",
    )
    cdef_lcoe = _make_calc_def("LCOECalc", ["lcoe_per_mwh", "npv"])

    # Virtual CalcUsage: cost_model with total_cost output
    usage_cost = _make_usage(
        instance_name="cost_model",
        qualified_name="SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model",
        calc_def_name="CostCalc",
    )
    cdef_cost = _make_calc_def("CostCalc", ["total_cost"])

    # Aggregation: solar_array capital_cost
    # Note: no "total_capex" alias here -- tested separately in TestContractAggregationKeys
    # to avoid collision with CHAIN alias test
    agg = _make_aggregation(
        instance_path="solar_battery_plant__solar_array",
        owning_part_qn="SolarBatteryLibrary__Solar_Array",
        owning_part_name="Solar_Array",
        attribute_name="capital_cost",
    )

    # FORMULA computed attribute: p_net_kw
    formula_attr = _make_computed_attr(
        name="p_net_kw",
        python_name="p_net_kw",
        owning_part_name="solar_battery_plant",
        owning_part_qualified_name="SolarBatteryDesign::solar_battery_plant",
    )

    # CHAIN alias: redefinition that points to cost_model's Key_C
    chain_alias = ChannelAlias(
        alias_name="solar_battery_plant.solar_array.total_capex",
        canonical_name="solar_battery_plant.solar_array.pv_module.cost_model.total_cost",
        owning_part_qn="SolarBatteryLibrary__Solar_Array",
        source="redefinition",
    )

    # Phase 4: transitive design attr
    transitive_attr = _make_design_attr(
        name="total_cost_override",
        parent_part="solar_battery_plant",
        default_value="cost_model.total_cost",
    )
    non_transitive_attr = _make_design_attr(
        name="width",
        parent_part="solar_battery_plant",
        default_value="10.0",
    )

    return (
        [usage_lcoe, usage_cost],
        [cdef_lcoe, cdef_cost],
        [agg],
        [formula_attr],
        [chain_alias],
        {Path("design.sysml"): [transitive_attr, non_transitive_attr]},
    )


def _build_attr_expr_probe_synthetic():
    """Build synthetic data mimicking attr_expr_probe model (Bug 2 case).

    The key scenario: EXPOSE_PURE alias for total_capex needs to resolve
    via scoped key "e2e_plant.total_capex".
    """
    # Virtual CalcUsage: component_cost with total_cost output
    usage_component = _make_usage(
        instance_name="component_cost",
        qualified_name="AttrExprProbeDesign__e2e_plant__component_cost",
        calc_def_name="ComponentCostCalc",
    )
    cdef_component = _make_calc_def("ComponentCostCalc", ["total_cost"])

    # FORMULA computed attribute: power_mw
    formula_power = _make_computed_attr(
        name="power_mw",
        python_name="power_mw",
        owning_part_name="e2e_plant",
        owning_part_qualified_name="AttrExprProbeDesign::e2e_plant",
    )

    # EXPOSE_PURE alias: total_capex -> component_cost's total_cost
    # canonical_name uses Key_A format (instance_name.attr), matching real extraction
    expose_alias = ChannelAlias(
        alias_name="total_capex",
        canonical_name="component_cost.total_cost",
        owning_part_qn="AttrExprProbeDesign__e2e_plant",
        source="expose_pure",
    )

    return (
        [usage_component],
        [cdef_component],
        [],  # no aggregations
        [formula_power],
        [expose_alias],
        {},  # no design attrs
    )


# ===========================================================================
# CONTRACT TESTS: Key format agreement
# ===========================================================================


class TestContractChainBindingKeys:
    """Contract: CHAIN binding source_path (dotted format) resolves via Key_C."""

    @pytest.fixture
    def registry(self):
        usages, defs, aggs, cas, aliases, da = _build_solar_battery_synthetic()
        return build_output_registry(
            calc_usages=usages,
            calc_defs=defs,
            aggregation_data=aggs,
            computed_attributes=cas,
            channel_aliases=aliases,
            design_attributes=da,
        )

    def test_chain_source_path_resolves_via_key_c(self, registry):
        """CHAIN binding source_path in dotted format matches Key_C.

        The backtracker sees source_path like
        "solar_battery_plant.lcoe.lcoe_per_mwh" for CHAIN bindings.
        Key_C is derived from derive_key_c() which produces exactly this format.
        """
        key_c = make_scoped_key(
            "SolarBatteryDesign__solar_battery_plant__lcoe", "lcoe_per_mwh"
        )
        assert key_c == "solar_battery_plant.lcoe.lcoe_per_mwh"
        result = registry_resolve(registry,key_c)
        assert result is not None
        assert result == "SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh"

    def test_chain_alias_resolves_after_phase2(self, registry):
        """Phase 2 CHAIN alias resolves to the canonical channel.

        The alias "solar_battery_plant.solar_array.total_capex" should resolve
        to the cost_model's total_cost canonical channel via Key_C chain.
        """
        result = registry_resolve(registry,
            "solar_battery_plant.solar_array.total_capex"
        )
        assert result is not None
        assert "cost_model__total_cost" in result

    def test_virtual_calcusage_key_c_resolves(self, registry):
        """Virtual CalcUsage Key_C (deep dotted path) resolves."""
        key_c = make_scoped_key(
            "SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model",
            "total_cost",
        )
        assert key_c == "solar_battery_plant.solar_array.pv_module.cost_model.total_cost"
        result = registry_resolve(registry,key_c)
        assert result is not None


class TestContractReferenceSecondaryKeys:
    """Contract: REFERENCE secondary resolution uses parent_part.leaf -> Key_F."""

    @pytest.fixture
    def registry(self):
        usages, defs, aggs, cas, aliases, da = _build_solar_battery_synthetic()
        return build_output_registry(
            calc_usages=usages,
            calc_defs=defs,
            aggregation_data=aggs,
            computed_attributes=cas,
            channel_aliases=aliases,
            design_attributes=da,
        )

    def test_formula_key_f_resolves(self, registry):
        """FORMULA computed attr Key_F ("owning_part.python_name") resolves.

        The backtracker's REFERENCE secondary resolution does:
            parent_part = segments[-2] of usage QN = "solar_battery_plant"
            leaf = last segment of source_path
            -> registry_resolve(registry,"solar_battery_plant.p_net_kw")

        Key_F registered in Phase 1: "solar_battery_plant.p_net_kw"
        """
        result = registry_resolve(registry,"solar_battery_plant.p_net_kw")
        assert result is not None

    def test_formula_bare_name_does_not_resolve(self, registry):
        """Bare FORMULA name is NOT registered in the typed registry.

        The typed registry requires Key_F format ("owning_part.python_name")
        or SysML QN format. Bare names like "p_net_kw" are not registered.
        """
        result = registry_resolve(registry, "p_net_kw")
        assert result is None, (
            "Bare FORMULA name should not resolve; use Key_F 'owning_part.python_name' instead"
        )

    def test_formula_sysml_qn_resolves(self, registry):
        """FORMULA SysML qualified name also registered."""
        result = registry_resolve(registry,
            "SolarBatteryDesign__solar_battery_plant__p_net_kw"
        )
        assert result is not None


class TestContractAggregationKeys:
    """Contract: Aggregation binding keys resolve."""

    @pytest.fixture
    def registry(self):
        """Build registry with aggregation that includes BF-7 aliases."""
        agg = _make_aggregation(
            instance_path="solar_battery_plant__solar_array",
            owning_part_qn="SolarBatteryLibrary__Solar_Array",
            owning_part_name="Solar_Array",
            attribute_name="capital_cost",
            aliases=["total_capex"],
        )
        return build_output_registry(
            calc_usages=[],
            calc_defs=[],
            aggregation_data=[agg],
            computed_attributes=[],
            channel_aliases=[],
            design_attributes={},
        )

    def test_aggregation_key_d_resolves(self, registry):
        """Key_D: "part_usage.attribute_name" resolves."""
        # instance_path = "solar_battery_plant__solar_array"
        # segments[-1] = "solar_array"
        result = registry_resolve(registry,"solar_array.capital_cost")
        assert result is not None

    def test_aggregation_full_design_prefix_does_not_resolve(self, registry):
        """Full design-prefix key does NOT resolve in the typed registry.

        instance_path = "solar_battery_plant__solar_array"
        Key_E_stripped = ".".join(instance_parts[1:] + [attr]) = "solar_array.capital_cost"
        The full-prefix version "solar_battery_plant.solar_array.capital_cost" is NOT registered.
        """
        result = registry_resolve(registry, "solar_battery_plant.solar_array.capital_cost")
        assert result is None, (
            "Full design-prefix key should not resolve; "
            "only Key_E_stripped 'solar_array.capital_cost' is registered"
        )

    def test_aggregation_bare_name_does_not_resolve(self, registry):
        """Bare aggregation attribute name is NOT registered in the typed registry.

        The typed registry requires Key_E_stripped format (dotted path with
        design prefix stripped). Bare names like "capital_cost" are not registered.
        """
        result = registry_resolve(registry, "capital_cost")
        assert result is None, (
            "Bare aggregation name should not resolve; "
            "use Key_E_stripped 'solar_array.capital_cost' instead"
        )

    def test_aggregation_alias_variant_resolves(self, registry):
        """BF-7 alias variant from expression.aliases resolves."""
        # "total_capex" is in expression.aliases
        result = registry_resolve(registry,"solar_array.total_capex")
        assert result is not None

    def test_aggregation_alias_bare_does_not_resolve(self, registry):
        """Bare BF-7 alias name is NOT registered in the typed registry.

        The typed registry registers BF-7 aliases in Key_E_stripped format
        (e.g., "solar_array.total_capex"). Bare alias names like "total_capex"
        are not registered.
        """
        result = registry_resolve(registry, "total_capex")
        assert result is None, (
            "Bare BF-7 alias should not resolve; "
            "use Key_E_stripped 'solar_array.total_capex' instead"
        )


class TestContractCalcUsageKeys:
    """Contract: CalcUsage output keys resolve."""

    @pytest.fixture
    def registry(self):
        usages, defs, aggs, cas, aliases, da = _build_solar_battery_synthetic()
        return build_output_registry(
            calc_usages=usages,
            calc_defs=defs,
            aggregation_data=aggs,
            computed_attributes=cas,
            channel_aliases=aliases,
            design_attributes=da,
        )

    def test_key_a_instance_dot_output(self, registry):
        """Key_A: "instance_name.output" resolves."""
        result = registry_resolve(registry,"lcoe.lcoe_per_mwh")
        assert result is not None
        assert result == "SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh"

    def test_key_b_eqn_channel_name(self, registry):
        """Key_B: EQN channel name resolves (self-registration)."""
        canonical = get_channel_name(
            "SolarBatteryDesign__solar_battery_plant__lcoe", "lcoe_per_mwh"
        )
        result = registry_resolve(registry,canonical)
        assert result == canonical

    def test_key_c_dotted_hierarchy(self, registry):
        """Key_C: dotted hierarchy resolves."""
        key_c = make_scoped_key(
            "SolarBatteryDesign__solar_battery_plant__lcoe", "npv"
        )
        result = registry_resolve(registry,key_c)
        assert result == "SolarBatteryDesign__solar_battery_plant__lcoe__npv"


class TestContractExposePureKeys:
    """Contract: EXPOSE_PURE scoped key resolves (Bug 2 fix proof)."""

    @pytest.fixture
    def registry(self):
        usages, defs, aggs, cas, aliases, da = _build_attr_expr_probe_synthetic()
        return build_output_registry(
            calc_usages=usages,
            calc_defs=defs,
            aggregation_data=aggs,
            computed_attributes=cas,
            channel_aliases=aliases,
            design_attributes=da,
        )

    def test_expose_pure_scoped_key_resolves(self, registry):
        """Bug 2: EXPOSE_PURE "e2e_plant.total_capex" resolves to MODULE_OUTPUT.

        Phase 3 registration scopes the alias:
            owning_part_short = "e2e_plant" (from owning_part_qn.split("__")[-1])
            scoped_key = "e2e_plant.total_capex"

        The backtracker's REFERENCE secondary resolution would try:
            parent_part.leaf -> "e2e_plant.total_capex"
        """
        result = registry_resolve(registry,"e2e_plant.total_capex")
        assert result is not None
        assert "component_cost__total_cost" in result


class TestPhase3DualFormatOwningPartQn:
    """Phase 3: :: vs __ owning_part_qn produce identical scoped keys."""

    def test_coloncolon_format_produces_correct_scoped_key(self):
        """owning_part_qn with '::' separator extracts correct short name."""
        usage = _make_usage("my_calc", "TopDesign__my_part__my_calc", "MyCalcDef")
        cdef = _make_calc_def("MyCalcDef", ["result"])
        alias = ChannelAlias(
            alias_name="my_alias",
            canonical_name="my_part.my_calc.result",  # Key_C from Phase 1
            owning_part_qn="TopDesign::my_part",  # :: format
            source="expose_pure",
        )
        registry = build_output_registry([usage], [cdef], [], [], [alias], {})
        assert registry_resolve(registry,"my_part.my_alias") is not None

    def test_dunder_format_produces_correct_scoped_key(self):
        """owning_part_qn with '__' separator extracts correct short name."""
        usage = _make_usage("my_calc", "TopDesign__my_part__my_calc", "MyCalcDef")
        cdef = _make_calc_def("MyCalcDef", ["result"])
        alias = ChannelAlias(
            alias_name="my_alias",
            canonical_name="my_part.my_calc.result",  # Key_C from Phase 1
            owning_part_qn="TopDesign__my_part",  # __ format
            source="expose_pure",
        )
        registry = build_output_registry([usage], [cdef], [], [], [alias], {})
        assert registry_resolve(registry,"my_part.my_alias") is not None

    def test_both_formats_resolve_to_same_channel(self):
        """Both :: and __ formats resolve to the same canonical channel."""
        usage = _make_usage("my_calc", "TopDesign__my_part__my_calc", "MyCalcDef")
        cdef = _make_calc_def("MyCalcDef", ["result"])
        alias_cc = ChannelAlias(
            alias_name="alias_cc",
            canonical_name="my_part.my_calc.result",
            owning_part_qn="TopDesign::my_part",  # ::
            source="expose_pure",
        )
        alias_du = ChannelAlias(
            alias_name="alias_du",
            canonical_name="my_part.my_calc.result",
            owning_part_qn="TopDesign__my_part",  # __
            source="expose_pure",
        )
        registry = build_output_registry(
            [usage], [cdef], [], [], [alias_cc, alias_du], {}
        )
        r1 = registry_resolve(registry,"my_part.alias_cc")
        r2 = registry_resolve(registry,"my_part.alias_du")
        assert r1 is not None
        assert r1 == r2


class TestContractTransitiveDesignAttrs:
    """Contract: Phase 4 transitive design attr aliases resolve."""

    @pytest.fixture
    def registry(self):
        usages, defs, aggs, cas, aliases, da = _build_solar_battery_synthetic()
        return build_output_registry(
            calc_usages=usages,
            calc_defs=defs,
            aggregation_data=aggs,
            computed_attributes=cas,
            channel_aliases=aliases,
            design_attributes=da,
        )

    def test_transitive_default_resolves(self, registry):
        """Phase 4: "parent_part.attr" with transitive default resolves.

        default_value="cost_model.total_cost" is a dotted path that resolves
        in the registry (via Key_A from Phase 1). Phase 4 registers
        "solar_battery_plant.total_cost_override" as an alias.
        """
        result = registry_resolve(registry,"solar_battery_plant.total_cost_override")
        assert result is not None

    def test_non_transitive_not_registered(self, registry):
        """Non-transitive (numeric) default NOT registered as alias."""
        result = registry_resolve(registry,"solar_battery_plant.width")
        # width has default_value="10.0" (numeric) -- should NOT be an alias
        assert result is None


# ===========================================================================
# PER-PHASE REGISTRATION VERIFICATION
# ===========================================================================


class TestBuildOutputRegistryPhases:
    """Verify that specific phases register specific keys."""

    def test_phase1_registers_canonical_and_lookup_keys(self):
        """Phase 1 only: CalcUsage, aggregation, and FORMULA keys registered."""
        usages, defs, aggs, cas, _aliases, _da = _build_solar_battery_synthetic()
        # Phase 1 only: no channel_aliases, no design_attributes
        registry = build_output_registry(usages, defs, aggs, cas, [], {})

        # CalcUsage Key_A
        assert registry_resolve(registry,"lcoe.lcoe_per_mwh") is not None
        # CalcUsage Key_C
        assert registry_resolve(registry,"solar_battery_plant.lcoe.lcoe_per_mwh") is not None
        # Aggregation Key_D
        assert registry_resolve(registry,"solar_array.capital_cost") is not None
        # FORMULA Key_F
        assert registry_resolve(registry,"solar_battery_plant.p_net_kw") is not None

        # Phase 2 CHAIN alias NOT present yet
        assert registry_resolve(registry,"solar_battery_plant.solar_array.total_capex") is None
        # Phase 4 transitive alias NOT present yet
        assert registry_resolve(registry,"solar_battery_plant.total_cost_override") is None

    def test_phase2_adds_chain_alias(self):
        """Phase 2 adds CHAIN aliases that Phase 1 alone does not have."""
        usages, defs, aggs, cas, aliases, _da = _build_solar_battery_synthetic()
        r1 = build_output_registry(usages, defs, aggs, cas, [], {})
        r2 = build_output_registry(usages, defs, aggs, cas, aliases, {})

        # Phase 2 key now present
        assert registry_resolve(r2,"solar_battery_plant.solar_array.total_capex") is not None
        # Registry grew by exactly 1 (the CHAIN alias)
        assert len(r2) == len(r1) + 1

    def test_phase3_adds_expose_pure_alias(self):
        """Phase 3 adds EXPOSE_PURE aliases with scoped keys."""
        usages, defs, aggs, cas, aliases, da = _build_attr_expr_probe_synthetic()
        r_no_alias = build_output_registry(usages, defs, aggs, cas, [], da)
        r_with_alias = build_output_registry(usages, defs, aggs, cas, aliases, da)

        assert registry_resolve(r_no_alias,"e2e_plant.total_capex") is None
        assert registry_resolve(r_with_alias,"e2e_plant.total_capex") is not None

    def test_phase4_adds_transitive_alias(self):
        """Phase 4 adds transitive design attr aliases."""
        usages, defs, aggs, cas, aliases, _da = _build_solar_battery_synthetic()
        _, _, _, _, _, da = _build_solar_battery_synthetic()
        r_no_da = build_output_registry(usages, defs, aggs, cas, aliases, {})
        r_full = build_output_registry(usages, defs, aggs, cas, aliases, da)

        assert registry_resolve(r_no_da,"solar_battery_plant.total_cost_override") is None
        assert registry_resolve(r_full,"solar_battery_plant.total_cost_override") is not None
        # Phase 4 adds exactly 1 alias (only total_cost_override is transitive)
        assert len(r_full) == len(r_no_da) + 1

    def test_real_solar_battery_chain_alias_count(self):
        """Real solar_battery: exact CHAIN alias count matches spec (41)."""
        from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

        model_path = FIXTURES_DIR / "solar_battery_model"
        ctx = build_pipeline_context([model_path])
        chain_aliases = [
            a for a in ctx.channel_aliases if a.source == "redefinition"
        ]
        assert len(chain_aliases) == 41, (
            f"Expected 41 CHAIN aliases, got {len(chain_aliases)}"
        )


# ===========================================================================
# INTEGRATION CONTRACT TESTS: Real model data
# ===========================================================================


class TestContractRealSolarBattery:
    """Contract tests with real solar_battery model data."""

    @pytest.fixture(scope="class")
    def pipeline_context(self):
        from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

        model_path = FIXTURES_DIR / "solar_battery_model"
        return build_pipeline_context([model_path])

    @pytest.fixture(scope="class")
    def registry(self, pipeline_context):
        ctx = pipeline_context
        return build_output_registry(
            calc_usages=ctx.calc_usages,
            calc_defs=ctx.calc_defs,
            aggregation_data=ctx.aggregation_expressions,
            computed_attributes=ctx.computed_attributes,
            channel_aliases=ctx.channel_aliases,
            design_attributes=ctx.design_attributes,
        )

    def test_registry_has_entries(self, registry):
        assert len(registry) > 0

    def test_known_chain_key_c_resolves(self, registry):
        """Known CHAIN source_path (Key_C format) resolves."""
        # lcoe.lcoe_per_mwh Key_A should resolve
        assert registry_resolve(registry,"lcoe.lcoe_per_mwh") is not None

    def test_reference_secondary_p_net_kw(self, registry):
        """REFERENCE secondary: solar_battery_plant.p_net_kw resolves.

        p_net_kw is a FORMULA computed attr on solar_battery_plant.
        """
        result = registry_resolve(registry,"solar_battery_plant.p_net_kw")
        assert result is not None, (
            "p_net_kw should resolve as a FORMULA computed attr on solar_battery_plant"
        )

    def test_reference_secondary_capital_cost(self, registry):
        """REFERENCE secondary: solar_battery_plant.solar_array.capital_cost resolves.

        capital_cost is an aggregation output on solar_array. In the real model,
        Key_E_stripped = ".".join(instance_parts[1:] + [attr]) which includes
        the full design-prefix-stripped path.
        """
        result = registry_resolve(registry, "solar_battery_plant.solar_array.capital_cost")
        assert result is not None

    def test_chain_alias_count_matches_spec(self, registry, pipeline_context):
        """Spec: 41 CHAIN aliases on solar_battery."""
        chain_aliases = [
            a for a in pipeline_context.channel_aliases
            if a.source == "redefinition"
        ]
        assert len(chain_aliases) == 41, (
            f"Expected 41 CHAIN aliases, got {len(chain_aliases)}"
        )


class TestContractRealAttrExprProbe:
    """Contract tests with real attr_expr_probe model data (Bug 2)."""

    @pytest.fixture(scope="class")
    def pipeline_context(self):
        from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

        model_path = FIXTURES_DIR / "attr_expr_probe"
        return build_pipeline_context([model_path])

    @pytest.fixture(scope="class")
    def registry(self, pipeline_context):
        ctx = pipeline_context
        return build_output_registry(
            calc_usages=ctx.calc_usages,
            calc_defs=ctx.calc_defs,
            aggregation_data=ctx.aggregation_expressions,
            computed_attributes=ctx.computed_attributes,
            channel_aliases=ctx.channel_aliases,
            design_attributes=ctx.design_attributes,
        )

    def test_registry_has_entries(self, registry):
        assert len(registry) > 0

    def test_expose_pure_scoped_key_resolves(self, registry):
        """EXPOSE_PURE alias with scoped key resolves via Phase 3.

        The attr_expr_probe model has EXPOSE_PURE aliases like scale_result
        on probe_design. Phase 3 scopes them as "probe_design.scale_result".
        """
        result = registry_resolve(registry,"probe_design.scale_result")
        assert result is not None, (
            "'probe_design.scale_result' should resolve via EXPOSE_PURE "
            "Phase 3 registration"
        )
        assert "scale_calc__result" in result


# ===========================================================================
# PHASE 4: Unit tests for backtracker integration methods
# ===========================================================================


from agentic_mbse.sysml.types import BindingInfo, BindingType

from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
from sysml_codegen.core.models import BindingResolution, BindingResolutionType


def _make_binding(
    param_name: str,
    source_path: str | None,
    binding_type: BindingType = BindingType.CHAIN,
) -> BindingInfo:
    """Minimal BindingInfo for testing."""
    return BindingInfo(
        param_name=param_name,
        source_path=source_path,
        binding_type=binding_type,
    )


class TestGetParentPartForUsage:
    """Tests for _get_parent_part_for_usage()."""

    def _make_bt(self):
        """Minimal backtracker (no usages/defs needed for this helper)."""
        return DependencyBacktracker([], [], output_registry=OutputRegistry())

    def test_normal_three_segments(self):
        """'Design__solar_battery_plant__lcoe' -> 'solar_battery_plant'."""
        bt = self._make_bt()
        usage = _make_usage("lcoe", "Design__solar_battery_plant__lcoe", "LCOECalc")
        assert bt._get_parent_part_for_usage(usage) == "solar_battery_plant"

    def test_two_segments(self):
        """'Design__lcoe' -> 'Design'."""
        bt = self._make_bt()
        usage = _make_usage("lcoe", "Design__lcoe", "LCOECalc")
        assert bt._get_parent_part_for_usage(usage) == "Design"

    def test_single_segment_returns_none(self):
        """'lcoe' (no __ separator) -> None."""
        bt = self._make_bt()
        usage = _make_usage("lcoe", "lcoe", "LCOECalc")
        assert bt._get_parent_part_for_usage(usage) is None

    def test_deep_hierarchy(self):
        """'A__B__C__D__lcoe' -> 'D' (always segments[-2])."""
        bt = self._make_bt()
        usage = _make_usage("lcoe", "A__B__C__D__lcoe", "LCOECalc")
        assert bt._get_parent_part_for_usage(usage) == "D"


def _leaf_channel(bt, source_path, usage):
    """Rows 14 and 15 — leaf recombined with the consumer's parent scope, then its full
    scope — are where `_resolve_reference_via_registry`'s behavior now lives (SR-R43)."""
    from sysml_codegen.resolution.producer_resolution import (
        Outcome,
        ProducerRequest,
        TerminalPolicy,
        resolve_producer,
    )

    resolution = resolve_producer(
        ProducerRequest(
            consumer_eqn=usage.qualified_name,
            reference=source_path,
            param_name="probe",
            consumer_scope=bt._consumer_scope_dotted(usage),
            parent_scope=bt._get_parent_part_for_usage(usage),
            policy=TerminalPolicy.LENIENT,
            diagnostic_context="leaf probe",
        ),
        bt._producer_context(),
    )
    return resolution.identity if resolution.outcome is Outcome.MODULE_OUTPUT else None


class TestResolveReferenceViaRegistry:
    """Tests for _resolve_reference_via_registry()."""

    def _make_bt_with_registry(self, registry):
        bt = DependencyBacktracker([], [], output_registry=registry)
        return bt

    def test_sysml_qn_extracts_leaf(self):
        """Source path 'Package::Part::attr' extracts leaf 'attr'."""
        usages, defs, aggs, cas, aliases, da = _build_solar_battery_synthetic()
        registry = build_output_registry(
            calc_usages=usages, calc_defs=defs,
            aggregation_data=aggs, computed_attributes=cas,
            channel_aliases=aliases, design_attributes=da,
        )
        bt = self._make_bt_with_registry(registry)
        usage = _make_usage(
            "lcoe", "Design__solar_battery_plant__lcoe", "LCOECalc"
        )
        # p_net_kw is registered as Key_F: "solar_battery_plant.p_net_kw"
        # parent_part = "solar_battery_plant", leaf = "p_net_kw"
        result = _leaf_channel(bt, "SolarBatteryDesign::solar_battery_plant::p_net_kw", usage
        )
        assert result is not None
        assert "p_net_kw" in result

    def test_dotted_path_extracts_leaf(self):
        """Source path 'part.attr' extracts leaf 'attr'."""
        usages, defs, aggs, cas, aliases, da = _build_solar_battery_synthetic()
        registry = build_output_registry(
            calc_usages=usages, calc_defs=defs,
            aggregation_data=aggs, computed_attributes=cas,
            channel_aliases=aliases, design_attributes=da,
        )
        bt = self._make_bt_with_registry(registry)
        usage = _make_usage(
            "lcoe", "Design__solar_battery_plant__lcoe", "LCOECalc"
        )
        result = _leaf_channel(bt, "some_other_part.p_net_kw", usage
        )
        assert result is not None

    def test_no_parent_part_returns_none(self):
        """Usage with single-segment QN -> no parent part -> None."""
        usages, defs, aggs, cas, aliases, da = _build_solar_battery_synthetic()
        registry = build_output_registry(
            calc_usages=usages, calc_defs=defs,
            aggregation_data=aggs, computed_attributes=cas,
            channel_aliases=aliases, design_attributes=da,
        )
        bt = self._make_bt_with_registry(registry)
        usage = _make_usage("lcoe", "lcoe", "LCOECalc")  # single segment
        result = _leaf_channel(bt, "p_net_kw", usage)
        assert result is None

    def test_self_reference_returns_none(self):
        """If resolved channel's producing usage == current usage, return None."""
        # Create a formula attr whose channel starts with the same usage QN
        ca = _make_computed_attr(
            name="output",
            python_name="output",
            owning_part_name="my_part",
            owning_part_qualified_name="Design::my_part",
        )
        registry = build_output_registry(
            calc_usages=[], calc_defs=[],
            aggregation_data=[], computed_attributes=[ca],
            channel_aliases=[], design_attributes={},
        )
        bt = self._make_bt_with_registry(registry)
        # The formula channel will be "Design__my_part__output__output"
        # producing_usage_qn = "Design__my_part__output"
        usage = _make_usage(
            "output", "Design__my_part__output", "OutputCalc"
        )
        result = _leaf_channel(bt, "Design::my_part::output", usage
        )
        assert result is None


class TestResolveBindingViaRegistry:
    """Tests for _resolve_binding_via_registry()."""

    def _make_bt_with_registry(self, registry):
        return DependencyBacktracker([], [], output_registry=registry)

    def test_chain_binding_resolves_to_module_output(self):
        """CHAIN binding with matching registry entry -> MODULE_OUTPUT."""
        usages, defs, aggs, cas, aliases, da = _build_solar_battery_synthetic()
        registry = build_output_registry(
            calc_usages=usages, calc_defs=defs,
            aggregation_data=aggs, computed_attributes=cas,
            channel_aliases=aliases, design_attributes=da,
        )
        bt = self._make_bt_with_registry(registry)
        usage = _make_usage(
            "consumer", "Design__solar_battery_plant__consumer", "ConsumerCalc"
        )
        # Key_A: "lcoe.lcoe_per_mwh" is registered in Phase 1
        binding = _make_binding(
            "input_cost", "lcoe.lcoe_per_mwh", BindingType.CHAIN
        )
        result = bt._resolve_binding_via_registry(binding, usage)
        assert result.resolution_type == BindingResolutionType.MODULE_OUTPUT
        assert "lcoe__lcoe_per_mwh" in result.qualified_name

    def test_self_reference_guard(self):
        """Self-referencing binding -> falls through to ENTRY_POINT."""
        usages, defs, aggs, cas, aliases, da = _build_solar_battery_synthetic()
        registry = build_output_registry(
            calc_usages=usages, calc_defs=defs,
            aggregation_data=aggs, computed_attributes=cas,
            channel_aliases=aliases, design_attributes=da,
        )
        bt = self._make_bt_with_registry(registry)
        # Usage is the lcoe calc itself
        usage = usages[0]  # lcoe
        # Binding source resolves to lcoe's own output
        binding = _make_binding(
            "self_input", "lcoe.lcoe_per_mwh", BindingType.CHAIN
        )
        result = bt._resolve_binding_via_registry(binding, usage)
        # Self-reference guard should catch this -> ENTRY_POINT
        assert result.resolution_type == BindingResolutionType.ENTRY_POINT

    def test_reference_secondary_resolves(self):
        """REFERENCE binding uses parent_part.leaf for secondary resolution."""
        usages, defs, aggs, cas, aliases, da = _build_solar_battery_synthetic()
        registry = build_output_registry(
            calc_usages=usages, calc_defs=defs,
            aggregation_data=aggs, computed_attributes=cas,
            channel_aliases=aliases, design_attributes=da,
        )
        bt = self._make_bt_with_registry(registry)
        usage = _make_usage(
            "consumer", "Design__solar_battery_plant__consumer", "ConsumerCalc"
        )
        # REFERENCE binding to SysML QN - secondary resolution uses parent_part.leaf
        binding = _make_binding(
            "power_input",
            "SolarBatteryDesign::solar_battery_plant::p_net_kw",
            BindingType.REFERENCE,
        )
        result = bt._resolve_binding_via_registry(binding, usage)
        assert result.resolution_type == BindingResolutionType.MODULE_OUTPUT
        assert "p_net_kw" in result.qualified_name

    def test_unresolved_binding_produces_entry_point(self):
        """Binding that doesn't resolve -> ENTRY_POINT with warning."""
        registry = build_output_registry(
            calc_usages=[], calc_defs=[],
            aggregation_data=[], computed_attributes=[],
            channel_aliases=[], design_attributes={},
        )
        bt = self._make_bt_with_registry(registry)
        usage = _make_usage("consumer", "Design__consumer", "ConsumerCalc")
        binding = _make_binding(
            "missing_param", "nonexistent.source", BindingType.CHAIN
        )
        result = bt._resolve_binding_via_registry(binding, usage)
        assert result.resolution_type == BindingResolutionType.ENTRY_POINT
        assert "missing_param" in result.qualified_name

    def test_unresolved_binding_is_visible_at_warning(self, caplog):
        """Every lenient terminal miss is visible (Item 2 / I7).

        Recorded behavior change: this line was DEBUG, and every other lenient miss
        except the multi-hop-chain shape was too, so a binding that quietly became an
        entry point left no trace a build log would show. Item 2 owes uniform
        visibility; the severity vocabulary is Item 4's.
        """
        import logging

        registry = build_output_registry(
            calc_usages=[], calc_defs=[],
            aggregation_data=[], computed_attributes=[],
            channel_aliases=[], design_attributes={},
        )
        bt = self._make_bt_with_registry(registry)
        usage = _make_usage("consumer", "Design__consumer", "ConsumerCalc")
        binding = _make_binding(
            "missing_param", "nonexistent.source", BindingType.CHAIN
        )
        with caplog.at_level(logging.DEBUG):
            bt._resolve_binding_via_registry(binding, usage)
        unresolved = [r for r in caplog.records if "Unresolved producer" in r.message]
        assert unresolved, "expected a visible unresolved-producer line"
        assert all(r.levelno == logging.WARNING for r in unresolved), (
            "a lenient terminal miss must be visible in a build log (I7)"
        )

    def test_expose_pure_resolves_via_reference_secondary(self):
        """Bug 2: EXPOSE_PURE total_capex resolves via REFERENCE secondary."""
        usages, defs, aggs, cas, aliases, da = _build_attr_expr_probe_synthetic()
        registry = build_output_registry(
            calc_usages=usages, calc_defs=defs,
            aggregation_data=aggs, computed_attributes=cas,
            channel_aliases=aliases, design_attributes=da,
        )
        bt = self._make_bt_with_registry(registry)
        # Consumer in the e2e_plant scope
        usage = _make_usage(
            "financial", "AttrExprProbeDesign__e2e_plant__financial", "FinancialCalc"
        )
        # REFERENCE binding to total_capex (EXPOSE_PURE alias)
        binding = _make_binding(
            "total_capex",
            "AttrExprProbeDesign::e2e_plant::total_capex",
            BindingType.REFERENCE,
        )
        result = bt._resolve_binding_via_registry(binding, usage)
        assert result.resolution_type == BindingResolutionType.MODULE_OUTPUT
        assert "component_cost__total_cost" in result.qualified_name

    def test_design_attr_fallback_resolves_to_entry_point(self):
        """Step 3: registry miss falls back to design attribute -> ENTRY_POINT."""
        from sysml_codegen.analysis.parameter_groups import DesignAttributeData

        da = DesignAttributeData(
            name="efficiency",
            sysml_type="Real",
            default_value="0.85",  # non-transitive (numeric)
            unit=None,
            source_file=Path("design.sysml"),
            source_line=10,
            parent_part="solar_panel",
            qualified_name="Design__solar_panel__efficiency",
        )
        # Empty registry so Steps 1 and 2 return None
        registry = OutputRegistry()
        bt = DependencyBacktracker(
            [], [],
            design_attributes={Path("design.sysml"): [da]},
            output_registry=registry,
        )
        usage = _make_usage(
            "consumer", "Design__solar_panel__consumer", "ConsumerCalc"
        )
        binding = _make_binding(
            "eff_input", "solar_panel.efficiency", BindingType.CHAIN
        )
        result = bt._resolve_binding_via_registry(binding, usage)
        assert result.resolution_type == BindingResolutionType.ENTRY_POINT
        assert "efficiency" in result.qualified_name


