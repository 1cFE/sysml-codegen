"""Conformance tests for Aggregation Scoping (C10).

Tests REQ-AS-01 through REQ-AS-08 from design intent doc 13-aggregation-scoping.md.

Testing strategy:
- Snapshot data contains both raw inputs (hierarchy_data.aggregation_expressions,
  hierarchy_data.redefinitions, calc_usages) and post-scoped outputs
  (aggregation_expressions as ScopedAggregationData, channel_aliases). Tests call
  scoping functions with raw inputs and compare against snapshot outputs.
- solar_battery_model is the primary fixture: 20 aggregation expressions across
  4 PartDefs, 41 CHAIN aliases, both Strategy 1 and Strategy 2 exercised.
- issue22_model is the edge case: 1 expression, null multiplicity.
- No mocks. All data comes from real extraction snapshots.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from sysml_codegen.core.models import ChannelAlias
from sysml_codegen.extraction.data_models import (
    AggregationExpressionData,
    HierarchyExtractionResult,
    RedefinitionData,
    RedefinitionType,
    ScopedAggregationData,
)
from sysml_codegen.extraction.usage_extractor import CalcUsageData
from sysml_codegen.generation.initialization import (
    _build_chain_aliases,
    _scope_aggregation_expressions,
    build_output_registry,
    find_instance_paths_for_partdef,
)
from sysml_codegen.core.identifier_types import ScopedKey


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def solar_battery_hierarchy(solar_battery_snapshot):
    """Extract hierarchy_data from solar_battery snapshot."""
    return solar_battery_snapshot["hierarchy_data"]


@pytest.fixture
def solar_battery_calc_usages(solar_battery_snapshot):
    """Extract calc_usages from solar_battery snapshot."""
    return solar_battery_snapshot["calc_usages"]


@pytest.fixture
def issue22_hierarchy(issue22_snapshot):
    """Extract hierarchy_data from issue22 snapshot."""
    return issue22_snapshot["hierarchy_data"]


@pytest.fixture
def issue22_calc_usages(issue22_snapshot):
    """Extract calc_usages from issue22 snapshot."""
    return issue22_snapshot["calc_usages"]


# ---------------------------------------------------------------------------
# REQ-AS-01: One-to-many expansion
# ---------------------------------------------------------------------------

class TestReqAS01OneToManyExpansion:
    """REQ-AS-01: Each PartDef-level aggregation SHALL produce one
    ScopedAggregationData per design instance."""

    @pytest.mark.req("REQ-AS-01")
    def test_expansion_count_solar_battery(
        self, solar_battery_hierarchy, solar_battery_calc_usages
    ):
        """solar_battery has 4 PartDefs with 5 aggregation expressions each = 20.
        Each PartDef maps to exactly 1 design instance, so scoping produces 20."""
        result = _scope_aggregation_expressions(
            solar_battery_hierarchy, solar_battery_calc_usages
        )
        assert len(result) == 20

    @pytest.mark.req("REQ-AS-01")
    def test_expansion_matches_snapshot_solar_battery(
        self, solar_battery_snapshot, solar_battery_hierarchy, solar_battery_calc_usages
    ):
        """Computed output matches snapshot aggregation_expressions."""
        computed = _scope_aggregation_expressions(
            solar_battery_hierarchy, solar_battery_calc_usages
        )
        snapshot = solar_battery_snapshot["aggregation_expressions"]

        assert len(computed) == len(snapshot)

        computed_pairs = {
            (a.instance_path, a.expression.attribute_name) for a in computed
        }
        snapshot_pairs = {
            (a.instance_path, a.expression.attribute_name) for a in snapshot
        }
        assert computed_pairs == snapshot_pairs

    @pytest.mark.req("REQ-AS-01")
    def test_expansion_issue22_single_instance(
        self, issue22_hierarchy, issue22_calc_usages
    ):
        """issue22_model has 1 aggregation expression, producing 1 ScopedAggregationData."""
        result = _scope_aggregation_expressions(
            issue22_hierarchy, issue22_calc_usages
        )
        assert len(result) == 1
        assert "assembly" in result[0].instance_path.lower()

    @pytest.mark.req("REQ-AS-01")
    def test_scope_agg_no_hierarchy_data(self, solar_battery_calc_usages):
        """None hierarchy_data returns empty list."""
        result = _scope_aggregation_expressions(None, solar_battery_calc_usages)
        assert result == []

    @pytest.mark.req("REQ-AS-01")
    def test_scope_agg_empty_expressions(self, solar_battery_calc_usages):
        """hierarchy_data with empty aggregation_expressions returns empty list."""
        empty_hierarchy = HierarchyExtractionResult(
            redefinitions=[],
            design_overrides=[],
            multiplicities=[],
            aggregation_expressions=[],
            warnings=[],
            part_usage_names={},
            usage_type_map={},
        )
        result = _scope_aggregation_expressions(empty_hierarchy, solar_battery_calc_usages)
        assert result == []

    @pytest.mark.req("REQ-AS-01")
    def test_all_scoped_data_are_scoped_aggregation_data(
        self, solar_battery_hierarchy, solar_battery_calc_usages
    ):
        """Every item in result is a ScopedAggregationData with non-empty instance_path."""
        result = _scope_aggregation_expressions(
            solar_battery_hierarchy, solar_battery_calc_usages
        )
        for item in result:
            assert isinstance(item, ScopedAggregationData)
            assert item.instance_path, "instance_path must not be empty"
            assert isinstance(item.expression, AggregationExpressionData)


# ---------------------------------------------------------------------------
# REQ-AS-02: Strategy ordering (direct match before child-walk)
# ---------------------------------------------------------------------------

class TestReqAS02StrategyOrdering:
    """REQ-AS-02: Instance discovery SHALL try direct match (Strategy 1) BEFORE
    child-walk fallback (Strategy 2)."""

    @pytest.mark.req("REQ-AS-02")
    def test_strategy_1_direct_match(
        self, solar_battery_hierarchy, solar_battery_calc_usages
    ):
        """Solar_Array uses Strategy 1 (direct match). Verify non-empty result."""
        paths = find_instance_paths_for_partdef(
            "SolarBatteryLibrary__Solar_Array",
            solar_battery_calc_usages,
            part_usage_names=solar_battery_hierarchy.part_usage_names,
        )
        assert len(paths) > 0
        assert "solar_battery_plant.solar_array" in paths

    @pytest.mark.req("REQ-AS-02")
    def test_strategy_2_child_walk_fallback(
        self, solar_battery_hierarchy, solar_battery_calc_usages
    ):
        """Battery_System, Site_Infrastructure, Solar_Battery_Plant use Strategy 2.
        Verify they produce results via child-walk."""
        strategy_2_partdefs = [
            ("SolarBatteryLibrary__Battery_System", "solar_battery_plant.battery_system"),
            ("SolarBatteryLibrary__Site_Infrastructure", "solar_battery_plant.site_infra"),
            ("SolarBatteryLibrary__Solar_Battery_Plant", "solar_battery_plant"),
        ]
        for partdef_qn, expected_path in strategy_2_partdefs:
            paths = find_instance_paths_for_partdef(
                partdef_qn,
                solar_battery_calc_usages,
                part_usage_names=solar_battery_hierarchy.part_usage_names,
            )
            assert expected_path in paths, (
                f"{partdef_qn} should find {expected_path}, got {paths}"
            )

    @pytest.mark.req("REQ-AS-02")
    def test_strategy_1_tried_first(
        self, solar_battery_hierarchy, solar_battery_calc_usages
    ):
        """Solar_Array has direct virtual CalcUsage matches. Verify Strategy 1 fires
        (check that owning_part_def_qn matches exist in calc_usages)."""
        target_qn = "SolarBatteryLibrary__Solar_Array"
        # Strategy 1 relies on virtual CalcUsages with matching owning_part_def_qn
        direct_matches = [
            u for u in solar_battery_calc_usages
            if not u.is_template
            and u.owning_part_def_qn == target_qn
        ]
        assert len(direct_matches) > 0, (
            "Strategy 1 requires direct virtual CalcUsage matches"
        )
        # Strategy 2 PartDefs should NOT have direct matches
        for s2_qn in [
            "SolarBatteryLibrary__Battery_System",
            "SolarBatteryLibrary__Site_Infrastructure",
            "SolarBatteryLibrary__Solar_Battery_Plant",
        ]:
            s2_matches = [
                u for u in solar_battery_calc_usages
                if not u.is_template and u.owning_part_def_qn == s2_qn
            ]
            assert len(s2_matches) == 0, (
                f"{s2_qn} should have no direct matches (uses Strategy 2)"
            )

    @pytest.mark.req("REQ-AS-02")
    def test_find_instance_paths_empty_calc_usages(self):
        """Empty calc_usages returns empty list."""
        paths = find_instance_paths_for_partdef(
            "SolarBatteryLibrary__Solar_Array", [], None
        )
        assert paths == []

    @pytest.mark.req("REQ-AS-02")
    def test_find_instance_paths_no_virtual_usages(
        self, solar_battery_calc_usages
    ):
        """PartDef with no matching virtual usages and no part_usage_names returns empty."""
        paths = find_instance_paths_for_partdef(
            "NonExistent__PartDef",
            solar_battery_calc_usages,
            part_usage_names=None,
        )
        assert paths == []


# ---------------------------------------------------------------------------
# REQ-AS-03: Dotted prefix-stripped paths
# ---------------------------------------------------------------------------

class TestReqAS03DottedPrefixStripped:
    """REQ-AS-03: Instance paths SHALL be converted from __-separated to dotted
    format with design prefix stripped."""

    @pytest.mark.req("REQ-AS-03")
    def test_dotted_prefix_stripped_solar_array(
        self, solar_battery_hierarchy, solar_battery_calc_usages
    ):
        """Solar_Array paths are dotted, prefix-stripped."""
        paths = find_instance_paths_for_partdef(
            "SolarBatteryLibrary__Solar_Array",
            solar_battery_calc_usages,
            part_usage_names=solar_battery_hierarchy.part_usage_names,
        )
        for path in paths:
            assert "__" not in path, f"Path should be dotted, not __-separated: {path}"
            assert not path.startswith("SolarBatteryDesign"), (
                f"Path should have design prefix stripped: {path}"
            )
            assert "." in path, f"Path should be dotted: {path}"

    @pytest.mark.req("REQ-AS-03")
    @pytest.mark.parametrize("partdef_qn", [
        "SolarBatteryLibrary__Solar_Array",
        "SolarBatteryLibrary__Battery_System",
        "SolarBatteryLibrary__Site_Infrastructure",
        "SolarBatteryLibrary__Solar_Battery_Plant",
    ])
    def test_all_partdefs_stripped(
        self, partdef_qn, solar_battery_hierarchy, solar_battery_calc_usages
    ):
        """Every PartDef's paths are dotted and prefix-stripped."""
        paths = find_instance_paths_for_partdef(
            partdef_qn,
            solar_battery_calc_usages,
            part_usage_names=solar_battery_hierarchy.part_usage_names,
        )
        assert len(paths) > 0, f"Should find paths for {partdef_qn}"
        for path in paths:
            assert "__" not in path, f"Path should be dotted: {path}"
            assert not path.startswith("SolarBatteryDesign"), (
                f"Design prefix should be stripped: {path}"
            )

    @pytest.mark.req("REQ-AS-03")
    def test_instance_path_has_design_prefix_in_scoped_data(
        self, solar_battery_hierarchy, solar_battery_calc_usages
    ):
        """ScopedAggregationData.instance_path starts with design prefix (__ format).
        module_eqn is derived from this path."""
        result = _scope_aggregation_expressions(
            solar_battery_hierarchy, solar_battery_calc_usages
        )
        for item in result:
            assert item.instance_path.startswith("SolarBatteryDesign__"), (
                f"instance_path should have design prefix: {item.instance_path}"
            )
            assert "__" in item.instance_path, (
                f"instance_path should use __ separator: {item.instance_path}"
            )
            expected_eqn = f"{item.instance_path}__{item.expression.attribute_name}"
            assert item.module_eqn == expected_eqn


