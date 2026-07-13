"""Stage-0 parity proof: the calc-compat renderer reproduces `compile_expression`.

For every corpus calc def's output/intermediate expression, asserts the new path
(`extract_expression_ir` -> `render_calc_expression`/`collect_calc_refs`) is byte-identical
to the old path (`build_expression_ast` -> `compile_expression`/`_collect_refs`), live, over
the whole calc-def corpus (design Stage 0, B1/B2/B4; plan Phase 0).

Name sets are derived exactly as `compile_calc_def` derives them (N1) -- not re-walked from
`owned_elements` -- so a green result here proves the production seam, not a synthetic stand-in.
No production caller has moved yet; this only proves the new path CAN replace the old one.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from agentic_mbse.sysml.constraint_extraction import extract_expression_ir

from scripts.capture_extraction_snapshots import EXTRACTION_ONLY_MODELS, MODELS
from sysml_codegen.extraction.calc_compat_renderer import (
    collect_calc_refs,
    render_calc_expression,
)
from sysml_codegen.extraction.expression_compiler import (
    CompilationError,
    _collect_refs,
    build_expression_ast,
    compile_expression,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import requires_license

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"

# The corpus `capture_extraction_snapshots.py` already covers (its MODELS +
# EXTRACTION_ONLY_MODELS), reused rather than re-listed so this test's corpus can never
# silently drift from the capture script's (N5: this set includes `return_styles`, whose
# two integer-literal outputs gate the literal rule).
CALC_CORPUS_FIXTURES = sorted({**MODELS, **EXTRACTION_ONLY_MODELS})


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
    calc_defs = _live_calc_defs(fixture)
    checked = 0
    for calc_def in calc_defs:
        if not calc_def.output_expression_asts:
            continue

        # N1: the sets compile_calc_def actually derives, not a re-derivation.
        input_names = {a.name for a in calc_def.input_attributes}
        output_names = {a.name for a in calc_def.output_attributes}
        member_names = output_names | (calc_def.all_member_names or set())

        for name, node in calc_def.output_expression_asts.items():
            old_ast = build_expression_ast(
                node, input_names, output_names, all_member_names=calc_def.all_member_names
            )
            ir = extract_expression_ir(node)

            try:
                old_expr = compile_expression(old_ast)
            except CompilationError:
                with pytest.raises(CompilationError):
                    render_calc_expression(ir, input_names, member_names)
                continue

            new_expr = render_calc_expression(ir, input_names, member_names)
            assert new_expr == old_expr, (
                f"{fixture}/{calc_def.name}.{name}: {new_expr!r} != {old_expr!r}"
            )

            old_refs = _collect_refs(old_ast)
            new_refs = collect_calc_refs(ir, input_names, member_names)
            assert new_refs == old_refs, (
                f"{fixture}/{calc_def.name}.{name}: refs {new_refs!r} != {old_refs!r}"
            )
            checked += 1

    if checked == 0:
        pytest.skip(f"{fixture}: no calc output expressions to compare")
