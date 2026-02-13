"""Bug 2 regression test: EXPOSE_PURE two-hop resolution failure.

Bug 2: In e2e_attr_expr (attr_expr_probe fixture), the EXPOSE_PURE attribute
`total_capex` on `e2e_plant` should wire to MODULE_OUTPUT (component_cost's
total_cost output), but instead falls through to ENTRY_POINT due to the
second-hop resolution failure with virtual CalcUsages.

This test is written BEFORE the fix (Item 1, epic OUTPUT-REGISTRY) and marked
xfail. When Item 3 (OutputRegistry backtracker integration) is complete,
the xfail is removed and this test goes green -- definitive proof the fix works.

See: .project/research/20260213-152845_bug2-expose-calcusage-wiring-persistent-failure.md
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.core.models import BindingResolutionType
from sysml_codegen.generation.initialization import build_pipeline_context

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestBug2ExposesPureTwoHopFailure:
    """Regression test for Bug 2: EXPOSE_PURE total_capex wiring."""

    @pytest.fixture(scope="class")
    def pipeline_context(self):
        model_path = FIXTURES_DIR / "attr_expr_probe"
        return build_pipeline_context([model_path])

    @pytest.mark.xfail(
        reason="Bug 2: EXPOSE_PURE two-hop failure -- total_capex resolves "
               "to ENTRY_POINT instead of MODULE_OUTPUT. Fix expected in "
               "epic OUTPUT-REGISTRY Item 3.",
        strict=True,
    )
    def test_total_capex_resolves_to_module_output(self, pipeline_context):
        """EXPOSE_PURE financial.total_capex should be MODULE_OUTPUT.

        In the current implementation, the second hop of transitive
        resolution fails for virtual CalcUsages because the output catalog
        key format doesn't match the dotted source_path format.
        """
        resolutions = pipeline_context.backtracking_result.binding_resolutions

        # Find the total_capex binding resolution
        capex_keys = [
            k for k in resolutions
            if "total_capex" in k or "capex" in k
        ]
        assert capex_keys, (
            "Expected at least one binding resolution containing 'total_capex' "
            f"or 'capex'. Available keys: {list(resolutions.keys())[:20]}"
        )

        # At least one total_capex resolution should be MODULE_OUTPUT
        capex_resolutions = [resolutions[k] for k in capex_keys]
        has_module_output = any(
            r.resolution_type == BindingResolutionType.MODULE_OUTPUT
            for r in capex_resolutions
        )
        assert has_module_output, (
            f"Bug 2: total_capex should resolve to MODULE_OUTPUT but got: "
            f"{[(k, r.resolution_type) for k, r in zip(capex_keys, capex_resolutions)]}"
        )
