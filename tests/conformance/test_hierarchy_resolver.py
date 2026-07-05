"""C06: Hierarchy Resolver conformance tests.

Verifies that hierarchy extraction output conforms to REQ-HR-01 through
REQ-HR-07 from design intent doc 25-hierarchy-resolver.md. All tests use
real snapshot data captured in Phase 0 -- no mocks.

Requirements: REQ-HR-01 through REQ-HR-07.
"""

from __future__ import annotations

import ast as python_ast
from pathlib import Path

import pytest

from sysml_codegen.extraction.data_models import (
    HierarchyExtractionResult,
    RedefinitionType,
)
from tests.helpers.static_analysis import find_is_instance_calls_in_function

# ---------------------------------------------------------------------------
# Source paths for static analysis
# ---------------------------------------------------------------------------

SRC_DIR = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "extraction"
HIERARCHY_RESOLVER_PATH = SRC_DIR / "hierarchy_resolver.py"


# ---------------------------------------------------------------------------
# Expected counts from Phase 0 snapshot analysis
# ---------------------------------------------------------------------------

# solar_battery redefinition type counts
SOLAR_BATTERY_REDEF_COUNTS = {
    RedefinitionType.CHAIN: 54,
    RedefinitionType.LITERAL: 4,
    RedefinitionType.EXPRESSION: 20,
}

# solar_battery multiplicity values
SOLAR_BATTERY_MULTIPLICITIES = {
    "pv_module": 20,
    "inverter": 4,
    "battery_pack": 8,
}

# All models with extraction snapshots
ALL_MODELS = [
    "sample_model",
    "solar_battery_model",
    "catf_mfe_model",
    "attr_expr_probe",
    "chain_spike_model",
    "issue22_model",
    "alias_agg_probe",
]


# ---------------------------------------------------------------------------
# REQ-HR-01: Every redefinition classified as LITERAL, CHAIN, or EXPRESSION
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-HR-01")
class TestReqHr01RedefinitionTypes:
    """Every RedefinitionData has a valid, exclusive RedefinitionType."""

    def test_every_redef_has_valid_type(self, extraction_snapshots):
        """Every redefinition_type in {LITERAL, CHAIN, EXPRESSION} across all models."""
        valid = set(RedefinitionType)
        for model_name, snapshot in extraction_snapshots.items():
            hd = snapshot["hierarchy_data"]
            for redef in hd.redefinitions:
                assert redef.redefinition_type in valid, (
                    f"{model_name}: redef {redef.attribute_name} has invalid type "
                    f"{redef.redefinition_type}"
                )

    def test_all_three_types_present_solar_battery(self, solar_battery_snapshot):
        """solar_battery has all 3 RedefinitionType values: 54 CHAIN, 4 LITERAL, 20 EXPRESSION."""
        from collections import Counter

        hd = solar_battery_snapshot["hierarchy_data"]
        counts = Counter(r.redefinition_type for r in hd.redefinitions)
        for rtype, expected in SOLAR_BATTERY_REDEF_COUNTS.items():
            assert counts[rtype] == expected, (
                f"{rtype.value}: expected {expected}, got {counts[rtype]}"
            )
        total = sum(SOLAR_BATTERY_REDEF_COUNTS.values())
        assert len(hd.redefinitions) == total, (
            f"Total redefinitions: expected {total}, got {len(hd.redefinitions)}"
        )

    def test_redef_type_exclusive(self, extraction_snapshots):
        """Each redefinition has exactly one type (not None, is valid enum member)."""
        for model_name, snapshot in extraction_snapshots.items():
            hd = snapshot["hierarchy_data"]
            for redef in hd.redefinitions:
                assert redef.redefinition_type is not None, (
                    f"{model_name}: redef {redef.attribute_name} has None type"
                )
                assert isinstance(redef.redefinition_type, RedefinitionType), (
                    f"{model_name}: redef {redef.attribute_name} type is "
                    f"{type(redef.redefinition_type)}, not RedefinitionType"
                )


