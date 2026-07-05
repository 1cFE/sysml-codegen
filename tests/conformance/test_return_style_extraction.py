"""Conformance tests for return-style and bare-parameter extraction (SC-2).

The calc-def member filter used to keep only ``AttributeUsage`` members, so
named ``return`` and bare ``in`` parameters (which syside models as
``ReferenceUsage``) vanished. The relaxed filter admits any direction-carrying
member; an anonymous ``return`` (unnamed result) now gets its own diagnostic
(V8) instead of the generic zero-output error (V7).

Two test layers:

- **Live extractor tests** (skip without a syside license) prove the raw
  extraction shape end-to-end: auto-impl AST presence, the V8 raise, the
  reworded V7, no double-ingestion. They mirror the ``_load_live_extractor``
  convention in ``test_extractor.py``.
- **Offline snapshot tests** (license-free) assert the committed
  ``return_styles`` snapshot's I/O and its ``compilation_results`` keys, which
  pin auto-impl (style B present, style D absent) without a live parser.

REQ-EXT-10: direction-carrying ReferenceUsage members (named return, bare in)
            are extracted; named inline return auto-implements.
REQ-EXT-11: anonymous return raises the V8 diagnostic, before V7.
REQ-EXT-12: the return-attribute + body-assignment form extracts its output
            once, with no phantom member (no double-ingestion).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.extraction.data_models import CalculationDefinitionData
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.snapshot import load_extraction_snapshot
from tests.conftest import snapshot_fixture

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"


def _load_live_extractor(model_name: str) -> SysMLDataExtractor:
    """Load a fixture model with a live extractor.

    Skips (does not fail) when syside cannot load -- e.g. no license in CI --
    mirroring the ``_load_live_extractor`` helper in ``test_extractor.py``.
    """
    extractor = SysMLDataExtractor([FIXTURES_DIR / model_name])
    try:
        loaded = extractor.load_models()
    except ImportError as exc:  # syside license not configured
        pytest.skip(f"syside unavailable: {exc}")
    if not loaded:
        pytest.skip(f"Could not load {model_name}")
    return extractor


def _live_calc_defs(model_name: str) -> dict[str, CalculationDefinitionData]:
    """Extract a fixture model live and return its calc defs keyed by name."""
    extractor = _load_live_extractor(model_name)
    return {cd.name: cd for cd in extractor.extract_calculation_definitions()}


# ---------------------------------------------------------------------------
# Live extractor tests (REQ-EXT-10/11/12) -- license-gated
# ---------------------------------------------------------------------------


@pytest.mark.req(id="REQ-EXT-10")
class TestReqExt10DirectionCarryingReferenceUsage:
    """Named return and bare in extract; named inline return auto-implements."""

    def test_named_return_autoimpls(self) -> None:
        """Style B: `return y : Real = expr;` -> output `y` with a captured AST
        (auto-impl, not a stencil) -- I5."""
        cd = _live_calc_defs("return_styles")["NamedReturnB"]
        assert "y" in {a.name for a in cd.output_attributes}
        assert cd.output_expression_asts.get("y"), (
            "named inline return must carry a captured expression AST"
        )

    def test_bare_in_extracted(self) -> None:
        """Bare `in x : Real;` (ReferenceUsage In) lands in input_attributes."""
        cd = _live_calc_defs("return_styles")["BareInC"]
        assert "x" in {a.name for a in cd.input_attributes}

    def test_control_style_unchanged(self) -> None:
        """Style A control: `in attribute`/`out attribute` extract as before."""
        cd = _live_calc_defs("return_styles")["ControlA"]
        assert "a" in {a.name for a in cd.input_attributes}
        assert "y" in {a.name for a in cd.output_attributes}
        assert cd.output_expression_asts.get("y")


@pytest.mark.req(id="REQ-EXT-12")
class TestReqExt12NoDoubleIngestion:
    """The return-attribute + body-assignment form yields one output, no phantom."""

    def test_body_assignment_single_output_no_phantom(self) -> None:
        cd = _live_calc_defs("return_styles")["StyleD"]
        output_names = [a.name for a in cd.output_attributes]
        assert output_names.count("y") == 1, (
            f"style D must extract `y` exactly once, got {output_names}"
        )
        # The direction-None body-assignment ReferenceUsage must not leak as a
        # phantom intermediate member.
        assert "y" not in cd.member_expressions
        # Degraded: no auto-impl for the body-assignment form (expression capture
        # deferred -- see backlog note).
        assert not cd.output_expression_asts.get("y")


@pytest.mark.req(id="REQ-EXT-11")
class TestReqExt11AnonymousReturnDiagnostic:
    """Anonymous return raises the V8 diagnostic (name the result), not V7."""

    def test_anonymous_return_raises_v8(self) -> None:
        extractor = _load_live_extractor("anonymous_return")
        with pytest.raises(ValueError, match="anonymous `return`") as exc:
            extractor.extract_calculation_definitions()
        message = str(exc.value)
        # V8's fix-naming text, not V7's generic zero-output message.
        assert "Give the result a name" in message
        assert "zero output attributes" not in message


@pytest.mark.req(id="REQ-EXT-08")
class TestV7Reworded:
    """The V7 zero-output message no longer claims return/bare-in are
    'not yet extracted (Item 3)'."""

    def test_v7_no_longer_says_not_yet_extracted(self) -> None:
        extractor = _load_live_extractor("zero_output_calc")
        with pytest.raises(ValueError, match="zero output attributes") as exc:
            extractor.extract_calculation_definitions()
        message = str(exc.value)
        assert "not yet extracted" not in message
        assert "Item 3" not in message


# ---------------------------------------------------------------------------
# Offline snapshot tests (REQ-EXT-10/12) -- license-free
# ---------------------------------------------------------------------------


def _snapshot_calc_defs() -> dict[str, CalculationDefinitionData]:
    snap = load_extraction_snapshot(snapshot_fixture("return_styles"))
    return {cd.name: cd for cd in snap["calc_defs"]}


@pytest.mark.req(id="REQ-EXT-10")
class TestReturnStylesSnapshotIO:
    """Offline I/O assertions on the committed return_styles snapshot."""

    def test_all_four_styles_present(self) -> None:
        defs = _snapshot_calc_defs()
        assert set(defs) == {"ControlA", "NamedReturnB", "BareInC", "StyleD"}

    def test_named_return_output(self) -> None:
        cd = _snapshot_calc_defs()["NamedReturnB"]
        assert [a.name for a in cd.input_attributes] == ["b"]
        assert [a.name for a in cd.output_attributes] == ["y"]

    def test_bare_in_input(self) -> None:
        cd = _snapshot_calc_defs()["BareInC"]
        assert "x" in {a.name for a in cd.input_attributes}
        assert [a.name for a in cd.output_attributes] == ["y"]

    def test_style_d_single_output(self) -> None:
        cd = _snapshot_calc_defs()["StyleD"]
        assert [a.name for a in cd.output_attributes].count("y") == 1


@pytest.mark.req(id="REQ-EXT-10")
class TestReturnStylesCompilationResults:
    """The snapshot's compilation_results block pins auto-impl offline (D4/M2)."""

    def test_style_b_compiled_style_d_absent(self) -> None:
        snap = load_extraction_snapshot(snapshot_fixture("return_styles"))
        keys = snap["compilation_results"].keys()
        # Style B's inline return expression compiled -> auto-impl.
        assert "NamedReturnB" in keys
        # Style D is EXPECTED degraded: no captured expression -> no compilation
        # entry. See the body-assignment-capture backlog note.
        assert "StyleD" not in keys
