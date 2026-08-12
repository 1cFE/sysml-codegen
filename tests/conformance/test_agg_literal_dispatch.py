"""REQ-AST-10: literal operands in an aggregation dispatch to the literal branch.

Row D of PIPELINE-TRUTH Item 8. `_walk_aggregation_ast`
(`extraction/hierarchy_resolver.py`) must dispatch a literal operand to its
literal branch (``is_literal_expression`` -> ``reconstruct_expression``) BEFORE
the invocation catch-all. Every SysIDE node carries a derived KerML
``.function.name``, so before the Item-8 hoist a numeric literal inside an
aggregation hit the invocation catch-all first: ``has_unsupported_nodes`` flipped
True and the literal rendered as garbage (``LiteralRationalEvaluation()``).

`agg_literal_probe` is the sole committed fixture with a literal-bearing
aggregation (``:>> total_cost = sum(module.cost) + 5.0``). The walk result lives in the
raw ``hierarchy_data.aggregation_expressions`` entry (the scoped, design-instance path is
not exercised by this extraction-only probe).

This read the fixture's committed v5 extraction snapshot until that retired with the
family (retirement step 2). It now runs the walk itself, which is what the assertions are
about — so the node is license-gated where it used to be license-free, and it reads the
dataclass field rather than the serialized key of the same name.
"""

from __future__ import annotations

from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.hierarchy_resolver import extract_hierarchy_data
from tests.conftest import FIXTURES_DIR, requires_license


def _raw_aggregation(model_name: str, attribute_name: str):
    """Return the walked AggregationExpressionData for one aggregation attr."""
    extractor = SysMLDataExtractor([FIXTURES_DIR / model_name])
    assert extractor.load_models(), f"failed to load {model_name}"
    aggs = extract_hierarchy_data(extractor.model).aggregation_expressions
    for agg in aggs:
        if agg.attribute_name == attribute_name:
            return agg
    raise AssertionError(
        f"no aggregation named {attribute_name!r} in {model_name} "
        f"(found: {[a.attribute_name for a in aggs]})"
    )


class TestReqAst10LiteralDispatch:
    """REQ-AST-10: aggregation literal/null branches dispatch before invocation."""

    @requires_license
    def test_literal_operand_dispatches_to_literal_branch(self):
        """The `5.0` operand survives to the transformed expression, unsupported stays False.

        RED before the Item-8 hoist: the literal hit the invocation catch-all, so
        ``has_unsupported_nodes`` was True and the term rendered as
        ``LiteralRationalEvaluation()``. GREEN after: the literal branch runs first.
        """
        agg = _raw_aggregation("agg_literal_probe", "total_cost")

        # The raw text is unchanged either way — sanity anchor on the input shape.
        assert agg.raw_expression_text == "sum(module.cost) + 5.0"

        # The corrected dispatch: the literal is not mis-classified as unsupported...
        assert agg.has_unsupported_nodes is False
        # ...and it survives into the transformed expression as a literal, not garbage.
        assert "5.0" in agg.transformed_expression
        assert "LiteralRationalEvaluation" not in agg.transformed_expression