# ---------------------------------------------------------------------------
# REQ-HR-02: CHAIN classification covers both FCE (dotted) and FRE (bare)
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-HR-02")
class TestReqHr02ChainPatterns:
    """CHAIN redefs include both dotted-path (FCE) and bare-name (FRE) source_paths."""

    def test_chain_includes_both_dotted_and_bare(self, solar_battery_snapshot):
        """CHAIN redefs in solar_battery include both dotted-path and bare-name source_paths."""
        hd = solar_battery_snapshot["hierarchy_data"]
        chains = [r for r in hd.redefinitions if r.redefinition_type == RedefinitionType.CHAIN]
        assert len(chains) == 54, f"Expected 54 CHAIN redefs, got {len(chains)}"

        dotted = [r for r in chains if r.source_path and "." in r.source_path]
        bare = [r for r in chains if r.source_path and "." not in r.source_path]
        assert len(dotted) > 0, "No dotted-path CHAIN redefs found (FCE pattern)"
        assert len(bare) > 0, "No bare-name CHAIN redefs found (FRE pattern)"

    def test_fce_and_fre_both_produce_chain(self, solar_battery_snapshot):
        """No CHAIN redef has redefinition_type other than CHAIN; both patterns map to same type."""
        hd = solar_battery_snapshot["hierarchy_data"]
        chains = [r for r in hd.redefinitions if r.redefinition_type == RedefinitionType.CHAIN]
        for redef in chains:
            assert redef.source_path is not None, (
                f"CHAIN redef {redef.attribute_name} has None source_path"
            )
            assert redef.redefinition_type == RedefinitionType.CHAIN, (
                f"Expected CHAIN type for {redef.attribute_name}, got {redef.redefinition_type}"
            )


# ---------------------------------------------------------------------------
# REQ-HR-03: Deep-path design overrides
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-HR-03")
class TestReqHr03DeepPath:
    """Design-level :>> overrides are correctly flagged as deep-path."""

    def test_design_overrides_deep_path(self, solar_battery_snapshot):
        """All 13 solar_battery design_overrides have is_deep_path=True."""
        hd = solar_battery_snapshot["hierarchy_data"]
        assert len(hd.design_overrides) == 13, (
            f"Expected 13 design_overrides, got {len(hd.design_overrides)}"
        )
        for override in hd.design_overrides:
            assert override.is_deep_path is True, (
                f"Override {override.attribute_name} on {override.owning_part_qn} "
                f"has is_deep_path={override.is_deep_path}, expected True"
            )

    def test_deep_path_target_populated(self, solar_battery_snapshot):
        """All deep-path overrides have non-empty target_path with >= 2 segments."""
        hd = solar_battery_snapshot["hierarchy_data"]
        for override in hd.design_overrides:
            assert len(override.target_path) >= 2, (
                f"Override {override.attribute_name} has target_path={override.target_path} "
                f"(expected >= 2 segments)"
            )

    def test_shallow_redefs_not_deep(self, solar_battery_snapshot):
        """Non-deep-path redefinitions have is_deep_path=False and empty target_path."""
        hd = solar_battery_snapshot["hierarchy_data"]
        for redef in hd.redefinitions:
            if not redef.is_deep_path:
                assert redef.target_path == [], (
                    f"Non-deep redef {redef.attribute_name} has non-empty "
                    f"target_path={redef.target_path}"
                )
            else:
                assert len(redef.target_path) >= 2, (
                    f"Deep redef {redef.attribute_name} has insufficient "
                    f"target_path={redef.target_path}"
                )


