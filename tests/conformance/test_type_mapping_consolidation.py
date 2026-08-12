"""Conformance tests for Type Mapping Consolidation (X01).

Requirements: REQ-GEN-06
Design intent: 08-generation.md

Tests verify that SysML-to-Python type mapping is consistent across all
generators, using a single shared function from type_mapping.py.

The cross-generator consistency class read two committed extraction snapshots through
the v5 route and retired with the v5 family (retirement step 1). What remains is the
type-map table itself: the primitive mapping, the no-divergent-copies AST scan, and the
shared-module API. The map's CONTENT stays pinned by the literal sibling tables in
``test_gen_schemas.py`` and ``test_gen_module_wrappers.py``.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import jinja2
import pytest

from sysml_codegen.generation.type_mapping import (
    map_sysml_type_to_python,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SRC_DIR = Path(__file__).parent.parent.parent / "src" / "sysml_codegen"
TEMPLATE_DIR = SRC_DIR / "templates"

# Generator source files that should NOT have their own type mapping copies
GENERATOR_FILES_TO_CHECK = {
    "modules": "generation/modules.py",
    "entry_point": "generation/entry_point.py",
    "schemas": "generation/schemas.py",
    "stencils": "generation/stencils.py",
    "registry": "generation/registry.py",
}


# ===========================================================================
# REQ-GEN-06: Primitive type mapping (Real, Integer, Boolean, String)
# ===========================================================================
class TestPrimitiveMapping:
    """REQ-GEN-06: SysML-to-Python type mapping for primitive types."""

    @pytest.mark.req("REQ-GEN-06")
    def test_map_real_to_float(self):
        """Real (both forms) maps to float."""
        assert map_sysml_type_to_python("Real") == "float"
        assert map_sysml_type_to_python("ScalarValues::Real") == "float"

    @pytest.mark.req("REQ-GEN-06")
    def test_map_integer_to_int(self):
        """Integer (both forms) maps to int."""
        assert map_sysml_type_to_python("Integer") == "int"
        assert map_sysml_type_to_python("ScalarValues::Integer") == "int"

    @pytest.mark.req("REQ-GEN-06")
    def test_map_boolean_to_bool(self):
        """Boolean (both forms) maps to bool."""
        assert map_sysml_type_to_python("Boolean") == "bool"
        assert map_sysml_type_to_python("ScalarValues::Boolean") == "bool"

    @pytest.mark.req("REQ-GEN-06")
    def test_map_string_to_str(self):
        """String (both forms) maps to str."""
        assert map_sysml_type_to_python("String") == "str"
        assert map_sysml_type_to_python("ScalarValues::String") == "str"

    @pytest.mark.req("REQ-GEN-06")
    def test_unknown_type_passthrough(self):
        """Unknown types pass through unchanged."""
        assert map_sysml_type_to_python("PlasmaParams") == "PlasmaParams"
        assert map_sysml_type_to_python("MyCustomType") == "MyCustomType"


# ===========================================================================
# REQ-GEN-06: No divergent copies across generators
# ===========================================================================
class TestNoDivergentCopies:
    """REQ-GEN-06: Generators must not define their own type mapping functions."""

    @pytest.mark.req("REQ-GEN-06")
    @pytest.mark.parametrize(
        "module_id,rel_path,forbidden_functions",
        [
            ("modules", "generation/modules.py", ["_map_input_type"]),
            ("entry_point", "generation/entry_point.py", ["_map_input_type"]),
            ("schemas", "generation/schemas.py", ["_map_input_type", "_map_output_type"]),
            ("stencils", "generation/stencils.py", ["_map_input_type"]),
            ("registry", "generation/registry.py", ["_map_output_type"]),
        ],
        ids=["modules", "entry_point", "schemas", "stencils", "registry"],
    )
    def test_no_divergent_copies(self, module_id, rel_path, forbidden_functions):
        """Generator file does NOT define its own type mapping function."""
        source_path = SRC_DIR / rel_path
        source = source_path.read_text()
        tree = ast.parse(source)

        # Find all function definitions in the file
        defined_functions = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                defined_functions.add(node.name)

        for func_name in forbidden_functions:
            assert func_name not in defined_functions, (
                f"{rel_path} still defines {func_name}(). "
                f"Should use shared function from generation/type_mapping.py instead."
            )


# ===========================================================================
# REQ-GEN-06: Shared module exists and has correct API
# ===========================================================================
class TestSharedModuleAPI:
    """REQ-GEN-06: type_mapping.py provides the expected public API."""

    @pytest.mark.req("REQ-GEN-06")
    def test_type_mapping_module_exists(self):
        """type_mapping.py module exists and is importable."""
        from sysml_codegen.generation import type_mapping
        assert hasattr(type_mapping, "map_sysml_type_to_python")

    @pytest.mark.req("REQ-GEN-06")
    def test_sysml_to_python_dict_has_8_entries(self):
        """SYSML_TO_PYTHON dict covers all 4 types × 2 forms."""
        from sysml_codegen.generation.type_mapping import SYSML_TO_PYTHON
        assert len(SYSML_TO_PYTHON) == 8