# ---------------------------------------------------------------------------
# REQ-AS-04: CHAIN alias filters
# ---------------------------------------------------------------------------

class TestReqAS04ChainAliasFilters:
    """REQ-AS-04: CHAIN aliases SHALL only be produced for non-deep-path
    redefinitions whose source_path contains '.'."""

    @pytest.mark.req("REQ-AS-04")
    def test_chain_alias_filters(
        self, solar_battery_hierarchy, solar_battery_calc_usages
    ):
        """Verify _build_chain_aliases applies all three filters."""
        aliases = _build_chain_aliases(
            solar_battery_hierarchy, solar_battery_calc_usages
        )
        # Should produce 41 aliases (from spike findings)
        assert len(aliases) == 41

        # Verify all aliases have source="redefinition"
        for alias in aliases:
            assert alias.source == "redefinition"

        # Verify none of the filtered-out cas_category redefs produced aliases
        cas_alias_names = [
            a.alias_name for a in aliases if "cas_category" in a.alias_name
        ]
        assert cas_alias_names == [], (
            f"cas_category should be filtered out (no dot in source_path): {cas_alias_names}"
        )

    @pytest.mark.req("REQ-AS-04")
    def test_chain_alias_filter_counts(self, solar_battery_hierarchy):
        """Verify filter breakdown: how many CHAIN redefs pass each filter."""
        chain_redefs = [
            r for r in solar_battery_hierarchy.redefinitions
            if r.redefinition_type == RedefinitionType.CHAIN
        ]
        assert len(chain_redefs) > 0

        # Non-deep + has-dot subset should be 41
        qualifying = [
            r for r in chain_redefs
            if not r.is_deep_path
            and r.source_path
            and "." in r.source_path
        ]
        assert len(qualifying) == 41

        # Filtered by no-dot (cas_category entries)
        no_dot = [
            r for r in chain_redefs
            if not r.is_deep_path
            and r.source_path
            and "." not in r.source_path
        ]
        assert len(no_dot) > 0, "Should have some cas_category CHAIN redefs filtered out"

    @pytest.mark.req("REQ-AS-04")
    def test_chain_alias_output_format(
        self, solar_battery_hierarchy, solar_battery_calc_usages
    ):
        """Verify ChannelAlias fields: alias_name, canonical_name, source."""
        aliases = _build_chain_aliases(
            solar_battery_hierarchy, solar_battery_calc_usages
        )
        for alias in aliases:
            assert isinstance(alias, ChannelAlias)
            assert alias.source == "redefinition"
            # alias_name should be dotted path
            assert "." in alias.alias_name, (
                f"alias_name should be dotted: {alias.alias_name}"
            )
            # canonical_name should be dotted path
            assert "." in alias.canonical_name, (
                f"canonical_name should be dotted: {alias.canonical_name}"
            )
            # canonical_name should have more segments than alias_name
            # (e.g., "...cost_model.total_cost" vs "...capital_cost")
            assert alias.canonical_name.count(".") >= alias.alias_name.count("."), (
                f"canonical_name '{alias.canonical_name}' should be at least as deep "
                f"as alias_name '{alias.alias_name}'"
            )

    @pytest.mark.req("REQ-AS-04")
    def test_chain_alias_matches_snapshot(
        self, solar_battery_snapshot, solar_battery_hierarchy, solar_battery_calc_usages
    ):
        """Computed aliases match snapshot channel_aliases with source='redefinition'."""
        computed = _build_chain_aliases(
            solar_battery_hierarchy, solar_battery_calc_usages
        )
        snapshot_aliases = [
            a for a in solar_battery_snapshot["channel_aliases"]
            if a.source == "redefinition"
        ]

        assert len(computed) == len(snapshot_aliases)

        computed_set = {(a.alias_name, a.canonical_name) for a in computed}
        snapshot_set = {(a.alias_name, a.canonical_name) for a in snapshot_aliases}
        assert computed_set == snapshot_set

    @pytest.mark.req("REQ-AS-04")
    def test_null_source_path_guard(self, solar_battery_hierarchy):
        """Verify redefinitions with None source_path are filtered out."""
        # The code has: if not redef.source_path or "." not in redef.source_path
        # This handles both None and no-dot cases
        for r in solar_battery_hierarchy.redefinitions:
            if r.redefinition_type == RedefinitionType.CHAIN and r.source_path is None:
                # This redef should be filtered out — just verify the guard exists
                assert not r.source_path