# ---------------------------------------------------------------------------
# REQ-HR-04: Multiplicity extraction
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-HR-04")
class TestReqHr04Multiplicity:
    """Multiplicity counts are correctly extracted from PartUsage declarations."""

    @pytest.mark.parametrize(
        "usage_name,expected_count",
        list(SOLAR_BATTERY_MULTIPLICITIES.items()),
        ids=list(SOLAR_BATTERY_MULTIPLICITIES.keys()),
    )
    def test_multiplicity_counts_correct(
        self, solar_battery_snapshot, usage_name, expected_count
    ):
        """solar_battery: pv_module=20, inverter=4, battery_pack=8."""
        hd = solar_battery_snapshot["hierarchy_data"]
        mult_map = {m.part_usage_name: m for m in hd.multiplicities}
        assert usage_name in mult_map, (
            f"Multiplicity for {usage_name} not found. "
            f"Available: {list(mult_map.keys())}"
        )
        assert mult_map[usage_name].count == expected_count, (
            f"{usage_name}: expected count={expected_count}, "
            f"got {mult_map[usage_name].count}"
        )

    def test_multiplicity_integer_type(self, solar_battery_snapshot):
        """All multiplicity count values are int (not float, not off-by-one)."""
        hd = solar_battery_snapshot["hierarchy_data"]
        for mult in hd.multiplicities:
            if mult.count is not None:
                assert isinstance(mult.count, int), (
                    f"{mult.part_usage_name}: count is {type(mult.count).__name__}, "
                    f"expected int"
                )

    def test_count_attribute_name_populated(self, solar_battery_snapshot):
        """All multiplicities with non-None count have non-None count_attribute_name."""
        hd = solar_battery_snapshot["hierarchy_data"]
        for mult in hd.multiplicities:
            if mult.count is not None:
                assert mult.count_attribute_name is not None, (
                    f"{mult.part_usage_name}: has count={mult.count} but "
                    f"count_attribute_name is None"
                )


# ---------------------------------------------------------------------------
# REQ-HR-05: FCE before OE dispatch ordering in _walk_aggregation_ast
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-HR-05")
class TestReqHr05DispatchOrdering:
    """Static analysis: FCE checked before OE in _walk_aggregation_ast."""

    def test_fce_before_oe_in_walk_aggregation_ast(self):
        """In _walk_aggregation_ast(), FCE check appears before OE check."""
        calls = find_is_instance_calls_in_function(
            HIERARCHY_RESOLVER_PATH, "_walk_aggregation_ast"
        )
        assert "FeatureChainExpression" in calls, (
            "No is_instance call for FeatureChainExpression in _walk_aggregation_ast"
        )
        assert "OperatorExpression" in calls, (
            "No is_instance call for OperatorExpression in _walk_aggregation_ast"
        )
        assert calls["FeatureChainExpression"] < calls["OperatorExpression"], (
            f"FCE check at line {calls['FeatureChainExpression']} must precede "
            f"OE check at line {calls['OperatorExpression']}"
        )

    def test_fce_before_oe_comment_present(self):
        """The FCE check in _walk_aggregation_ast() has the invariant comment."""
        source = HIERARCHY_RESOLVER_PATH.read_text()
        # Find the relevant section in _walk_aggregation_ast
        assert "MUST be before OperatorExpression" in source, (
            "Invariant comment 'MUST be before OperatorExpression' not found in "
            "hierarchy_resolver.py"
        )


# ---------------------------------------------------------------------------
# REQ-HR-06: SumTerm parametric multiply
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-HR-06")
class TestReqHr06SumTerms:
    """SumTerm aggregation with parametric multiply transformation."""

    def test_sum_terms_have_multiplicity(self, solar_battery_snapshot):
        """All SumTerms in solar_battery have non-None multiplicity_attr and multiplicity_count."""
        hd = solar_battery_snapshot["hierarchy_data"]
        for agg in hd.aggregation_expressions:
            for st in agg.sum_terms:
                assert st.multiplicity_attr is not None, (
                    f"SumTerm {st.part_usage_name}.{st.attribute_name} on "
                    f"{agg.attribute_name} has None multiplicity_attr"
                )
                assert st.multiplicity_count is not None, (
                    f"SumTerm {st.part_usage_name}.{st.attribute_name} on "
                    f"{agg.attribute_name} has None multiplicity_count"
                )

    def test_transformed_expression_has_parametric_multiply(self, solar_battery_snapshot):
        """Transformed expressions with sum_terms contain (mult_attr * child.attr) pattern."""
        hd = solar_battery_snapshot["hierarchy_data"]
        for agg in hd.aggregation_expressions:
            for st in agg.sum_terms:
                if st.multiplicity_attr is not None:
                    mult = st.multiplicity_attr
                    child = f"{st.part_usage_name}.{st.attribute_name}"
                    expected_pattern = f"({mult} * {child})"
                    assert expected_pattern in agg.transformed_expression, (
                        f"Expression for {agg.attribute_name} missing parametric multiply "
                        f"'{expected_pattern}' in: {agg.transformed_expression}"
                    )

    def test_entry_points_contain_multiplicity_attrs(self, solar_battery_snapshot):
        """For expressions with sum_terms, entry_points includes the multiplicity_attr names."""
        hd = solar_battery_snapshot["hierarchy_data"]
        for agg in hd.aggregation_expressions:
            for st in agg.sum_terms:
                if st.multiplicity_attr is not None:
                    assert st.multiplicity_attr in agg.entry_points, (
                        f"Entry points for {agg.attribute_name} missing "
                        f"multiplicity_attr '{st.multiplicity_attr}'. "
                        f"entry_points={agg.entry_points}"
                    )

    def test_no_multiplicity_edge_case_issue22(self, issue22_snapshot):
        """issue22 SumTerm has multiplicity_attr=None (no named count attribute)."""
        hd = issue22_snapshot["hierarchy_data"]
        assert len(hd.aggregation_expressions) == 1, (
            f"Expected 1 aggregation expression, got {len(hd.aggregation_expressions)}"
        )
        agg = hd.aggregation_expressions[0]
        assert len(agg.sum_terms) == 1, (
            f"Expected 1 sum_term, got {len(agg.sum_terms)}"
        )
        st = agg.sum_terms[0]
        assert st.multiplicity_attr is None, (
            f"issue22 SumTerm should have multiplicity_attr=None, got {st.multiplicity_attr}"
        )
        assert st.multiplicity_count is None, (
            f"issue22 SumTerm should have multiplicity_count=None, got {st.multiplicity_count}"
        )
        # Transformed expression should NOT have parametric multiply
        assert "*" not in agg.transformed_expression, (
            f"issue22 expression should not have multiply: {agg.transformed_expression}"
        )


