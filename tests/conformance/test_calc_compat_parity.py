"""Stage-0 parity proof: the calc-compat renderer reproduces `compile_expression` (D4 golden).

For every corpus calc def's output/intermediate expression, asserts
`extract_expression_ir` -> `render_calc_expression`/`collect_calc_refs` is byte-identical to
`tests/fixtures/golden/calc_compat_parity_golden.json` -- strings and ref lists captured live
from the old `build_expression_ast` -> `compile_expression`/`_collect_refs` path before it was
deleted (CONSTRAINT-EXEC Item 13 Phase 4, D4). This is the permanent successor to the
Phase-0/1-3 live old-vs-new parity test: it proved the swap was safe while both paths
existed; once `compile_expression` is gone there is nothing live left to compare against, so
its last act was freezing that comparison into this golden.

Name sets are derived exactly as `compile_calc_def` derives them (N1) -- not re-walked from
`owned_elements` -- so a green result here proves the production seam, not a synthetic stand-in.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from agentic_mbse.sysml.constraint_extraction import extract_expression_ir

from scripts.capture_extraction_snapshots import EXTRACTION_ONLY_MODELS, MODELS
from sysml_codegen.extraction.calc_compat_renderer import (
    collect_calc_refs,
    render_calc_expression,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import requires_license

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
GOLDEN_PATH = FIXTURES_DIR / "golden" / "calc_compat_parity_golden.json"

# The corpus `capture_extraction_snapshots.py` already covers (its MODELS +
# EXTRACTION_ONLY_MODELS), reused rather than re-listed so this test's corpus can never
# silently drift from the capture script's (N5: this set includes `return_styles`, whose
# two integer-literal outputs gate the literal rule).
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


@requires_license
@pytest.mark.parametrize("fixture", CALC_CORPUS_FIXTURES)
def test_calc_compat_parity(fixture):
    golden = _golden()
    fixture_golden = golden.get(fixture)
    if fixture_golden is None:
        pytest.skip(f"{fixture}: no calc output expressions in the golden")

    calc_defs = {cd.name: cd for cd in _live_calc_defs(fixture)}
    checked = 0
    for calc_def_name, expected_outputs in fixture_golden.items():
        calc_def = calc_defs[calc_def_name]

        # N1: the sets compile_calc_def actually derives, not a re-derivation.
        input_names = {a.name for a in calc_def.input_attributes}
        output_names = {a.name for a in calc_def.output_attributes}
        member_names = output_names | (calc_def.all_member_names or set())

        for name, expected in expected_outputs.items():
            node = calc_def.output_expression_asts[name]
            ir = extract_expression_ir(node)

            new_expr = render_calc_expression(ir, input_names, member_names)
            assert new_expr == expected["expr"], (
                f"{fixture}/{calc_def_name}.{name}: {new_expr!r} != {expected['expr']!r}"
            )

            new_refs = collect_calc_refs(ir, input_names, member_names)
            expected_refs = (expected["input_refs"], expected["intermediate_refs"])
            assert new_refs == expected_refs, (
                f"{fixture}/{calc_def_name}.{name}: refs {new_refs!r} != {expected_refs!r}"
            )
            checked += 1

    assert checked == sum(len(outs) for outs in fixture_golden.values())
