"""REQ-AST-10: literal operands in an aggregation dispatch to the literal branch.

Row D of PIPELINE-TRUTH Item 8. `_walk_aggregation_ast`
(`extraction/hierarchy_resolver.py`) must dispatch a literal operand to its
literal branch (``is_literal_expression`` -> ``reconstruct_expression``) BEFORE
the invocation catch-all. Every SysIDE node carries a derived KerML
``.function.name``, so before the Item-8 hoist a numeric literal inside an
aggregation hit the invocation catch-all first: ``has_unsupported_nodes`` flipped
True and the literal rendered as garbage (``LiteralRationalEvaluation()``).

`agg_literal_probe` is the sole committed fixture with a literal-bearing
aggregation (``:>> total_cost = sum(module.cost) + 5.0``). Its captured snapshot
pins the corrected dispatch: the walk result lives in the raw
``hierarchy_data.aggregation_expressions`` entry (the scoped, design-instance path
is not exercised by this extraction-only probe).
"""

from __future__ import annotations

import json

from tests.conftest import snapshot_fixture


def _raw_aggregation(model_name: str, attribute_name: str) -> dict:
    """Return the raw walked AggregationExpressionData for one aggregation attr."""
    snapshot = json.loads(snapshot_fixture(model_name).read_text())
    aggs = snapshot["hierarchy_data"]["aggregation_expressions"]
    for agg in aggs:
        if agg["attribute_name"] == attribute_name:
            return agg
    raise AssertionError(
        f"no aggregation named {attribute_name!r} in {model_name} "
        f"(found: {[a.get('attribute_name') for a in aggs]})"
    )


class TestReqAst10LiteralDispatch:
    """REQ-AST-10: aggregation literal/null branches dispatch before invocation."""

    def test_literal_operand_dispatches_to_literal_branch(self):
        """The `5.0` operand survives to the transformed expression, unsupported stays False.

        RED before the Item-8 hoist: the literal hit the invocation catch-all, so
        ``has_unsupported_nodes`` was True and the term rendered as
        ``LiteralRationalEvaluation()``. GREEN after: the literal branch runs first.
        """
        agg = _raw_aggregation("agg_literal_probe", "total_cost")

        # The raw text is unchanged either way — sanity anchor on the input shape.
        assert agg["raw_expression_text"] == "sum(module.cost) + 5.0"

        # The corrected dispatch: the literal is not mis-classified as unsupported...
        assert agg["has_unsupported_nodes"] is False
        # ...and it survives into the transformed expression as a literal, not garbage.
        assert "5.0" in agg["transformed_expression"]
        assert "LiteralRationalEvaluation" not in agg["transformed_expression"]