# ---------------------------------------------------------------------------
# REQ-HR-07: Alias detection for CHAIN siblings
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-HR-07")
class TestReqHr07AliasDetection:
    """CHAIN-type alias detection on aggregation expressions."""

    def test_alias_detection_zero_result_correct(self, solar_battery_snapshot):
        """All 20 solar_battery aggregation expressions have empty aliases.

        This is correct because no CHAIN sibling source_path ends with an
        aggregation attribute_name. Zero-alias is the expected result, not a bug.
        """
        hd = solar_battery_snapshot["hierarchy_data"]
        assert len(hd.aggregation_expressions) == 20
        for agg in hd.aggregation_expressions:
            assert agg.aliases == [], (
                f"Aggregation {agg.attribute_name} on {agg.owning_part_qn} "
                f"has unexpected aliases: {agg.aliases}"
            )

    def test_alias_field_exists_and_is_list(self, extraction_snapshots):
        """Every AggregationExpressionData has aliases field of type list."""
        for model_name, snapshot in extraction_snapshots.items():
            hd = snapshot["hierarchy_data"]
            for agg in hd.aggregation_expressions:
                assert isinstance(agg.aliases, list), (
                    f"{model_name}: {agg.attribute_name} aliases is "
                    f"{type(agg.aliases).__name__}, expected list"
                )

    def test_alias_detection_positive_case(self, alias_agg_probe_snapshot):
        """alias_agg_probe: CHAIN sibling 'reported_cost = total_cost' detected as alias.

        This is the POSITIVE case for REQ-HR-07. The hierarchy resolver detects
        that ':>> reported_cost = total_cost' is a CHAIN-type sibling redef
        whose source_path ends with the aggregation attribute_name 'total_cost'.
        """
        hd = alias_agg_probe_snapshot["hierarchy_data"]
        assert len(hd.aggregation_expressions) == 1, (
            f"Expected 1 aggregation expression, got {len(hd.aggregation_expressions)}"
        )
        agg = hd.aggregation_expressions[0]
        assert agg.attribute_name == "total_cost", (
            f"Expected aggregation attribute_name='total_cost', got {agg.attribute_name!r}"
        )
        assert agg.aliases == ["reported_cost"], (
            f"Expected aliases=['reported_cost'], got {agg.aliases}"
        )

    def test_alias_sibling_redef_is_chain_type(self, alias_agg_probe_snapshot):
        """The alias sibling redefinition has type=CHAIN, source_path='total_cost'."""
        hd = alias_agg_probe_snapshot["hierarchy_data"]
        alias_redef = [
            r for r in hd.redefinitions
            if r.attribute_name == "reported_cost"
            and "Widget_Assembly" in r.owning_part_qn
        ]
        assert len(alias_redef) == 1, (
            f"Expected 1 'reported_cost' redef on Widget_Assembly, got {len(alias_redef)}"
        )
        redef = alias_redef[0]
        assert redef.redefinition_type == RedefinitionType.CHAIN, (
            f"Expected CHAIN type, got {redef.redefinition_type}"
        )
        assert redef.source_path == "total_cost", (
            f"Expected source_path='total_cost', got {redef.source_path!r}"
        )


