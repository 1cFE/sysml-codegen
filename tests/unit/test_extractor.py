"""Unit tests for the extraction layer.

Tests:
- SysMLDataExtractor uses SysideAdapter from agentic-mbse
- No direct syside imports outside adapter
- No references to old sysml_to_teax name
"""

from __future__ import annotations

import ast
from pathlib import Path


def test_extractor_imports_from_agentic_mbse():
    """Verify SysMLDataExtractor uses agentic-mbse types."""
    from sysml_codegen.extraction.extractor import SysMLDataExtractor
    from agentic_mbse.sysml.syside_adapter import SysideAdapter

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
        assert "sysml_to_teax" not in content, (
            f"Reference to sysml_to_teax in {py_file}"
        )


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
    from sysml_codegen.extraction.data_models import CalculationDefinitionData

    # Check for required fields
    import inspect
    sig = inspect.signature(CalculationDefinitionData)
    params = list(sig.parameters.keys())

    assert "name" in params
    assert "qualified_name" in params
    assert "input_attributes" in params
    assert "output_attributes" in params