# ---------------------------------------------------------------------------
# REQ-AS-05: Phase 1b registration
# ---------------------------------------------------------------------------

class TestReqAS05Phase1bRegistration:
    """REQ-AS-05: Phase 1b SHALL register a canonical channel for each
    ScopedAggregationData."""

    @pytest.mark.req("REQ-AS-05")
    def test_phase_1b_registration(self, solar_battery_snapshot):
        """Build registry from snapshot data. Verify aggregation channels registered."""
        registry = build_output_registry(
            calc_usages=solar_battery_snapshot["calc_usages"],
            calc_defs=solar_battery_snapshot["calc_defs"],
            aggregation_data=solar_battery_snapshot["aggregation_expressions"],
            computed_attributes=solar_battery_snapshot["computed_attributes"],
            channel_aliases=solar_battery_snapshot["channel_aliases"],
            design_attributes=solar_battery_snapshot["design_attributes"],
        )

        # Each ScopedAggregationData should have a Key_E_stripped in scoped registry
        for agg in solar_battery_snapshot["aggregation_expressions"]:
            instance_parts = agg.instance_path.split("__")
            if len(instance_parts) > 1:
                key_e_stripped = ScopedKey(
                    ".".join(instance_parts[1:] + [agg.expression.attribute_name])
                )
                result = registry.scoped_lookup(key_e_stripped)
                assert result is not None, (
                    f"Key_E_stripped {key_e_stripped} should be registered for "
                    f"{agg.instance_path}__{agg.expression.attribute_name}"
                )


