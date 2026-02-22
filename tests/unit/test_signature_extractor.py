"""Unit tests for signature extraction and field-level comparison.

Tests:
- FunctionSignature.matches() with identical, added, removed, renamed fields
- Field order independence in comparison
- None fallback for legacy files (FR-3)
- Type-level mismatch still detected with field info present
- Input field extraction from impl file AST
- Empty stub produces input_fields=None
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from sysml_codegen.analysis.signature_extractor import (
    FunctionSignature,
    extract_signature_from_impl,
)

# ---------------------------------------------------------------------------
# FunctionSignature.matches() -- field-level comparison
# ---------------------------------------------------------------------------


def test_matches_with_identical_fields():
    """Both signatures have same input_fields -> True."""
    sig_a = FunctionSignature("run_area", "AreaInput", "float", input_fields=["length", "width"])
    sig_b = FunctionSignature("run_area", "AreaInput", "float", input_fields=["length", "width"])
    assert sig_a.matches(sig_b)


def test_matches_detects_added_field():
    """Expected has extra field -> False."""
    existing = FunctionSignature("run_area", "AreaInput", "float", input_fields=["length", "width"])
    expected = FunctionSignature(
        "run_area", "AreaInput", "float", input_fields=["length", "width", "scale"]
    )
    assert not existing.matches(expected)


def test_matches_detects_removed_field():
    """Expected missing a field -> False."""
    existing = FunctionSignature(
        "run_area", "AreaInput", "float", input_fields=["length", "width", "scale"]
    )
    expected = FunctionSignature("run_area", "AreaInput", "float", input_fields=["length", "width"])
    assert not existing.matches(expected)


def test_matches_detects_renamed_field():
    """Field name changed -> False."""
    existing = FunctionSignature(
        "run_area", "AreaInput", "float", input_fields=["length", "width"]
    )
    expected = FunctionSignature(
        "run_area", "AreaInput", "float", input_fields=["length", "height"]
    )
    assert not existing.matches(expected)


def test_matches_field_order_independent():
    """Same fields in different order -> True."""
    sig_a = FunctionSignature("run_area", "AreaInput", "float", input_fields=["width", "length"])
    sig_b = FunctionSignature("run_area", "AreaInput", "float", input_fields=["length", "width"])
    assert sig_a.matches(sig_b)


def test_matches_none_fallback_extracted():
    """Extracted input_fields=None, expected has fields -> True (FR-3)."""
    existing = FunctionSignature("run_area", "AreaInput", "float", input_fields=None)
    expected = FunctionSignature("run_area", "AreaInput", "float", input_fields=["length", "width"])
    assert existing.matches(expected)


def test_matches_none_fallback_both():
    """Both None -> True."""
    sig_a = FunctionSignature("run_area", "AreaInput", "float", input_fields=None)
    sig_b = FunctionSignature("run_area", "AreaInput", "float", input_fields=None)
    assert sig_a.matches(sig_b)


def test_matches_type_change_still_detected():
    """Different input_type with same fields -> False (existing behavior)."""
    sig_a = FunctionSignature(
        "run_area", "AreaInput", "float", input_fields=["length", "width"]
    )
    sig_b = FunctionSignature(
        "run_area", "AreaInputV2", "float", input_fields=["length", "width"]
    )
    assert not sig_a.matches(sig_b)


def test_matches_return_type_change_still_detected():
    """Different return_type with same fields -> False."""
    sig_a = FunctionSignature(
        "run_area", "AreaInput", "float", input_fields=["length", "width"]
    )
    sig_b = FunctionSignature(
        "run_area", "AreaInput", "tuple[float, float]", input_fields=["length", "width"]
    )
    assert not sig_a.matches(sig_b)


# ---------------------------------------------------------------------------
# extract_signature_from_impl -- input field extraction
# ---------------------------------------------------------------------------


def test_extract_input_field_refs_from_impl(tmp_path: Path):
    """Impl with inputs.x attribute accesses -> correct field list."""
    impl = tmp_path / "area_impl.py"
    impl.write_text(
        textwrap.dedent("""\
        from pkg.modules.area import AreaInput

        def run_area(inputs: AreaInput) -> float:
            length = inputs.length
            width = inputs.width
            return length * width
        """)
    )
    sig = extract_signature_from_impl(impl)
    assert sig is not None
    assert sig.input_fields == ["length", "width"]


def test_extract_input_field_refs_empty_stub(tmp_path: Path):
    """Unmodified stub with only raise NotImplementedError -> input_fields is None."""
    impl = tmp_path / "area_impl.py"
    impl.write_text(
        textwrap.dedent('''\
        from pkg.modules.area import AreaInput

        def run_area(inputs: AreaInput) -> float:
            """Execute AreaCalc.

            Implementation Pattern:
                # Extract input fields from the validated Input model:
                length = inputs.length
                width = inputs.width
            """
            raise NotImplementedError("Manual implementation required")
        ''')
    )
    sig = extract_signature_from_impl(impl)
    assert sig is not None
    # Docstring inputs.X are string literals, not AST attribute accesses
    assert sig.input_fields is None


def test_extract_input_field_refs_auto_impl(tmp_path: Path):
    """Auto-generated impl with inputs.X in expressions -> correct field list."""
    impl = tmp_path / "area_impl.py"
    impl.write_text(
        textwrap.dedent("""\
        AUTO_IMPLEMENTED = True

        from pkg.modules.area import AreaInput

        def run_area(inputs: AreaInput) -> float:
            return (inputs.length * inputs.width)
        """)
    )
    sig = extract_signature_from_impl(impl)
    assert sig is not None
    assert sig.input_fields == ["length", "width"]


def test_extract_nonexistent_file(tmp_path: Path):
    """Nonexistent file returns None."""
    sig = extract_signature_from_impl(tmp_path / "does_not_exist.py")
    assert sig is None
