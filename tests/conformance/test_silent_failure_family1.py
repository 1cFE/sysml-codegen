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

import logging

import pytest

from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.usage_extractor import extract_calculation_usages
from tests.conftest import requires_license, snapshot_fixture

CLEAN_CORPUS = ["attr_expr_probe", "sample_model", "chain_spike_model"]


def _extract_live(fixture: str):
    fixture_dir = snapshot_fixture(fixture).parent
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
    from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

    fixture_dir = snapshot_fixture("d38_caret").parent
    ctx = build_pipeline_context([fixture_dir])
    aggs = ctx.hierarchy_data.aggregation_expressions if ctx.hierarchy_data else []
    caret = [a for a in aggs if a.attribute_name == "total_cost"]
    assert caret, f"no total_cost aggregation extracted: {[a.attribute_name for a in aggs]}"
    for a in caret:
        assert " ** " in a.transformed_expression, a.transformed_expression
        assert " ^ " not in a.transformed_expression, a.transformed_expression
        assert not a.has_unsupported_nodes, a.transformed_expression


# --- D3-9: empty-refs tripwire (RECLASSIFIED to guard) --------------------------


def test_d39_nonliteral_root_empty_refs_warns(caplog):
    """A genuine literal has a literal AST root. A *non*-literal root with zero
    extracted refs is suspicious (extract_feature_refs under-reported) — the
    classifier keeps returning LITERAL but must warn (tripwire), so a real
    computed attribute is not silently dropped as a constant. A plain sentinel is
    a legitimate non-literal input (its is_instance checks are all False)."""
    from sysml_codegen.extraction.computed_attribute_extractor import (
        _classify_attribute_expression,
    )
    from sysml_codegen.extraction.data_models import ComputedAttributeClassification

    non_literal_root = object()  # not a SysIDE literal node
    with caplog.at_level(logging.WARNING):
        result = _classify_attribute_expression(
            refs=[],
            owning_part_qualified_name="Pkg::Part",
            calc_usage_names=set(),
            sibling_attr_names=set(),
            expression_ast=non_literal_root,
            reference_chain=None,
        )
    assert result == ComputedAttributeClassification.LITERAL
    assert any("D3-9 tripwire" in r.message for r in caplog.records), caplog.records


def test_d39_no_ast_root_stays_silent(caplog):
    """The documented `not refs → LITERAL` branch stays silent when there is no
    AST root to judge (a genuine literal) — the tripwire fires only on a
    non-literal root."""
    from sysml_codegen.extraction.computed_attribute_extractor import (
        _classify_attribute_expression,
    )

    with caplog.at_level(logging.WARNING):
        _classify_attribute_expression(
            refs=[],
            owning_part_qualified_name="Pkg::Part",
            calc_usage_names=set(),
            sibling_attr_names=set(),
            expression_ast=None,
            reference_chain=None,
        )
    assert not any("D3-9 tripwire" in r.message for r in caplog.records)


# --- silent-on-clean (INV-6): Family-1 diagnostics silent on the clean corpus ---


@requires_license
@pytest.mark.parametrize("fixture", CLEAN_CORPUS)
def test_family1_silent_on_clean_corpus(fixture):
    """No Family-1 extraction warning fires on a clean corpus fixture (INV-6)."""
    _usages, report = _extract_live(fixture)
    assert report.warnings == [], f"{fixture} emitted warnings: {report.warnings}"
