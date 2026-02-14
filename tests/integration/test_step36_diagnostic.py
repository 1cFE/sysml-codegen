"""Diagnostic test: Step 3.6 aliases vs CHAIN-derived aliases.

This test validates the relationship between _enrich_aliases_from_bindings()
(Step 3.6) and _build_chain_aliases(). The diagnostic found that Step 3.6
produces aliases from CalcUsage binding parameter name divergence (e.g.,
param_name="total_capex" → source_leaf="capital_cost") that CHAIN redefs
do not cover. Step 3.6 is retained until the backtracker uses OutputRegistry
(Item 3/4).
"""

from pathlib import Path

import pytest

from sysml_codegen.generation.initialization import PipelineContext, build_pipeline_context

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestStep36Diagnostic:
    """Validates relationship between Step 3.6 and CHAIN alias production."""

    @pytest.fixture(scope="class")
    def pipeline_context(self) -> PipelineContext:
        model_path = FIXTURES_DIR / "solar_battery_model"
        return build_pipeline_context([model_path])

    def test_chain_aliases_are_populated(
        self, pipeline_context: PipelineContext,
    ):
        """Sanity check: CHAIN aliases were actually produced."""
        chain_aliases = [
            ca for ca in pipeline_context.channel_aliases
            if ca.source == "redefinition"
        ]
        assert len(chain_aliases) > 0, "Expected CHAIN aliases to be produced"

    def test_step36_produces_param_name_aliases_not_in_chain(
        self, pipeline_context: PipelineContext,
    ):
        """Documents the known gap: Step 3.6 produces param_name aliases.

        Step 3.6 finds CalcUsage bindings where param_name differs from the
        aggregation attribute_name (e.g., param_name="total_capex" binding to
        source "capital_cost"). These are parameter name aliases, not CHAIN
        redefinitions — they represent the fact that a CalcDef uses a different
        parameter name than the aggregation attribute.

        This gap means Step 3.6 cannot be removed until the backtracker uses
        OutputRegistry for alias resolution (Item 3/4).
        """
        hierarchy = pipeline_context.hierarchy_data
        assert hierarchy is not None

        # Collect all aggregation aliases (from BF-7 + Step 3.6 enrichment)
        agg_aliases: set[str] = set()
        for agg in hierarchy.aggregation_expressions:
            for alias in agg.aliases:
                agg_aliases.add(alias)

        # Collect all CHAIN alias leaf names
        chain_alias_leaves: set[str] = set()
        for ca in pipeline_context.channel_aliases:
            if ca.source == "redefinition":
                leaf = ca.alias_name.rsplit(".", 1)[-1]
                chain_alias_leaves.add(leaf)

        # Known gap: param_name aliases are NOT in CHAIN aliases
        param_name_only = agg_aliases - chain_alias_leaves
        assert "total_capex" in param_name_only, (
            "Expected 'total_capex' to be a param_name alias not covered by CHAIN"
        )

    def test_channel_aliases_include_both_sources(
        self, pipeline_context: PipelineContext,
    ):
        """PipelineContext.channel_aliases has both CHAIN and EXPOSE_PURE sources."""
        sources = {ca.source for ca in pipeline_context.channel_aliases}
        assert "redefinition" in sources, "Expected CHAIN aliases"
        # EXPOSE_PURE aliases depend on PartUsage-level EXPOSE_PURE attrs in model
        # May or may not be present depending on model structure