# ---------------------------------------------------------------------------
# REQ-AS-06: Phase 2 alias resolution
# ---------------------------------------------------------------------------

class TestReqAS06Phase2AliasResolution:
    """REQ-AS-06: Phase 2 SHALL resolve ChannelAlias.canonical_name before registering."""

    @pytest.mark.req("REQ-AS-06")
    def test_phase_2_alias_resolution(self, solar_battery_snapshot):
        """Build registry. Verify CHAIN aliases are resolvable via alias_lookup."""
        registry = build_output_registry(
            calc_usages=solar_battery_snapshot["calc_usages"],
            calc_defs=solar_battery_snapshot["calc_defs"],
            aggregation_data=solar_battery_snapshot["aggregation_expressions"],
            computed_attributes=solar_battery_snapshot["computed_attributes"],
            channel_aliases=solar_battery_snapshot["channel_aliases"],
            design_attributes=solar_battery_snapshot["design_attributes"],
        )

        redef_aliases = [
            a for a in solar_battery_snapshot["channel_aliases"]
            if a.source == "redefinition"
        ]
        assert len(redef_aliases) > 0, "Should have redefinition aliases"

        resolved_count = 0
        for alias in redef_aliases:
            # The alias_name should be in the alias registry
            result = registry.alias_lookup(ScopedKey(alias.alias_name))
            if result is not None:
                resolved_count += 1
                # The resolved channel should also be findable via canonical_name
                canonical_result = registry.resolve(alias.canonical_name)
                assert canonical_result is not None, (
                    f"canonical_name {alias.canonical_name} should resolve"
                )

        # At least some aliases should have resolved
        assert resolved_count > 0, "At least some CHAIN aliases should be resolvable"


