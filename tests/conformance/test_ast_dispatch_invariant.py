"""AST dispatch-order audit over the live tree.

The FCE-before-OE invariant: a dual-match syside node (FeatureChainExpression that is
also an OperatorExpression) must hit the FCE handler first, or chains are silently
mis-decomposed. The parametrized site audits over the legacy extraction lane
(``usage_extractor._extract_single_binding``, ``hierarchy_resolver._walk_aggregation_ast``)
and over agentic-mbse's ``_decompose_node`` / ``classify_redefinition`` retired with that
lane (REPO-CLEANUP Move C, 2026-08-25): no live code imports those subjects. What remains
live is the guardrail — no unaudited dispatch site may appear in ``src/`` — and the
``reconstruct_expression`` output-format legs, whose subject ``extraction/expression_utils``
is called from the live extractor (``extraction/extractor.py``).
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from uuid import NAMESPACE_URL, uuid5

import pytest
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from tests.helpers.static_analysis import find_all_dispatch_functions

# ---------------------------------------------------------------------------
# Source paths for static analysis
# ---------------------------------------------------------------------------

SRC_ROOT = Path(__file__).parent.parent.parent / "src" / "sysml_codegen"

# Expression type names used for dispatch site identification
EXPRESSION_TYPE_NAMES = frozenset(
    {
        "FeatureChainExpression",
        "OperatorExpression",
        "FeatureReferenceExpression",
    }
)

#: The audited live multi-type dispatch sites (each dispatches on 2+ expression types).
#: Both check FeatureChainExpression before FeatureReferenceExpression; neither touches
#: OperatorExpression, so no FCE+OE dual-check site exists in the live tree at all.
AUDITED_MULTI_TYPE_SITES = {
    ("elaboration/elaborate.py", "_is_reference_expression"),
    ("elaboration/expression_evidence.py", "_is_plain_reference"),
}


# ---------------------------------------------------------------------------
# Mock infrastructure (SysIDE adapter boundary stubs)
# ---------------------------------------------------------------------------


class MockFeatureReferenceExpression:
    """Mock syside FeatureReferenceExpression node."""

    def __init__(self, name: str):
        self.referent = _semantic_feature(name)


class MockFeatureChainExpression:
    """Exact-MRO adapter test double for a feature-chain expression."""


class MockOperatorExpression:
    """Exact-MRO adapter test double for an operator expression."""


class MockFeatureChainExpressionOperatorExpression(
    MockFeatureChainExpression,
    MockOperatorExpression,
):
    """Mock that dual-matches both FeatureChainExpression and OperatorExpression.

    Its MRO carries both exact mapped test-double names. Used to verify that the
    FCE handling fires first when both metatype checks match.
    """

    def __init__(self, operands: list | None = None, target_feature=None):
        self.operator = "."
        self.operands = operands or []
        self.target_feature = target_feature


def _semantic_feature(name: str) -> SimpleNamespace:
    """An exact semantic target accepted by Agentic's reference-use boundary."""
    return SimpleNamespace(
        name=name,
        qualified_name=f"Mock::{name}",
        element_id=uuid5(NAMESPACE_URL, f"https://sysml-codegen.test/mock/{name}"),
        owned_redefinitions=(),
        owning_type=None,
        document=SimpleNamespace(
            url="file:///mock.sysml",
            document_tier=SysideAdapter.document_tier_type().Project,
        ),
    )


# ---------------------------------------------------------------------------
# REQ-AST-04: Total dispatch site guardrail
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-AST-04")
class TestReqAst04DispatchSiteGuardrail:
    """Guard against new unaudited dispatch sites appearing in the codebase."""

    def test_no_dual_check_site_exists(self):
        """Zero functions in src/ check both FCE and OE via is_instance().

        The two audited dual-check sites (agentic aggregation _decompose_node,
        usage_extractor._extract_single_binding) retired with the legacy extraction
        lane. A new FCE+OE site must be audited for FCE-before-OE ordering and added
        here deliberately, never silently.
        """
        all_dispatch = find_all_dispatch_functions(SRC_ROOT, EXPRESSION_TYPE_NAMES)
        dual_check = {
            key: types
            for key, types in all_dispatch.items()
            if "FeatureChainExpression" in types and "OperatorExpression" in types
        }
        assert dual_check == {}, (
            f"Unaudited FCE+OE dual-check sites appeared: {sorted(dual_check.keys())}"
        )

    def test_total_dispatch_function_count(self):
        """Exactly the audited functions dispatch on 2+ expression types."""
        all_dispatch = find_all_dispatch_functions(SRC_ROOT, EXPRESSION_TYPE_NAMES)
        multi_type = {key: types for key, types in all_dispatch.items() if len(types) >= 2}
        assert set(multi_type) == AUDITED_MULTI_TYPE_SITES, (
            f"Audited set drifted: found {sorted(multi_type.keys())}"
        )

    def test_audited_sites_check_fce_before_fre(self):
        """Both live multi-type sites check FCE before the broader FRE."""
        all_dispatch = find_all_dispatch_functions(SRC_ROOT, EXPRESSION_TYPE_NAMES)
        for site in sorted(AUDITED_MULTI_TYPE_SITES):
            calls = all_dispatch[site]
            assert calls["FeatureChainExpression"] < calls["FeatureReferenceExpression"], (
                f"{site}: FCE at {calls['FeatureChainExpression']} must precede "
                f"FRE at {calls['FeatureReferenceExpression']}"
            )


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
            target_feature=_semantic_feature("attr"),
        )
        result = reconstruct_expression(node)
        assert result == "instance.attr", f"Expected 'instance.attr', got {result!r}"

    def test_reconstruct_expression_fce_no_dot_paren_format(self):
        """Dual-match FCE+OE mock -> result does NOT contain '.(' pattern (Bug A symptom)."""
        from sysml_codegen.extraction.expression_utils import reconstruct_expression

        node = MockFeatureChainExpressionOperatorExpression(
            operands=[MockFeatureReferenceExpression("instance")],
            target_feature=_semantic_feature("attr"),
        )
        result = reconstruct_expression(node)
        assert ".(" not in result, f"Bug A regression: result contains '.(' pattern: {result!r}"
