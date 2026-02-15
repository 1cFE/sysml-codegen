"""Bug 2 regression test: EXPOSE_PURE two-hop resolution.

Bug 2: EXPOSE_PURE attributes that alias upstream CalcUsage outputs should
resolve to MODULE_OUTPUT, not fall through to ENTRY_POINT. This was caused
by the old cascade's second-hop resolution failure with virtual CalcUsages.

Fixed by OutputRegistry Phase 3 (ChannelAlias) which provides direct
single-lookup resolution for EXPOSE_PURE aliases.

Validated on solar_battery model where `total_capex` (input to
annualized_financial) is wired to the capital_cost aggregation output.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.generation.initialization import build_pipeline_context

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestBug2ExposePureTwoHopResolution:
    """Regression test for Bug 2: EXPOSE_PURE total_capex wiring."""

    @pytest.fixture(scope="class")
    def pipeline_context(self):
        return build_pipeline_context([FIXTURES_DIR / "solar_battery_model"])

    def test_total_capex_wired_to_module_output(self, pipeline_context):
        """EXPOSE_PURE total_capex is wired to capital_cost aggregation output.

        In solar_battery, annualized_financial.total_capex should be wired
        to the capital_cost aggregation module output (MODULE_OUTPUT), not
        treated as an entry point parameter.
        """
        graph = pipeline_context.computation_graph

        # Find annualized_financial module
        fin_modules = [
            m for m in graph.modules
            if "annualized_financial" in m.name
        ]
        assert fin_modules, (
            f"Expected annualized_financial module. "
            f"Available: {[m.name for m in graph.modules]}"
        )

        fin = fin_modules[0]
        capex_inputs = [
            inp for inp in fin.inputs
            if inp.param_name == "total_capex"
        ]
        assert capex_inputs, (
            f"Expected total_capex input on annualized_financial. "
            f"Inputs: {[i.param_name for i in fin.inputs]}"
        )

        capex = capex_inputs[0]
        assert capex.source.source_type == "module_output", (
            f"Bug 2: total_capex should be module_output (wired to "
            f"capital_cost aggregation) but is {capex.source.source_type}"
        )
