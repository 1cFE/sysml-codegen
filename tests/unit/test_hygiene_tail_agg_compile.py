"""D3 Hygiene Tail Site 2 — aggregation-compile `.replace()` collision
(TRUTH-DEBT Item 6).

`_build_aggregation_module`'s compile loop substituted symbolic refs with
their `inputs.X` form via a plain `str.replace()`. When one ref is a
substring of another (`cost` / `cost_total`), the length-sort only orders
the pass over the *original* text — the `inputs.` substitution reintroduces
the collision: replacing `cost_total` first leaves a bare `cost` inside
`inputs.cost_total`, and the next pass's `.replace("cost", ...)` matches it,
producing `inputs.inputs.cost_total`. The fix anchors each ref to a whole
token (`\\b`) so a later pass can never match inside an earlier
substitution's output. Expectations are anchored to the hand-written
expected compiled string, never computed by the code under test (R1).
"""

from __future__ import annotations

from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.extraction.data_models import (
    AggregationExpressionData,
    ScopedAggregationData,
    SingletonTerm,
)
from sysml_codegen.resolution.graph_builder import _build_aggregation_module


def _build(refs_expr: str, source_paths: list[str]) -> str | None:
    expr = AggregationExpressionData(
        owning_part_qn="Lib__Widget",
        owning_part_name="Widget",
        attribute_name="net",
        raw_expression_text=refs_expr,
        transformed_expression=refs_expr,
        sum_terms=[],
        singleton_terms=[SingletonTerm(source_path=p) for p in source_paths],
        local_terms=[],
        input_channels=[],
        entry_points=[],
        has_unsupported_nodes=False,
    )
    agg = ScopedAggregationData(expression=expr, instance_path="Design__plant__widget")
    module, _ = _build_aggregation_module(agg, [], OutputRegistry(), {}, None)
    return module.compiled_expression


def test_nested_ref_names_do_not_corrupt():
    compiled = _build("cost + cost_total", ["cost", "cost_total"])
    assert compiled == "inputs.cost + inputs.cost_total"
    assert "inputs.inputs." not in (compiled or "")


def test_disjoint_ref_names_unchanged():
    compiled = _build("a + b", ["a", "b"])
    assert compiled == "inputs.a + inputs.b"