# ---------------------------------------------------------------------------
# Additional tests: Checklist AC coverage
# ---------------------------------------------------------------------------


class TestPartUsageNames:
    """part_usage_names correctly maps assembly PartDefs to child names."""

    def test_part_usage_names_populated(self, solar_battery_snapshot):
        """solar_battery part_usage_names has entries for assembly PartDefs."""
        hd = solar_battery_snapshot["hierarchy_data"]
        assert len(hd.part_usage_names) == 4, (
            f"Expected 4 part_usage_names entries, got {len(hd.part_usage_names)}"
        )
        # At least Solar_Array and Battery_System should be present
        qn_keys = list(hd.part_usage_names.keys())
        solar_array_keys = [k for k in qn_keys if "Solar_Array" in k]
        assert len(solar_array_keys) == 1, (
            f"Expected one Solar_Array key, got {solar_array_keys}"
        )

    def test_part_usage_names_child_names_correct(self, solar_battery_snapshot):
        """Solar_Array's children include {pv_module, inverter, array_bos}."""
        hd = solar_battery_snapshot["hierarchy_data"]
        solar_array_key = [k for k in hd.part_usage_names if "Solar_Array" in k][0]
        children = hd.part_usage_names[solar_array_key]
        expected = {"pv_module", "inverter", "array_bos"}
        assert expected.issubset(children), (
            f"Solar_Array missing expected children: {expected - children}. "
            f"Actual: {children}"
        )

    def test_part_usage_names_all_models(self, extraction_snapshots):
        """part_usage_names populated correctly across all models with hierarchy data."""
        for model_name, snapshot in extraction_snapshots.items():
            hd = snapshot["hierarchy_data"]
            for qn, names in hd.part_usage_names.items():
                assert isinstance(qn, str), (
                    f"{model_name}: part_usage_names key is {type(qn)}, expected str"
                )
                assert isinstance(names, set), (
                    f"{model_name}: part_usage_names[{qn}] is {type(names)}, expected set"
                )
                assert len(names) > 0, (
                    f"{model_name}: part_usage_names[{qn}] is empty"
                )


class TestUsageTypeMap:
    """usage_type_map maps (parent_qn, child_name) to type PartDef QN."""

    def test_usage_type_map_populated(self, solar_battery_snapshot):
        """solar_battery usage_type_map has entries mapping usage names to type PartDef QNs."""
        hd = solar_battery_snapshot["hierarchy_data"]
        assert len(hd.usage_type_map) == 12, (
            f"Expected 12 usage_type_map entries, got {len(hd.usage_type_map)}"
        )

    def test_usage_type_map_tuple_keys(self, solar_battery_snapshot):
        """All usage_type_map keys are tuple[str, str] (deserialized correctly)."""
        hd = solar_battery_snapshot["hierarchy_data"]
        for key, value in hd.usage_type_map.items():
            assert isinstance(key, tuple), (
                f"usage_type_map key is {type(key)}, expected tuple"
            )
            assert len(key) == 2, (
                f"usage_type_map key has {len(key)} elements, expected 2"
            )
            assert isinstance(key[0], str) and isinstance(key[1], str), (
                f"usage_type_map key elements are ({type(key[0])}, {type(key[1])}), "
                f"expected (str, str)"
            )
            assert isinstance(value, str), (
                f"usage_type_map value is {type(value)}, expected str"
            )