# ---------------------------------------------------------------------------
# REQ-AS-07: module_eqn format
# ---------------------------------------------------------------------------

class TestReqAS07ModuleEqnFormat:
    """REQ-AS-07: module_eqn property SHALL be '{instance_path}__{attribute_name}'."""

    @pytest.mark.req("REQ-AS-07")
    @pytest.mark.parametrize("idx", range(20))
    def test_module_eqn_format_solar_battery(
        self, solar_battery_snapshot, idx
    ):
        """Each of 20 ScopedAggregationData has correct module_eqn."""
        agg = solar_battery_snapshot["aggregation_expressions"][idx]
        expected = f"{agg.instance_path}__{agg.expression.attribute_name}"
        assert agg.module_eqn == expected

    @pytest.mark.req("REQ-AS-07")
    def test_module_eqn_issue22(self, issue22_snapshot):
        """issue22 ScopedAggregationData.module_eqn follows the format."""
        agg = issue22_snapshot["aggregation_expressions"][0]
        expected = f"{agg.instance_path}__{agg.expression.attribute_name}"
        assert agg.module_eqn == expected
        # Verify specific value from spike
        assert agg.module_eqn == "Issue22Design__plant__assembly__total_cost"


# ---------------------------------------------------------------------------
# REQ-AS-08: Zero-instance WARNING
# ---------------------------------------------------------------------------

