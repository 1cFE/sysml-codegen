"""Unit tests for Step 4.5: FORMULA filtering from design_attrs.

Tests the _remove_formula_from_design_attrs() helper that removes FORMULA
computed attributes from the design_attrs dict before ParameterGroupDeriver
processes them (preventing false entry points).
"""

from pathlib import Path

from sysml_codegen.analysis.parameter_groups import DesignAttributeData
from sysml_codegen.extraction.data_models import (
    ComputedAttributeClassification,
    ComputedAttributeData,
)
from sysml_codegen.extraction.expression_compiler import Compilability


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _make_design_attr(
    name: str, parent_part: str, qualified_name: str
) -> DesignAttributeData:
    """Helper to create a DesignAttributeData with minimal fields."""
    return DesignAttributeData(
        name=name,
        sysml_type="Real",
        default_value="1.0",
        unit=None,
        source_file=Path("test.sysml"),
        source_line=1,
        parent_part=parent_part,
        qualified_name=qualified_name,
    )


def _make_computed_attr(
    name: str,
    owning_part_name: str,
    owning_part_qn: str,
    classification: ComputedAttributeClassification,
    compilability: Compilability = Compilability.FULLY_COMPILABLE,
    compiled_expression: str | None = None,
) -> ComputedAttributeData:
    """Helper to create a ComputedAttributeData with minimal fields."""
    return ComputedAttributeData(
        name=name,
        python_name=name,
        owning_part_name=owning_part_name,
        owning_part_qualified_name=owning_part_qn,
        expression_ast=None,
        expression_text=f"{name} expression",
        references=[],
        classification=classification,
        compilability=compilability,
        compiled_expression=compiled_expression,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestFormulaRemovalFromDesignAttrs:
    """Test that FORMULA attributes are removed from design_attrs dict."""

    def test_formula_removed_expose_preserved(self):
        """FORMULA attrs removed, EXPOSE_PURE and plain design attrs kept."""
        from sysml_codegen.orchestration.pipeline_builder import (
            _remove_formula_from_design_attrs,
        )

        design_attrs = {
            Path("test.sysml"): [
                _make_design_attr("area", "Part", "Pkg__Part__area"),
                _make_design_attr("length", "Part", "Pkg__Part__length"),
            ]
        }
        computed_attrs = [
            _make_computed_attr(
                "area", "Part", "Pkg::Part",
                ComputedAttributeClassification.FORMULA,
            ),
            _make_computed_attr(
                "eta", "Part", "Pkg::Part",
                ComputedAttributeClassification.EXPOSE_PURE,
            ),
        ]

        removed = _remove_formula_from_design_attrs(computed_attrs, design_attrs)

        # "area" removed (FORMULA), "length" preserved (not computed)
        assert removed == 1
        remaining = design_attrs[Path("test.sysml")]
        assert len(remaining) == 1
        assert remaining[0].name == "length"

    def test_empty_computed_attrs_no_op(self):
        """No computed attrs -> design_attrs unchanged."""
        from sysml_codegen.orchestration.pipeline_builder import (
            _remove_formula_from_design_attrs,
        )

        design_attrs = {
            Path("test.sysml"): [
                _make_design_attr("length", "Part", "Pkg__Part__length"),
                _make_design_attr("width", "Part", "Pkg__Part__width"),
            ]
        }

        removed = _remove_formula_from_design_attrs([], design_attrs)

        assert removed == 0
        assert len(design_attrs[Path("test.sysml")]) == 2

    def test_formula_qn_format_matches_design_attr_qn(self):
        """Verify the QN format built from ComputedAttributeData matches
        DesignAttributeData.qualified_name (produced by build_element_qualified_name).

        Uses realistic QN format: "Package__Part__attr".
        """
        from sysml_codegen.orchestration.pipeline_builder import (
            _remove_formula_from_design_attrs,
        )

        design_attrs = {
            Path("design.sysml"): [
                _make_design_attr(
                    "area", "probe_design",
                    "AttrExprProbeDesign__probe_design__area",
                ),
            ]
        }
        computed_attrs = [
            _make_computed_attr(
                "area", "probe_design",
                "AttrExprProbeDesign::probe_design",
                ComputedAttributeClassification.FORMULA,
            ),
        ]

        removed = _remove_formula_from_design_attrs(computed_attrs, design_attrs)

        assert removed == 1
        assert len(design_attrs[Path("design.sysml")]) == 0

    def test_expose_computed_preserved_in_design_attrs(self):
        """EXPOSE_COMPUTED attributes are NOT removed from design_attrs."""
        from sysml_codegen.orchestration.pipeline_builder import (
            _remove_formula_from_design_attrs,
        )

        design_attrs = {
            Path("test.sysml"): [
                _make_design_attr("scaled", "Part", "Pkg__Part__scaled"),
            ]
        }
        computed_attrs = [
            _make_computed_attr(
                "scaled", "Part", "Pkg::Part",
                ComputedAttributeClassification.EXPOSE_COMPUTED,
            ),
        ]

        removed = _remove_formula_from_design_attrs(computed_attrs, design_attrs)

        assert removed == 0
        assert len(design_attrs[Path("test.sysml")]) == 1

    def test_multiple_files_filtered_independently(self):
        """FORMULA removal works across multiple source files."""
        from sysml_codegen.orchestration.pipeline_builder import (
            _remove_formula_from_design_attrs,
        )

        design_attrs = {
            Path("file1.sysml"): [
                _make_design_attr("area", "Part", "Pkg__Part__area"),
                _make_design_attr("length", "Part", "Pkg__Part__length"),
            ],
            Path("file2.sysml"): [
                _make_design_attr("cost", "Part", "Pkg__Part__cost"),
            ],
        }
        computed_attrs = [
            _make_computed_attr(
                "area", "Part", "Pkg::Part",
                ComputedAttributeClassification.FORMULA,
            ),
            _make_computed_attr(
                "cost", "Part", "Pkg::Part",
                ComputedAttributeClassification.FORMULA,
            ),
        ]

        removed = _remove_formula_from_design_attrs(computed_attrs, design_attrs)

        assert removed == 2
        assert len(design_attrs[Path("file1.sysml")]) == 1
        assert design_attrs[Path("file1.sysml")][0].name == "length"
        assert len(design_attrs[Path("file2.sysml")]) == 0

    def test_manual_required_formula_not_removed(self):
        """FORMULA with MANUAL_REQUIRED compilability is still removed.

        The classification (FORMULA) determines removal, not compilability.
        Even MANUAL_REQUIRED FORMULAs should not create entry points.
        """
        from sysml_codegen.orchestration.pipeline_builder import (
            _remove_formula_from_design_attrs,
        )

        design_attrs = {
            Path("test.sysml"): [
                _make_design_attr("broken_formula", "Part", "Pkg__Part__broken_formula"),
            ]
        }
        computed_attrs = [
            _make_computed_attr(
                "broken_formula", "Part", "Pkg::Part",
                ComputedAttributeClassification.FORMULA,
                compilability=Compilability.MANUAL_REQUIRED,
            ),
        ]

        removed = _remove_formula_from_design_attrs(computed_attrs, design_attrs)

        assert removed == 1
        assert len(design_attrs[Path("test.sysml")]) == 0