class TestTermTypeClassification:
    """Aggregation terms are correctly classified into SumTerm, SingletonTerm, LocalTerm."""

    def test_term_type_all_three_present(self, solar_battery_snapshot):
        """solar_battery aggregation expressions collectively have all 3 term types."""
        hd = solar_battery_snapshot["hierarchy_data"]
        has_sum = any(len(a.sum_terms) > 0 for a in hd.aggregation_expressions)
        has_singleton = any(len(a.singleton_terms) > 0 for a in hd.aggregation_expressions)
        has_local = any(len(a.local_terms) > 0 for a in hd.aggregation_expressions)
        assert has_sum, "No SumTerms found in solar_battery aggregation expressions"
        assert has_singleton, "No SingletonTerms found in solar_battery aggregation expressions"
        assert has_local, "No LocalTerms found in solar_battery aggregation expressions"

    def test_singleton_terms_have_dotted_source_path(self, solar_battery_snapshot):
        """Every SingletonTerm.source_path contains '.' (dotted FCE pattern)."""
        hd = solar_battery_snapshot["hierarchy_data"]
        for agg in hd.aggregation_expressions:
            for st in agg.singleton_terms:
                assert "." in st.source_path, (
                    f"SingletonTerm source_path={st.source_path!r} missing '.' "
                    f"in aggregation {agg.attribute_name}"
                )

    def test_local_terms_have_bare_name(self, solar_battery_snapshot):
        """Every LocalTerm.attribute_name does NOT contain '.' (bare name FRE pattern)."""
        hd = solar_battery_snapshot["hierarchy_data"]
        for agg in hd.aggregation_expressions:
            for lt in agg.local_terms:
                assert "." not in lt.attribute_name, (
                    f"LocalTerm attribute_name={lt.attribute_name!r} contains '.' "
                    f"in aggregation {agg.attribute_name}"
                )

    def test_sum_terms_have_child_dot_attr(self, solar_battery_snapshot):
        """Every SumTerm has non-empty part_usage_name and attribute_name."""
        hd = solar_battery_snapshot["hierarchy_data"]
        for agg in hd.aggregation_expressions:
            for st in agg.sum_terms:
                assert st.part_usage_name, (
                    f"SumTerm in {agg.attribute_name} has empty part_usage_name"
                )
                assert st.attribute_name, (
                    f"SumTerm in {agg.attribute_name} has empty attribute_name"
                )


class TestExpressionValidity:
    """Transformed expressions are valid Python."""

    def test_transformed_expression_valid_python(self, solar_battery_snapshot):
        """All 20 transformed expressions pass ast.parse() as valid Python (no .() syntax)."""
        hd = solar_battery_snapshot["hierarchy_data"]
        assert len(hd.aggregation_expressions) == 20
        for agg in hd.aggregation_expressions:
            try:
                python_ast.parse(agg.transformed_expression, mode="eval")
            except SyntaxError as e:
                pytest.fail(
                    f"Aggregation {agg.attribute_name} on {agg.owning_part_qn}: "
                    f"transformed_expression is not valid Python: "
                    f"{agg.transformed_expression!r} -- {e}"
                )


class TestCrossModelIssue22:
    """Cross-model validation on issue22_model."""

    def test_cross_model_issue22_hierarchy(self, issue22_snapshot):
        """issue22 has 2 redefinitions, 1 multiplicity, 1 aggregation expression."""
        hd = issue22_snapshot["hierarchy_data"]
        assert len(hd.redefinitions) == 2, (
            f"Expected 2 redefinitions, got {len(hd.redefinitions)}"
        )
        assert len(hd.design_overrides) == 0, (
            f"Expected 0 design_overrides, got {len(hd.design_overrides)}"
        )
        assert len(hd.multiplicities) == 1, (
            f"Expected 1 multiplicity, got {len(hd.multiplicities)}"
        )
        assert len(hd.aggregation_expressions) == 1, (
            f"Expected 1 aggregation_expression, got {len(hd.aggregation_expressions)}"
        )


