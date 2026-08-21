"""Family 1 — Blind-dispatch fall-throughs made total and loud (PIPELINE-TRUTH Item 5).

INV-1 (totality): every terminal dispatch arm on a load-bearing extraction path
routes an unhandled input to a *distinct*, warned disposition — never a silent
reuse of a valid category (UNBOUND, XOR pass-through).

Findings covered here: D3-1 (unhandled binding-expr type), D3-8 (`^` aggregation
operator), D3-9 (empty-refs tripwire). D3-2's fires-on-shape lives with its fixture
(test_deep_cross_scope_probe.py). Expectations are independently anchored to the
fixture source, never computed by the code under test (R1).
"""

from __future__ import annotations

import pytest

from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.usage_extractor import extract_calculation_usages
from tests.conftest import FIXTURES_DIR, requires_license

CLEAN_CORPUS = ["attr_expr_probe", "sample_model", "chain_spike_model"]


def _extract_live(fixture: str):
    fixture_dir = FIXTURES_DIR / fixture
    extractor = SysMLDataExtractor([fixture_dir])
    assert extractor.load_models(), f"failed to load {fixture}"
    calc_defs = extractor.extract_calculation_definitions()
    return extract_calculation_usages(extractor.model, calc_defs=calc_defs)


# --- D3-1: unhandled binding-expression type (InvocationExpression) -------------


@requires_license
def test_d31_invocation_binding_warns_not_silent():
    """`in x = Doubler(v=a)` is an InvocationExpression — not one of the four
    handled dispatch types. The silent fall-through gave `x` an entry point with
    NO diagnostic; the fix WARNS (naming the param + node type). ADR-003 requires
    every input to resolve, so `x` stays an entry point — now a loud one, not a
    silent one — and is not mis-classified as a real binding."""
    usages, report = _extract_live("invocation_binding_probe")
    assert any(
        "InvocationExpression" in w and "x" in w for w in report.warnings
    ), report.warnings
    for u in usages:
        if u.instance_name == "c":
            # Not fabricated as a real binding (it is not a resolvable ref/chain).
            assert "x" not in {b.param_name for b in u.bindings}, u.bindings
            # It is a loud entry point (warned above), per ADR-003.
            assert "x" in u.unbound_params, u.unbound_params


# --- D3-8: `^` aggregation operator is power, not Python XOR ---------------------


@requires_license
def test_d38_caret_aggregation_compiles_to_power_not_xor():
    """`total_cost = sum(cell.total_cost) ^ exponent`: `^` is exponentiation and
    must translate to Python ` ** `, never ` ^ ` (bitwise XOR). All operands are
    known, so has_unsupported_nodes stays False."""
    from sysml_codegen.extraction.hierarchy_resolver import extract_hierarchy_data

    # Read the aggregation walk from its own owner. This node used to reach it through
    # ``build_pipeline_context``, which retired with the v5 family (retirement step 2);
    # the walk itself is in ``extraction/hierarchy_resolver.py`` and is what the
    # assertions are about, so the legacy builder was only ever a courier.
    extractor = SysMLDataExtractor([FIXTURES_DIR / "d38_caret"])
    assert extractor.load_models(), "failed to load d38_caret"
    aggs = extract_hierarchy_data(extractor.model).aggregation_expressions
    caret = [a for a in aggs if a.attribute_name == "total_cost"]
    assert caret, f"no total_cost aggregation extracted: {[a.attribute_name for a in aggs]}"
    for a in caret:
        assert " ** " in a.transformed_expression, a.transformed_expression
        assert " ^ " not in a.transformed_expression, a.transformed_expression
        assert not a.has_unsupported_nodes, a.transformed_expression


# --- silent-on-clean (INV-6): Family-1 diagnostics silent on the clean corpus ---


@requires_license
@pytest.mark.parametrize("fixture", CLEAN_CORPUS)
def test_family1_silent_on_clean_corpus(fixture):
    """No Family-1 extraction warning fires on a clean corpus fixture (INV-6)."""
    _usages, report = _extract_live(fixture)
    assert report.warnings == [], f"{fixture} emitted warnings: {report.warnings}"
