"""The unsuffixed calculation compiler is the sole exact-ID compiler core."""

from __future__ import annotations

import inspect
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest

from sysml_codegen.extraction import expression_compiler
from sysml_codegen.extraction.data_models import AttributeInfo, CalculationDefinitionData
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license


@pytest.fixture(scope="module")
def calc_defs():
    extractor = SysMLDataExtractor([FIXTURES_DIR / "elab_payload_identity"])
    assert extractor.load_models()
    return extractor.extract_calculation_definitions()


def test_all_call_shapes_use_one_id_keyed_compiler_core(calc_defs) -> None:
    assert "compile_calc_def" + "_exact" not in vars(expression_compiler)
    assert list(inspect.signature(expression_compiler.compile_calc_def).parameters) == [
        "calc_def"
    ]

    results = [expression_compiler.compile_calc_def(calc_def) for calc_def in calc_defs]
    assert {result.definition_id for result in results} == {
        calc_def.element_id for calc_def in calc_defs
    }
    assert {type(result).__name__ for result in results} == {"CalcDefCompilationResult"}

    by_definition = {result.definition_id: result for result in results}
    for calc_def in calc_defs:
        result = by_definition[calc_def.element_id]
        assert result.declared_output_ids == tuple(
            member.element_id for member in calc_def.output_attributes
        )
        assert set(result.execution_order) == {
            item.output_id for item in result.output_results
        }
        assert all(item.output_id in calc_def.all_member_ids for item in result.output_results)

    first = next(
        result
        for result in results
        if len(result.output_results) == 2
    )
    intermediate, output = first.output_results
    assert intermediate.python_expression == "(inputs.same_input * 3.0)"
    assert output.python_expression == "(hidden_value + 1.0)"
    assert intermediate.input_ids
    assert output.dependency_ids == (intermediate.output_id,)


def test_same_rendered_names_remain_distinct_by_definition_and_member_id(calc_defs) -> None:
    results = [expression_compiler.compile_calc_def(calc_def) for calc_def in calc_defs]
    assert len({result.definition_id for result in results}) == 2
    outputs = [
        item
        for result in results
        for item in result.output_results
        if not item.is_undeclared_intermediate
    ]
    assert [item.output_name for item in outputs] == ["same_output", "same_output"]
    assert len({item.output_id for item in outputs}) == 2
    assert len({item.input_ids for item in outputs}) == 2


def test_exact_dependency_cycle_is_total_and_manual(monkeypatch) -> None:
    definition_id = UUID("00000000-0000-5000-8000-000000000200")
    first_id = UUID("00000000-0000-5000-8000-000000000201")
    second_id = UUID("00000000-0000-5000-8000-000000000202")
    first_expression = object()
    second_expression = object()
    refs = {
        id(first_expression): [
            SimpleNamespace(name="second", element=SimpleNamespace(element_id=second_id))
        ],
        id(second_expression): [
            SimpleNamespace(name="first", element=SimpleNamespace(element_id=first_id))
        ],
    }
    monkeypatch.setattr(
        expression_compiler,
        "extract_feature_refs",
        lambda expression, ignore_std_lib=True: refs[id(expression)],
    )
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
        output_expression_asts={
            first_id: first_expression,
            second_id: second_expression,
        },
        all_member_ids={first_id, second_id},
        member_names={first_id: "first", second_id: "second"},
    )

    result = expression_compiler.compile_calc_def(calc_def)

    assert result.definition_id == definition_id
    assert result.execution_order == ()
    assert {item.output_id for item in result.output_results} == {first_id, second_id}
    assert all(item.compilability.value == "manual_required" for item in result.output_results)
    assert {item.unsupported_reason for item in result.output_results} == {
        "circular dependency detected"
    }
