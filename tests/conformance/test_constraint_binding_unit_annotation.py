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

_ITEM4_D2 = "CONSTRAINT-SEMANTICS Item 4 — the fourth lane (D2)"


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


@pytest.mark.xfail(strict=True, reason=_ITEM4_D2)
def test_an_annotated_literal_binding_is_read_as_its_value(graph: InstanceGraph) -> None:
    """Shape (i): `in tol = 0.05 [m];` contributes the number, and the number is 0.05."""
    assert _bindings(graph, "__band")["tol"] == LiteralInput(0.05)


@pytest.mark.xfail(strict=True, reason=_ITEM4_D2)
def test_an_annotated_reference_binding_is_read_as_a_reference(graph: InstanceGraph) -> None:
    """Shape (ii): `in ref_value = other_feature [m];` still names the feature it binds."""
    assert isinstance(_bindings(graph, "__band")["ref_value"], NodeRef)


@pytest.mark.xfail(strict=True, reason=_ITEM4_D2)
def test_neither_annotated_binding_is_refused_as_an_expression_source(
    graph: InstanceGraph,
) -> None:
    assert not [name for name in _refused_formals(graph) if "__band." in name]


def test_a_genuine_expression_source_is_still_refused(graph: InstanceGraph) -> None:
    """The bound on what D2 admits: `in tol = a + b;` is arithmetic, not an annotation."""
    assert [name for name in _refused_formals(graph) if name.endswith("__bad_band.tol")]
