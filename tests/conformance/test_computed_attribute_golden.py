"""Computed-attribute classifications against exact agentic evidence.

`tests/fixtures/golden/computed_attribute_golden.json` was captured live, over the whole
corpus, from `extract_computed_attributes` **before** its FORMULA branch was flipped onto
`extract_expression_ir`/`render_calc_expression` (the F4 rule). This test asserts the
post-flip `compiled_expression` and `compilability` reproduce exactly, per part+attribute.
The 0.1.3 evidence contract additionally refuses to infer a tentative chain when
SysIDE supplied no exact resolved target; those rows are recorded as unresolvable.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.extraction.computed_attribute_extractor import extract_computed_attributes
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import requires_license
from tests.helpers.corpus import corpus_fixture_names

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
GOLDEN_PATH = FIXTURES_DIR / "golden" / "computed_attribute_golden.json"
CALC_CORPUS_FIXTURES = corpus_fixture_names()


def _golden() -> dict[str, dict[str, dict]]:
    return json.loads(GOLDEN_PATH.read_text())


def _load_model(model_name: str):
    extractor = SysMLDataExtractor([FIXTURES_DIR / model_name])
    try:
        loaded = extractor.load_models()
    except ImportError as exc:
        pytest.skip(f"syside unavailable: {exc}")
    if not loaded:
        pytest.skip(f"Could not load {model_name}")
    return extractor.model


@requires_license
@pytest.mark.parametrize("fixture", CALC_CORPUS_FIXTURES)
def test_computed_attribute_golden(fixture):
    golden = _golden()
    fixture_golden = golden.get(fixture)
    if fixture_golden is None:
        pytest.skip(f"{fixture}: no computed attributes in the golden")

    model = _load_model(fixture)
    part_elements = list(SysideAdapter.elements_of_type(model, "PartDefinition"))
    part_elements.extend(SysideAdapter.elements_of_type(model, "PartUsage"))

    actual: dict[str, dict] = {}
    for part_elem in part_elements:
        calc_usage_names = {
            m.name for m in part_elem.owned_members
            if SysideAdapter.is_instance(m, "CalculationUsage")
        }
        computed, _aliases = extract_computed_attributes(None, part_elem, calc_usage_names)
        for ca in computed:
            key = f"{ca.owning_part_qualified_name}::{ca.name}"
            actual[key] = {
                "classification": ca.classification.value,
                "compilability": ca.compilability.value,
                "compiled_expression": ca.compiled_expression,
            }

    for key, expected in fixture_golden.items():
        assert key in actual, f"{fixture}: {key} missing from post-flip extraction"
        assert actual[key] == expected, f"{fixture}/{key}: {actual[key]} != {expected}"
