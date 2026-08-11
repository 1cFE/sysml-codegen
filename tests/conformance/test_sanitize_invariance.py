"""Literal generated-name invariance on the public exact projector."""

from sysml_codegen.core.qualified_names import sanitize_name
from sysml_codegen.orchestration import build_pipeline_context
from tests.conftest import FIXTURES_DIR, requires_license


@requires_license
def test_quoted_owner_projects_to_the_pinned_literal_names() -> None:
    """The authored quoted owner changes once, at the presentation boundary."""
    context = build_pipeline_context([FIXTURES_DIR / "quoted_owner_formula"])

    assert sanitize_name("'Margin Part'") == "Margin_Part"
    assert [(module.name, module.module_type) for module in context.computation_graph.modules] == [
        (
            "quotedownerformuladesign__margin_part__net_margin",
            "quotedownerformuladesign.margin_part.net_marginModule",
        ),
        (
            "quotedownerformuladesign__margin_part__total_payout",
            "quotedownerformuladesign.margin_part.total_payoutModule",
        ),
    ]
