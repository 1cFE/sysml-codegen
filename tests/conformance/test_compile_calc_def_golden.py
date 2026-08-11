"""Exact compiler output projected onto the maintained name-rendering golden.

`tests/fixtures/golden/calc_def_compilation_golden.json` was captured live, over the whole
calc-def corpus, from `compile_calc_def` **before** it was flipped onto
`extract_expression_ir`/`render_calc_expression`/`collect_calc_refs` (the F4 rule: the
comparand is the exact replaced function's output, not a downstream proxy). This test asserts
the exact-ID `compile_calc_def` reproduces every rendered output field -- `python_expression`,
input/dependency names, and compilability -- exactly (INV-1, B3). Exact declaration IDs decide
among independent topological orders, so this name-rendering golden compares output records by
their rendered name and only checks execution-order membership. `CUT-COMP-01` owns exact ordering.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sysml_codegen.extraction.expression_compiler import compile_calc_def
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import requires_license

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
GOLDEN_PATH = FIXTURES_DIR / "golden" / "calc_def_compilation_golden.json"
CALC_CORPUS_FIXTURES = sorted(json.loads(GOLDEN_PATH.read_text()))


def _golden() -> dict[str, dict[str, dict]]:
    return json.loads(GOLDEN_PATH.read_text())


def _live_calc_defs(model_name: str):
    extractor = SysMLDataExtractor([FIXTURES_DIR / model_name])
    try:
        loaded = extractor.load_models()
    except ImportError as exc:
        pytest.skip(f"syside unavailable: {exc}")
    if not loaded:
        pytest.skip(f"Could not load {model_name}")
    return extractor.extract_calculation_definitions()


def _result_to_dict(result, calc_def) -> dict:
    names = calc_def.member_names
    return {
        "calc_def_name": calc_def.name,
        "execution_order": [names[member_id] for member_id in result.execution_order],
        "output_results": [
            {
                "compilability": item.compilability.value,
                "input_refs": [names[member_id] for member_id in item.input_ids],
                "intermediate_refs": [
                    names[member_id] for member_id in item.dependency_ids
                ],
                "is_undeclared_intermediate": item.is_undeclared_intermediate,
                "output_name": item.output_name,
                "python_expression": item.python_expression,
                "unsupported_reason": item.unsupported_reason,
            }
            for item in result.output_results
        ],
        "overall_compilability": result.overall_compilability.value,
    }


def _assert_rendered_result(actual: dict, expected: dict, context: str) -> None:
    assert actual["calc_def_name"] == expected["calc_def_name"], context
    assert actual["overall_compilability"] == expected["overall_compilability"], context
    assert len(actual["execution_order"]) == len(set(actual["execution_order"])), context
    assert set(actual["execution_order"]) == set(expected["execution_order"]), context
    assert {
        item["output_name"]: item for item in actual["output_results"]
    } == {
        item["output_name"]: item for item in expected["output_results"]
    }, context


@requires_license
@pytest.mark.parametrize("fixture", CALC_CORPUS_FIXTURES)
def test_compile_calc_def_golden(fixture):
    golden = _golden()
    fixture_golden = golden.get(fixture)
    if fixture_golden is None:
        pytest.skip(f"{fixture}: no calc defs with output expressions in the golden")

    calc_defs = {cd.name: cd for cd in _live_calc_defs(fixture)}
    checked = 0
    for calc_def_name, expected in fixture_golden.items():
        calc_def = calc_defs[calc_def_name]
        result = compile_calc_def(calc_def)
        actual = _result_to_dict(result, calc_def)
        _assert_rendered_result(
            actual,
            expected,
            f"{fixture}/{calc_def_name}: {actual} != {expected}",
        )
        checked += 1

    assert checked == len(fixture_golden)