class TestCrossModelNoHierarchy:
    """Cross-model: models with empty hierarchy data."""

    @pytest.mark.parametrize(
        "model_name",
        ["sample_model", "chain_spike_model"],
        ids=["sample", "chain_spike"],
    )
    def test_cross_model_no_hierarchy_models(self, extraction_snapshots, model_name):
        """sample_model and chain_spike_model have empty hierarchy data."""
        hd = extraction_snapshots[model_name]["hierarchy_data"]
        assert len(hd.redefinitions) == 0, (
            f"{model_name}: expected 0 redefinitions, got {len(hd.redefinitions)}"
        )
        assert len(hd.design_overrides) == 0, (
            f"{model_name}: expected 0 design_overrides, got {len(hd.design_overrides)}"
        )
        assert len(hd.multiplicities) == 0, (
            f"{model_name}: expected 0 multiplicities, got {len(hd.multiplicities)}"
        )
        assert len(hd.aggregation_expressions) == 0, (
            f"{model_name}: expected 0 aggregation_expressions, "
            f"got {len(hd.aggregation_expressions)}"
        )


class TestDataIntegrity:
    """HierarchyExtractionResult structural completeness."""

    def test_hierarchy_data_structure_complete(self, solar_battery_snapshot):
        """HierarchyExtractionResult has all 7 expected fields."""
        hd = solar_battery_snapshot["hierarchy_data"]
        assert isinstance(hd, HierarchyExtractionResult)
        assert hasattr(hd, "redefinitions")
        assert hasattr(hd, "design_overrides")
        assert hasattr(hd, "multiplicities")
        assert hasattr(hd, "aggregation_expressions")
        assert hasattr(hd, "warnings")
        assert hasattr(hd, "part_usage_names")
        assert hasattr(hd, "usage_type_map")

    def test_aggregation_expression_count(self, solar_battery_snapshot):
        """solar_battery has exactly 20 aggregation expressions, one per EXPRESSION-type redef."""
        hd = solar_battery_snapshot["hierarchy_data"]
        expression_redefs = [
            r for r in hd.redefinitions
            if r.redefinition_type == RedefinitionType.EXPRESSION
        ]
        assert len(hd.aggregation_expressions) == len(expression_redefs) == 20, (
            f"Expected 20 EXPRESSION redefs and 20 aggregation expressions, "
            f"got {len(expression_redefs)} redefs and {len(hd.aggregation_expressions)} aggs"
        )


