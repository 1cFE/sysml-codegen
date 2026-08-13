"""The fourth lane: a unit annotation on a constraint usage binding.

`_binding_evidence` (`elaborate.py:1839-1846`) classifies a binding expression chain →
reference → literal → else expression. A unit annotation is an `OperatorExpression`, so
`in tol = 0.05 [m];` was none of the first three and fell to `expression_evidence`,
which stamps `EXPRESSION_SOURCE` and gets refused as
`SI_EXPRESSION_SOURCE_UNSUPPORTED` — the same category error as Defect A, one lane over.

The lane matters because it is Item 5's blessed tolerance-band recipe, and because the
rewrite Defect B's new message advertises *is* a binding. A diagnostic that sends a
modeler into a lane that still refuses would be worse than the tautology it replaces.

The cure admits exactly two shapes: an annotated literal and an annotated
reference/chain. `bad_band` is the bound — `a + b` has an operator that is not `[`, so
it passes through the unwrap unchanged and is still refused.

Read non-strict, because `bad_band` is *meant* to keep producing a readiness finding and
strict elaboration turns any finding into a halt.
"""

from __future__ import annotations

import pytest

from sysml_codegen.elaboration import elaborate
from sysml_codegen.elaboration.graph import InstanceGraph, LiteralInput, NodeRef
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "constraint_binding_unit_annotation"

@pytest.fixture(scope="module")
def graph() -> InstanceGraph:
    extractor = SysMLDataExtractor([FIXTURE])
    assert extractor.load_models()
    assert extractor.diagnostics is not None
    return elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
        strict=False,
    )


def _bindings(graph: InstanceGraph, usage_suffix: str) -> dict[str, object]:
    [node] = [
        node for node in graph.constraints.values() if node.display_path.endswith(usage_suffix)
    ]
    return {node.input_names[port]: value for port, value in node.inputs.items()}


def _refused_formals(graph: InstanceGraph) -> set[str]:
    """`{usage_display}.{formal}` for every expression-source refusal on this graph."""
    return {
        f"{diagnostic.consumer_display}.{diagnostic.param_name}"
        for diagnostic in graph.diagnostics
        if diagnostic.code.value == "SI_EXPRESSION_SOURCE_UNSUPPORTED"
    }


def test_an_annotated_literal_binding_is_read_as_its_value(graph: InstanceGraph) -> None:
    """Shape (i): `in tol = 0.05 [m];` contributes the number, and the number is 0.05.

    The annotation leaves the evidence text with it: `literal_evidence` sets
    `written_text = str(literal_value)`, so it reads `"0.05"`, not `"0.05 [m]"`. That is
    the rule, not a loss — the annotation contributed its operand.
    """
    assert _bindings(graph, "__band")["tol"] == LiteralInput(0.05)


def test_an_annotated_reference_binding_is_read_as_a_reference(graph: InstanceGraph) -> None:
    """Shape (ii): `in ref_value = other_feature [m];` still names the feature it binds."""
    assert isinstance(_bindings(graph, "__band")["ref_value"], NodeRef)


def test_neither_annotated_binding_is_refused_as_an_expression_source(
    graph: InstanceGraph,
) -> None:
    assert not [name for name in _refused_formals(graph) if "__band." in name]


@pytest.mark.parametrize(
    "refused_formal",
    ["__bad_band.tol", "__invoked_band.tol"],
    ids=["arithmetic", "invocation"],
)
def test_a_genuine_expression_source_is_still_refused(
    graph: InstanceGraph, refused_formal: str
) -> None:
    """The bound on what D2 admits, on both members the design named.

    Arithmetic (`in tol = a + b;`) and an invocation (`in tol = sum(other_feature);`) each
    carry an operator that is not `[`, so `annotated_ast_value` returns them unchanged,
    `_binding_evidence` still falls through to `expression_evidence`, and `_unsupported_code`
    still refuses them. The unwrap admits annotations, not expressions.
    """
    assert [name for name in _refused_formals(graph) if name.endswith(refused_formal)]


def test_an_annotated_chain_binding_resolves_as_a_chain(graph: InstanceGraph) -> None:
    """The other edge of shape (ii): `in ref_value = cell.reading [m];`.

    Named in D2's admitted set alongside the plain reference and otherwise untested. The
    unwrap contributes the chain, so `_binding_evidence` classifies it as a chain binding and
    it resolves to the cross-part attribute, instead of falling to `expression_evidence`.
    """
    bindings = _bindings(graph, "__chain_band")
    assert isinstance(bindings["ref_value"], NodeRef)
    assert bindings["tol"] == LiteralInput(0.05)
    assert not [name for name in _refused_formals(graph) if "__chain_band." in name]
