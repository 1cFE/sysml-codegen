"""Unit tests for the extraction layer.

Tests:
- SysMLDataExtractor uses SysideAdapter from agentic-mbse
- No direct syside imports outside adapter
- No references to old sysml_to_teax name
"""

from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID


def test_extractor_imports_from_agentic_mbse():
    """Verify SysMLDataExtractor uses agentic-mbse types."""
    from agentic_mbse.sysml.syside_adapter import SysideAdapter

    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    # Verify the class uses SysideAdapter
    extractor = SysMLDataExtractor([])
    assert hasattr(extractor, "adapter")
    assert isinstance(extractor.adapter, SysideAdapter)


def test_no_direct_syside_imports():
    """Verify no direct syside imports outside adapter."""
    src_dir = Path(__file__).parent.parent.parent / "src" / "sysml_codegen"

    for py_file in src_dir.rglob("*.py"):
        content = py_file.read_text()

        # Skip empty files
        if not content.strip():
            continue

        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue  # Skip files with syntax errors

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("syside"), (
                        f"Direct syside import in {py_file}: {alias.name}"
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("syside"):
                    # Only syside_adapter.py should have direct syside imports
                    assert "syside_adapter" in str(py_file.name), (
                        f"Direct syside import in {py_file}: {node.module}"
                    )


def test_no_sysml_to_teax_references():
    """Verify no references to old sysml_to_teax name."""
    src_dir = Path(__file__).parent.parent.parent / "src" / "sysml_codegen"

    for py_file in src_dir.rglob("*.py"):
        content = py_file.read_text()
        assert "sysml_to_teax" not in content, f"Reference to sysml_to_teax in {py_file}"


def test_extractor_class_exists():
    """Verify SysMLDataExtractor can be imported."""
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    assert SysMLDataExtractor is not None


def test_extractor_has_required_methods():
    """Verify SysMLDataExtractor has required methods."""
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    extractor = SysMLDataExtractor([])

    # Check for required methods
    assert hasattr(extractor, "load_models")
    assert hasattr(extractor, "extract_calculation_definitions")
    assert callable(extractor.load_models)
    assert callable(extractor.extract_calculation_definitions)


def test_calculation_definition_data_structure():
    """Verify CalculationDefinitionData has expected fields."""
    # Check for required fields
    import inspect

    from sysml_codegen.extraction.data_models import CalculationDefinitionData

    sig = inspect.signature(CalculationDefinitionData)
    params = list(sig.parameters.keys())

    assert "name" in params
    assert "qualified_name" in params
    assert "input_attributes" in params
    assert "output_attributes" in params
    assert "element_id" in params
    assert "output_expression_asts_by_id" in params
    assert "all_member_ids" in params
    assert "member_expressions_by_id" in params
    assert "member_names_by_id" in params


def test_live_identity_sidecars_are_snapshot_excluded():
    """Live parser UUIDs cannot leak into the frozen snapshot-v5 envelope."""
    import dataclasses

    from sysml_codegen.extraction.data_models import (
        AttributeInfo,
        CalculationDefinitionData,
    )

    calc_fields = {field.name: field for field in dataclasses.fields(CalculationDefinitionData)}
    attr_fields = {field.name: field for field in dataclasses.fields(AttributeInfo)}
    for name in (
        "element_id",
        "output_expression_asts_by_id",
        "all_member_ids",
        "member_expressions_by_id",
        "member_names_by_id",
    ):
        assert calc_fields[name].metadata["snapshot_exclude"] is True
    assert attr_fields["element_id"].metadata["snapshot_exclude"] is True


def test_shared_extractor_leaves_unstable_live_identity_sidecar_empty():
    """Legacy extraction accepts members outside the exact route's UUID boundary."""
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    extractor = SysMLDataExtractor([])
    cases = (
        (None, UUID("00000000-0000-4000-8000-000000000001")),
        ("Pkg::Calc::unstable", UUID("00000000-0000-4000-8000-000000000002")),
    )
    for qualified_name, element_id in cases:
        member = SimpleNamespace(
            name="unstable_member",
            qualified_name=qualified_name,
            element_id=element_id,
            heritage=(),
            documentation=(),
            feature_value_expression=None,
            owned_memberships=(),
            cst_node=None,
        )

        extracted = extractor._extract_attribute(member, capture_element_id=True)

        assert extracted is not None
        assert extracted.element_id is None


def test_extract_expression_text_deleted():
    """_extract_expression_text is fully removed (DD-3: dead code removal)."""
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    extractor = SysMLDataExtractor([])
    assert not hasattr(extractor, "_extract_expression_text"), (
        "_extract_expression_text should be deleted after replacement "
        "with expression_utils.reconstruct_expression"
    )


def test_extractor_imports_reconstruct_expression():
    """extractor.py uses expression_utils.reconstruct_expression for calc_expressions."""
    source = (
        Path(__file__).parent.parent.parent
        / "src"
        / "sysml_codegen"
        / "extraction"
        / "extractor.py"
    )
    content = source.read_text()
    assert "from sysml_codegen.extraction.expression_utils import reconstruct_expression" in content


def test_operator_expression_classified_as_expression():
    """OperatorExpression binding -> BindingType.EXPRESSION, not UNBOUND."""
    from unittest.mock import MagicMock, patch

    from agentic_mbse.sysml.types import BindingType

    from sysml_codegen.extraction.usage_extractor import _extract_single_binding

    usage_elem = MagicMock()
    param_elem = MagicMock()
    param_elem.element_id = UUID("00000000-0000-5000-8000-000000000010")
    param_elem.qualified_name = "Pkg::Calc::test_param"
    param_elem.owned_redefinitions = ()
    mock_expr = MagicMock()
    param_elem.feature_value_expression = mock_expr

    # SysideAdapter.is_instance should return True only for OperatorExpression
    def mock_is_instance(obj, type_name):
        if obj is mock_expr and type_name == "OperatorExpression":
            return True
        return False

    with (
        patch(
            "sysml_codegen.extraction.usage_extractor.SysideAdapter.is_instance",
            side_effect=mock_is_instance,
        ),
        patch(
            "sysml_codegen.extraction.usage_extractor._is_literal_expression",
            return_value=False,
        ),
    ):
        result = _extract_single_binding(usage_elem, param_elem, "test_param", [])

    assert result.binding_type == BindingType.EXPRESSION
    assert result.param_name == "test_param"


def test_deep_chain_emits_full_path_chain_not_reject():
    """D1 (Item 2): a 3+-segment FeatureChainExpression extracts as a full-path CHAIN,
    not a hard-rejected UNBOUND. source_path carries every segment untruncated, and
    the deep-chain arm sets ONLY source_path (N-1: element refs stay unset)."""
    from unittest.mock import MagicMock, patch

    from agentic_mbse.sysml.types import BindingType

    from sysml_codegen.extraction.usage_extractor import _extract_single_binding

    usage_elem = MagicMock()
    param_elem = MagicMock()
    param_elem.element_id = UUID("00000000-0000-5000-8000-000000000011")
    param_elem.qualified_name = "Pkg::Calc::data_point"
    param_elem.owned_redefinitions = ()
    mock_expr = MagicMock()
    mock_expr.operands = []
    mock_expr.target_feature = None
    param_elem.feature_value_expression = mock_expr

    def mock_is_instance(obj, type_name):
        return obj is mock_expr and type_name == "FeatureChainExpression"

    warnings: list[str] = []
    with (
        patch(
            "sysml_codegen.extraction.usage_extractor.SysideAdapter.is_instance",
            side_effect=mock_is_instance,
        ),
        patch(
            "sysml_codegen.extraction.usage_extractor.extract_feature_chain_segments",
            return_value=["station", "array", "derived_calc", "derived_value"],
        ),
    ):
        result = _extract_single_binding(usage_elem, param_elem, "data_point", warnings)

    assert result.binding_type == BindingType.CHAIN
    assert result.source_path == "station.array.derived_calc.derived_value"  # full
    # N-1: element refs intentionally unset on the deep-chain arm
    assert result.source_instance_elem is None
    assert result.source_attribute_elem is None
    # No extraction-time warning: the loud diagnostic moved to the backtracker (D3)
    assert warnings == []


def test_operator_expression_stores_ast():
    """OperatorExpression binding stores raw AST on BindingInfo."""
    from unittest.mock import MagicMock, patch

    from sysml_codegen.extraction.usage_extractor import _extract_single_binding

    usage_elem = MagicMock()
    param_elem = MagicMock()
    param_elem.element_id = UUID("00000000-0000-5000-8000-000000000012")
    param_elem.qualified_name = "Pkg::Calc::test_param"
    param_elem.owned_redefinitions = ()
    mock_expr = MagicMock()
    param_elem.feature_value_expression = mock_expr

    def mock_is_instance(obj, type_name):
        if obj is mock_expr and type_name == "OperatorExpression":
            return True
        return False

    with (
        patch(
            "sysml_codegen.extraction.usage_extractor.SysideAdapter.is_instance",
            side_effect=mock_is_instance,
        ),
        patch(
            "sysml_codegen.extraction.usage_extractor._is_literal_expression",
            return_value=False,
        ),
    ):
        result = _extract_single_binding(usage_elem, param_elem, "test_param", [])

    assert result.expression_ast is mock_expr