# ---------------------------------------------------------------------------
# C5: alias_agg_probe — CHAIN alias for aggregation attribute (REQ-HR-07)
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-HR-07")
class TestAliasAggProbe:
    """Comprehensive tests for alias_agg_probe fixture (C5 gap closure).

    This fixture exercises the POSITIVE case for REQ-HR-07: a CHAIN sibling
    redefinition that targets an aggregation attribute, producing a non-empty
    aliases list. Previously, all fixture models had empty aliases.
    """

    def test_hierarchy_structure(self, alias_agg_probe_snapshot):
        """alias_agg_probe has 3 redefs, 0 design overrides, 1 multiplicity, 1 aggregation."""
        hd = alias_agg_probe_snapshot["hierarchy_data"]
        assert len(hd.redefinitions) == 3, (
            f"Expected 3 redefinitions, got {len(hd.redefinitions)}"
        )
        assert len(hd.design_overrides) == 0, (
            f"Expected 0 design_overrides, got {len(hd.design_overrides)}"
        )
        assert len(hd.multiplicities) == 1, (
            f"Expected 1 multiplicity, got {len(hd.multiplicities)}"
        )
        assert len(hd.aggregation_expressions) == 1, (
            f"Expected 1 aggregation expression, got {len(hd.aggregation_expressions)}"
        )

    def test_redefinition_types(self, alias_agg_probe_snapshot):
        """3 redefinitions: 2 CHAIN (Widget.total_cost, WA.reported_cost), 1 EXPRESSION (WA.total_cost)."""
        from collections import Counter

        hd = alias_agg_probe_snapshot["hierarchy_data"]
        counts = Counter(r.redefinition_type for r in hd.redefinitions)
        assert counts[RedefinitionType.CHAIN] == 2, (
            f"Expected 2 CHAIN redefs, got {counts[RedefinitionType.CHAIN]}"
        )
        assert counts[RedefinitionType.EXPRESSION] == 1, (
            f"Expected 1 EXPRESSION redef, got {counts[RedefinitionType.EXPRESSION]}"
        )

    def test_aggregation_sum_term(self, alias_agg_probe_snapshot):
        """Aggregation has 1 SumTerm: widget.total_cost with literal multiplicity (no attr)."""
        hd = alias_agg_probe_snapshot["hierarchy_data"]
        agg = hd.aggregation_expressions[0]
        assert len(agg.sum_terms) == 1, (
            f"Expected 1 sum_term, got {len(agg.sum_terms)}"
        )
        st = agg.sum_terms[0]
        assert st.part_usage_name == "widget", (
            f"Expected part_usage_name='widget', got {st.part_usage_name!r}"
        )
        assert st.attribute_name == "total_cost", (
            f"Expected attribute_name='total_cost', got {st.attribute_name!r}"
        )
        # Literal [3] multiplicity — no count_attribute_name
        assert st.multiplicity_attr is None, (
            f"Expected multiplicity_attr=None (literal [3]), got {st.multiplicity_attr!r}"
        )

    def test_multiplicity_literal(self, alias_agg_probe_snapshot):
        """widget has count=3 with count_attribute_name=None (literal multiplicity)."""
        hd = alias_agg_probe_snapshot["hierarchy_data"]
        assert len(hd.multiplicities) == 1
        mult = hd.multiplicities[0]
        assert mult.part_usage_name == "widget", (
            f"Expected part_usage_name='widget', got {mult.part_usage_name!r}"
        )
        assert mult.count == 3, (
            f"Expected count=3, got {mult.count}"
        )
        assert mult.count_attribute_name is None, (
            f"Expected count_attribute_name=None, got {mult.count_attribute_name!r}"
        )

    def test_calc_usages_correct(self, alias_agg_probe_snapshot):
        """3 CalcUsages: cost_model (leaf), margin_calc (direct), report_calc (via alias)."""
        calc_usages = alias_agg_probe_snapshot["calc_usages"]
        instance_names = {cu.instance_name for cu in calc_usages}
        expected_suffixes = {"cost_model", "margin_calc", "report_calc"}
        for suffix in expected_suffixes:
            matching = [n for n in instance_names if n.endswith(suffix)]
            assert len(matching) >= 1, (
                f"No CalcUsage instance ending with '{suffix}'. "
                f"Actual: {instance_names}"
            )

    def test_report_calc_binds_through_alias(self, alias_agg_probe_snapshot):
        """report_calc binds cost_input to reported_cost (the CHAIN alias attribute)."""
        calc_usages = alias_agg_probe_snapshot["calc_usages"]
        report_calc = [cu for cu in calc_usages if cu.instance_name.endswith("report_calc")]
        assert len(report_calc) == 1
        bindings = report_calc[0].bindings
        cost_input_binding = [b for b in bindings if b.param_name == "cost_input"]
        assert len(cost_input_binding) == 1, (
            f"Expected 1 cost_input binding, got {len(cost_input_binding)}"
        )
        binding = cost_input_binding[0]
        assert binding.source_path is not None, (
            "cost_input binding should have non-None source_path"
        )
        assert "reported_cost" in binding.source_path, (
            f"cost_input binding source_path should reference 'reported_cost', "
            f"got {binding.source_path!r}"
        )

    def test_part_usage_names_widget_assembly(self, alias_agg_probe_snapshot):
        """Widget_Assembly's part_usage_names includes 'widget'."""
        hd = alias_agg_probe_snapshot["hierarchy_data"]
        wa_keys = [k for k in hd.part_usage_names if "Widget_Assembly" in k]
        assert len(wa_keys) == 1, (
            f"Expected 1 Widget_Assembly key, got {wa_keys}"
        )
        children = hd.part_usage_names[wa_keys[0]]
        assert "widget" in children, (
            f"Expected 'widget' in children, got {children}"
        )

    def test_channel_alias_from_chain_redef(self, alias_agg_probe_snapshot):
        """Widget's ':>> total_cost = cost_model.unit_cost' produces a channel alias."""
        aliases = alias_agg_probe_snapshot["channel_aliases"]
        assert len(aliases) >= 1, (
            f"Expected at least 1 channel alias, got {len(aliases)}"
        )
        # The CHAIN redef on Widget produces a channel alias
        widget_aliases = [a for a in aliases if "Widget" in a.owning_part_qn]
        assert len(widget_aliases) >= 1, (
            f"Expected at least 1 Widget-related alias, got {len(widget_aliases)}"
        )
