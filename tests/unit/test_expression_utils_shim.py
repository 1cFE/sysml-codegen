"""Compatibility tests for the permanent expression_utils shim."""

from agentic_mbse.sysml import expression as shared

from sysml_codegen.extraction import expression_utils as shim


def test_expression_utils_shim_exports_segments_and_aliases_literal_name():
    assert "authored_chain_segments" in shim.__all__
    assert shim.is_literal_expression is shared.is_literal_node
    assert shim.reconstruct_expression is shared.reconstruct_expression
    assert shim.reconstruct_operator_expression is shared.reconstruct_operator_expression
    assert callable(shim.authored_chain_segments)
    assert not hasattr(shim, "extract_feature_chain_segments")
    assert shim.SysideAdapter is shared.SysideAdapter


def test_expression_utils_all_names_are_importable():
    for name in shim.__all__:
        assert getattr(shim, name) is not None