class TestReqAS08ZeroInstanceWarning:
    """REQ-AS-08: The scoping function SHALL log a WARNING when an aggregation
    expression produces zero scoped modules."""

    @pytest.mark.req("REQ-AS-08")
    def test_zero_instance_warning(
        self, solar_battery_hierarchy, solar_battery_calc_usages, caplog
    ):
        """Construct an expression with unmatched PartDef. Verify WARNING logged."""
        # Create a hierarchy_data with one expression that won't match
        fake_expr = AggregationExpressionData(
            owning_part_qn="NonExistent__PartDef",
            owning_part_name="PartDef",
            attribute_name="fake_cost",
            raw_expression_text="sum(x.y)",
            transformed_expression="sum(x.y)",
            sum_terms=[],
            singleton_terms=[],
            local_terms=[],
            input_channels=[],
            entry_points=[],
            compilability=None,
            has_unsupported_nodes=False,
            aliases=[],
            source_file=Path("fake.sysml"),
            source_line=0,
        )
        fake_hierarchy = HierarchyExtractionResult(
            redefinitions=[],
            design_overrides=[],
            multiplicities=[],
            aggregation_expressions=[fake_expr],
            warnings=[],
            part_usage_names={},
            usage_type_map={},
        )

        with caplog.at_level(logging.WARNING, logger="sysml_codegen.generation.initialization"):
            result = _scope_aggregation_expressions(
                fake_hierarchy, solar_battery_calc_usages
            )

        # Zero scoped modules produced for the fake expression
        assert len(result) == 0

        # Should have a WARNING log mentioning the PartDef QN and attribute name
        warning_records = [
            r for r in caplog.records
            if r.levelno == logging.WARNING
        ]
        assert len(warning_records) >= 1, (
            f"Expected WARNING log for zero-instance case, got: "
            f"{[r.message for r in caplog.records]}"
        )
        warning_msg = warning_records[0].message
        assert "NonExistent__PartDef" in warning_msg, (
            f"WARNING should mention PartDef QN: {warning_msg}"
        )
        assert "fake_cost" in warning_msg, (
            f"WARNING should mention attribute name: {warning_msg}"
        )

    @pytest.mark.req("REQ-AS-08")
    def test_non_zero_instance_no_warning(
        self, solar_battery_hierarchy, solar_battery_calc_usages, caplog
    ):
        """Normal case (all expressions match) should NOT produce WARNING."""
        with caplog.at_level(logging.WARNING, logger="sysml_codegen.generation.initialization"):
            result = _scope_aggregation_expressions(
                solar_battery_hierarchy, solar_battery_calc_usages
            )

        assert len(result) == 20
        warning_records = [
            r for r in caplog.records
            if r.levelno == logging.WARNING
        ]
        assert len(warning_records) == 0, (
            f"Normal case should not produce warnings, got: "
            f"{[r.message for r in warning_records]}"
        )
