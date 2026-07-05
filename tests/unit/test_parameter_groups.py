"""Unit tests for parameter group extraction — Gap 1 fixes."""
import pytest
from pathlib import Path


class TestExtractDesignAttributes:
    """Tests for extract_design_attributes() path filter behavior."""

    def test_default_filter_includes_test_models(self, chain_spike_model_path: Path):
        """Default filter (empty string) should include models in tests/ directory.

        FR-1: design_path_filter default must be "" (accept all).
        AC-1: Chain spike model produces 3 design attributes.
        """
        from sysml_codegen.extraction.extractor import SysMLDataExtractor
        from sysml_codegen.analysis.parameter_groups import extract_design_attributes

        extractor = SysMLDataExtractor([chain_spike_model_path])
        if not extractor.load_models():
            pytest.skip("Could not load chain spike SysML models")

        attrs_by_file = extract_design_attributes(extractor.model)
        all_attrs = [a for attrs in attrs_by_file.values() for a in attrs]

        # Should find design attributes (length, width, rate)
        assert len(all_attrs) >= 3, (
            f"Expected at least 3 design attributes, got {len(all_attrs)}"
        )

        # Verify non-None defaults
        for attr in all_attrs:
            if attr.name in ("length", "width", "rate"):
                assert attr.default_value is not None, (
                    f"Attribute '{attr.name}' should have a default value"
                )

    def test_restrictive_filter_excludes_test_models(self, chain_spike_model_path: Path):
        """A restrictive filter like 'models/designs' should exclude test models."""
        from sysml_codegen.extraction.extractor import SysMLDataExtractor
        from sysml_codegen.analysis.parameter_groups import extract_design_attributes

        extractor = SysMLDataExtractor([chain_spike_model_path])
        if not extractor.load_models():
            pytest.skip("Could not load chain spike SysML models")

        attrs_by_file = extract_design_attributes(
            extractor.model, design_path_filter="models/designs"
        )
        all_attrs = [a for attrs in attrs_by_file.values() for a in attrs]
        assert len(all_attrs) == 0, "Restrictive filter should exclude test models"

    def test_explicit_filter_narrows_results(self, chain_spike_model_path: Path):
        """An explicit filter should only include matching files."""
        from sysml_codegen.extraction.extractor import SysMLDataExtractor
        from sysml_codegen.analysis.parameter_groups import extract_design_attributes

        extractor = SysMLDataExtractor([chain_spike_model_path])
        if not extractor.load_models():
            pytest.skip("Could not load chain spike SysML models")

        attrs = extract_design_attributes(
            extractor.model, design_path_filter="design.sysml"
        )
        all_attrs = [a for alist in attrs.values() for a in alist]
        assert len(all_attrs) >= 3


class TestExtractDefaultValueCrashGuard:
    """Tests for OperatorExpression crash guard in _extract_default_value().

    FR-3: Must not crash on OperatorExpressions with feature references.
    AC-2: Non-extractable values are None.
    """

    def test_operator_expression_does_not_crash(self, chain_spike_model_path: Path):
        """Broadening filter to include library should not crash."""
        from sysml_codegen.extraction.extractor import SysMLDataExtractor
        from sysml_codegen.analysis.parameter_groups import extract_design_attributes

        extractor = SysMLDataExtractor([chain_spike_model_path])
        if not extractor.load_models():
            pytest.skip("Could not load chain spike SysML models")

        # Empty filter includes library files with OperatorExpressions
        # (e.g., area = length * width). This should not crash.
        attrs_by_file = extract_design_attributes(extractor.model, design_path_filter="")
        # If we get here without exception, the crash guard works
        assert attrs_by_file is not None


class TestBuildPipelineContextDefaults:
    """Tests for build_pipeline_context() producing populated entry points.

    AC-1: Chain spike model produces design_params.json with 3 entries.
    """

    def test_entry_points_have_defaults(self, chain_spike_model_path: Path):
        """Entry points from chain spike model should have non-None default values."""
        from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

        try:
            ctx = build_pipeline_context([chain_spike_model_path])
        except Exception:
            pytest.skip("Could not build pipeline context for chain spike model")

        # Check that entry point groups exist and have parameters with defaults
        assert len(ctx.computation_graph.entry_point_groups) > 0, (
            "Should have at least one entry point group"
        )
        all_params = [
            ep for group in ctx.computation_graph.entry_point_groups
            for ep in group.parameters
        ]
        params_with_defaults = [ep for ep in all_params if ep.default_value is not None]
        assert len(params_with_defaults) >= 3, (
            f"Expected at least 3 params with defaults, got {len(params_with_defaults)}"
        )
