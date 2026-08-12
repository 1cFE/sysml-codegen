"""C07: AST Dispatch Invariant conformance tests.

Verifies that every is_instance() dispatch site in the codebase that checks
both FeatureChainExpression (FCE) and OperatorExpression (OE) always checks
FCE first. FCE is a subtype of OE in SysIDE's type system, so checking OE
first misclassifies FCE nodes. This was the root cause of Bug A (commit 20b720e).

Testing strategy:
- Static analysis tests parse source files with Python ast module -- no mocks.
- Behavioral tests use SysIDE adapter name-based fallback with dual-match mock
  classes (acceptable per Ground Rule 1).
- Model-fact tests read live extraction (``tests/helpers/live_extraction.py``), not the
  retiring v5 extraction snapshots; they are license-gated by the fixture.

Requirements: REQ-AST-01 through REQ-AST-07.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.helpers.static_analysis import (
    find_all_dispatch_functions,
    find_comment_near_line,
    find_is_instance_calls_in_function,
    is_any_is_instance_call,
)

# ---------------------------------------------------------------------------
# Source paths for static analysis
# ---------------------------------------------------------------------------

SRC_ROOT = Path(__file__).parent.parent.parent / "src" / "sysml_codegen"
EXTRACTION_DIR = SRC_ROOT / "extraction"

HIERARCHY_RESOLVER_PATH = EXTRACTION_DIR / "hierarchy_resolver.py"
USAGE_EXTRACTOR_PATH = EXTRACTION_DIR / "usage_extractor.py"
EXTRACTOR_PATH = EXTRACTION_DIR / "extractor.py"
ELABORATOR_PATH = SRC_ROOT / "elaboration" / "elaborate.py"
AGENTIC_HIERARCHY_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "agentic-mbse"
    / "src"
    / "agentic_mbse"
    / "sysml"
    / "hierarchy.py"
)
AGENTIC_AGGREGATION_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "agentic-mbse"
    / "src"
    / "agentic_mbse"
    / "sysml"
    / "aggregation.py"
)

# Expression type names used for dispatch site identification
EXPRESSION_TYPE_NAMES = frozenset(
    {
        "FeatureChainExpression",
        "OperatorExpression",
        "FeatureReferenceExpression",
    }
)

# ---------------------------------------------------------------------------
# Dispatch site inventory (foundation for all audit tests)
# ---------------------------------------------------------------------------

# Sites where both FCE and OE are checked (the critical invariant sites). The calc-side
# dispatch site (build_expression_ast) was audited here through CONSTRAINT-EXEC Item 13's
# Phase 4: that responsibility moved cross-repo to agentic-mbse's extract_expression_ir
# (its own dispatch, its own tests), so it drops out of this repo's audited set rather than
# being replaced by a new site here (the renderer consumes ExpressionIR via isinstance on IR
# node classes, not raw-syside is_instance() -- no dispatch site to audit).
DUAL_CHECK_SITES = [
    (AGENTIC_AGGREGATION_PATH, "_decompose_node"),
    (USAGE_EXTRACTOR_PATH, "_extract_single_binding"),
    (ELABORATOR_PATH, "_expression_references"),
]

DUAL_CHECK_IDS = [
    "agentic_aggregation._decompose_node",
    "_extract_single_binding",
    "elaboration._expression_references",
]

# Sites that use if/if/if chains (not elif) and must follow full canonical ordering
CANONICAL_SITES = [
    (AGENTIC_AGGREGATION_PATH, "_decompose_node"),
]

CANONICAL_IDS = [
    "agentic_aggregation._decompose_node",
]

# Sites that use elif chains -- FCE < OE is sufficient, full canonical not required
ELIF_SITES = [
    (USAGE_EXTRACTOR_PATH, "_extract_single_binding"),
]

ELIF_IDS = [
    "_extract_single_binding",
]


# ---------------------------------------------------------------------------
# Mock infrastructure (SysIDE adapter boundary stubs -- Ground Rule 1)
# ---------------------------------------------------------------------------


class MockFeatureReferenceExpression:
    """Mock syside FeatureReferenceExpression node."""

    def __init__(self, name: str):
        self.referent = SimpleNamespace(name=name)


class MockFeatureChainExpressionOperatorExpression:
    """Mock that dual-matches both FeatureChainExpression and OperatorExpression.

    Class name contains both type names, triggering SysideAdapter.is_instance()'s
    name-based fallback for both type checks. Used to verify that FCE handler fires
    first when both would match.
    """

    def __init__(self, operands: list | None = None, target_feature=None):
        self.operator = "."
        self.operands = operands or []
        self.target_feature = target_feature


# ---------------------------------------------------------------------------
# REQ-AST-01: FCE before OE at every dual-check site
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-AST-01")
class TestReqAst01FceBeforeOe:
    """Static analysis: FCE is_instance check precedes OE at every dual-check site."""

    @pytest.mark.parametrize(
        "source_path,function_name",
        DUAL_CHECK_SITES,
        ids=DUAL_CHECK_IDS,
    )
    def test_fce_before_oe_all_dual_check_sites(self, source_path, function_name):
        """FCE check line < OE check line in the given function."""
        calls = find_is_instance_calls_in_function(
            source_path, function_name, predicate=is_any_is_instance_call
        )
        assert "FeatureChainExpression" in calls, (
            f"No is_instance call for FeatureChainExpression in {source_path.name}:{function_name}"
        )
        assert "OperatorExpression" in calls, (
            f"No is_instance call for OperatorExpression in {source_path.name}:{function_name}"
        )
        assert calls["FeatureChainExpression"] < calls["OperatorExpression"], (
            f"{source_path.name}:{function_name}: "
            f"FCE at line {calls['FeatureChainExpression']} must precede "
            f"OE at line {calls['OperatorExpression']}"
        )


# ---------------------------------------------------------------------------
# REQ-AST-02: Comment present at every dual-check site
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-AST-02")
class TestReqAst02CommentPresent:
    """Invariant comment 'MUST be before OperatorExpression' present at every dual-check site."""

    @pytest.mark.parametrize(
        "source_path,function_name",
        DUAL_CHECK_SITES,
        ids=DUAL_CHECK_IDS,
    )
    def test_invariant_comment_at_all_dual_check_sites(self, source_path, function_name):
        """Comment matching 'MUST be before OperatorExpression' appears within 5 lines
        above the FCE check in the given function."""
        calls = find_is_instance_calls_in_function(
            source_path, function_name, predicate=is_any_is_instance_call
        )
        assert "FeatureChainExpression" in calls, (
            f"No is_instance call for FeatureChainExpression in {source_path.name}:{function_name}"
        )

        fce_line = calls["FeatureChainExpression"]
        source_lines = source_path.read_text().splitlines()

        assert find_comment_near_line(
            source_lines, fce_line, "MUST be before OperatorExpression"
        ), (
            f"{source_path.name}:{function_name}: "
            f"Missing invariant comment 'MUST be before OperatorExpression' "
            f"within 5 lines above FCE check at line {fce_line}"
        )


# ---------------------------------------------------------------------------
# REQ-AST-03: Canonical ordering at all dual-check sites
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-AST-03")
class TestReqAst03CanonicalOrdering:
    """Dispatch ordering: canonical (FCE < OE < FRE) at if-chain sites,
    critical invariant (FCE < OE) at elif-chain sites."""

    @pytest.mark.parametrize(
        "source_path,function_name",
        CANONICAL_SITES,
        ids=CANONICAL_IDS,
    )
    def test_canonical_ordering_fce_oe_fre(self, source_path, function_name):
        """Full canonical ordering: FCE < OE < FRE at if-chain sites."""
        calls = find_is_instance_calls_in_function(
            source_path, function_name, predicate=is_any_is_instance_call
        )
        assert "FeatureChainExpression" in calls
        assert "OperatorExpression" in calls
        assert "FeatureReferenceExpression" in calls

        fce = calls["FeatureChainExpression"]
        oe = calls["OperatorExpression"]
        fre = calls["FeatureReferenceExpression"]

        assert fce < oe < fre, (
            f"{source_path.name}:{function_name}: Expected FCE({fce}) < OE({oe}) < FRE({fre})"
        )

    @pytest.mark.parametrize(
        "source_path,function_name",
        ELIF_SITES,
        ids=ELIF_IDS,
    )
    def test_elif_sites_fce_before_oe(self, source_path, function_name):
        """Critical invariant: FCE < OE at elif-chain sites (full canonical not required)."""
        calls = find_is_instance_calls_in_function(
            source_path, function_name, predicate=is_any_is_instance_call
        )
        assert "FeatureChainExpression" in calls
        assert "OperatorExpression" in calls

        assert calls["FeatureChainExpression"] < calls["OperatorExpression"], (
            f"{source_path.name}:{function_name}: "
            f"FCE at line {calls['FeatureChainExpression']} must precede "
            f"OE at line {calls['OperatorExpression']}"
        )


# ---------------------------------------------------------------------------
# REQ-AST-04: Total dispatch site guardrail
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-AST-04")
class TestReqAst04DispatchSiteGuardrail:
    """Guard against new unaudited dispatch sites appearing in the codebase."""

    def test_total_dual_check_site_count(self):
        """Exactly 3 audited functions have both FCE and OE is_instance() checks.

        The exact-ID reference collector checks OperatorExpression only to keep
        operator syntax out of the explicit-invocation branch. It still belongs
        in this critical FCE-before-OE inventory.

        The fourth site was ``analysis/parameter_groups.py:_extract_default_value``; it
        retired with the v5 family (retirement step 2)."""
        all_dispatch = find_all_dispatch_functions(SRC_ROOT, EXPRESSION_TYPE_NAMES)
        shared_aggregation_calls = find_is_instance_calls_in_function(
            AGENTIC_AGGREGATION_PATH,
            "_decompose_node",
            predicate=is_any_is_instance_call,
        )
        shared_aggregation_types = {
            name: line
            for name, line in shared_aggregation_calls.items()
            if name in EXPRESSION_TYPE_NAMES
        }
        if len(shared_aggregation_types) >= 2:
            all_dispatch[("agentic_mbse/sysml/aggregation.py", "_decompose_node")] = (
                shared_aggregation_types
            )
        dual_check = {
            key: types
            for key, types in all_dispatch.items()
            if "FeatureChainExpression" in types and "OperatorExpression" in types
        }
        assert len(dual_check) == 3, (
            f"Expected 3 dual-check sites (FCE+OE), found {len(dual_check)}: "
            f"{sorted(dual_check.keys())}"
        )

    def test_total_dispatch_function_count(self):
        """Exactly 7 audited functions dispatch on 2+ expression types.

        The exact-ID elaborator contributes three FCE/FRE-only functions:
        classification, binding evidence, and reference collection."""
        all_dispatch = find_all_dispatch_functions(SRC_ROOT, EXPRESSION_TYPE_NAMES)
        shared_classifier_calls = find_is_instance_calls_in_function(
            AGENTIC_HIERARCHY_PATH,
            "classify_redefinition",
            predicate=is_any_is_instance_call,
        )
        shared_classifier_types = {
            name: line
            for name, line in shared_classifier_calls.items()
            if name in EXPRESSION_TYPE_NAMES
        }
        if len(shared_classifier_types) >= 2:
            all_dispatch[("agentic_mbse/sysml/hierarchy.py", "classify_redefinition")] = (
                shared_classifier_types
            )
        shared_aggregation_calls = find_is_instance_calls_in_function(
            AGENTIC_AGGREGATION_PATH,
            "_decompose_node",
            predicate=is_any_is_instance_call,
        )
        shared_aggregation_types = {
            name: line
            for name, line in shared_aggregation_calls.items()
            if name in EXPRESSION_TYPE_NAMES
        }
        if len(shared_aggregation_types) >= 2:
            all_dispatch[("agentic_mbse/sysml/aggregation.py", "_decompose_node")] = (
                shared_aggregation_types
            )
        multi_type = {key: types for key, types in all_dispatch.items() if len(types) >= 2}
        assert len(multi_type) == 7, (
            f"Expected 7 audited multi-type dispatch functions, found {len(multi_type)}: "
            f"{sorted(multi_type.keys())}"
        )


# ---------------------------------------------------------------------------
# REQ-AST-05: FCE -> SingletonTerm in aggregation
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-AST-05")
class TestReqAst05SingletonTermClassification:
    """FCE nodes in aggregation AST must be classified as SingletonTerm, not LocalTerm."""

    def test_fce_classified_as_singleton_term_solar_battery(self, solar_battery_facts):
        """Every SingletonTerm in solar_battery has dotted source_path (from FCE)."""
        hd = solar_battery_facts["hierarchy_data"]
        for agg in hd.aggregation_expressions:
            for st in agg.singleton_terms:
                assert "." in st.source_path, (
                    f"SingletonTerm source_path={st.source_path!r} missing '.' "
                    f"(expected dotted FCE path) in aggregation {agg.attribute_name}"
                )

    def test_no_singleton_term_in_local_terms(self, solar_battery_facts):
        """No LocalTerm has a dotted attribute_name (Bug A regression)."""
        hd = solar_battery_facts["hierarchy_data"]
        for agg in hd.aggregation_expressions:
            for lt in agg.local_terms:
                assert "." not in lt.attribute_name, (
                    f"LocalTerm attribute_name={lt.attribute_name!r} contains '.' -- "
                    f"Bug A regression: FCE misclassified as LocalTerm in "
                    f"aggregation {agg.attribute_name}"
                )

    def test_walk_aggregation_ast_fce_produces_singleton_behavioral(self):
        """Behavioral: dual-match FCE+OE mock node -> SingletonTerm in _AggregationContext.

        Uses SysideAdapter name-based fallback (no monkeypatch needed).
        """
        from sysml_codegen.extraction.hierarchy_resolver import (
            _AggregationContext,
            _walk_aggregation_ast,
        )

        node = MockFeatureChainExpressionOperatorExpression(
            operands=[MockFeatureReferenceExpression("child")],
            target_feature=SimpleNamespace(name="attr"),
        )

        ctx = _AggregationContext()
        _walk_aggregation_ast(node, {}, ctx)

        assert len(ctx.singleton_terms) == 1, (
            f"Expected 1 SingletonTerm, got {len(ctx.singleton_terms)}"
        )
        assert "child" in ctx.singleton_terms[0].source_path, (
            f"SingletonTerm source_path={ctx.singleton_terms[0].source_path!r} missing 'child'"
        )
        assert len(ctx.local_terms) == 0, (
            f"Expected 0 LocalTerms (FCE should not be classified as LocalTerm), "
            f"got {len(ctx.local_terms)}"
        )


# ---------------------------------------------------------------------------
# REQ-AST-06 retired (CONSTRAINT-EXEC Item 13): its two tests exercised
# build_expression_ast's FCE diagnostic directly. That dispatch responsibility moved
# cross-repo to agentic-mbse's extract_expression_ir; the calc-compat renderer's own
# feature-chain rejection is covered by
# tests/unit/test_expression_compiler.py, in
# TestRenderCalcExpression.test_feature_chain_raises_compilation_error.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# REQ-AST-07: reconstruct_expression FCE output format
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-AST-07")
class TestReqAst07ReconstructExpressionFormat:
    """reconstruct_expression must return 'name.attr' for FCE, not '.(name)'."""

    def test_reconstruct_expression_fce_returns_dotted_name(self):
        """Dual-match FCE+OE mock with operands=[FRE('instance')] and
        target_feature.name='attr' -> returns 'instance.attr'."""
        from sysml_codegen.extraction.expression_utils import reconstruct_expression

        node = MockFeatureChainExpressionOperatorExpression(
            operands=[MockFeatureReferenceExpression("instance")],
            target_feature=SimpleNamespace(name="attr"),
        )
        result = reconstruct_expression(node)
        assert result == "instance.attr", f"Expected 'instance.attr', got {result!r}"

    def test_reconstruct_expression_fce_no_dot_paren_format(self):
        """Dual-match FCE+OE mock -> result does NOT contain '.(' pattern (Bug A symptom)."""
        from sysml_codegen.extraction.expression_utils import reconstruct_expression

        node = MockFeatureChainExpressionOperatorExpression(
            operands=[MockFeatureReferenceExpression("instance")],
            target_feature=SimpleNamespace(name="attr"),
        )
        result = reconstruct_expression(node)
        assert ".(" not in result, f"Bug A regression: result contains '.(' pattern: {result!r}"

    def test_transformed_expressions_no_dot_paren_in_snapshots(self, solar_battery_facts):
        """No solar_battery transformed_expression contains the '.()' pattern."""
        hd = solar_battery_facts["hierarchy_data"]
        for agg in hd.aggregation_expressions:
            assert ".(" not in agg.transformed_expression, (
                f"Bug A regression: aggregation {agg.attribute_name} "
                f"transformed_expression contains '.(' pattern: "
                f"{agg.transformed_expression!r}"
            )


# ---------------------------------------------------------------------------
# Regression: order reversal detection
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-AST-01")
class TestRegressionOrderReversal:
    """Verify the current code takes the FCE path for dual-match nodes."""

    def test_regression_if_oe_checked_before_fce_in_walk_agg_ast(self):
        """Construct dual-match FCE+OE mock node. With correct dispatch order,
        _walk_aggregation_ast classifies it as SingletonTerm (FCE handler).
        If OE handler fired instead, the node would be recursed into as an
        operator expression, producing wrong results."""
        from sysml_codegen.extraction.hierarchy_resolver import (
            _AggregationContext,
            _walk_aggregation_ast,
        )

        node = MockFeatureChainExpressionOperatorExpression(
            operands=[MockFeatureReferenceExpression("pv_module")],
            target_feature=SimpleNamespace(name="capital_cost"),
        )

        ctx = _AggregationContext()
        result = _walk_aggregation_ast(node, {}, ctx)

        # FCE handler produces a chain name and SingletonTerm
        assert result == "pv_module.capital_cost", (
            f"Expected 'pv_module.capital_cost', got {result!r}. "
            f"If this fails, FCE handler may not be firing (OE checked first?)"
        )
        assert len(ctx.singleton_terms) == 1, (
            f"Expected 1 SingletonTerm from FCE handler, got {len(ctx.singleton_terms)}. "
            f"If 0, OE handler may be firing instead of FCE."
        )
        assert ctx.singleton_terms[0].source_path == "pv_module.capital_cost"
        assert len(ctx.local_terms) == 0, (
            f"Expected 0 LocalTerms, got {len(ctx.local_terms)}. "
            f"LocalTerm would indicate FCE misclassified (Bug A)."
        )
