"""The exact-ID calculation compiler, and the implementation it makes the stencil render.

Three properties, all about identity rather than spelling:

- Rendered member names collide across calculation definitions; declaration UUIDs do not.
  The compiler keys everything by UUID, so two definitions that render the same names keep
  separate expressions, separate dependencies, and separate results.
- The rendered implementation's assignment steps and return values follow the compiler's
  execution order and the projection's declaration-UUID output order. A flat list of compiled
  results cannot express either, which is what `exact_calc_ordering` exists to show.
- A reference the parser did not resolve has no declaration UUID, so it stops the compile
  rather than becoming a degraded verdict. Identity is the compiler's only input; missing
  identity is a refusal, not a result.
"""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest

from sysml_codegen.elaboration import project
from sysml_codegen.extraction import expression_compiler
from sysml_codegen.extraction.data_models import (
    AttributeInfo,
    CalculationDefinitionData,
)
from sysml_codegen.extraction.expression_compiler import (
    Compilability,
    compile_calc_def_exact,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.expression_evidence import calculation_dependencies
from tests.helpers.raw_elaboration import elaborate

pytestmark = requires_license


@pytest.fixture(scope="module")
def collision_calc_defs() -> tuple[object, list[CalculationDefinitionData]]:
    extractor = SysMLDataExtractor([FIXTURES_DIR / "elab_payload_identity"])
    assert extractor.load_models()
    return extractor.model, extractor.extract_calculation_definitions()


@pytest.fixture(scope="module")
def ordering_module():
    extractor = SysMLDataExtractor([FIXTURES_DIR / "exact_calc_ordering"])
    assert extractor.load_models()
    assert extractor.diagnostics is not None
    graph = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
    )
    projected = project(graph)
    return next(
        module for module in projected.modules if module.name.endswith("__split")
    )


def test_colliding_rendered_names_stay_distinct_by_definition_and_member_id(
    collision_calc_defs: tuple[object, list[CalculationDefinitionData]],
) -> None:
    """Two definitions rendering `same_output` compile to two results, not one."""
    model, calc_defs = collision_calc_defs
    dependencies = calculation_dependencies(model)
    results = [compile_calc_def_exact(calc_def, dependencies) for calc_def in calc_defs]

    assert {result.definition_id for result in results} == {
        calc_def.element_id for calc_def in calc_defs
    }
    assert len({result.definition_id for result in results}) == 2

    declared = [
        item
        for result in results
        for item in result.output_results
        if not item.is_undeclared_intermediate
    ]
    assert [item.output_name for item in declared] == ["same_output", "same_output"]
    assert len({item.output_id for item in declared}) == 2
    assert {item.python_expression for item in declared} == {
        "(hidden_value + 1.0)",
        "(inputs.same_input + 7.0)",
    }

    by_definition = {result.definition_id: result for result in results}
    for calc_def in calc_defs:
        result = by_definition[calc_def.element_id]
        assert result.declared_output_ids == tuple(
            member.element_id for member in calc_def.output_attributes
        )
        assert {item.output_id for item in result.output_results} == set(
            result.execution_order
        )
        assert all(
            item.output_id in calc_def.all_member_ids for item in result.output_results
        )


def test_an_exact_dependency_cycle_is_total_and_manual() -> None:
    """A cycle refuses every declared output by UUID and orders none of them."""
    definition_id = UUID("00000000-0000-5000-8000-000000000200")
    first_id = UUID("00000000-0000-5000-8000-000000000201")
    second_id = UUID("00000000-0000-5000-8000-000000000202")
    first_expression = object()
    second_expression = object()
    calc_def = CalculationDefinitionData(
        name="Cycle",
        qualified_name="Exact::Cycle",
        doc_comment="",
        calc_expressions=[],
        input_attributes=[],
        output_attributes=[
            AttributeInfo(name="first", element_id=first_id),
            AttributeInfo(name="second", element_id=second_id),
        ],
        references=[],
        source_file=Path("cycle.sysml"),
        element_id=definition_id,
        output_expression_asts_by_id={
            first_id: first_expression,
            second_id: second_expression,
        },
        all_member_ids={first_id, second_id},
        member_names_by_id={first_id: "first", second_id: "second"},
    )

    result = compile_calc_def_exact(
        calc_def,
        {first_id: (second_id,), second_id: (first_id,)},
    )

    assert result.definition_id == definition_id
    assert result.execution_order == ()
    assert result.overall_compilability is Compilability.MANUAL_REQUIRED
    assert {item.output_id for item in result.output_results} == {first_id, second_id}
    assert {item.unsupported_reason for item in result.output_results} == {
        "circular dependency detected"
    }


def test_a_member_without_an_evidence_row_is_refused_not_degraded() -> None:
    """An absent inventory row stops the compile; it does not become a MANUAL verdict.

    The legacy compiler answered an unresolved reference with a `MANUAL_REQUIRED` result and
    carried on, so a calculation whose dependency graph could not be built still produced a
    result object. The exact compiler has no fallback walk: if the conversion boundary did
    not supply the member's evidence row, there is no dependency answer. It raises instead.

    Named replacement for `test_expression_compiler.py`'s
    `test_edge1_unresolved_reference_verdict_escalation`, whose subject (verdict escalation
    on an unresolved reference) ends with `compile_calc_def`.
    """
    definition_id = UUID("00000000-0000-5000-8000-000000000300")
    input_id = UUID("00000000-0000-5000-8000-000000000301")
    output_id = UUID("00000000-0000-5000-8000-000000000302")
    expression = object()
    calc_def = CalculationDefinitionData(
        name="Unresolved",
        qualified_name="Exact::Unresolved",
        doc_comment="",
        calc_expressions=[],
        input_attributes=[AttributeInfo(name="given", element_id=input_id)],
        output_attributes=[AttributeInfo(name="answer", element_id=output_id)],
        references=[],
        source_file=Path("unresolved.sysml"),
        element_id=definition_id,
        output_expression_asts_by_id={output_id: expression},
        all_member_ids={input_id, output_id},
        member_names_by_id={input_id: "given", output_id: "answer"},
    )

    with pytest.raises(
        expression_compiler.CompilationError, match="no evidence row"
    ):
        compile_calc_def_exact(calc_def, {})


def test_an_undeclared_intermediate_is_assigned_before_the_output_that_uses_it(
    ordering_module,
) -> None:
    """`scaled` is a step in the rendered body, never a returned value."""
    context = ordering_module.auto_impl_context
    assert context is not None
    assert context.execution_steps[0].name == "scaled"
    assert context.execution_steps[0].expression == "(inputs.total * 2.0)"
    assert "scaled" not in [item.name for item in context.output_expressions]


def test_an_output_read_by_another_output_is_assigned_once_then_returned_by_name(
    ordering_module,
) -> None:
    """`half` feeds `doubled_half`, so it is a step and its return value is its name."""
    context = ordering_module.auto_impl_context
    assert [item.name for item in context.execution_steps] == ["scaled", "half"]
    assert context.execution_steps[1].expression == "(scaled / 4.0)"
    assert [(item.name, item.expression) for item in context.output_expressions] == [
        ("half", "half"),
        ("doubled_half", "(half * 2.0)"),
    ]


def test_returned_values_line_up_with_the_projected_output_schema(
    ordering_module,
) -> None:
    """The tuple the stencil returns is positionally the module's output list."""
    context = ordering_module.auto_impl_context
    assert [item.name for item in context.output_expressions] == [
        output.field_name for output in ordering_module.outputs
    ]
    assert context.output_count == len(ordering_module.outputs) == 2
    assert context.single_output_expression is None
