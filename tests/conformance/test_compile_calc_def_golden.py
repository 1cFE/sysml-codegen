"""Stage-1 golden: `compile_calc_def` is byte-identical after the seam flip.

`tests/fixtures/golden/calc_def_compilation_golden.json` was captured live, over the whole
calc-def corpus, from `compile_calc_def` **before** it was flipped onto
`extract_expression_ir`/`render_calc_expression`/`collect_calc_refs` (the F4 rule: the
comparand is the exact replaced function's output, not a downstream proxy). This test asserts
the post-flip `compile_calc_def` reproduces every field -- `python_expression`, `input_refs`,
`intermediate_refs`, `compilability`, and `execution_order` -- exactly (INV-1, B3).
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pytest

from scripts.capture_extraction_snapshots import EXTRACTION_ONLY_MODELS, MODELS
from sysml_codegen.extraction.expression_compiler import compile_calc_def
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import requires_license

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
GOLDEN_PATH = FIXTURES_DIR / "golden" / "calc_def_compilation_golden.json"
CALC_CORPUS_FIXTURES = sorted({**MODELS, **EXTRACTION_ONLY_MODELS})


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


def _result_to_dict(result) -> dict:
    data = asdict(result)
    data["overall_compilability"] = data["overall_compilability"].value
    for r in data["output_results"]:
        r["compilability"] = r["compilability"].value
    return data


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
        result = compile_calc_def(
            calc_def=calc_def,
            expression_asts=calc_def.output_expression_asts,
            all_member_names=calc_def.all_member_names or None,
            member_expressions=calc_def.member_expressions or None,
        )
        actual = _result_to_dict(result)
        assert actual == expected, f"{fixture}/{calc_def_name}: {actual} != {expected}"
        checked += 1

    assert checked == len(fixture_golden)
